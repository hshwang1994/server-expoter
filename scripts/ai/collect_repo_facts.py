#!/usr/bin/env python3
"""server-exporter 저장소 팩트 수집 — 채널 / Python / Ansible / 벤더 / 테스트 카운트.

세션 시작 hook에서 1회 실행 후 .claude/.cache/repo_facts.json에 캐시.

Usage:
    python scripts/ai/collect_repo_facts.py [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict


def _count_files(repo_root: Path, glob: str) -> int:
    """glob 패턴 매치 파일 수."""
    try:
        return sum(1 for _ in repo_root.rglob(glob))
    except Exception:
        return 0


def _python_version() -> str:
    """Python 인터프리터 버전 (Agent에서 사용 중인 것)."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _ansible_version(repo_root: Path) -> str:
    """ansible-core 버전 검색 (ansible.cfg 또는 시스템 ansible)."""
    try:
        r = subprocess.run(
            ["ansible", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            m = re.search(r"core ([\d\.]+)", r.stdout)
            if m:
                return m.group(1)
            m = re.search(r"ansible \[core ([\d\.]+)\]", r.stdout)
            if m:
                return m.group(1)
    except Exception:
        pass
    return "?"


def _vendor_count(repo_root: Path) -> int:
    """adapters/redfish/ 안의 벤더별 어댑터 수 (generic 제외)."""
    rf_dir = repo_root / "adapters" / "redfish"
    if not rf_dir.is_dir():
        return 0
    return sum(
        1 for f in rf_dir.glob("*.yml")
        if f.name not in ("redfish_generic.yml",)
    )


def _channel_dirs(repo_root: Path) -> Dict[str, bool]:
    """3-channel gather 디렉터리 존재 확인."""
    return {
        "os-gather": (repo_root / "os-gather").is_dir(),
        "esxi-gather": (repo_root / "esxi-gather").is_dir(),
        "redfish-gather": (repo_root / "redfish-gather").is_dir(),
    }


def collect_facts(repo_root: Path) -> Dict[str, object]:
    """저장소 핵심 사실 수집."""
    py_files = _count_files(repo_root, "*.py")
    yml_files = _count_files(repo_root, "*.yml") + _count_files(repo_root, "*.yaml")
    pytest_files = _count_files(repo_root, "test_*.py") + _count_files(repo_root, "*_test.py")
    fixture_files = _count_files(repo_root / "tests" / "fixtures", "*.json") if (repo_root / "tests" / "fixtures").is_dir() else 0
    baseline_files = _count_files(repo_root / "tests" / "baseline_v1", "*.json") if (repo_root / "tests" / "baseline_v1").is_dir() else 0
    adapter_files = _count_files(repo_root / "adapters", "*.yml")

    return {
        "project": "server-exporter",
        "python_version": _python_version(),
        "ansible_version": _ansible_version(repo_root),
        "vendor_count": _vendor_count(repo_root),
        "adapter_files": adapter_files,
        "python_files": py_files,
        "yaml_files": yml_files,
        "pytest_files": pytest_files,
        "fixture_files": fixture_files,
        "baseline_files": baseline_files,
        "channels": _channel_dirs(repo_root),
        # clovirone 호환 필드 (session_start.py가 참조)
        "existing_module_count": sum(_channel_dirs(repo_root).values()),
        "java_files_total": py_files,  # 호환: '코드 파일' 의미로 사용
        "test_files_total": pytest_files,
        "spring_boot_version": _ansible_version(repo_root),  # 호환
        "java_version": _python_version(),  # 호환
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="server-exporter 저장소 팩트")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    facts = collect_facts(Path(args.repo_root).resolve())

    if args.json:
        print(json.dumps(facts, ensure_ascii=False, indent=2))
    else:
        print(f"프로젝트: {facts['project']}")
        print(f"Python {facts['python_version']} / Ansible {facts['ansible_version']}")
        print(f"채널: 3종 ({sum(facts['channels'].values())}개 활성)")
        print(f"벤더 어댑터: {facts['adapter_files']}개 (벤더 {facts['vendor_count']}종)")
        print(f"Python 파일: {facts['python_files']}개 / pytest: {facts['pytest_files']}개")
        print(f"Fixture: {facts['fixture_files']}개 / Baseline: {facts['baseline_files']}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
