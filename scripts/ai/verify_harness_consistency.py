#!/usr/bin/env python3
"""하네스 일관성 검증 — rules ↔ skills ↔ agents ↔ policy 참조 정합.

각 rule/skill/agent 본문에서 다른 rule/skill/agent를 참조할 때
실제 존재하는 파일인지 grep + 파일 존재 검증.

또한 server-exporter 어휘 whitelist 적용 — clovirone 잔재 (Java/Spring/MyBatis/...) 검출.

Usage:
    python scripts/ai/verify_harness_consistency.py [--strict]

Exit codes:
    0 = 통과
    1 = 실행 에러
    2 = 일관성 위반 발견
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# clovirone 잔재 어휘 (server-exporter 본문에 등장하면 안 됨)
FORBIDDEN_WORDS = [
    "MyBatis",
    "Spring Boot",
    "Spring Bean",
    "Freemarker",
    "FTL",
    "Vue.js",
    "jQuery",
    "Gradle",
    "MariaDB",
    "Flyway",
    "Spock",
    "Playwright",
    "Bitbucket Pipelines",
    "clovircm-domain",
    "clovircm-web",
    "plugin-posco",
    "plugin-smilegate",
    "plugin-sdk",
    "sk-hynix-dev",
    "sk-hynix-claude",
    "BillingCalculator",
]

# rule reference 패턴: "rule NN" 또는 "rules/NN-..."
RULE_REF_RE = re.compile(r"\.claude/rules/(\d{2}-[a-z0-9-]+)\.md")
SKILL_REF_RE = re.compile(r"\.claude/skills/([a-z0-9-]+)/")
AGENT_REF_RE = re.compile(r"\.claude/agents/([a-z0-9-]+)\.md")
POLICY_REF_RE = re.compile(r"\.claude/policy/([a-z0-9-]+\.yaml)")


def _scan_file(path: Path) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    """단일 파일에서 참조 + 잔재 어휘 추출."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return [], [], [], [], []

    rule_refs = RULE_REF_RE.findall(text)
    skill_refs = SKILL_REF_RE.findall(text)
    agent_refs = AGENT_REF_RE.findall(text)
    policy_refs = POLICY_REF_RE.findall(text)

    forbidden = []
    # 의도적 인용/명시 표현 — false positive 방지
    allow_markers = (
        "clovirone-base", "clovirone", "출처", "변환", "잔재", "금지 패턴",
        "Forbidden", "사용 안 함", "동등 역할", "동일 정신", "대신", "→",
        "(과거)", "관찰된", "이전", "deprecate", "polyfill",
        "와 달리", "에 대응", "DBA", "etc",
    )
    for word in FORBIDDEN_WORDS:
        if word in text:
            for line in text.splitlines():
                if word in line and not any(marker in line for marker in allow_markers):
                    forbidden.append(f"{word}: {line.strip()[:80]}")
                    break

    return rule_refs, skill_refs, agent_refs, policy_refs, forbidden


def main() -> int:
    parser = argparse.ArgumentParser(description="하네스 일관성 검증")
    parser.add_argument("--strict", action="store_true", help="잔재 어휘도 위반 처리")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    claude_dir = repo_root / ".claude"

    if not claude_dir.is_dir():
        print(f".claude/ 없음: {claude_dir}", file=sys.stderr)
        return 1

    # 존재하는 rule/skill/agent/policy 카탈로그
    existing_rules: Set[str] = {
        f.stem for f in (claude_dir / "rules").glob("*.md")
    } if (claude_dir / "rules").is_dir() else set()
    existing_skills: Set[str] = {
        d.name for d in (claude_dir / "skills").iterdir() if d.is_dir()
    } if (claude_dir / "skills").is_dir() else set()
    existing_agents: Set[str] = {
        f.stem for f in (claude_dir / "agents").glob("*.md")
    } if (claude_dir / "agents").is_dir() else set()
    existing_policies: Set[str] = {
        f.name for f in (claude_dir / "policy").glob("*.yaml")
    } if (claude_dir / "policy").is_dir() else set()

    issues: List[str] = []
    forbidden_total: List[str] = []

    # SKILL.md frontmatter name ↔ 폴더명 일치 검사 (NEXT_ACTIONS P2 — 2026-04-27 추가)
    skill_name_re = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
    for skill_dir in (claude_dir / "skills").iterdir() if (claude_dir / "skills").is_dir() else []:
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            issues.append(f".claude/skills/{skill_dir.name}/SKILL.md: 누락")
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception:
            continue
        m = skill_name_re.search(text)
        if not m:
            issues.append(f".claude/skills/{skill_dir.name}/SKILL.md: frontmatter 'name' 누락")
        elif m.group(1).strip().strip('"').strip("'") != skill_dir.name:
            issues.append(
                f".claude/skills/{skill_dir.name}/SKILL.md: name '{m.group(1).strip()}' "
                f"↔ 폴더 '{skill_dir.name}' 불일치"
            )

    for path in claude_dir.rglob("*.md"):
        rule_refs, skill_refs, agent_refs, policy_refs, forbidden = _scan_file(path)
        rel = path.relative_to(repo_root).as_posix()

        for r in rule_refs:
            if r not in existing_rules:
                issues.append(f"{rel}: 존재하지 않는 rule 참조 — {r}")
        for s in skill_refs:
            if s not in existing_skills:
                issues.append(f"{rel}: 존재하지 않는 skill 참조 — {s}")
        for a in agent_refs:
            if a not in existing_agents:
                issues.append(f"{rel}: 존재하지 않는 agent 참조 — {a}")
        for p in policy_refs:
            if p not in existing_policies:
                issues.append(f"{rel}: 존재하지 않는 policy 참조 — {p}")

        for fw in forbidden:
            forbidden_total.append(f"{rel}: {fw}")

    print("=== 하네스 일관성 검증 ===")
    print(f"rules: {len(existing_rules)}, skills: {len(existing_skills)}, "
          f"agents: {len(existing_agents)}, policies: {len(existing_policies)}")

    if issues:
        print(f"\n참조 위반: {len(issues)}건")
        for i in issues[:50]:
            print(f"  - {i}")
        if len(issues) > 50:
            print(f"  ... ({len(issues) - 50}건 추가)")

    if forbidden_total:
        print(f"\nclovirone 잔재 어휘: {len(forbidden_total)}건")
        for f in forbidden_total[:20]:
            print(f"  - {f}")
        if len(forbidden_total) > 20:
            print(f"  ... ({len(forbidden_total) - 20}건 추가)")

    if issues or (args.strict and forbidden_total):
        return 2

    print("\n통과: 모든 참조 정합 확인")
    return 0


if __name__ == "__main__":
    sys.exit(main())
