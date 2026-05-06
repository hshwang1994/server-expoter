# M-E2 — HPE Superdome adapter 작성

> status: [PENDING] | depends: M-E1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-E1 web 검색 결과 → adapter YAML 작성 (priority=80, lab 부재 — F44~F47 패턴 동일).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/hpe_superdome*.yml` (신규) 또는 `adapters/redfish/superdome*.yml` (M-E1 결정에 따라), `redfish-gather/library/redfish_gather.py` (`_FALLBACK_VENDOR_MAP` / `_BMC_PRODUCT_HINTS` / `bmc_names`) |
| 영향 vendor | HPE (sub-line 결정 시) 또는 신 vendor "superdome" (별도 결정 시) |
| 함께 바뀔 것 | M-E3 ai-context / M-E4 boundary-map / M-E5 docs / M-E6 회귀 |
| 리스크 top 3 | (1) priority 결정 — HPE sub-line 시 generic hpe_*.yml 보다 높이 / (2) 기존 hpe adapter 와 충돌 / (3) lab 부재 → 정적 검증만 |
| 진행 확인 | M-E1 [DONE] 후 진입. M-E1 결정 (a)/(b) 따라 adapter 위치 |

## 작업 spec

### (A) adapter 구조 (M-E1 결정 (a) HPE sub-line 시)

**파일**: `adapters/redfish/hpe_superdome.yml` (priority=85)
**파일**: `adapters/redfish/hpe_superdome_flex_280.yml` (priority=90, 최신 모델)

```yaml
# adapters/redfish/hpe_superdome.yml
# source: M-E1 web 검색 결과 (HPE Superdome Flex / Flex 280 docs)
# tested_against: ["iLO 5 2.x", "iLO 5 3.x", "RMC 2.x"]
# lab: 부재 — web sources only (rule 96 R1-A)
# 마지막 동기화 확인: 2026-05-06

priority: 85
specificity: 5
adapter_id: hpe_superdome
match:
  manufacturer: ["HPE", "Hewlett Packard Enterprise"]
  model_patterns:
    - "Superdome Flex*"
    - "Superdome Flex 280*"
  # 일반 ProLiant 보다 model_patterns 우선
capabilities:
  endpoints:
    service_root: "/redfish/v1/"
    systems: "/redfish/v1/Systems"
    chassis: "/redfish/v1/Chassis"
    managers: "/redfish/v1/Managers"  # iLO 5 + RMC 두 entry 가능
    update_service: "/redfish/v1/UpdateService"
  oem_path: "Oem.Hpe"
  bmc_name: "iLO 5 + RMC"
  multi_partition: true  # nPAR 지원
collect:
  strategy: standard+oem
  oem_tasks: redfish-gather/tasks/vendors/hpe/collect_oem.yml  # 기존 HPE OEM 재활용
  fallback:
    power: "Chassis/{id}/PowerSubsystem → fallback Chassis/{id}/Power"
    network: "NetworkAdapters/{id}/Ports → fallback NetworkPorts (deprecated since iLO 6)"
normalize:
  vendor: "hpe"
  bmc_label: "iLO 5"  # primary BMC. RMC 는 보조
  multi_manager_handling: "primary_ilo + auxiliary_rmc"
credentials:
  profile: hpe
  fallback_profiles: []
metadata:
  generation: "Superdome Flex / Flex 280"
  release_year: "2017+"
  notes: |
    - 일반 ProLiant 와 model_patterns 차이 — Superdome 모델은 본 adapter 우선
    - nPAR 정보는 향후 partitioning section 진입 시 처리 (현 cycle 외)
    - RMC 는 보조 manager — iLO 5 가 primary
```

### (B) Legacy Superdome (2 / X / Integrity) 처리

**파일**: `adapters/redfish/hpe_superdome_legacy.yml` (priority=70 — fallback 용)

```yaml
priority: 70
specificity: 3
adapter_id: hpe_superdome_legacy
match:
  manufacturer: ["HPE", "Hewlett-Packard"]
  model_patterns:
    - "Superdome 2*"
    - "Superdome X*"
    - "Integrity Superdome*"
capabilities:
  endpoints:
    service_root: "/redfish/v1/"
  notes: "Itanium / Onboard Administrator — Redfish 부분 지원 또는 미지원. graceful_degradation"
collect:
  strategy: graceful_degradation
  on_protocol_fail: "status=failed, errors=['Superdome legacy OA — Redfish 부분 지원']"
metadata:
  notes: "lab 부재. Superdome 2/X/Integrity 는 legacy. 운영 도입 시 재검증."
```

### (C) `_FALLBACK_VENDOR_MAP` 갱신 (M-E1 결정 (a) 시 변경 없음 — HPE 그대로)

만약 (b) 별도 vendor 결정 시:

```python
# redfish_gather.py:338
_FALLBACK_VENDOR_MAP = {
    # ...
    "hpe": ["HPE", "Hewlett Packard Enterprise", "Hewlett-Packard", "HP"],
    "superdome": ["HPE Superdome", "HPE Integrity"],  # 별도 분류 시
    # ...
}
```

### (D) `_BMC_PRODUCT_HINTS` 갱신

```python
# redfish_gather.py 의 _detect_from_product
# 일반 ProLiant 의 "ilo" 외에 Superdome 명시 추가
```

### (E) `bmc_names` 갱신

```python
bmc_names = {
    'dell': 'iDRAC',
    'hpe': 'iLO',  # ProLiant
    'hpe_superdome': 'iLO 5 + RMC',  # Superdome
    # ...
}
```

→ rule 12 R1 Allowed 영역.

## 회귀 / 검증

- pytest 회귀 (M-E6 에서 추가)
- 정적 검증:
  - `python scripts/ai/verify_vendor_boundary.py` (rule 12)
  - `python scripts/ai/hooks/adapter_origin_check.py` (rule 96 R1)
  - yamllint adapter YAML
  - score-adapter-match skill: Superdome Flex 280 → hpe_superdome_flex_280 (priority=90) 우선 선택 검증

## risk

- (HIGH) priority 충돌 — 기존 hpe_proliant_gen11 등과 모델 패턴 검증 필요
- (MED) lab 부재 → 정적 분석만. 실 BMC 응답 차이 가능
- (LOW) Additive only — 기존 5 hpe_*.yml adapter 동작 변경 0

## 완료 조건

- [ ] M-E1 결정 (a)/(b) 따라 adapter 위치
- [ ] adapter YAML 2~3개 생성 (Flex / Flex 280 / Legacy) — origin 주석 포함
- [ ] `_FALLBACK_VENDOR_MAP` / `_BMC_PRODUCT_HINTS` / `bmc_names` 갱신 (필요 시)
- [ ] verify_vendor_boundary / adapter_origin_check PASS
- [ ] score-adapter-match 검증 (mock manufacturer/model 으로)
- [ ] commit: `feat: [M-E2 DONE] HPE Superdome adapter 추가 (lab 부재, web sources)`

## 다음 세션 첫 지시 템플릿

```
M-E2 Superdome adapter 작성 진입.

읽기 우선순위:
1. fixes/M-E2.md
2. M-E1 결과 (모델 매트릭스 / endpoint / OEM / 결정 (a)/(b))
3. adapters/redfish/hpe_*.yml (5 기존 generation 패턴)
4. adapters/redfish/huawei_ibmc.yml (cycle-019 phase 2 신규 패턴 — lab 부재 priority=80)
5. redfish-gather/library/redfish_gather.py:338 (_FALLBACK_VENDOR_MAP)

작업:
1. M-E1 결정 따라 adapter 위치 결정
2. hpe_superdome*.yml (또는 superdome*.yml) 2~3개 생성
3. _FALLBACK_VENDOR_MAP / bmc_names 갱신 (필요 시)
4. 정적 검증 PASS

선행: M-E1 [DONE]
후속: M-E3 (ai-context) + M-E4 (boundary-map) + M-E5 (docs) + M-E6 (회귀)
```

## 관련

- rule 50 R2 (vendor 추가 9단계 — 본 ticket 은 단계 2)
- rule 12 R1 Allowed 영역
- rule 96 R1+R1-A
- skill: add-new-vendor, score-adapter-match
- 패턴 reference: cycle-019 phase 2 신규 vendor 4 (commit 7c67942e)
