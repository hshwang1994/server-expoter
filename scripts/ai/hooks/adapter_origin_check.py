#!/usr/bin/env python3
"""adapter_origin_check — adapter YAML origin 주석 자동 검증.

cycle 2026-05-01 신규. rule 96 R1 + R1-A 자동 검증 hook.

adapter YAML 변경 시 다음 4종 origin sources 중 1개 이상 주석 의무:
1. vendor 공식 docs URL
2. DMTF Redfish 표준 URL (redfish.dmtf.org)
3. GitHub issue / community URL
4. tests/evidence/ 사이트 실측 reference

검출 패턴 — adapter 파일 상단 (priority: 이전) 주석에서:
- `# source:` 또는 `# 원본 위치:` 또는 `# 출처:` 라인
- `# tested_against:` (펌웨어 list)
- `# evidence:` (tests/evidence/ 경로)
- `# lab:` (있음/부재)

advisory 모드 (exit 0). 발견 시 stderr 경고 + 보고서.

Self-test:
    python scripts/ai/hooks/adapter_origin_check.py --self-test
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

ADAPTER_DIRS = (
    "adapters/redfish/",
    "adapters/os/",
    "adapters/esxi/",
)

# 사이트 검증 PASS adapter (cycle 2026-05-06 commit `0a485823`).
# 본 adapter 들의 origin 주석에는 `lab tested` / `Lab status: PASS` /
# `사이트 검증` 또는 사이트 IP / commit hash 표기가 있어야 함 (rule 96 R1-A).
SITE_VERIFIED_ADAPTERS = {
    "adapters/redfish/dell_idrac10.yml",
    "adapters/redfish/hpe_ilo7.yml",
    "adapters/redfish/lenovo_xcc3.yml",
    "adapters/redfish/cisco_ucs_xseries.yml",
}

# Generic fallback adapter — vendor 특정 없음. lab_status / next_action 면제.
# (rule 96 R1-A 의무는 vendor-specific adapter 에 한정)
GENERIC_FALLBACK_ADAPTERS = {
    "adapters/redfish/redfish_generic.yml",
}

SITE_VERIFIED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"lab\s+tested", re.IGNORECASE),
    re.compile(r"Lab\s*status\s*:\s*PASS", re.IGNORECASE),
    re.compile(r"사이트\s*검증", re.IGNORECASE),
    re.compile(r"0a485823", re.IGNORECASE),  # cycle 2026-05-06 site validation commit
    re.compile(r"Tested\s+against\b", re.IGNORECASE),
)

LAB_ABSENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"부재", re.IGNORECASE),
    re.compile(r"lab\s*:\s*부재", re.IGNORECASE),
    re.compile(r"Lab\s*status\s*:\s*부재", re.IGNORECASE),
    re.compile(r"web\s+sources?\s+only", re.IGNORECASE),
)

NEXT_ACTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"#\s*Next\s*action\s*:", re.IGNORECASE),
    re.compile(r"#\s*next_action\s*:", re.IGNORECASE),
    re.compile(r"lab\s+도입\s+후\s+별도\s+cycle", re.IGNORECASE),
    re.compile(r"capture-site-fixture", re.IGNORECASE),
)

ORIGIN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*#\s*source\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*sources\s*(?:\(|:)", re.IGNORECASE),
    re.compile(r"^\s*#\s*origin\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*last\s*sync\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*lab\s*status\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*tested\s*against", re.IGNORECASE),
    re.compile(r"^\s*#\s*원본\s*위치", re.IGNORECASE),
    re.compile(r"^\s*#\s*출처", re.IGNORECASE),
    re.compile(r"^\s*#\s*tested_against\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*evidence\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*lab\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*마지막\s*동기화\s*확인", re.IGNORECASE),
    re.compile(r"redfish\.dmtf\.org|dmtf\.org/standards/redfish", re.IGNORECASE),
    re.compile(r"developer\.dell\.com", re.IGNORECASE),
    re.compile(r"support\.hpe\.com|support\.huawei\.com|support\.ts\.fujitsu\.com", re.IGNORECASE),
    re.compile(r"pubs\.lenovo\.com|lenovopress\.lenovo\.com|cisco\.com|supermicro\.com", re.IGNORECASE),
    re.compile(r"inspur\.com|quantaqct\.com|github\.com/Huawei|hewlettpackard\.github\.io", re.IGNORECASE),
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


def is_adapter_yaml(path: str) -> bool:
    return any(path.startswith(d) for d in ADAPTER_DIRS) and path.endswith((".yml", ".yaml"))


def has_origin_annotation(text: str) -> bool:
    """adapter 헤더 영역 (priority: 이전 또는 첫 80 줄) 에 origin 주석 있는지.

    cycle 2026-05-07 M-K1: 40 → 80 으로 확장 (origin 주석이 긴 adapter 대응).
    """
    head_lines = text.splitlines()[:80]
    for line in head_lines:
        if any(p.search(line) for p in ORIGIN_PATTERNS):
            return True
    return False


def header_section(text: str, max_lines: int = 80) -> str:
    """adapter 헤더 영역 (priority: 이전 또는 첫 max_lines 줄) 텍스트 반환."""
    lines = text.splitlines()
    out: list[str] = []
    for line in lines[:max_lines]:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped != "---":
            # YAML body 진입 — 헤더 끝
            break
        out.append(line)
    return "\n".join(out)


def has_site_verified_marker(header: str) -> bool:
    return any(p.search(header) for p in SITE_VERIFIED_PATTERNS)


def has_lab_absent_marker(header: str) -> bool:
    return any(p.search(header) for p in LAB_ABSENT_PATTERNS)


def has_next_action_marker(header: str) -> bool:
    return any(p.search(header) for p in NEXT_ACTION_PATTERNS)


def list_all_adapters() -> list[Path]:
    paths: list[Path] = []
    for d in ADAPTER_DIRS:
        base = REPO_ROOT / d
        if not base.is_dir():
            continue
        paths.extend(sorted(base.glob("*.yml")))
        paths.extend(sorted(base.glob("*.yaml")))
    return paths


def scan_all_adapters() -> list[dict[str, str]]:
    """cycle 2026-05-07 M-K1: 30 adapter 전수 일관성 검증.

    검사 항목 (rule 96 R1 + R1-A + R1-C):
    - origin sources 1개 이상 (기존 ORIGIN_PATTERNS)
    - 사이트 검증 adapter — `lab tested` / `Lab status: PASS` / 사이트 IP / commit hash 표기
    - lab 부재 adapter — `부재` 표기 + next_action 라인 (rule 96 R1-C)

    advisory 모드 — 위반 시 stderr 경고 + 보고서.
    """
    findings: list[dict[str, str]] = []
    for full in list_all_adapters():
        rel = full.relative_to(REPO_ROOT).as_posix()
        try:
            text = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if not has_origin_annotation(text):
            findings.append({
                "file": rel,
                "category": "missing_origin",
                "advisory": "adapter origin 주석 부재 (rule 96 R1)",
            })
            continue

        # redfish 채널 한정 lab_status / next_action 검증 (OS / ESXi 는 본 cycle 범위 외)
        if not rel.startswith("adapters/redfish/"):
            continue

        # generic fallback adapter 는 vendor 특정 없음 — 면제
        if rel in GENERIC_FALLBACK_ADAPTERS:
            continue

        header = header_section(text)
        is_site = rel in SITE_VERIFIED_ADAPTERS

        if is_site:
            if not has_site_verified_marker(header):
                findings.append({
                    "file": rel,
                    "category": "site_verified_missing_marker",
                    "advisory": (
                        "사이트 검증 adapter 인데 `lab tested` / `Lab status: PASS` / "
                        "사이트 검증 / commit 표기 부재 (rule 96 R1-A)"
                    ),
                })
        else:
            if not has_lab_absent_marker(header):
                findings.append({
                    "file": rel,
                    "category": "lab_absent_marker",
                    "advisory": "lab 부재 adapter 인데 `부재` / `web sources` 명시 부재 (rule 96 R1-A)",
                })
            if not has_next_action_marker(header):
                findings.append({
                    "file": rel,
                    "category": "next_action_missing",
                    "advisory": (
                        "lab 부재 adapter 인데 `Next action:` 또는 `lab 도입 후 별도 cycle` "
                        "라인 부재 (rule 96 R1-C)"
                    ),
                })

    return findings


def scan_adapters(changed_files: list[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for f in changed_files:
        if not is_adapter_yaml(f):
            continue
        full = REPO_ROOT / f
        if not full.is_file():
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if not has_origin_annotation(text):
            findings.append({
                "file": f,
                "category": "missing_origin",
                "advisory": "adapter origin 주석 부재 (rule 96 R1)",
            })

    return findings


def write_advisory_report(findings: list[dict[str, str]]) -> Path | None:
    if not findings:
        return None
    out_dir = REPO_ROOT / "docs/ai/incoming-review"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out = out_dir / f"{today}-adapter-origin-advisory.md"
    lines = [
        f"# adapter origin 주석 advisory — {today}",
        "",
        "> rule 96 R1 + R1-A 자동 검출. adapter 변경 시 origin sources 1개 이상 의무.",
        "",
        f"## 발견 ({len(findings)} 건)",
        "",
    ]
    for f in findings:
        lines.append(f"- `{f['file']}` — {f['advisory']}")
    lines.append("")
    lines.append("## 권장 주석")
    lines.append("```yaml")
    lines.append("# source: <vendor docs URL> (확인 YYYY-MM-DD)")
    lines.append("# source: https://redfish.dmtf.org/schemas/v1/...")
    lines.append("# tested_against: [\"펌웨어 X.Y.Z\"]")
    lines.append("# evidence: tests/evidence/<날짜>-<vendor>.md")
    lines.append("# lab: 보유 / 부재")
    lines.append("```")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def self_test() -> int:
    print("[adapter_origin_check] self-test 시작", file=sys.stderr)
    with_origin = """\
# source: https://developer.dell.com/.../iDRAC9_Redfish.pdf
# tested_against: ["5.10.x"]
priority: 100
"""
    without_origin = """\
priority: 50
match:
  manufacturer: ["Acme"]
"""
    if has_origin_annotation(with_origin) and not has_origin_annotation(without_origin):
        print("[adapter_origin_check] self-test PASS", file=sys.stderr)
        return 0
    print("[adapter_origin_check] self-test FAIL", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="adapter origin advisory")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 adapter 전수 검사 (cycle 2026-05-07 M-K1 — 30 adapter 일관성)",
    )
    parser.add_argument(
        "--redfish-only",
        action="store_true",
        help="--all 과 함께 사용. adapters/redfish/ 만 검사 (M-K1 범위)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if args.all:
        findings = scan_all_adapters()
        adapters = list_all_adapters()
        if args.redfish_only:
            findings = [f for f in findings
                        if f["file"].startswith("adapters/redfish/")]
            adapters = [a for a in adapters
                        if "adapters/redfish" in a.as_posix()]
        total = len(adapters)
        if not findings:
            print(f"[adapter_origin_check] --all PASS — {total} adapter 일관성 OK",
                  file=sys.stderr)
            return 0
        print(f"[adapter_origin_check] --all advisory — {len(findings)} 건 / "
              f"{total} adapter", file=sys.stderr)
        for f in findings:
            print(f"  - [{f['category']}] {f['file']} — {f['advisory']}",
                  file=sys.stderr)
        out = write_advisory_report(findings)
        if out:
            rel = out.relative_to(REPO_ROOT)
            print(f"[adapter_origin_check] 보고서: {rel}", file=sys.stderr)
        return 1 if args.strict else 0

    changed = get_changed_files()
    if not changed:
        return 0

    findings = scan_adapters(changed)
    if not findings:
        return 0

    print(f"[adapter_origin_check] advisory: {len(findings)} 건 adapter "
          "origin 부재", file=sys.stderr)
    for f in findings[:5]:
        print(f"  - {f['file']}", file=sys.stderr)
    out = write_advisory_report(findings)
    if out:
        rel = out.relative_to(REPO_ROOT)
        print(f"[adapter_origin_check] 보고서: {rel}", file=sys.stderr)

    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
