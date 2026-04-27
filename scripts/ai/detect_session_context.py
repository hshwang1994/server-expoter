#!/usr/bin/env python3
"""세션 컨텍스트 감지 — 브랜치 → 작업 유형 매핑.

server-exporter는 main + feature/* 단순 구조.
clovirone과 달리 고객사 자동 감지는 없고, 작업 유형만 추론.

Usage:
    python scripts/ai/detect_session_context.py [--json]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict


def get_current_branch(repo_root: Path) -> str:
    """현재 git 브랜치 이름 반환."""
    try:
        r = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def detect_context(branch: str) -> Dict[str, object]:
    """브랜치에서 컨텍스트 추론.

    server-exporter:
    - main → 운영 기준선
    - feature/<name> → 기능 작업
    - fix/<name> → 버그 수정
    - vendor/<name> → 새 벤더 추가 (예: vendor/huawei)
    - docs/<name> → 문서 작업
    """
    branch = branch or "unknown"

    if branch == "main" or branch == "master":
        kind = "main"
        purpose = "운영 기준선"
    elif branch.startswith("feature/"):
        kind = "feature"
        purpose = f"기능 작업 ({branch.split('/', 1)[1]})"
    elif branch.startswith("fix/"):
        kind = "fix"
        purpose = f"버그 수정 ({branch.split('/', 1)[1]})"
    elif branch.startswith("vendor/"):
        kind = "vendor"
        purpose = f"새 벤더 추가 ({branch.split('/', 1)[1]})"
    elif branch.startswith("docs/"):
        kind = "docs"
        purpose = f"문서 작업 ({branch.split('/', 1)[1]})"
    elif branch.startswith("harness/"):
        kind = "harness"
        purpose = f"하네스 변경 ({branch.split('/', 1)[1]})"
    else:
        kind = "other"
        purpose = "기타"

    return {
        "detected": kind != "other",
        "branch": branch,
        "kind": kind,
        "purpose": purpose,
        "project": "server-exporter",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="세션 컨텍스트 감지")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    parser.add_argument("--repo-root", default=".", help="저장소 루트")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    branch = get_current_branch(repo_root)
    ctx = detect_context(branch)

    if args.json:
        print(json.dumps(ctx, ensure_ascii=False, indent=2))
    else:
        if ctx["detected"]:
            print(f"server-exporter — {ctx['purpose']} (브랜치: {ctx['branch']})")
        else:
            print(f"브랜치 '{ctx['branch']}'에서 컨텍스트를 감지할 수 없습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
