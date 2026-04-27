#!/usr/bin/env python3
"""post-commit hook — measurement targets 무효화 trigger 감지 (rule 28).

커밋된 변경 파일이 측정 대상의 무효화 trigger에 해당하면 안내.

server-exporter 측정 대상 (rule 28 R1):
- schema/sections.yml or field_dictionary.yml 수정 → 출력 schema 재측정
- adapters/ 수정 → 벤더 어댑터 매트릭스 재측정
- Jenkinsfile* 수정 → cron 인벤토리 재측정
- 채널 디렉터리 추가 → PROJECT_MAP 재측정

Usage:
    git commit 후 자동 호출. 수동:
    python scripts/ai/hooks/post_commit_measurement_trigger.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


TRIGGERS = [
    (re.compile(r"^schema/(sections|field_dictionary)\.yml$"),
     "출력 schema", "update-output-schema-evidence skill 호출 권장"),
    (re.compile(r"^adapters/.*\.yml$"),
     "벤더 어댑터 매트릭스",
     "docs/ai/catalogs/VENDOR_ADAPTERS.md 갱신 권장"),
    (re.compile(r"^Jenkinsfile"),
     "Jenkinsfile cron 인벤토리",
     "docs/ai/catalogs/JENKINS_PIPELINES.md 갱신 권장"),
    (re.compile(r"^(os|esxi|redfish)-gather/"),
     "채널 / gather 구조",
     "scripts/ai/check_project_map_drift.py --update 실행 권장"),
    (re.compile(r"^common/library/"),
     "공통 라이브러리 (precheck 등)",
     "tests/redfish-probe 회귀 권장"),
]


def main() -> int:
    repo_root = Path(".").resolve()
    try:
        r = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1..HEAD"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
        files = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    except Exception:
        return 0

    triggered = []
    for f in files:
        for pattern, target, action in TRIGGERS:
            if pattern.search(f):
                triggered.append((target, action, f))

    if triggered:
        seen = set()
        print("\n[measurement trigger] 변경된 측정 대상:")
        for target, action, f in triggered:
            if target in seen:
                continue
            seen.add(target)
            print(f"  - {target}: {action}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
