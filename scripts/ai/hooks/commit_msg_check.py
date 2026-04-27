#!/usr/bin/env python3
"""commit-msg hook — rule 90 commit convention 준수 검증.

검사:
- type prefix (feat/fix/refactor/docs/test/chore/harness/hotfix) 필수
- 제목 50자 이하
- 금지어 단독 사용 금지 (버그수정, 수정, fix 등)
- 본문 4줄 이하 권장 (advisory)

Advisory mode (warn only, allow commit). 강제 차단은 사용자 명시 시.

Usage:
    python scripts/ai/hooks/commit_msg_check.py <commit-msg-file>
    python scripts/ai/hooks/commit_msg_check.py --self-test

Exit codes (advisory):
    0 = 항상 (commit 허용)
"""

import argparse
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


VALID_TYPES = {"feat", "fix", "refactor", "docs", "test", "chore", "harness", "hotfix"}

FORBIDDEN_SOLO = {
    "버그수정", "버그 수정", "수정", "변경", "업데이트", "작업",
    "fix", "update", "change", "WIP", "wip", "임시", "test",
}

TYPE_PREFIX_RE = re.compile(r"^([a-z]+):\s+(.+)$")


def check_message(text: str) -> list[str]:
    """commit 메시지 검증. 위반 사항 리스트 반환."""
    issues = []

    lines = text.splitlines()
    if not lines or not lines[0].strip():
        issues.append("commit 제목이 비어있음")
        return issues

    title = lines[0].rstrip()

    # type prefix
    m = TYPE_PREFIX_RE.match(title)
    if not m:
        issues.append(f"type prefix 누락 (feat/fix/refactor/docs/test/chore/harness/hotfix:): '{title}'")
    else:
        ctype = m.group(1)
        subject = m.group(2).strip()
        if ctype not in VALID_TYPES:
            issues.append(f"알 수 없는 type '{ctype}' (허용: {', '.join(sorted(VALID_TYPES))})")
        if subject in FORBIDDEN_SOLO:
            issues.append(f"제목 subject가 금지어 단독: '{subject}'")
        if len(title) > 50:
            issues.append(f"제목 50자 초과 ({len(title)}자)")

    # 본문 길이 advisory
    if len(lines) > 1:
        body_lines = [ln for ln in lines[2:] if ln.strip()]
        if len(body_lines) > 4:
            issues.append(f"본문 4줄 초과 ({len(body_lines)}줄) — 상세는 PR/티켓으로 (advisory)")

    return issues


def self_test() -> int:
    cases = [
        ("feat: 새 기능 추가", []),
        ("fix: BillingCalculator 월별 합계 오산 수정", []),
        ("버그수정", ["type prefix 누락"]),
        ("fix: 수정", ["제목 subject가 금지어 단독"]),
        ("WIP", ["type prefix 누락"]),
        ("feat: " + "x" * 60, ["제목 50자 초과"]),
    ]
    all_pass = True
    for msg, expected_substrs in cases:
        issues = check_message(msg)
        ok = True
        for expected in expected_substrs:
            if not any(expected in i for i in issues):
                ok = False
                break
        if not expected_substrs and issues:
            ok = False
        print(f"{'PASS' if ok else 'FAIL'}: '{msg[:40]}...' → {issues}")
        if not ok:
            all_pass = False
    return 0 if all_pass else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="commit-msg 검증")
    parser.add_argument("path", nargs="?", help="commit msg 파일 경로 (.git/COMMIT_EDITMSG)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.path:
        return 0

    msg_path = Path(args.path)
    if not msg_path.is_file():
        return 0

    text = msg_path.read_text(encoding="utf-8")
    # commented lines 제외
    text = "\n".join(ln for ln in text.splitlines() if not ln.startswith("#"))

    issues = check_message(text)
    if issues:
        print("[commit-msg] 경고 (advisory — commit은 허용):", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        print("  → rule 90 (commit-convention) 참조", file=sys.stderr)

    return 0  # advisory mode


if __name__ == "__main__":
    sys.exit(main())
