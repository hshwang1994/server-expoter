#!/usr/bin/env python3
"""벤더 경계 검증 — gather/common 코드에 vendor 이름 하드코딩 금지.

server-exporter 원칙:
- common/, *-gather/ 코드는 vendor-agnostic
- vendor-specific 로직은 adapters/ YAML 또는 redfish-gather/tasks/vendors/{vendor}/ 안에만
- vendor_aliases.yml은 어떤 코드에서도 참조 가능 (정규화 메타)

검사 대상:
- os-gather/, esxi-gather/, redfish-gather/ 안의 .py / .yml (단, tasks/vendors/ 제외)
- common/ 안의 .py / .yml

검사 패턴: vendor 이름 (Dell, HPE, Lenovo, Supermicro, Cisco) 하드코딩

Usage:
    python scripts/ai/verify_vendor_boundary.py [--strict]

Exit codes:
    0 = 통과
    2 = 위반 발견
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List

# Windows cp949 환경에서 비-ASCII 출력 시 UnicodeEncodeError 방지
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass


# 벤더 이름 (대소문자 구분 없이)
VENDORS = ["Dell", "HPE", "Hewlett", "Lenovo", "Supermicro", "Cisco", "iDRAC", "iLO", "XCC", "CIMC"]

# 검사 대상 디렉터리
SCAN_DIRS = ["common", "os-gather", "esxi-gather", "redfish-gather"]

# 제외 (벤더 분기가 정상인 경로)
# rule 12 R1 Allowed:
#   - redfish-gather/tasks/vendors/{vendor}/  (OEM tasks)
#   - adapters/{channel}/{vendor}_*.yml       (어댑터 YAML)
#   - common/vars/vendor_aliases.yml          (vendor alias 정규화 메타)
EXCLUDE_PATTERNS = [
    re.compile(r"redfish-gather/tasks/vendors/"),
    re.compile(r"adapters/"),
    re.compile(r"vault/"),
    re.compile(r"tests/"),
    re.compile(r"common/vars/vendor_aliases\.yml$"),
]


def _is_excluded(rel_path: str) -> bool:
    return any(p.search(rel_path) for p in EXCLUDE_PATTERNS)


def _python_docstring_lines(lines: List[str]) -> set:
    """Python 파일 triple-quote docstring 라인 번호 set (1-indexed).

    docstring 안의 vendor 이름은 코드 분기 아니므로 검사 제외.
    """
    in_doc = False
    quote = None
    result: set = set()
    for i, line in enumerate(lines, start=1):
        if not in_doc:
            # 둘 중 먼저 나오는 triple-quote 위치 비교
            triple_idx_3d = line.find('"""')
            triple_idx_3s = line.find("'''")
            candidates = [(idx, q) for idx, q in
                          [(triple_idx_3d, '"""'), (triple_idx_3s, "'''")]
                          if idx >= 0]
            if not candidates:
                continue
            # 가장 먼저 나오는 quote
            candidates.sort(key=lambda x: x[0])
            idx, q = candidates[0]
            after = line[idx + 3:]
            if q in after:
                # 같은 라인에 닫는 quote — 한 줄 docstring
                result.add(i)
            else:
                in_doc = True
                quote = q
                result.add(i)
        else:
            result.add(i)
            if quote in line:
                in_doc = False
                quote = None
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="벤더 경계 검증")
    parser.add_argument("--strict", action="store_true",
                        help="comment 안의 vendor 이름도 위반 처리")
    parser.add_argument("--full", action="store_true",
                        help="위반 30건 초과 시 전체 출력")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    violations: List[str] = []

    vendor_re = re.compile(
        r"\b(" + "|".join(VENDORS) + r")\b",
        re.IGNORECASE,
    )

    for scan_dir in SCAN_DIRS:
        d = repo_root / scan_dir
        if not d.is_dir():
            continue

        for f in d.rglob("*"):
            if not f.is_file() or f.suffix not in (".py", ".yml", ".yaml"):
                continue
            rel = f.relative_to(repo_root).as_posix()
            if _is_excluded(rel):
                continue

            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue

            # Python 파일 triple-quote docstring 영역 (--strict 아닐 때만 skip 대상)
            ds_lines: set = (
                _python_docstring_lines(lines)
                if f.suffix == ".py" and not args.strict
                else set()
            )

            # 라인별 silence 마커 매칭 — 라인 또는 직전 라인에 nosec rule12-r1
            # 형식: # nosec rule12-r1 / {# nosec rule12-r1 ... #} / {#- nosec rule12-r1 ... -#}
            nosec_re = re.compile(r"\bnosec\s+rule12-r1", re.IGNORECASE)

            for lineno, line in enumerate(lines, start=1):
                stripped = line.strip()
                # comment 라인 skip (--strict 아니면)
                if not args.strict:
                    if stripped.startswith("#") or stripped.startswith("//"):
                        continue
                    # Python triple-quote docstring 영역 skip
                    if lineno in ds_lines:
                        continue
                    # YAML 안의 # comment는 라인 끝 부분만
                    if "#" in line and vendor_re.search(line.split("#", 1)[0]) is None:
                        continue
                    # 라인 자체에 nosec rule12-r1 silence
                    if nosec_re.search(line):
                        continue
                    # 직전 라인 (또는 직전 직전, Jinja2 {#...#} 줄바꿈)에 nosec 주석
                    if lineno >= 2 and nosec_re.search(lines[lineno - 2]):
                        continue

                m = vendor_re.search(line)
                if m:
                    violations.append(f"{rel}:{lineno}: {m.group(1)} - {stripped[:80]}")

    if violations:
        print(f"벤더 경계 위반: {len(violations)}건")
        head = 30
        for v in violations[:head]:
            print(f"  - {v}")
        if len(violations) > head:
            if args.full:
                for v in violations[head:]:
                    print(f"  - {v}")
            else:
                print(f"  ... ({len(violations) - head}건 추가, --full 로 전체 출력)")
        return 2

    print("벤더 경계 통과: common/ + 3-channel gather에 vendor 이름 하드코딩 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
