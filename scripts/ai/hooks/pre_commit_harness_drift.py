#!/usr/bin/env python3
"""pre-commit hook — 하네스 표면 drift 감지 (rule 28 #7).

`.claude/policy/surface-counts.yaml` baseline ↔ 실 카운트 비교.
drift 시 pre-commit 차단 (사용자가 surface-counts.yaml 갱신 후 재커밋).

Usage:
    pre-commit git hook이 자동 호출. 수동:
    python scripts/ai/hooks/pre_commit_harness_drift.py [--update]

Exit codes:
    0 = 일치
    2 = drift (commit 차단)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _count_files(path: Path, glob: str = "*.md") -> int:
    if not path.is_dir():
        return 0
    return sum(1 for f in path.rglob(glob) if f.is_file())


def _count_dirs(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for d in path.iterdir() if d.is_dir())


def _read_baseline(path: Path) -> dict[str, int]:
    """surface-counts.yaml에서 카운트 읽기 (단순 'key: value' 파서)."""
    out: dict[str, int] = {}
    if not path.is_file():
        return out
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                v = v.strip().split("#")[0].strip()
                try:
                    out[k.strip()] = int(v)
                except ValueError:
                    continue
    except Exception:
        pass
    return out


def _format_yaml(counts: dict[str, int]) -> str:
    lines = [
        "# Hardness 표면 카운트 — pre-commit drift 감지용",
        "# scripts/ai/hooks/pre_commit_harness_drift.py --update 로 갱신",
        "",
    ]
    for k in sorted(counts.keys()):
        lines.append(f"{k}: {counts[k]}")
    return "\n".join(lines) + "\n"


def main() -> int:
    if os.environ.get("HARNESS_DRIFT_SKIP") == "1":
        return 0

    parser = argparse.ArgumentParser(description="하네스 표면 drift")
    parser.add_argument("--update", action="store_true", help="baseline 갱신")
    args = parser.parse_args()

    repo_root = Path(".").resolve()
    claude = repo_root / ".claude"

    counts = {
        "rules":     _count_files(claude / "rules", "*.md"),
        "skills":    _count_dirs(claude / "skills"),
        "agents":    _count_files(claude / "agents", "*.md"),
        "policies":  _count_files(claude / "policy", "*.yaml"),
        "roles":     _count_dirs(claude / "role"),
        "templates": _count_files(claude / "templates", "*"),
        "commands":  _count_files(claude / "commands", "*.md"),
        "hooks":     _count_files(repo_root / "scripts" / "ai" / "hooks", "*.py"),
    }

    baseline_path = claude / "policy" / "surface-counts.yaml"

    if args.update:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(_format_yaml(counts), encoding="utf-8")
        print(f"surface-counts.yaml 갱신: {counts}")
        return 0

    baseline = _read_baseline(baseline_path)
    if not baseline:
        # baseline 없음 → 첫 커밋이면 생성 권고만 (advisory)
        print("[harness drift] surface-counts.yaml baseline 없음.")
        print("  → python scripts/ai/hooks/pre_commit_harness_drift.py --update 권장")
        return 0

    drifted = []
    for k, current in counts.items():
        b = baseline.get(k)
        if b is None:
            drifted.append(f"  - {k}: 미등록 → {current}")
        elif b != current:
            drifted.append(f"  - {k}: {b} → {current}")

    if drifted:
        print("[harness drift] 표면 카운트 변경 감지:", file=sys.stderr)
        for d in drifted:
            print(d, file=sys.stderr)
        print("\n→ surface-counts.yaml 갱신 후 재커밋:", file=sys.stderr)
        print("  python scripts/ai/hooks/pre_commit_harness_drift.py --update", file=sys.stderr)
        print("  HARNESS_DRIFT_SKIP=1 git commit ... (skip 옵션)", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
