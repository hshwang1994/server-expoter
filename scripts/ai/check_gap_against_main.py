#!/usr/bin/env python3
"""현재 작업 브랜치 ↔ origin/main 갭 감지.

server-exporter는 단일 main 운영. main 외 feature/* 브랜치에서 작업 중일 때
origin/main 대비 변경 / 누락을 출력. 세션 시작 hook + post-merge hook에서 호출.

Usage:
    python scripts/ai/check_gap_against_main.py [--no-fetch]

Exit codes:
    0 = 정상 (gap 정보 stdout)
    1 = 실행 에러
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path, timeout: int = 10) -> str:
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(cwd),
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="origin/main 갭 감지")
    parser.add_argument("--no-fetch", action="store_true",
                        help="git fetch skip (느린 환경 대응)")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if not args.no_fetch:
        _run(["git", "fetch", "origin", "main"], repo_root, timeout=15)

    branch = _run(["git", "branch", "--show-current"], repo_root).strip()
    if not branch or branch == "main":
        # main 자체에서 동작 시 갭 의미 없음
        return 0

    ahead = _run(["git", "rev-list", "--count", "origin/main..HEAD"], repo_root).strip()
    behind = _run(["git", "rev-list", "--count", "HEAD..origin/main"], repo_root).strip()

    print(f"[브랜치 갭] {branch} ↔ origin/main")
    print(f"  ahead (내 브랜치 앞선 커밋): {ahead or '0'}")
    print(f"  behind (origin/main 앞선 커밋): {behind or '0'}")

    if behind and behind != "0":
        # 변경/삭제 파일 요약
        diff = _run(["git", "diff", "--stat", "HEAD..origin/main"], repo_root)
        if diff:
            print("\n[origin/main이 앞선 변경 요약]")
            for line in diff.splitlines()[:10]:
                print(f"  {line}")
            print("  → 전체: git diff HEAD..origin/main")

    return 0


if __name__ == "__main__":
    sys.exit(main())
