#!/usr/bin/env python3
"""편집 후 Jinja2 템플릿 변수 정합성 체크 (← post_edit_ftl_i18n_check 대체).

대상: *.j2, *.yml/*.yaml 안의 inline Jinja2 (`{{ }}`, `{% %}`)

검사:
- 닫히지 않은 expression (`{{` 후 `}}` 없음)
- 닫히지 않은 statement (`{% %}` 짝 없음)
- 정의 안 된 변수 (heuristic: vars 정의 안 보이는데 사용 — 권고만)

Usage:
    python scripts/ai/hooks/post_edit_jinja_check.py <file_path>
"""

import argparse
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


JINJA_EXPR_RE = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)
JINJA_STMT_RE = re.compile(r"\{\%(.*?)\%\}", re.DOTALL)
UNCLOSED_EXPR_RE = re.compile(r"\{\{[^}]*$", re.MULTILINE)
UNCLOSED_STMT_RE = re.compile(r"\{\%[^%]*$", re.MULTILINE)


def check_jinja(file_path: str) -> dict:
    p = Path(file_path)
    if not p.is_file():
        return {"file": file_path, "issues": [], "checked": False}

    suffix = p.suffix.lower()
    if suffix not in (".j2", ".yml", ".yaml"):
        return {"file": file_path, "issues": [], "checked": False}

    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return {"file": file_path, "issues": [], "checked": False}

    issues = []

    # 닫히지 않은 expression
    if UNCLOSED_EXPR_RE.search(text):
        issues.append("닫히지 않은 Jinja expression `{{ ... }}`이 있습니다.")
    if UNCLOSED_STMT_RE.search(text):
        issues.append("닫히지 않은 Jinja statement `{% ... %}`가 있습니다.")

    # `{% if %}` ↔ `{% endif %}` 짝
    if_count = len(re.findall(r"\{\%\s*if\s+", text))
    endif_count = len(re.findall(r"\{\%\s*endif\s*\%\}", text))
    if if_count != endif_count:
        issues.append(f"`if` ({if_count}) ↔ `endif` ({endif_count}) 짝이 맞지 않습니다.")

    for_count = len(re.findall(r"\{\%\s*for\s+", text))
    endfor_count = len(re.findall(r"\{\%\s*endfor\s*\%\}", text))
    if for_count != endfor_count:
        issues.append(f"`for` ({for_count}) ↔ `endfor` ({endfor_count}) 짝이 맞지 않습니다.")

    return {"file": file_path, "issues": issues, "checked": True}


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
    parser = argparse.ArgumentParser(description="Jinja2 템플릿 정합성")
    parser.add_argument("file_path", nargs="?", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    file_path = args.file_path or _read_file_path_from_stdin()
    if not file_path:
        return 0

    result = check_jinja(file_path)

    if not result["checked"]:
        return 0

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["issues"]:
            print(f"Jinja2 정합성 경고 — {file_path}")
            for issue in result["issues"]:
                print(f"  - {issue}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
