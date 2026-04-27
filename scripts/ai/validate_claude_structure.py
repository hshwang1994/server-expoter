#!/usr/bin/env python3
"""`.claude/` 구조 검증 — 필수 디렉터리/파일 존재 여부 점검.

세션 시작 hook에서 빠른 sanity check. issue 발견 시 경고만 출력 (세션 차단 안 함).

Usage:
    python scripts/ai/validate_claude_structure.py [.claude] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


REQUIRED_DIRS = [
    "rules",
    "skills",
    "agents",
    "policy",
    "role",
    "ai-context",
    "templates",
    "commands",
]

REQUIRED_FILES = [
    "settings.json",
]

REQUIRED_POLICY_YAML = [
    "approval-authority.yaml",
    "vendor-boundary-map.yaml",
    "protected-paths.yaml",
    "review-matrix.yaml",
]

REQUIRED_ROLE_DIRS = [
    "gather",
    "output-schema",
    "infra",
    "qa",
    "po",
    "tpm",
]


def validate_structure(claude_dir: Path) -> Dict[str, object]:
    """`.claude/` 디렉터리 구조 검증."""
    issues: List[str] = []

    if not claude_dir.is_dir():
        return {
            "passed": False,
            "issues": [f".claude/ 디렉터리가 없습니다: {claude_dir}"],
            "checked_dir": str(claude_dir),
        }

    for d in REQUIRED_DIRS:
        if not (claude_dir / d).is_dir():
            issues.append(f"누락 디렉터리: .claude/{d}/")

    for f in REQUIRED_FILES:
        if not (claude_dir / f).is_file():
            issues.append(f"누락 파일: .claude/{f}")

    policy_dir = claude_dir / "policy"
    if policy_dir.is_dir():
        for y in REQUIRED_POLICY_YAML:
            if not (policy_dir / y).is_file():
                issues.append(f"누락 policy YAML: .claude/policy/{y}")

    role_dir = claude_dir / "role"
    if role_dir.is_dir():
        for r in REQUIRED_ROLE_DIRS:
            if not (role_dir / r).is_dir():
                issues.append(f"누락 role 디렉터리: .claude/role/{r}/")
            elif not (role_dir / r / "README.md").is_file():
                issues.append(f"누락 role README: .claude/role/{r}/README.md")

    return {
        "passed": not issues,
        "issues": issues,
        "checked_dir": str(claude_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=".claude/ 구조 검증")
    parser.add_argument("path", nargs="?", default=".claude", help=".claude 경로")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_structure(Path(args.path).resolve())

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["passed"]:
            print(".claude/ 구조: OK")
        else:
            print(f".claude/ 구조: 이슈 {len(result['issues'])}건")
            for issue in result["issues"]:
                print(f"  - {issue}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
