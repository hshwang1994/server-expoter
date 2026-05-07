#!/usr/bin/env python3
"""advisory hook 4종 codebase 전체 false-positive 스캔.

Usage:
    python scripts/ai/scan_advisory_hooks.py
    python scripts/ai/scan_advisory_hooks.py --hook=jinja_namespace
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 같은 디렉터리의 hook 모듈 import
sys.path.insert(0, str(Path(__file__).parent / "hooks"))

from pre_commit_jinja_namespace_check import (  # noqa: E402
    _check_file as jinja_check_file,
)
from pre_commit_fragment_skeleton_sync import (  # noqa: E402
    EXPECTED_SECTIONS,
    SKELETON_FILES,
    extract_skeleton_sections,
)


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def scan_jinja_namespace() -> int:
    """rule 22 R7 — Jinja2 loop-scoping false-positive 스캔."""
    print("[1/3] Jinja namespace scan (yml + j2)...")
    targets: list[Path] = []
    for ext in ("yml", "yaml", "j2"):
        targets.extend(REPO_ROOT.rglob(f"*.{ext}"))
    targets = [
        p
        for p in targets
        if ".git" not in p.parts
        and "venv" not in p.parts
        and "node_modules" not in p.parts
    ]
    issues_total: dict[str, list] = {}
    for path in targets:
        try:
            issues = jinja_check_file(path)
        except Exception as exc:
            print(f"  ERROR reading {path}: {exc}", file=sys.stderr)
            continue
        if issues:
            issues_total[str(path.relative_to(REPO_ROOT))] = issues
    print(f"  scanned: {len(targets)} files")
    if issues_total:
        print(f"  ISSUES: {len(issues_total)} files")
        for f, issues in issues_total.items():
            for ln, var, snippet in issues:
                print(f"    {f}:{ln} var={var!r} -> {snippet[:80]!r}")
        return 1
    print("  CLEAN — false-positive 0")
    return 0


def scan_fragment_skeleton() -> int:
    """rule 22 R5 + 13 R1 — fragment skeleton 동기화 스캔.

    EXPECTED_SECTIONS 10 모두 3 파일에 존재 + 동일 set.
    """
    print("[2/3] Fragment skeleton sync scan...")
    issues: list[str] = []
    section_sets: list[tuple[str, set[str]]] = []
    for skel_path in SKELETON_FILES:
        full = REPO_ROOT / skel_path
        if not full.exists():
            issues.append(f"{skel_path}: 파일 부재")
            continue
        text = full.read_text(encoding="utf-8")
        sections = extract_skeleton_sections(text)
        section_sets.append((skel_path, sections))
        missing = EXPECTED_SECTIONS - sections
        extra = sections - EXPECTED_SECTIONS
        if missing or extra:
            issues.append(
                f"{skel_path}: missing={sorted(missing)} extra={sorted(extra)}"
            )
    # 3 파일 동일성 검증
    if section_sets and len({frozenset(s) for _, s in section_sets}) > 1:
        issues.append(
            "3 파일 sections set 불일치: "
            + " | ".join(f"{p}={sorted(s)}" for p, s in section_sets)
        )
    if not issues:
        print(f"  CLEAN — 정본 10 sections ({sorted(EXPECTED_SECTIONS)})")
        return 0
    print("  ISSUES:")
    for line in issues:
        print(f"    {line}")
    return 1


def scan_envelope_change() -> int:
    """rule 96 R1-B — envelope shape 변경 스캔 (현재 staged 없으므로 skip)."""
    print("[3/3] Envelope change scan (no staged files — skipped)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hook", choices=["jinja_namespace", "fragment_skeleton", "all"], default="all")
    args = parser.parse_args()

    rc = 0
    if args.hook in ("jinja_namespace", "all"):
        rc |= scan_jinja_namespace()
    if args.hook in ("fragment_skeleton", "all"):
        rc |= scan_fragment_skeleton()
    if args.hook == "all":
        rc |= scan_envelope_change()

    print()
    if rc == 0:
        print("[RESULT] 모든 advisory hook false-positive 0 — blocking 격상 검토 가능")
    else:
        print("[RESULT] 위반 발견 — blocking 격상 보류")
    return rc


if __name__ == "__main__":
    sys.exit(main())
