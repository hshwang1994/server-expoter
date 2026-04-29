#!/usr/bin/env python3
"""pre-commit hook — Jenkinsfile* cron 변경 시 가드 (← pre_commit_scheduler_guard 대체).

server-exporter는 Jenkins multi-pipeline (Jenkinsfile / _portal) 구조 (cycle-015에서 _grafana 제거).
cron 트리거 변경은 운영 영향 큼 → 변경 시 사용자 확인 권고 (advisory).

Usage:
    pre-commit hook 자동 호출. 수동:
    python scripts/ai/hooks/pre_commit_jenkinsfile_guard.py

Exit codes:
    0 = 통과 (advisory)
"""

import os
import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


CRON_RE = re.compile(r"(cron\s*\(|triggers\s*\{|H\s+\*\s+|H/[0-9]+\s+\*)")


def main() -> int:
    if os.environ.get("JENKINSFILE_GUARD_SKIP") == "1":
        return 0

    repo_root = Path(".").resolve()
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
        files = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    except Exception:
        return 0

    jenkinsfiles = [f for f in files if re.match(r"^Jenkinsfile", f)]
    if not jenkinsfiles:
        return 0

    cron_changes = []
    for f in jenkinsfiles:
        try:
            r = subprocess.run(
                ["git", "diff", "--cached", f],
                capture_output=True, text=True, cwd=str(repo_root), timeout=5,
                encoding="utf-8", errors="replace",
            )
            diff = r.stdout or ""
        except Exception:
            continue

        # +/- 라인 중 cron 관련 변경 있으면
        for line in diff.splitlines():
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                if CRON_RE.search(line):
                    cron_changes.append(f"{f}: {line[:80]}")
                    break

    if cron_changes:
        print("[Jenkinsfile guard] cron 트리거 변경 감지 (advisory):", file=sys.stderr)
        for c in cron_changes:
            print(f"  - {c}", file=sys.stderr)
        print("\n  → rule 92 R5 (Flyway 버전 사용자 확인) 와 동일 정신 — "
              "운영 영향 확인 후 commit", file=sys.stderr)
        print("  → JENKINSFILE_GUARD_SKIP=1 git commit ... (skip 옵션)", file=sys.stderr)

    return 0  # advisory


if __name__ == "__main__":
    sys.exit(main())
