#!/usr/bin/env python3
"""skill 편집 후 SKILL.md 형식 검증.

체크 항목:
- frontmatter (name, description) 존재
- description 1024자 이하 (Anthropic skill metadata 한도)
- description에 트리거 phrase ("when to use") 단서 존재 권장
- name이 폴더 이름과 일치

Usage:
    python scripts/ai/hooks/skill_edit_validate.py <SKILL.md>
"""

import argparse
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def validate_skill_md(path: Path) -> dict:
    """SKILL.md 형식 검증."""
    issues = []

    if path.name != "SKILL.md":
        return {"file": str(path), "issues": [], "checked": False}

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"file": str(path), "issues": [f"읽기 실패: {e}"], "checked": True}

    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        issues.append("frontmatter (--- ... ---) 가 없거나 위치가 잘못됨")
        return {"file": str(path), "issues": issues, "checked": True}

    fm_text = fm_match.group(1)
    fm: dict = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")

    skill_name = fm.get("name", "")
    skill_desc = fm.get("description", "")

    if not skill_name:
        issues.append("frontmatter `name` 누락")
    elif skill_name != path.parent.name:
        issues.append(f"name '{skill_name}' ↔ 폴더 '{path.parent.name}' 불일치")

    if not skill_desc:
        issues.append("frontmatter `description` 누락")
    elif len(skill_desc) > 1024:
        issues.append(f"description 1024자 초과 ({len(skill_desc)}자)")

    # 트리거 단서 (use, when, 사용자가, ...)
    if skill_desc and not re.search(
        r"(when |Use when|use this when|사용자가|할 때|invoke|trigger)",
        skill_desc,
        re.IGNORECASE,
    ):
        issues.append("description에 트리거 단서 (when/use/사용자가/...) 권장")

    return {"file": str(path), "issues": issues, "checked": True}


def _read_file_path_from_stdin() -> str | None:
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        payload = json.loads(raw)
        return payload.get("tool_input", {}).get("file_path")
    except (json.JSONDecodeError, AttributeError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="SKILL.md 검증")
    parser.add_argument("file_path", nargs="?", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    file_path = args.file_path or _read_file_path_from_stdin()
    if not file_path:
        return 0

    p = Path(file_path)
    if p.name != "SKILL.md":
        return 0

    result = validate_skill_md(p)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["issues"]:
        print(f"SKILL.md 검증 — {file_path}")
        for issue in result["issues"]:
            print(f"  - {issue}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
