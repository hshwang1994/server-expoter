#!/usr/bin/env python3
"""PROJECT_MAP fingerprint drift 체크.

`.claude/policy/project-map-fingerprint.yaml`에 baseline 파일/디렉터리 SHA-1 카운트를 기록.
실제 저장소와 비교하여 drift 감지.

Exit codes:
    0 = 일치 (drift 없음)
    2 = drift 감지
    3 = baseline 없음
    1 = 실행 에러

Usage:
    python scripts/ai/check_project_map_drift.py [--update]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict


WATCHED_DIRS = [
    "os-gather",
    "esxi-gather",
    "redfish-gather",
    "common",
    "adapters",
    "schema",
    "callback_plugins",
    "filter_plugins",
    "lookup_plugins",
    "module_utils",
    "tests",
]


def fingerprint_dir(d: Path) -> str:
    """디렉터리 안의 파일 경로/크기 list를 SHA-1로 해싱."""
    if not d.is_dir():
        return "missing"
    h = hashlib.sha1()
    for f in sorted(d.rglob("*")):
        if f.is_file():
            try:
                rel = f.relative_to(d).as_posix()
                size = f.stat().st_size
                h.update(f"{rel}:{size}\n".encode("utf-8"))
            except Exception:
                pass
    return h.hexdigest()[:12]


def _parse_fingerprint_yaml(yaml_text: str) -> Dict[str, str]:
    """간단한 키:값 YAML 파서 (stdlib only)."""
    out: Dict[str, str] = {}
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _format_fingerprint_yaml(fp: Dict[str, str]) -> str:
    """fingerprint dict를 YAML로 직렬화."""
    lines = ["# PROJECT_MAP fingerprint — 디렉터리별 SHA-1 (앞 12자)",
             "# scripts/ai/check_project_map_drift.py --update 로 갱신",
             ""]
    for k in sorted(fp.keys()):
        lines.append(f"{k}: {fp[k]}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="PROJECT_MAP drift check")
    parser.add_argument("--update", action="store_true", help="baseline 갱신")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    fp_path = repo_root / ".claude" / "policy" / "project-map-fingerprint.yaml"

    current = {d: fingerprint_dir(repo_root / d) for d in WATCHED_DIRS}

    if args.update:
        fp_path.parent.mkdir(parents=True, exist_ok=True)
        fp_path.write_text(_format_fingerprint_yaml(current), encoding="utf-8")
        print(f"baseline 갱신: {fp_path}")
        return 0

    if not fp_path.is_file():
        print(f"baseline 없음: {fp_path}")
        print("→ python scripts/ai/check_project_map_drift.py --update 실행 권장")
        return 3

    baseline = _parse_fingerprint_yaml(fp_path.read_text(encoding="utf-8"))

    drifted = []
    for d, h in current.items():
        if baseline.get(d) and baseline[d] != h:
            drifted.append((d, baseline[d], h))
        elif d not in baseline:
            drifted.append((d, "(미등록)", h))

    if drifted:
        print(f"drift 감지: {len(drifted)}건")
        for d, old, new in drifted:
            print(f"  - {d}: {old} → {new}")
        return 2

    print("PROJECT_MAP fingerprint 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
