#!/usr/bin/env python3
"""post-merge hook — git merge/pull/rebase 직후 origin/main 갭 출력.

session_start와 동일하게 check_gap_against_main.py를 호출하지만, 머지 직후 시점이라
"이번 머지로 들어온 변경"이 무엇인지 사용자에게 즉시 환기.

Usage:
    post-merge git hook이 자동 호출. 수동:
    python scripts/ai/hooks/post_merge_gap_check.py
"""

import os
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    if os.environ.get("POST_MERGE_GAP_SKIP") == "1":
        return 0

    repo_root = Path(".").resolve()
    gap_script = repo_root / "scripts" / "ai" / "check_gap_against_main.py"
    if not gap_script.is_file():
        return 0

    try:
        r = subprocess.run(
            [sys.executable, str(gap_script), "--no-fetch"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=10,
            encoding="utf-8", errors="replace",
        )
        if r.returncode == 0 and r.stdout.strip():
            print("\n[post-merge] 머지 후 origin/main 갭:")
            for line in r.stdout.splitlines():
                if line.strip():
                    print(line)
            print("\n→ rule 95 R4 / rule 97 (incoming-merge) 검증 권장")
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
