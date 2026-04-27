#!/usr/bin/env python3
"""post-merge hook — 머지로 들어온 변경에 대한 자동 검사 (rule 97).

server-exporter 자동 검사 5종:
(a) Jenkinsfile cron 변경 검사 (rule 92 R5 — Jenkinsfile cron 표 동기화)
(b) Ansible/Python/YAML 의심 패턴 (rule 95 R1)
    - raw 모듈 권한 미설정
    - vault 변수가 실 평문에 누설
    - 다른 gather의 fragment 침범 (rule 22)
(c) Adapter YAML metadata 주석 누락 (rule 96 R1 — origin 주석 의무)
(d) schema/sections.yml + field_dictionary.yml 버전 충돌 (rule 92 R5)
(e) 결과 보고: docs/ai/incoming-review/<YYYY-MM-DD>-<sha>.md

Advisory: 머지 차단하지 않음. 위반 발견 시 후속 PR 권고.

Usage:
    git checkout 후 자동 호출 (post-merge git hook). 수동 호출도 가능:
    python scripts/ai/hooks/post_merge_incoming_review.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

if os.environ.get("INCOMING_REVIEW_SKIP") == "1":
    sys.exit(0)


def _run(cmd: list[str], cwd: Path, timeout: int = 10) -> str:
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(cwd),
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def _changed_files_in_merge(repo_root: Path) -> List[str]:
    """머지로 들어온 변경 파일 목록 (HEAD@{1}..HEAD diff)."""
    out = _run(
        ["git", "diff", "--name-only", "HEAD@{1}..HEAD"], repo_root
    )
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def check_jenkinsfile_cron(repo_root: Path, files: List[str]) -> List[str]:
    """Jenkinsfile* 변경 시 cron 트리거 변경 의심."""
    issues = []
    for f in files:
        if not re.match(r"^Jenkinsfile", f):
            continue
        full = repo_root / f
        if not full.is_file():
            continue
        text = full.read_text(encoding="utf-8", errors="replace")
        if "cron(" in text or "triggers" in text:
            issues.append(f"[Jenkinsfile cron] {f} — cron 표현식 변경 가능. "
                          "rule 92 R5 동기화 확인 권장")
    return issues


def check_python_yaml_suspicions(repo_root: Path, files: List[str]) -> List[str]:
    """Ansible/Python/YAML 의심 패턴."""
    issues = []
    for f in files:
        if not f.endswith((".py", ".yml", ".yaml")):
            continue
        full = repo_root / f
        if not full.is_file():
            continue
        text = full.read_text(encoding="utf-8", errors="replace")

        # vault 평문 누설 의심
        if re.search(r"vault.*password.*[:=].*[\'\"][a-zA-Z0-9]{4,}[\'\"]", text, re.IGNORECASE):
            issues.append(f"[vault 누설 의심] {f} — vault password가 평문에 보입니다. rule 60 확인")

        # raw 모듈 권한 미설정
        if "raw:" in text and "become:" not in text:
            # context 따라 false positive 가능 (sudo 불필요한 명령) → advisory
            if re.search(r"^\s*-\s*name:.*", text, re.MULTILINE):  # 작업 정의 형태
                issues.append(f"[raw 모듈] {f} — become 미지정. 권한 확인 권장")

        # 다른 gather의 fragment 침범 의심 (rule 22)
        # 예: redfish-gather의 task가 _sections_cpu_collected_fragment 같은 변수를
        # 직접 set_fact로 수정하는 경우
        if "gather" in f and re.search(r"set_fact:\s*\n\s*_sections_\w+_collected_fragment", text):
            issues.append(f"[fragment 침범 의심] {f} — 다른 섹션의 fragment 변수를 set_fact로 수정. rule 22 확인")

    return issues


def check_adapter_metadata(repo_root: Path, files: List[str]) -> List[str]:
    """Adapter YAML origin 주석 누락 (rule 96 R1)."""
    issues = []
    for f in files:
        if not re.match(r"^adapters/", f) or not f.endswith(".yml"):
            continue
        full = repo_root / f
        if not full.is_file():
            continue
        text = full.read_text(encoding="utf-8", errors="replace")
        # 첫 30줄 안에 vendor / firmware / tested_against 또는 origin 주석 있는지
        head = "\n".join(text.splitlines()[:30])
        has_meta = any(
            kw in head.lower()
            for kw in ("vendor:", "firmware:", "tested_against:", "# origin:", "# 출처:")
        )
        if not has_meta:
            issues.append(f"[adapter metadata 누락] {f} — vendor/firmware/tested_against 주석 권장 (rule 96)")
    return issues


def check_schema_version_conflict(repo_root: Path, files: List[str]) -> List[str]:
    """sections.yml / field_dictionary.yml 동시 변경 시 버전 충돌 의심."""
    issues = []
    schema_files = [f for f in files
                    if f.startswith("schema/") and f.endswith((".yml", ".yaml"))]
    if len(schema_files) >= 2:
        if "schema/sections.yml" in schema_files and "schema/field_dictionary.yml" in schema_files:
            issues.append(
                "[schema 동시 변경] sections.yml + field_dictionary.yml 동시 변경. "
                "baseline_v1 회귀 검증 권장 (rule 13)"
            )
    return issues


def main() -> int:
    repo_root = Path(".").resolve()
    files = _changed_files_in_merge(repo_root)

    if not files:
        return 0

    all_issues: List[Tuple[str, List[str]]] = [
        ("Jenkinsfile cron 변경", check_jenkinsfile_cron(repo_root, files)),
        ("Python/YAML 의심 패턴", check_python_yaml_suspicions(repo_root, files)),
        ("Adapter metadata", check_adapter_metadata(repo_root, files)),
        ("Schema 버전 충돌", check_schema_version_conflict(repo_root, files)),
    ]

    total_issues = sum(len(issues) for _, issues in all_issues)

    # 보고서 생성
    sha = _run(["git", "rev-parse", "--short", "HEAD"], repo_root).strip() or "unknown"
    date = time.strftime("%Y-%m-%d")
    report_dir = repo_root / "docs" / "ai" / "incoming-review"
    try:
        report_dir.mkdir(parents=True, exist_ok=True)
        report = report_dir / f"{date}-{sha}.md"

        lines = [
            f"# Incoming merge review — {date} ({sha})",
            "",
            f"머지로 들어온 변경 파일 {len(files)}건. 자동 검사 결과:",
            "",
        ]
        for category, issues in all_issues:
            if issues:
                lines.append(f"## {category}\n")
                for i in issues:
                    lines.append(f"- {i}")
                lines.append("")

        if total_issues == 0:
            lines.append("자동 검출 위반 없음 (clean)")

        report.write_text("\n".join(lines) + "\n", encoding="utf-8")

        if total_issues > 0:
            print(f"\n[incoming review] 위반 {total_issues}건 — 보고서: {report}")
        else:
            print(f"\n[incoming review] clean ({len(files)} 파일) — 보고서: {report}")
    except OSError:
        pass

    return 0  # advisory


if __name__ == "__main__":
    sys.exit(main())
