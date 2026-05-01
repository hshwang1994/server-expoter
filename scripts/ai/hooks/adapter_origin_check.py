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

ORIGIN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*#\s*source\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*원본\s*위치", re.IGNORECASE),
    re.compile(r"^\s*#\s*출처", re.IGNORECASE),
    re.compile(r"^\s*#\s*tested_against\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*evidence\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*lab\s*:", re.IGNORECASE),
    re.compile(r"^\s*#\s*마지막\s*동기화\s*확인", re.IGNORECASE),
    re.compile(r"redfish\.dmtf\.org", re.IGNORECASE),
    re.compile(r"developer\.dell\.com", re.IGNORECASE),
    re.compile(r"support\.hpe\.com|support\.huawei\.com", re.IGNORECASE),
    re.compile(r"pubs\.lenovo\.com|cisco\.com|supermicro\.com", re.IGNORECASE),
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
    """adapter 헤더 영역 (priority: 이전 또는 첫 30 줄) 에 origin 주석 있는지."""
    head_lines = text.splitlines()[:40]
    for line in head_lines:
        if any(p.search(line) for p in ORIGIN_PATTERNS):
            return True
    return False


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
    args = parser.parse_args()

    if args.self_test:
        return self_test()

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
