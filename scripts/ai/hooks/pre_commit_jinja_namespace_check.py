#!/usr/bin/env python3
"""pre-commit hook — Jinja2 loop-scoping 회귀 차단 (rule 22 R7 + rule 95 R1).

cycle-015 (ESXi vendor 정규화) / cycle-016 (Windows runtime swap_total_mb
aggregation) / cycle 2026-04-30 M-D2 (Fragment _errors_fragment) 등
**3 차례 반복된 Jinja2 namespace scoping 회귀 패턴**을 정적 검출:

  WRONG (loop 내 set 이 outer scope 에 반영 안 됨):
    {%- set total = 0 -%}
    {%- for x in items -%}
      {%- set total = total + x.size -%}   # ← outer total 안 갱신
    {%- endfor -%}
    {{ total }}                             # 항상 0

  RIGHT (namespace 사용):
    {%- set ns = namespace(total=0) -%}
    {%- for x in items -%}
      {%- set ns.total = ns.total + x.size -%}
    {%- endfor -%}
    {{ ns.total }}

검사 대상:
- *.yml, *.yaml, *.j2 파일의 inline Jinja2 (`{% set %}` 안의 for-block)

Advisory (exit 0):
- 의심 패턴 발견 시 stderr 경고만, commit 허용
- 1 cycle 모니터링 후 false-positive 0 시 blocking 격상 검토

비활성화 환경변수:
    JINJA_NAMESPACE_SKIP=1     — 본 hook skip
    JINJA_NAMESPACE_SKIP_FILE=<path:path:...> — 특정 파일만 skip

Usage:
    pre-commit hook 자동 호출. 수동:
    python scripts/ai/hooks/pre_commit_jinja_namespace_check.py
    python scripts/ai/hooks/pre_commit_jinja_namespace_check.py --self-test
    python scripts/ai/hooks/pre_commit_jinja_namespace_check.py <file_path>
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


# Jinja2 statement 패턴
_FOR_RE = re.compile(r"\{\%-?\s*for\s+(\w+)(?:\s*,\s*\w+)?\s+in\s+", re.IGNORECASE)
_ENDFOR_RE = re.compile(r"\{\%-?\s*endfor\s*-?\%\}", re.IGNORECASE)
# `{%- set var = ... %}` — plain var (의심)
# `{%- set ns.x = ... %}` — namespace member 접근 (안전)
_SET_RE = re.compile(r"\{\%-?\s*set\s+(\w+)\s*=", re.IGNORECASE)
_SET_NAMESPACE_MEMBER_RE = re.compile(
    r"\{\%-?\s*set\s+\w+\.\w+\s*=", re.IGNORECASE
)
_NAMESPACE_RE = re.compile(r"namespace\s*\(", re.IGNORECASE)
# `_ = x.update(...)` / `_ = x.append(...)` 같은 dict/list 이미 mutable 패턴
_MUTATION_SET_RE = re.compile(
    r"\{\%-?\s*set\s+_\s*=\s*\w+\.(?:update|append|extend)\s*\(",
    re.IGNORECASE,
)


def _strip_comments(text: str) -> str:
    """Jinja2 comment `{# ... #}` 제거 — 코멘트 안 패턴 false-positive 방지."""
    return re.sub(r"\{#.*?#\}", "", text, flags=re.DOTALL)


def find_loop_scoping_issues(text: str) -> list[tuple[int, str, str]]:
    """loop 내 self-reference 누적 패턴 검출 (cycle-015/016/M-D2 회귀 패턴).

    검출 대상은 `{% set var = var + ... %}` 같은 **자기 참조 누적** 패턴만.
    단순 per-iteration local 변수 (`{% set parts = line.split('|') %}`) 는
    안전한 패턴이므로 false positive 회피 위해 미검출.

    Returns: [(line_number, var_name, snippet), ...]
    """
    text = _strip_comments(text)
    lines = text.splitlines()
    issues: list[tuple[int, str, str]] = []

    in_for_depth = 0
    for_var_stack: list[set[str]] = []

    for idx, line in enumerate(lines, start=1):
        # for 진입
        for_match = _FOR_RE.search(line)
        if for_match:
            in_for_depth += 1
            for_var_stack.append({for_match.group(1)})
            continue

        # endfor
        if _ENDFOR_RE.search(line):
            if in_for_depth > 0:
                in_for_depth -= 1
                if for_var_stack:
                    for_var_stack.pop()
            continue

        # for-block 내부만 검사
        if in_for_depth == 0:
            continue

        # `_ = x.update(...)` mutation 패턴은 안전
        if _MUTATION_SET_RE.search(line):
            continue

        # `set ns.x = ...` namespace member 접근 — 안전
        if _SET_NAMESPACE_MEMBER_RE.search(line):
            continue

        # `{% set var = ... %}` 검출
        set_match = _SET_RE.search(line)
        if not set_match:
            continue

        var = set_match.group(1)
        if var == "_":
            continue
        # loop variable 자체 set 은 무관 (per-iteration local)
        current_loop_vars = (
            for_var_stack[-1] if for_var_stack else set()
        )
        if var in current_loop_vars:
            continue

        # **핵심 검출**: 자기 참조 누적 패턴 (`set var = var + ...` /
        # `set var = var | ...` / `set var = X(var, ...)` 등)
        # (단순 line-by-line — multi-line 누적은 별도 분석 필요)
        rhs_match = re.search(
            rf"\{{\%-?\s*set\s+{re.escape(var)}\s*=\s*(.*?)\s*-?\%\}}",
            line,
        )
        if not rhs_match:
            continue
        rhs = rhs_match.group(1)
        # 자기 참조 검출 — `var` 가 RHS 에 등장.
        # negative lookbehind/lookahead: `.` (attribute 접근) / word char /
        # quote (`'var'`, `"var"` 문자열 리터럴 — dict key 등) 직전/직후면 제외
        self_ref = re.search(
            rf"(?<![.\w'\"]){re.escape(var)}(?![.\w'\"])", rhs
        )
        if not self_ref:
            continue

        issues.append((idx, var, line.strip()))

    return issues


def _staged_files(repo_root: Path) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
    except Exception:
        return []
    return [
        ln.strip() for ln in (r.stdout or "").splitlines()
        if ln.strip().endswith((".yml", ".yaml", ".j2"))
    ]


def _check_file(path: Path) -> list[tuple[int, str, str]]:
    if not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    return find_loop_scoping_issues(text)


def self_test() -> int:
    cases: list[tuple[str, str, int]] = [
        (
            "self-ref 누적 (위반 — cycle-016 패턴)",
            "{%- set total = 0 -%}\n"
            "{%- for x in items -%}\n"
            "  {%- set total = total + x.size -%}\n"
            "{%- endfor -%}\n",
            1,
        ),
        (
            "namespace 사용 (안전)",
            "{%- set ns = namespace(total=0) -%}\n"
            "{%- for x in items -%}\n"
            "  {%- set ns.total = ns.total + x.size -%}\n"
            "{%- endfor -%}\n",
            0,
        ),
        (
            "mutation 패턴 (안전 — dict.update)",
            "{%- set out = {} -%}\n"
            "{%- for s in sections -%}\n"
            "  {%- set _ = out.update({s: 'failed'}) -%}\n"
            "{%- endfor -%}\n",
            0,
        ),
        (
            "per-iteration local (안전 — false positive 회피)",
            "{%- for line in lines -%}\n"
            "  {%- set parts = line.split('|') -%}\n"
            "  {%- set cap = parts[1] | int -%}\n"
            "{%- endfor -%}\n",
            0,
        ),
        (
            "loop variable set (안전)",
            "{%- for item in items -%}\n"
            "  {%- set item = item | upper -%}\n"
            "{%- endfor -%}\n",
            0,
        ),
        (
            "loop 밖 set (안전 — for 외부)",
            "{%- set total = 0 -%}\n"
            "{%- if items -%}\n"
            "  {%- set total = items | length -%}\n"
            "{%- endif -%}\n",
            0,
        ),
        (
            "comment 안 패턴 (안전 — false positive 방지)",
            "{# {%- for x in items -%} {%- set total = total + 1 -%} {%- endfor -%} #}\n",
            0,
        ),
        (
            "중첩 for self-ref (위반)",
            "{%- set count = 0 -%}\n"
            "{%- for outer in xs -%}\n"
            "  {%- for inner in outer -%}\n"
            "    {%- set count = count + 1 -%}\n"
            "  {%- endfor -%}\n"
            "{%- endfor -%}\n",
            1,
        ),
        (
            "self-ref via filter (위반)",
            "{%- set acc = [] -%}\n"
            "{%- for x in items -%}\n"
            "  {%- set acc = acc + [x] -%}\n"
            "{%- endfor -%}\n",
            1,
        ),
    ]
    all_pass = True
    for label, text, expected_count in cases:
        issues = find_loop_scoping_issues(text)
        ok = len(issues) == expected_count
        print(
            f"{'PASS' if ok else 'FAIL'}: {label} → "
            f"{len(issues)} 의심 (expected {expected_count})"
        )
        if not ok:
            all_pass = False
            for ln, var, snippet in issues:
                print(f"  line {ln}: var={var!r}, snippet={snippet!r}")
    return 0 if all_pass else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="rule 22 R7 / rule 95 R1 Jinja2 loop-scoping 검증"
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "file_path", nargs="?", default=None,
        help="단일 파일 검사 (생략 시 staged YAML 전수)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if os.environ.get("JINJA_NAMESPACE_SKIP") == "1":
        return 0
    skip_files = set(
        os.environ.get("JINJA_NAMESPACE_SKIP_FILE", "").split(":")
    )

    repo_root = Path(".").resolve()
    if args.file_path:
        files = [args.file_path]
    else:
        files = _staged_files(repo_root)

    if not files:
        return 0

    total_issues: dict[str, list[tuple[int, str, str]]] = {}
    for f in files:
        if f in skip_files:
            continue
        path = Path(f)
        if not path.is_absolute():
            path = repo_root / path
        issues = _check_file(path)
        if issues:
            total_issues[f] = issues

    if not total_issues:
        return 0

    print(
        "[jinja namespace] rule 22 R7 / rule 95 R1 — loop 내 set 의심 (advisory):",
        file=sys.stderr,
    )
    print(
        "  Jinja2 default scoping: for-block 내 {% set var %} 가 outer scope 에 반영 안 됨.",
        file=sys.stderr,
    )
    print(
        "  → namespace() 또는 dict/list mutation (set _ = x.update(...)) 사용 권장.\n",
        file=sys.stderr,
    )
    for f, issues in total_issues.items():
        print(f"  {f}:", file=sys.stderr)
        for ln, var, snippet in issues:
            print(f"    line {ln}: set {var}=... → {snippet}", file=sys.stderr)
    print(
        "\n  → false-positive 시 의심 line 직전에 `{# noqa-jinja-namespace #}` 또는 환경변수 skip:",
        file=sys.stderr,
    )
    print(
        "       JINJA_NAMESPACE_SKIP=1 git commit ...\n"
        "       JINJA_NAMESPACE_SKIP_FILE='path/to/file.yml' git commit ...",
        file=sys.stderr,
    )

    return 0  # advisory


if __name__ == "__main__":
    sys.exit(main())
