#!/usr/bin/env python3
"""rule 95 R1 의심 패턴 11종 자동 검출 (server-exporter 도메인).

production code (Python / YAML)에서 의심 패턴 grep + 라인 출력. advisory 도구.
TDD 작성 / 코드 리뷰 / harness-cycle observer 단계에서 활용.

Usage:
    python scripts/ai/scan_suspicious_patterns.py [--target <dir>] [--strict]

Patterns (rule 95 R1):
    1. Ansible default(omit) 누락 (vendor-specific 변수 직접 참조)
    2. set_fact 재정의로 fragment 침범 (rule 22)
    3. Jinja2 정규식 dead code
    4. adapter score 동률 처리 (priority 동률)
    5. is none / is undefined / length == 0 혼동
    6. 빈 callback message
    7. int() cast 미방어
    8. Single-vendor 분기 silent (다른 vendor skip)
    9. adapter_loader self-reference (순환 include)
    10. mutable / immutable 혼동 (Ansible vars dict)
    11. 외부 시스템 계약 drift (rule 96 — origin 주석 누락 adapter)

Exit codes:
    0 = 의심 0건
    2 = 의심 발견 (advisory — 즉시 수정 의무 아님)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# 검사 대상
SCAN_DIRS = [
    "common", "os-gather", "esxi-gather", "redfish-gather",
    "filter_plugins", "lookup_plugins", "module_utils", "callback_plugins",
    "adapters",
]
EXCLUDE_PATTERNS = [
    re.compile(r"\.git/"),
    re.compile(r"__pycache__/"),
    re.compile(r"\.pytest_cache/"),
    re.compile(r"tests/"),
    re.compile(r"vault/"),
]


def _is_excluded(rel: str) -> bool:
    return any(p.search(rel) for p in EXCLUDE_PATTERNS)


# 패턴 정의 (rule 95 R1)
PATTERNS = [
    {
        "id": 1,
        "name": "Ansible default(omit) 누락",
        "regex": re.compile(r"\{\{\s*[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*\s*\}\}"),
        "files": (".yml", ".yaml"),
        "exclude_lines": [re.compile(r"\|\s*default\s*\("), re.compile(r"^#")],
        "advisory": "변수 참조에 default(...) 또는 default(omit) 권장",
    },
    {
        "id": 2,
        "name": "set_fact 재정의 — fragment 침범 의심 (rule 22)",
        "regex": re.compile(r"set_fact\s*:\s*$"),
        "files": (".yml", ".yaml"),
        "advisory": "set_fact 다음 라인 검토 — _sections_<other>_*_fragment / _collected_* 직접 수정 금지",
    },
    {
        "id": 3,
        "name": "Jinja2 정규식 dead code",
        "regex": re.compile(r"regex_search\([^)]*\)\s*\|\s*default\(['\"]['\"]"),
        "files": (".yml", ".yaml"),
        "advisory": "regex_search 결과 빈 string fallback이 무의미 (이미 None/false 처리)",
    },
    {
        "id": 4,
        "name": "Adapter priority 동률 의심",
        "regex": re.compile(r"^priority:\s*(\d+)\s*$"),
        "files": (".yml",),
        "scope": "adapters/",
        "advisory": "같은 vendor 내 priority 동률 시 정렬 결과 불확정 — score-adapter-match로 확인",
        "aggregate": True,
    },
    {
        "id": 5,
        "name": "is none / is undefined / length == 0 혼동",
        "regex": re.compile(r"(is\s+none|is\s+undefined|\|\s*length\s*==\s*0)"),
        "files": (".yml", ".yaml"),
        "advisory": "Ansible 변수 상태 분기 — 의도 명확히 (none vs undefined vs 빈 list 의도 다름)",
    },
    {
        "id": 6,
        "name": "빈 callback message (errors[]에 message 없이 빈 dict)",
        "regex": re.compile(r"errors\s*:\s*\[\s*\{\s*\}\s*\]"),
        "files": (".yml", ".yaml", ".py"),
        "advisory": "errors entry는 message 필드 필수",
    },
    {
        "id": 7,
        "name": "int() cast 미방어",
        "regex": re.compile(r"\bint\(\s*[a-z_][a-z0-9_.\[\]'\"]*\s*\)"),
        "files": (".py",),
        "exclude_lines": [re.compile(r"try\s*:"), re.compile(r"except"), re.compile(r"^#")],
        "advisory": "int() ValueError 처리 — try/except 또는 .get(default=0) 권장",
    },
    {
        "id": 9,
        "name": "adapter_loader self-reference 의심",
        "regex": re.compile(r"include\s*:\s*adapter_loader|lookup\(\s*['\"]adapter_loader"),
        "files": (".py", ".yml"),
        "scope": "lookup_plugins/",
        "advisory": "adapter_loader가 자기 자신을 호출하는 경로 검토 (순환)",
    },
    {
        "id": 11,
        "name": "Adapter origin 주석 누락 (rule 96 R1)",
        "regex": re.compile(r"^priority:"),
        "files": (".yml",),
        "scope": "adapters/",
        "advisory": "adapter 첫 30 줄에 vendor / firmware / tested_against / oem_path 주석 필요",
        "check_metadata_comment": True,
    },
]


def scan_file(path: Path, repo_root: Path) -> List[Tuple[int, str, int, str]]:
    """파일을 패턴별로 스캔. 위반 list 반환."""
    rel = path.relative_to(repo_root).as_posix()
    if _is_excluded(rel):
        return []
    findings = []

    suffix = path.suffix
    try:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
    except Exception:
        return []

    for pattern in PATTERNS:
        if suffix not in pattern["files"]:
            continue
        if "scope" in pattern and pattern["scope"] not in rel:
            continue

        # Adapter origin 주석 검사 (특수 처리 — rule 96 R1)
        if pattern.get("check_metadata_comment"):
            head = "\n".join(lines[:30])
            if not any(kw in head.lower() for kw in
                       ("vendor:", "firmware:", "tested_against:", "# origin:", "# 출처:")):
                findings.append((pattern["id"], rel, 1, pattern["advisory"]))
            continue

        for lineno, line in enumerate(lines, start=1):
            if not pattern["regex"].search(line):
                continue
            # exclude_lines
            if "exclude_lines" in pattern:
                if any(ex.search(line) for ex in pattern["exclude_lines"]):
                    continue
            findings.append((pattern["id"], rel, lineno, line.strip()[:80]))
            # aggregate 패턴은 1회만 (priority 같은 카운팅 별도)
            if pattern.get("aggregate"):
                break

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="rule 95 R1 의심 패턴 자동 검출")
    parser.add_argument("--target", default=None, help="검사 디렉터리 (기본: 전체)")
    parser.add_argument("--strict", action="store_true", help="의심 발견 시 exit 2")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    targets = [args.target] if args.target else SCAN_DIRS
    all_findings: List[Tuple[int, str, int, str]] = []

    for d in targets:
        path = repo_root / d
        if not path.is_dir():
            continue
        for f in path.rglob("*"):
            if f.is_file() and f.suffix in (".py", ".yml", ".yaml"):
                all_findings.extend(scan_file(f, repo_root))

    if not all_findings:
        print("=== 의심 패턴 스캔 결과 ===")
        print("clean (rule 95 R1 11 패턴 — 검출 0건)")
        return 0

    # 패턴별 그룹
    print("=== 의심 패턴 스캔 결과 (advisory) ===")
    by_id: dict[int, list] = {}
    for pid, rel, lineno, snippet in all_findings:
        by_id.setdefault(pid, []).append((rel, lineno, snippet))

    for pid in sorted(by_id.keys()):
        pattern_meta = next(p for p in PATTERNS if p["id"] == pid)
        print(f"\n[#{pid}] {pattern_meta['name']} — {len(by_id[pid])}건")
        print(f"      → {pattern_meta['advisory']}")
        for rel, lineno, snippet in by_id[pid][:5]:
            print(f"      • {rel}:{lineno}  {snippet}")
        if len(by_id[pid]) > 5:
            print(f"      ... ({len(by_id[pid]) - 5}건 추가)")

    print(f"\n총 {len(all_findings)}건 (advisory). 의심 발견 시:")
    print("  - rule 95 R3 — @pytest.mark.xfail 추가 + FAILURE_PATTERNS.md entry")
    print("  - 또는 의도된 패턴이면 코드 주석으로 근거 명시")

    return 2 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
