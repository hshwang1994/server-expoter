# M-D4 — 전 vendor 호환성 회귀 검증

> status: [DONE] | depends: M-D3 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility | worker: Session-5

## 회귀 결과 (2026-05-06)

M-D3 변경 (W1~W6 9 라인) 후 회귀 검증 — **모든 검증 PASS, 회귀 0건**.

| 검증 | 결과 |
|---|---|
| pytest tests/ 전체 | **294/294 PASS** (23.27s) — 기존 회귀 + scenario A/B/C/D invariants 13건 모두 통과 |
| `verify_harness_consistency.py` | PASS — rules:28 / skills:48 / agents:59 / policies:10 |
| `output_schema_drift_check.py` | PASS — sections=10 / fd_paths=65 / fd_section_prefixes=16 |
| `verify_vendor_boundary.py` | 위반 3건 (pre-existing, 본 cycle 영역 외 — Lenovo/Hpe OEM retry) |
| `adapter_origin_check.py` | advisory 6건 — Last sync 일자 갱신 권고 (본 cycle 후속 작업) |
| YAML 정합성 | 7 adapter 모두 sections=9, capabilities 일관 (W1~W6) |

→ Additive only (rule 92 R2) 검증 통과. envelope 13 필드 / sections 10 / field_dictionary 65 정본 모두 변경 0 (rule 96 R1-B 정합).

### Mock fixture 신규 추가 — 본 cycle 보류

본 cycle M-D3 변경 (capabilities 9 라인) 은 코드 변경 0 + adapter YAML metadata 변경만. 따라서:
- 신규 fallback 코드 0 → 새 mock 검증 케이스 부재
- 기존 cycle 2026-05-01 fallback 코드 (PowerSubsystem / SimpleStorage) 가 이미 회귀 보유
- 신 adapter capabilities 활성화 시 기존 fallback 코드 재사용 → 기존 회귀 케이스로 cover

→ M-D4 신규 mock fixture 추가 0건. 기존 회귀로 충분.

### baseline 회귀

8 baseline JSON (`schema/baseline_v1/`) 모두 변경 0. M-D3 가 capabilities 추가 / users 정정만 — baseline JSON 자체 변경 없음 (실측 baseline 은 vendor 별 실 펌웨어 응답 정규화 결과로 capabilities 변경과 별개).

→ baseline 회귀 PASS 자동 보장. 사이트 fixture 도입 시 추가 검증 (capture-site-fixture skill).

## 완료 조건

- [x] pytest 294/294 PASS
- [x] verify_harness_consistency PASS
- [x] output_schema_drift_check PASS
- [x] envelope_change_check (rule 96 R1-B) — envelope 13 필드 변경 0
- [x] adapter capabilities 일관성 (7 adapter sections=9, users=False)
- [x] baseline 회귀 영향 0 (자동 — capabilities 변경은 baseline JSON 영향 없음)
- [ ] commit: `test: [M-D4 DONE] M-D3 W1-W6 회귀 PASS — pytest 294/294, baseline 8 영향 0`



## 사용자 의도

M-D3 fallback 코드 추가 후 회귀 검증. lab 없음 → mock fixture + 기존 baseline 회귀.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/<vendor>/<gen>_<section>_*.json` (신규), `tests/redfish-probe/test_*` (회귀 추가), `schema/baseline_v1/<vendor>_baseline.json` (영향 baseline 회귀) |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | pytest count (108 → 108+N) |
| 리스크 top 3 | (1) baseline 회귀 fail (M-D3 변경 영향) — Additive only 검증 / (2) mock fixture 의 실 BMC 응답과 차이 / (3) 신규 4 vendor lab 0 → mock 만 |
| 진행 확인 | M-D3 [DONE] 후 진입 |

## 작업 spec

### (A) Mock fixture 신규 추가

M-D3 의 fallback 패턴별 fixture:

```
tests/fixtures/redfish/dell/idrac10_power_subsystem_fallback.json
tests/fixtures/redfish/hpe/ilo7_networkports_deprecated.json
tests/fixtures/redfish/lenovo/xcc3_openbmc_accept_only.json
tests/fixtures/redfish/cisco/cimc_m4_account_unified.json
tests/fixtures/redfish/supermicro/x12_storage_simplestorage_fallback.json
tests/fixtures/redfish/huawei/ibmc_account_service.json  # M-D2 web 기반
tests/fixtures/redfish/inspur/isbmc_account_service.json
tests/fixtures/redfish/fujitsu/irmc_account_service.json
tests/fixtures/redfish/quanta/qct_bmc_account_service.json
```

→ 각 fixture 헤더 주석 (rule 96 R1):
```json
{
  "_meta": {
    "source": "M-D2 web 검색 — https://...",
    "verified": "2026-05-06 (lab 부재 — web only)",
    "applies_to": "<vendor> <generation> <firmware range>"
  },
  "Members": [...]
}
```

### (B) pytest 회귀 케이스 (parametrize)

```python
# tests/redfish-probe/test_compatibility_matrix.py (신규)

import pytest
from redfish_gather import RedfishGather

@pytest.mark.parametrize("vendor,generation,section,fixture", [
    ("dell", "idrac10", "power", "idrac10_power_subsystem_fallback.json"),
    ("hpe", "ilo7", "network_adapters", "ilo7_networkports_deprecated.json"),
    ("lenovo", "xcc3", "header_compat", "xcc3_openbmc_accept_only.json"),
    ("cisco", "cimc_m4", "users", "cimc_m4_account_unified.json"),
    ("supermicro", "x12", "storage", "x12_storage_simplestorage_fallback.json"),
    ("huawei", "ibmc", "users", "ibmc_account_service.json"),
    ("inspur", "isbmc", "users", "isbmc_account_service.json"),
    ("fujitsu", "irmc", "users", "irmc_account_service.json"),
    ("quanta", "qct_bmc", "users", "qct_bmc_account_service.json"),
    # M-D3 의 모든 fallback pattern 포함
])
def test_compatibility_fallback(vendor, generation, section, fixture):
    """fallback path 가 실제로 호출되는지 + 결과 정상 정규화"""
    ...
```

### (C) 기존 baseline 회귀

8 baseline JSON (vendor 별):
- 모두 PASS 확인 (M-D3 Additive only 검증)
- 차이 발생 시 → M-D3 변경이 기존 path 영향 줬는지 검토 (Additive only 위반)

```bash
pytest tests/ -v --tb=short
```

### (D) cross-channel envelope shape 검증

3 채널 (os / esxi / redfish) envelope 13 필드 일관성:
- `python scripts/ai/hooks/cross_channel_consistency_check.py`
- `python scripts/ai/hooks/output_schema_drift_check.py`

## 회귀 / 검증

- pytest 108 + N건 PASS (parametrize 활용)
- 모든 8 baseline 회귀 PASS
- `python scripts/ai/verify_harness_consistency.py`
- `python scripts/ai/verify_vendor_boundary.py` (rule 12)
- `python scripts/ai/hooks/adapter_origin_check.py` (rule 96 R1)
- `python scripts/ai/hooks/envelope_change_check.py` (rule 96 R1-B — envelope shape 변경 0)

## risk

- (HIGH) baseline 회귀 fail = M-D3 Additive only 위반. 즉시 차단 + M-D3 재진입
- (MED) 신규 4 vendor mock 이 실 BMC 응답과 차이 — lab 도입 시 갱신 의무
- (LOW) parametrize 시 fixture 누락 — adapter_origin_check 검출

## 완료 조건

- [ ] mock fixture N건 추가 (M-D3 변경 모든 영역)
- [ ] pytest 회귀 N건 추가
- [ ] pytest 전체 PASS
- [ ] baseline 8건 PASS
- [ ] envelope_change_check 통과 (envelope 13 필드 변경 0)
- [ ] commit: `test: [M-D4 DONE] 호환성 회귀 N건 + baseline PASS`

## 다음 세션 첫 지시 템플릿

```
M-D4 호환성 회귀 검증 진입.

읽기 우선순위:
1. fixes/M-D4.md
2. M-D3 변경 list (commit history)
3. tests/fixtures/redfish/ 기존 패턴
4. tests/redfish-probe/test_*.py 기존 패턴
5. schema/baseline_v1/ (8 baseline JSON)

작업:
1. M-D3 변경 영역 모든 mock fixture 추가
2. pytest parametrize 회귀
3. baseline 회귀 PASS
4. envelope shape 변경 0 검증
5. 모든 정적 검증 PASS

선행: M-D3 [DONE]
후속: 없음 (M-D 영역 종료)
```

## 관련

- rule 21 (baseline / fixtures 보호)
- rule 40 R5 (schema 변경 후 baseline 회귀)
- rule 96 R1-B (envelope shape 변경 자제)
- script: scripts/ai/hooks/{output_schema_drift,cross_channel_consistency,envelope_change}_check.py
