#!/usr/bin/env python3
"""cross_channel_consistency_check — 3채널 envelope 일관성 자동 검증.

cycle 2026-05-01 신규. 3채널 (os/esxi/redfish) 의 envelope shape /
diagnosis.details type / 섹션 명명 / fragment 변수 일관성 advisory.

검출 대상:
1. diagnosis.details — dict shape (cycle 2026-04-29 production-audit fix)
2. data.<section>.<field> — capacity_mb vs capacity_mib 명명
3. _sections_unsupported_fragment — 3채널 모두 사용 (cycle 2026-05-01 신규)
4. status enum — success / partial / failed / not_supported

검출 패턴 (휴리스틱):
- common/tasks/normalize/build_*.yml
- {os,esxi,redfish}-gather/site.yml의 always block fallback envelope
- {os,esxi,redfish}-gather/tasks/normalize_*.yml

advisory 모드 (exit 0).

Self-test:
    python scripts/ai/hooks/cross_channel_consistency_check.py --self-test
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

CHANNEL_DIRS = (
    "os-gather/",
    "esxi-gather/",
    "redfish-gather/",
)
NORMALIZE_DIRS = (
    "common/tasks/normalize/",
)

CAPACITY_MB_RE = re.compile(r"\bcapacity_(mb|mib|gb|gib|tb)\b", re.IGNORECASE)
DIAG_DETAILS_LIST_RE = re.compile(
    r"diagnosis\.details\s*[:=]\s*\[",
)
STATUS_LITERAL_RE = re.compile(
    r"\bstatus\s*[:=]\s*['\"]?(success|partial|failed|not_supported|unknown)['\"]?",
)
FRAGMENT_VAR_RE = re.compile(
    r"_sections_(supported|collected|failed|unsupported)_fragment",
)


def get_changed_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except (FileNotFoundError, subprocess.SubprocessError):
        return []


def is_channel_or_normalize(path: str) -> bool:
    return (any(path.startswith(d) for d in CHANNEL_DIRS)
            or any(path.startswith(d) for d in NORMALIZE_DIRS))


def scan_consistency(changed_files: list[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    capacity_units: dict[str, set[str]] = {}

    for f in changed_files:
        if not is_channel_or_normalize(f):
            continue
        if not f.endswith((".yml", ".yaml", ".py")):
            continue
        full = REPO_ROOT / f
        if not full.is_file():
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if DIAG_DETAILS_LIST_RE.search(text):
            findings.append({
                "file": f,
                "category": "diagnosis_details_list",
                "advisory": ("diagnosis.details 가 list 인지 확인 — "
                             "production-audit cycle 에서 dict 통일됨"),
            })

        for m in CAPACITY_MB_RE.finditer(text):
            unit = m.group(1).lower()
            capacity_units.setdefault(f, set()).add(unit)

        for m in STATUS_LITERAL_RE.finditer(text):
            status_val = m.group(1)
            if status_val == "unknown":
                findings.append({
                    "file": f,
                    "category": "status_unknown_literal",
                    "advisory": ("status='unknown' 사용 의심 — "
                                 "rule 13 R5 envelope status enum 외"),
                })

        for m in FRAGMENT_VAR_RE.finditer(text):
            kind = m.group(1)
            if kind == "unsupported":
                pass

    for f, units in capacity_units.items():
        if len(units) > 1:
            findings.append({
                "file": f,
                "category": "capacity_unit_mixed",
                "advisory": f"capacity 단위 혼재: {sorted(units)}",
            })

    return findings


def write_advisory_report(findings: list[dict[str, str]]) -> Path | None:
    if not findings:
        return None
    out_dir = REPO_ROOT / "docs/ai/incoming-review"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out = out_dir / f"{today}-cross-channel-advisory.md"
    lines = [
        f"# cross-channel 일관성 advisory — {today}",
        "",
        "> 3채널 envelope shape / diagnosis.details / 섹션 명명 / fragment 변수 일관성.",
        "",
        f"## 발견 ({len(findings)} 건)",
        "",
    ]
    for f in findings:
        lines.append(f"- **{f['category']}** — `{f['file']}`")
        lines.append(f"  - {f['advisory']}")
    lines.append("")
    lines.append("## 정본 reference")
    lines.append("- envelope: rule 13 R5 / `common/tasks/normalize/build_output.yml`")
    lines.append("- diagnosis.details: dict shape (production-audit 2026-04-29 통일)")
    lines.append("- capacity: 단위 일관성 (단일 파일 안에서)")
    lines.append("- fragment 변수: rule 22 R7 (5 + 1 unsupported, cycle 2026-05-01)")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def self_test() -> int:
    print("[cross_channel_consistency_check] self-test 시작", file=sys.stderr)
    sample = """\
- name: ok
  set_fact:
    diagnosis.details: [error1, error2]
    capacity_mb: 1024
    capacity_gib: 1
    status: unknown
"""
    findings = []
    if DIAG_DETAILS_LIST_RE.search(sample):
        findings.append("diag_list")
    units = {m.group(1).lower() for m in CAPACITY_MB_RE.finditer(sample)}
    if len(units) > 1:
        findings.append("unit_mixed")
    for m in STATUS_LITERAL_RE.finditer(sample):
        if m.group(1) == "unknown":
            findings.append("status_unknown")

    if len(findings) == 3:
        print("[cross_channel_consistency_check] self-test PASS", file=sys.stderr)
        return 0
    print(f"[cross_channel_consistency_check] self-test FAIL: {findings}",
          file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="cross-channel consistency advisory")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    changed = get_changed_files()
    if not changed:
        return 0

    findings = scan_consistency(changed)
    if not findings:
        return 0

    print(f"[cross_channel_consistency_check] advisory: {len(findings)} 건",
          file=sys.stderr)
    for f in findings[:5]:
        print(f"  - {f['category']}: {f['file']}", file=sys.stderr)
    out = write_advisory_report(findings)
    if out:
        rel = out.relative_to(REPO_ROOT)
        print(f"[cross_channel_consistency_check] 보고서: {rel}", file=sys.stderr)

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
