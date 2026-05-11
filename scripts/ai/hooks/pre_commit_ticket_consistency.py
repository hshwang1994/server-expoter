#!/usr/bin/env python3
"""pre-commit hook — docs/ai/tickets/ cold-start 6 절 검증.

write-cold-start-ticket skill 정본 적용. fixes/M-X#.md 또는 fixes/F##.md 변경 시
6 절 (사용자 의도 / 작업 범위 / 분석 / 결정 / 회귀 / 다음 지시) 모두 존재 확인.

Blocking (exit 1) — cycle 2026-05-11 격상 (Phase 7).
이전 cycle 2026-05-06 도입 시 advisory (exit 0). cycle 2026-05-11 hint 확장 +
107 기존 ticket stub 변환 + 전수 위반 0 확인 후 blocking 격상.

6 절 중 누락 시 commit 차단. fixes/INDEX.md 같은 메타 파일 / archive/ 는 skip.

비활성화 환경변수:
    TICKET_CONSISTENCY_SKIP=1   — 본 hook skip

Usage:
    pre-commit hook 자동 호출. 수동:
    python scripts/ai/hooks/pre_commit_ticket_consistency.py
    python scripts/ai/hooks/pre_commit_ticket_consistency.py --self-test

Exit codes:
    0 = 통과
    1 = 위반 (BLOCKING — cycle 2026-05-11 격상)
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


TICKETS_PREFIX = "docs/ai/tickets/"
TICKET_FILENAME_RE = re.compile(r"fixes/(M-[A-Z]\d+|F\d+)\.md$", re.IGNORECASE)
SKIP_FILENAMES = ("INDEX.md", "SESSION-HANDOFF.md", "DEPENDENCIES.md",
                  "SESSION-PROMPTS.md", "COMPATIBILITY-MATRIX.md",
                  "LAB-INVENTORY.md", "HARNESS-RETROSPECTIVE.md")

REQUIRED_SECTION_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    # cycle 2026-05-11 hint 확장 (Phase 7 — 의미 일치하는 ticket 패턴 추가)
    # 각 label 의 stub 헤더 (`## <label>`) 도 hint 에 명시 — Phase 7 stub append 자기 매칭 보장.
    ("사용자 의도", ("## 사용자 의도", "## 1. 사용자 의도", "## 사용자 명시")),
    ("작업 범위", ("## 작업 범위", "## 2. 작업 범위", "## 변경", "## 우리 영향",
                   "## 변경 (Additive)", "## BMC", "## 대표 모델")),
    ("분석 / 구현", ("## 분석 / 구현", "## 분석 결과", "## 3. 분석",
                    "## 작업 spec", "## Session-0 분석 결과",
                    "## 컨텍스트", "## 현재 동작", "## 구현",
                    "## Sources", "## Web sources (rule 96 R1-A)",
                    "## web sources (rule 96 R1-A origin)",
                    "## fixture 구조")),
    ("결정 / 결과", ("## 결정 / 결과", "## 사용자 결정",
                    "## 4. 사용자 결정", "## 결정", "## 결정 spec",
                    "## option", "## 완료 조건", "## 결과", "## Vault 상태")),
    ("회귀 / 검증", ("## 회귀 / 검증", "## 회귀", "## 5. 회귀", "## 검증",
                    "## 완료 조건", "## risk", "## 회귀 risk")),
    ("다음 지시 / 관련", ("## 다음 지시 / 관련", "## 다음 세션 첫 지시",
                          "## 6. 다음 세션", "## 관련", "## 다음 ticket",
                          "## 다음 세션 첫 지시 템플릿", "## Cold-start")),
)


def _normalize(p: str) -> str:
    return p.replace("\\", "/").strip()


def _is_target_ticket(path: str) -> bool:
    p = _normalize(path)
    if not p.startswith(TICKETS_PREFIX):
        return False
    if "/archive/" in p:
        return False
    fname = p.rsplit("/", 1)[-1]
    if fname in SKIP_FILENAMES:
        return False
    return bool(TICKET_FILENAME_RE.search(p))


def detect_missing_sections(content: str) -> list[str]:
    """ticket 본문에서 6 절 중 누락된 섹션 라벨 list."""
    missing: list[str] = []
    for label, hints in REQUIRED_SECTION_HINTS:
        if not any(h in content for h in hints):
            missing.append(label)
    return missing


def _staged_files(repo_root: Path) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
    except Exception:
        return []
    return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]


def _read_staged_blob(repo_root: Path, path: str) -> str:
    try:
        r = subprocess.run(
            ["git", "show", f":{path}"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
        return r.stdout or ""
    except Exception:
        full = repo_root / path.replace("/", os.sep)
        try:
            return full.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""


def self_test() -> int:
    all_pass = True

    target_cases: list[tuple[str, bool]] = [
        ("docs/ai/tickets/2026-05-06-foo/fixes/M-A1.md", True),
        ("docs/ai/tickets/2026-05-06-foo/fixes/F01.md", True),
        ("docs/ai/tickets/2026-05-06-foo/INDEX.md", False),
        ("docs/ai/tickets/2026-05-06-foo/SESSION-HANDOFF.md", False),
        ("docs/ai/tickets/archive/2026-04-30/fixes/F01.md", False),
        ("adapters/redfish/dell.yml", False),
        ("docs/ai/tickets/2026-05-06-foo/fixes/INDEX.md", False),
    ]
    for path, expected in target_cases:
        actual = _is_target_ticket(path)
        ok = actual == expected
        print(f"{'PASS' if ok else 'FAIL'}: target check {path} → {actual}")
        if not ok:
            all_pass = False

    section_cases: list[tuple[str, str, list[str]]] = [
        (
            "6 절 모두 존재 → 누락 0",
            ("## 사용자 의도\n인용\n"
             "## 작업 범위\n표\n"
             "## 분석 결과\n분석\n"
             "## 사용자 결정\nN 포인트\n"
             "## 회귀 / 검증\npytest\n"
             "## 다음 세션 첫 지시 템플릿\n작업\n"
             "## 관련\nrule\n"),
            [],
        ),
        (
            "6 절 일부 누락 → 결정+회귀 누락",
            ("## 사용자 의도\n인용\n"
             "## 작업 범위\n표\n"
             "## 분석 결과\n분석\n"
             "## 다음 세션 첫 지시 템플릿\n작업\n"),
            ["결정 / 결과", "회귀 / 검증"],
        ),
        (
            "번호 매김 형식 (## 1. ~ ## 6.) → 누락 0",
            ("## 1. 사용자 의도\n인용\n"
             "## 2. 작업 범위\n표\n"
             "## 3. 분석 결과\n분석\n"
             "## 4. 사용자 결정\nN 포인트\n"
             "## 5. 회귀\npytest\n"
             "## 6. 다음 세션 첫 지시 템플릿\n작업\n"),
            [],
        ),
        (
            "범위만 + 다음 지시 — 분석/결정/회귀 누락",
            ("## 사용자 의도\n인용\n"
             "## 작업 범위\n표\n"
             "## 다음 세션 첫 지시 템플릿\n작업\n"),
            ["분석 / 구현", "결정 / 결과", "회귀 / 검증"],
        ),
    ]
    for label, content, expected in section_cases:
        actual = detect_missing_sections(content)
        ok = sorted(actual) == sorted(expected)
        print(f"{'PASS' if ok else 'FAIL'}: {label} → missing={actual}")
        if not ok:
            all_pass = False
            print(f"  expected: {expected}")
    return 0 if all_pass else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="docs/ai/tickets/ cold-start 6 절 검증")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if os.environ.get("TICKET_CONSISTENCY_SKIP") == "1":
        return 0

    repo_root = Path(".").resolve()
    staged = _staged_files(repo_root)
    if not staged:
        return 0

    targets = [f for f in staged if _is_target_ticket(_normalize(f))]
    if not targets:
        return 0

    violations: list[tuple[str, list[str]]] = []
    for f in targets:
        content = _read_staged_blob(repo_root, _normalize(f))
        if not content:
            continue
        missing = detect_missing_sections(content)
        if missing:
            violations.append((f, missing))

    if not violations:
        return 0

    print(
        "[ticket consistency] cold-start 6 절 검증 — 누락 (BLOCKING — cycle 2026-05-11 격상):",
        file=sys.stderr,
    )
    for path, missing in violations:
        print(f"  - {path}", file=sys.stderr)
        for m in missing:
            print(f"      누락: {m}", file=sys.stderr)
    print(
        "\n  → ticket fixes/M-X#.md / F##.md 는 6 절 cold-start 형식 의무.",
        file=sys.stderr,
    )
    print(
        "  → write-cold-start-ticket skill / ticket-decomposer agent 참조.",
        file=sys.stderr,
    )
    print("  → 강제 skip: TICKET_CONSISTENCY_SKIP=1 git commit ...", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
