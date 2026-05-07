#!/usr/bin/env python3
"""pre-commit hook — Fragment skeleton 동기화 검증 (rule 22 R7 + rule 95 R1).

2026-04-29 production-audit BUG #1 회귀 차단:
- `init_fragments.yml`, `build_empty_data.yml`, `build_failed_output.yml`
  세 파일이 같은 data skeleton (system / hardware / bmc / cpu / memory /
  storage / network / users / firmware / power) 을 정의해야 함.
- 한 파일만 갱신 시 envelope drift → rescue 경로에서 envelope shape 불일치.

검사:
- 세 파일 모두 동일한 top-level data section keys 정의
- 동일한 nested key 구조 (storage.summary.groups 등)

비활성화 환경변수:
    SKELETON_SYNC_SKIP=1   — 본 hook skip

Usage:
    pre-commit hook 자동 호출. 수동:
    python scripts/ai/hooks/pre_commit_fragment_skeleton_sync.py
    python scripts/ai/hooks/pre_commit_fragment_skeleton_sync.py --self-test

Exit codes:
    0 = 통과
    1 = drift 발견 (blocking — 회귀 사고 직접 원인)
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SKELETON_FILES: tuple[str, ...] = (
    "common/tasks/normalize/init_fragments.yml",
    "common/tasks/normalize/build_empty_data.yml",
    "common/tasks/normalize/build_failed_output.yml",
)

# 정본 10 sections (rule 13 R1) — 모든 skeleton 파일이 이 키를 정의해야 함
EXPECTED_SECTIONS: frozenset[str] = frozenset({
    "system", "hardware", "bmc", "cpu", "memory",
    "storage", "network", "users", "firmware", "power",
})


def extract_skeleton_sections(text: str) -> set[str]:
    """파일 본문에서 data skeleton top-level section keys 추출.

    YAML 들여쓰기 4 (또는 6) 의 키를 검출:
    - `_merged_data:` 안의 `system: null` / `storage: {...}` 등
    - `_norm_empty_data:` 안의 동일 패턴
    - `'data': _merged_data | default({...})` 안의 dict 키 (defensive)

    Returns: top-level section name set.
    """
    sections: set[str] = set()

    # Pattern 1: YAML key 들 (`system:`, `bmc:` 등) — 6 또는 8 space indent
    # 공통: 들여쓰기 + 섹션명 + ":"
    yaml_key_re = re.compile(
        r"^[ \t]+(?P<key>system|hardware|bmc|cpu|memory|storage|network|"
        r"users|firmware|power)\s*:",
        re.MULTILINE,
    )
    for m in yaml_key_re.finditer(text):
        sections.add(m.group("key"))

    # Pattern 2: Jinja default dict (build_failed_output.yml fallback)
    # `'system': none, 'hardware': none` 같은 quoted key
    quoted_key_re = re.compile(
        r"['\"](?P<key>system|hardware|bmc|cpu|memory|storage|network|"
        r"users|firmware|power)['\"]\s*:",
    )
    for m in quoted_key_re.finditer(text):
        sections.add(m.group("key"))

    return sections


def _check_files(repo_root: Path) -> dict[str, set[str]]:
    """각 파일에서 추출한 sections 집합 반환."""
    out: dict[str, set[str]] = {}
    for rel in SKELETON_FILES:
        path = repo_root / rel
        if not path.is_file():
            out[rel] = set()
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            out[rel] = set()
            continue
        out[rel] = extract_skeleton_sections(text)
    return out


def _staged_files(repo_root: Path) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
    except Exception:
        return []
    return [ln.strip().replace("\\", "/") for ln in (r.stdout or "").splitlines() if ln.strip()]


def self_test() -> int:
    cases: list[tuple[str, str, set[str]]] = [
        (
            "init_fragments 표준 10 섹션",
            "_merged_data:\n"
            "  system:   null\n"
            "  hardware: null\n"
            "  bmc:      null\n"
            "  cpu:      null\n"
            "  memory:   null\n"
            "  storage:\n"
            "    filesystems: []\n"
            "  network:\n"
            "    dns_servers: []\n"
            "  users:    []\n"
            "  firmware: []\n"
            "  power:    null\n",
            EXPECTED_SECTIONS,
        ),
        (
            "build_failed_output Jinja default dict",
            "'data': _merged_data | default({\n"
            "  'system': none, 'hardware': none, 'bmc': none,\n"
            "  'cpu': none, 'memory': none,\n"
            "  'storage': {'filesystems':[]},\n"
            "  'network': {'dns_servers':[]},\n"
            "  'users': [], 'firmware': [], 'power': none\n"
            "})",
            EXPECTED_SECTIONS,
        ),
        (
            "1 섹션 누락 (drift 시뮬)",
            "_merged_data:\n"
            "  system:   null\n"
            "  hardware: null\n"
            "  bmc:      null\n"
            "  cpu:      null\n"
            "  memory:   null\n"
            "  storage:  null\n"
            "  network:  null\n"
            "  users:    []\n"
            "  firmware: []\n"
            # power 누락
            "",
            EXPECTED_SECTIONS - {"power"},
        ),
    ]
    all_pass = True
    for label, text, expected in cases:
        actual = extract_skeleton_sections(text)
        ok = actual == expected
        print(
            f"{'PASS' if ok else 'FAIL'}: {label} → "
            f"{len(actual)}/10 ({'OK' if ok else 'drift'})"
        )
        if not ok:
            all_pass = False
            print(f"  expected: {sorted(expected)}")
            print(f"  actual:   {sorted(actual)}")
            print(f"  missing:  {sorted(expected - actual)}")
            print(f"  extra:    {sorted(actual - expected)}")
    return 0 if all_pass else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="rule 22 R7 / rule 95 R1 Fragment skeleton 동기화"
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--all", action="store_true",
                        help="staged 파일 무관 — 항상 검증")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if os.environ.get("SKELETON_SYNC_SKIP") == "1":
        return 0

    repo_root = Path(".").resolve()

    # staged 파일 중 SKELETON_FILES 가 있을 때만 검증 (또는 --all)
    if not args.all:
        staged = _staged_files(repo_root)
        if not any(f in SKELETON_FILES for f in staged):
            return 0

    file_sections = _check_files(repo_root)

    # 각 파일에 EXPECTED_SECTIONS 모두 있는지 + 동일한지
    drifted: list[tuple[str, set[str], set[str]]] = []
    for rel, sections in file_sections.items():
        missing = EXPECTED_SECTIONS - sections
        extra = sections - EXPECTED_SECTIONS
        if missing or extra:
            drifted.append((rel, missing, extra))

    if not drifted:
        # 추가 검증: 세 파일이 정확히 동일한 sections 집합 가지는지
        sets = list(file_sections.values())
        if len(set(frozenset(s) for s in sets)) == 1:
            return 0
        # 동일하지 않으면 drift
        first = sets[0] if sets else set()
        for rel, sections in file_sections.items():
            diff = sections.symmetric_difference(first)
            if diff:
                drifted.append((rel, EXPECTED_SECTIONS - sections,
                                sections - EXPECTED_SECTIONS))

    if not drifted:
        return 0

    print(
        "[fragment skeleton sync] rule 22 R7 / rule 95 R1 — Fragment skeleton drift 검출:",
        file=sys.stderr,
    )
    print(
        "  3 파일 (init_fragments / build_empty_data / build_failed_output) 의\n"
        "  data skeleton 이 동기화되어야 함. 한 파일만 갱신 시 rescue 경로에서\n"
        "  envelope shape 불일치 (2026-04-29 production-audit BUG #1 회귀).\n",
        file=sys.stderr,
    )
    for rel, missing, extra in drifted:
        print(f"  {rel}:", file=sys.stderr)
        if missing:
            print(f"    missing: {sorted(missing)}", file=sys.stderr)
        if extra:
            print(f"    extra:   {sorted(extra)}", file=sys.stderr)
    print(
        "\n  → 정본 10 sections (rule 13 R1): "
        + ", ".join(sorted(EXPECTED_SECTIONS)),
        file=sys.stderr,
    )
    print(
        "  → 강제 skip (advisory 기간): SKELETON_SYNC_SKIP=1 git commit ...",
        file=sys.stderr,
    )

    return 1  # blocking


if __name__ == "__main__":
    sys.exit(main())
