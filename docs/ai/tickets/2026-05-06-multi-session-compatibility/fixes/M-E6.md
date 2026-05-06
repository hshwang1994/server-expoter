# M-E6 — Superdome pytest 회귀 mock

> status: [PENDING] | depends: M-E5 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-E2~M-E5 적용 후 회귀 검증. lab 부재 → mock fixture + score-adapter-match 검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/hpe_superdome_*.json` (신규), `tests/redfish-probe/test_superdome_compat.py` (신규) |
| 영향 vendor | HPE Superdome 3 모델 |
| 리스크 | LOW (회귀만) |

## 작업 spec

### (A) Mock fixture

```
tests/fixtures/redfish/hpe_superdome/flex_280_service_root.json
tests/fixtures/redfish/hpe_superdome/flex_280_systems.json
tests/fixtures/redfish/hpe_superdome/flex_280_chassis.json
tests/fixtures/redfish/hpe_superdome/flex_280_managers_ilo5.json
tests/fixtures/redfish/hpe_superdome/flex_280_managers_rmc.json
tests/fixtures/redfish/hpe_superdome/legacy_oa_partial.json  # graceful_degradation 케이스
```

각 fixture 헤더 origin 주석 (rule 96 R1):

```json
{
  "_meta": {
    "source": "M-E1 web 검색 — HPE Superdome Flex docs (https://support.hpe.com/.../)",
    "verified": "2026-05-06 (lab 부재 — web only)",
    "applies_to": "Superdome Flex 280 with iLO 5 firmware 3.x"
  },
  "@odata.id": "/redfish/v1/",
  ...
}
```

### (B) score-adapter-match 회귀

```python
# tests/redfish-probe/test_superdome_compat.py

import pytest
from adapter_loader import select_adapter

@pytest.mark.parametrize("manufacturer,model,expected_adapter", [
    ("HPE", "Superdome Flex 280", "hpe_superdome_flex_280.yml"),
    ("HPE", "Superdome Flex", "hpe_superdome.yml"),
    ("HPE", "ProLiant DL380 Gen11", "hpe_proliant_gen11.yml"),  # 충돌 검증 — Superdome 패턴 안 매칭
    ("HPE", "Superdome 2", "hpe_superdome_legacy.yml"),
    ("HPE", "Integrity Superdome", "hpe_superdome_legacy.yml"),
])
def test_superdome_adapter_selection(manufacturer, model, expected_adapter):
    """Superdome 모델별 정확한 adapter 선택"""
    adapter = select_adapter(manufacturer=manufacturer, model=model)
    assert adapter.adapter_id in expected_adapter
```

### (C) 기존 hpe ProLiant 회귀 (Additive only 검증)

기존 hpe_proliant_gen10 / gen11 / gen12 모델은 Superdome adapter 매칭 안 됨 (model_patterns 차이).

```python
def test_hpe_proliant_unaffected():
    """기존 ProLiant 모델은 Superdome adapter 매칭 안 됨 (Additive only)"""
    for model in ["ProLiant DL380 Gen10", "ProLiant DL380 Gen11", "ProLiant DL380 Gen12"]:
        adapter = select_adapter(manufacturer="HPE", model=model)
        assert "superdome" not in adapter.adapter_id
```

## 회귀 / 검증

- pytest 108 + N건 (예상 +5~7)
- 모든 baseline 회귀 PASS (Additive only 검증)
- `python scripts/ai/verify_vendor_boundary.py`
- `python scripts/ai/hooks/adapter_origin_check.py`

## risk

- (MED) priority 충돌 — score-adapter-match 검증 누락 시 잘못된 adapter 선택
- (LOW) mock fixture 가 web 검색 결과만 → 실 Superdome 응답과 차이 가능 (lab 도입 시 갱신)

## 완료 조건

- [ ] mock fixture 6 종 (Flex 280 / Flex / Legacy 각각 + ProLiant 영향 X 검증용)
- [ ] pytest 회귀 5+건 (parametrize)
- [ ] pytest 전체 PASS
- [ ] baseline 8건 회귀 PASS
- [ ] commit: `test: [M-E6 DONE] Superdome 회귀 N건 + ProLiant Additive only 검증`

## 다음 세션 첫 지시 템플릿

```
M-E6 Superdome 회귀 진입.

선행: M-E5 [DONE] (M-E2/E3/E4 모두 [DONE])
작업:
1. mock fixture 6 종 (origin 주석 포함)
2. pytest 회귀 5+건 (Superdome 매칭 + ProLiant Additive only)
3. pytest 전체 + baseline PASS
```

## 관련

- rule 21 R2 (Fixture 출처 기록)
- rule 50 R2 단계 9 (사용자 결정 → decision-log)
- skill: score-adapter-match
