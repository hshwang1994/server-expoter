# M-H4 — Cisco 미검증 generation (BMC / CIMC C-series 1.x ~ 4.x / S-series / B-series) 보강

> status: [PENDING] | depends: — | priority: P1 | worker: W4 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "사이트 검증 안 된 Cisco generation 도 코드 path 깔자."

Cisco 사이트 검증: UCS X-series 만. BMC / CIMC C-series 1.x~4.x / S-series / B-series 미검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/cisco_bmc.yml`, `cisco_cimc.yml` (origin + capability), `tests/fixtures/redfish/cisco_*/` (mock) |
| 영향 vendor | Cisco (lab 부재 — UCS X-series 외) |
| 함께 바뀔 것 | M-I1 / M-I2 / M-J1 (Cisco vendor task 신설) |
| 리스크 top 3 | (1) Cisco UCS B-series (chassis-based) vs C-series (rack) 응답 차이 / (2) S-series storage server 분기 / (3) Cisco vendor task 부재 (M-J1 신설) |
| 진행 확인 | Cisco vault 이미 존재 — cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| generation | URL | 매트릭스 |
|---|---|---|
| Cisco BMC (legacy) | Cisco UCS C-series Standalone archive | Redfish 미지원 또는 v1.0 부분 |
| CIMC C-series 1.x | `https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/cli/config/guide/1-x/` | DSP0268 v1.0 부분 |
| CIMC C-series 2.x | (Cisco docs) | DSP0268 v1.4+ |
| CIMC C-series 3.x | (Cisco docs) | DSP0268 v1.6+ |
| CIMC C-series 4.x | (Cisco docs) | DSP0268 v1.10+ |
| UCS S-series (storage) | (Cisco docs) | CIMC 와 유사 + Storage 강화 |
| UCS B-series (blade) | UCS Manager 통합 — chassis-based | 단독 BMC 가 아닌 UCS Manager 매개 — 별도 분기 |
| UCS X-series | (사이트 검증 — out of scope) | DSP0268 v1.13+ |

---

## 구현

### 1. cisco_bmc.yml (legacy) origin

```yaml
metadata:
  vendor: cisco
  generation: bmc_legacy
  generation_year: "2009-2014"
  redfish_introduction: "미지원 또는 v1.0 부분"
  origin: "Cisco UCS C-series Standalone archive"
  lab_status: "부재"
  protocol_support: "IPMI / xml-api 우선 — Redfish 부분"
```

### 2. cisco_cimc.yml capability + firmware_patterns 분기

```yaml
priority: 80
specificity: 50

match:
  manufacturer: ["Cisco Systems Inc", "Cisco Systems Inc.", "Cisco Systems, Inc.", "Cisco Systems", "Cisco"]
  model_patterns:
    - "UCS*C*"          # C-series rack
    - "UCS*S*"          # S-series storage
    - "UCS*B*"          # B-series blade (UCS Manager 매개 — 별도 검토)
  firmware_patterns:
    - "CIMC*1.*"
    - "CIMC*2.*"
    - "CIMC*3.*"
    - "CIMC*4.*"

capabilities:
  redfish_version: "1.0+"            # 1.x 의 최소
  power_subsystem: "conditional"      # 4.x+ 일부 지원
  storage_strategy: "conditional"     # 1.x: simple / 2.x+: standard
  oem_strategy: "standard+oem"
  oem_namespace: "Oem.Cisco"

collect:
  strategy: standard+oem
  oem_tasks: "redfish-gather/tasks/vendors/cisco/collect_oem.yml"   # M-J1 신설 dep
  storage_strategy: "standard_with_simple_fallback"
  power_strategy: "subsystem_with_legacy_fallback"

normalize:
  bmc_name: "CIMC"
  vendor_namespace: "Oem.Cisco"
  oem_normalize: "redfish-gather/tasks/vendors/cisco/normalize_oem.yml"

metadata:
  vendor: cisco
  generation: cimc
  generation_year: "2009-2024"
  redfish_introduction: "DSP0268 v1.0+ ~ v1.10+"
  origin: "https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/"
  lab_status: "부재 — UCS X-series 사이트 검증"
  generation_matrix:
    "1.x": "DSP0268 v1.0 부분 / SimpleStorage / Power legacy (2009-2013)"
    "2.x": "DSP0268 v1.4+ / standard storage (2013-2017)"
    "3.x": "DSP0268 v1.6+ (2017-2020)"
    "4.x": "DSP0268 v1.10+ / PowerSubsystem 일부 (2020-2024)"
```

### 3. mock fixture (4+1 디렉터리)

```
tests/fixtures/redfish/cisco_bmc/         # legacy
tests/fixtures/redfish/cisco_cimc_v2/     # CIMC 2.x (대표)
tests/fixtures/redfish/cisco_cimc_v3/     # CIMC 3.x
tests/fixtures/redfish/cisco_cimc_v4/     # CIMC 4.x (PowerSubsystem 일부)
tests/fixtures/redfish/cisco_ucs_sseries/ # S-series storage (선택)
```

UCS B-series 는 UCS Manager 매개 — 본 cycle 범위 밖. 별도 cycle 검토.

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check` 통과
- [ ] `verify_harness_consistency.py` 통과

### Additive only

- [ ] cisco_ucs_xseries.yml 변경 0
- [ ] tests/fixtures/redfish/cisco_ucs_xseries/ 변경 0

### 동적 검증

- [ ] CIMC mock 별로 firmware_patterns 매칭 + capability 분기 동작
- [ ] Oem.Cisco fragment 추출 (M-J1 Cisco vendor task 신설 후 통합 검증)

---

## risk

- (MED) UCS B-series chassis-based — 본 ticket 에서는 model_patterns 만 추가. 실 BMC 응답 처리는 별도 cycle (UCS Manager 통합)
- (MED) Cisco vendor task 부재 — M-J1 의 dep. M-H4 + M-J1 동시 진행 또는 M-H4 capability collect 의 oem_tasks 경로만 명시

## 완료 조건

- [ ] cisco_bmc / cisco_cimc metadata + capability 보강
- [ ] cisco_cimc.yml firmware_patterns 분기 (1.x ~ 4.x)
- [ ] mock fixture 4 디렉터리 (priority: cimc_v3 > cimc_v2 > cimc_v4 > bmc legacy)
- [ ] UCS X-series 영향 0 검증
- [ ] commit: `feat: [M-H4 DONE] Cisco 미검증 generation (BMC/CIMC 1.x~4.x/S-series) capability + origin + mock`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W4 → M-I1 (storage section 변형 매트릭스).

## 관련

- M-J1 (Cisco vendor task 신설 — dep)
- M-I1 / M-I2 (storage / power 매트릭스)
- rule 92 R2 / rule 96 R1-A
