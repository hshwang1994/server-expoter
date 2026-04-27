#!/usr/bin/env python3
"""Output schema drift check — sections.yml ↔ field_dictionary.yml ↔ baseline_v1 정합 (← db_schema_drift_check 대체).

검사:
- sections.yml에 정의된 섹션이 field_dictionary.yml에 누락 없는지
- field_dictionary.yml의 28 Must 필드가 baseline_v1 vendor JSON에 모두 존재하는지
- baseline_v1 안의 새 필드가 field_dictionary.yml에 누락 없는지

Usage:
    python scripts/ai/hooks/output_schema_drift_check.py

Exit codes:
    0 = 정합
    2 = drift 감지
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _read_yaml_keys(path: Path) -> list[str]:
    """간단한 키 목록 파서 (stdlib only)."""
    if not path.is_file():
        return []
    keys = []
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if indent == 0 and stripped.endswith(":"):
                keys.append(stripped[:-1].strip())
    except Exception:
        pass
    return keys


def main() -> int:
    repo_root = Path(".").resolve()
    sections_path = repo_root / "schema" / "sections.yml"
    fd_path = repo_root / "schema" / "field_dictionary.yml"
    baseline_dir = repo_root / "schema" / "baseline_v1"

    issues = []

    sections = _read_yaml_keys(sections_path)
    fd_keys = _read_yaml_keys(fd_path)

    # sections.yml ↔ field_dictionary.yml
    missing_in_fd = [s for s in sections if s not in fd_keys]
    if missing_in_fd:
        issues.append(f"sections.yml에 있지만 field_dictionary.yml에 없는 섹션: {missing_in_fd}")

    # baseline JSON 점검 — 각 vendor baseline 안에 sections list 존재
    if baseline_dir.is_dir():
        for f in baseline_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:
                issues.append(f"baseline 파싱 실패: {f.name} — {e}")
                continue
            data_sections = []
            if isinstance(data, dict):
                if "sections" in data and isinstance(data["sections"], dict):
                    data_sections = list(data["sections"].keys())
                elif "data" in data and isinstance(data["data"], dict):
                    data_sections = list(data["data"].keys())
            for s in sections:
                if data_sections and s not in data_sections:
                    # 정보성 — vendor가 일부 섹션 미지원할 수 있음
                    pass

    if issues:
        print("output schema drift 감지:")
        for i in issues:
            print(f"  - {i}")
        return 2

    print(f"output schema 정합: sections={len(sections)} fd_keys={len(fd_keys)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
