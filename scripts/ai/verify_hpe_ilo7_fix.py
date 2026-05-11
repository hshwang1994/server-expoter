"""Mock 5 시나리오 점수 검증 — cycle hpe-ilo7-gen12-match-fix.

hpe_ilo7.yml firmware_patterns 확장 (cycle 2026-05-11) 후
S1~S5 mock 시나리오에서 의도된 adapter 가 선택되는지 검증.

Usage:
    python scripts/ai/verify_hpe_ilo7_fix.py

Exits 0 on PASS, 1 on FAIL.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from module_utils.adapter_common import adapter_score


REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTERS_DIR = REPO_ROOT / "adapters" / "redfish"

ADAPTER_NAMES: tuple[str, ...] = (
    "hpe_ilo7",
    "hpe_ilo6",
    "hpe_ilo5",
    "hpe_ilo4",
    "hpe_csus_3200",
    "hpe_superdome_flex",
)


def load_adapters() -> dict[str, dict]:
    return {
        name: yaml.safe_load((ADAPTERS_DIR / f"{name}.yml").read_text(encoding="utf-8"))
        for name in ADAPTER_NAMES
    }


#
# Mock 시나리오 — cycle hpe-ilo7-gen12-match-fix 회귀 검증
#   S1: 갭 재현 (fix 후 iLO7 선택 기대)
#   S2~S5: 기존 adapter 매치 회귀 보존 검증
#
# S4 (CSUS 3200) / S5 (SDFlex) firmware 는 각 adapter origin 주석의 spec
# (RMC 3.x.y / 2.x.y 3-part) 일치 형식. 2-part 형식의 fw drift 발견 시
# 별도 cycle (사이트 실측 — Option A / SDFlex lab cycle) 에서 정정.
SCENARIOS: tuple[tuple[str, dict[str, str], str], ...] = (
    ("S1", {"vendor": "HPE", "model": "ProLiant DL380 Gen12", "firmware": "1.10"}, "hpe_ilo7"),
    ("S2", {"vendor": "HPE", "model": "ProLiant DL380 Gen12", "firmware": "1.16.00"}, "hpe_ilo7"),
    ("S3", {"vendor": "HPE", "model": "ProLiant DL380 Gen11", "firmware": "1.73"}, "hpe_ilo6"),
    ("S4", {"vendor": "HPE", "model": "HPE Compute Scale-up Server 3200", "firmware": "3.10.00"}, "hpe_csus_3200"),
    ("S5", {"vendor": "HPE", "model": "Superdome Flex 280", "firmware": "2.10.00"}, "hpe_superdome_flex"),
)


def main() -> int:
    adapters = load_adapters()
    fail = 0
    header = ["Scen", "Expected", "iLO7", "iLO6", "iLO5", "iLO4", "CSUS", "SDFlex", "Selected", "Result"]
    print("  ".join(f"{h:<18}" for h in header))
    print("-" * 200)
    for sname, facts, expected in SCENARIOS:
        scores = {name: adapter_score(adapters[name], facts) for name in ADAPTER_NAMES}
        selected_name = max(scores, key=lambda k: scores[k])
        result = "[PASS]" if selected_name == expected else "[FAIL]"
        if selected_name != expected:
            fail += 1
        row = [
            sname,
            expected,
            str(scores["hpe_ilo7"]),
            str(scores["hpe_ilo6"]),
            str(scores["hpe_ilo5"]),
            str(scores["hpe_ilo4"]),
            str(scores["hpe_csus_3200"]),
            str(scores["hpe_superdome_flex"]),
            selected_name,
            result,
        ]
        print("  ".join(f"{c:<18}" for c in row))
    print("-" * 200)
    print(f"FAIL: {fail}/{len(SCENARIOS)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
