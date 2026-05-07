# M-E1 — Fujitsu iRMC adapter S2/S4/S5/S6 generation 분기

> status: [PENDING] | depends: M-A3 | priority: P1 | worker: W3 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Fujitsu iRMC S2/S4/S5/S6 모든 generation 코드 path." (cycle 진입)

현재 `fujitsu_irmc.yml` (priority=70) 단일 adapter — generation 분기 없음. firmware_patterns 분기 보강.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/fujitsu_irmc.yml` (capability + firmware_patterns 보강) |
| 영향 vendor | Fujitsu iRMC (lab 부재) |
| 함께 바뀔 것 | M-E2 OEM tasks, M-E3 mock |
| 리스크 top 3 | (1) iRMC S2 (2010 시기) Redfish 미지원 가능 / (2) PRIMERGY vs PRIMEQUEST 차이 / (3) iRMC S6 최신 펌웨어 web sources 약함 |
| 진행 확인 | M-A3 vault 후 진입 |

---

## Web sources (rule 96 R1-A)

| source | 항목 | URL |
|---|---|---|
| Fujitsu 공식 | iRMC S2/S4/S5/S6 User Guide | `https://support.ts.fujitsu.com/IndexDownload.asp` |
| Fujitsu 공식 | PRIMERGY Server Redfish Guide | `https://www.fujitsu.com/global/products/computing/servers/primergy/` |
| Fujitsu 공식 | PRIMEQUEST 매뉴얼 (mission-critical) | `https://www.fujitsu.com/global/products/computing/servers/primequest/` |
| DMTF Redfish | DSP0268 v1.0 ~ v1.13 | iRMC S* generation 매핑 |

→ Fujitsu iRMC generation 매트릭스:
- **iRMC S2** (2010-2014): IPMI 우선 / Redfish 미지원 또는 v1.0 부분
- **iRMC S4** (2014-2019): DSP0268 v1.0+, 표준 가까움
- **iRMC S5** (2019-2022): DSP0268 v1.6+, OEM 강화
- **iRMC S6** (2022+): DSP0268 v1.10+, PowerSubsystem 일부

---

## 구현 (adapters/redfish/fujitsu_irmc.yml 갱신)

```yaml
---
# adapters/redfish/fujitsu_irmc.yml
# Fujitsu iRMC S2/S4/S5/S6 generation adapter
#
# source: https://support.ts.fujitsu.com/IndexDownload.asp (확인 2026-05-07)
# source: https://www.fujitsu.com/global/products/computing/servers/primergy/
# source: https://www.fujitsu.com/global/products/computing/servers/primequest/
# source: https://redfish.dmtf.org/schemas/v1/ (DSP0268 v1.0 ~ v1.13)
# lab: 부재 (사용자 명시 2026-05-01)
# tested_against: ["iRMC S4", "iRMC S5", "iRMC S6"] (web sources 기반 — S2 는 Redfish 미지원 가능성)

priority: 70
specificity: 50

match:
  manufacturer: ["Fujitsu", "FUJITSU", "Fujitsu Limited", "Fujitsu Technology Solutions"]
  model_patterns:
    # PRIMERGY (rack)
    - "*PRIMERGY*"
    - "*RX*"          # RX1330 / RX2540 등 (rack)
    - "*TX*"          # TX1330 등 (tower)
    # PRIMEQUEST (mission-critical)
    - "*PRIMEQUEST*"
    - "*PQ*"
    # CELSIUS (workstation — 제외)
  firmware_patterns:
    - "iRMC*S2*"      # iRMC S2 (legacy)
    - "iRMC*S4*"      # iRMC S4
    - "iRMC*S5*"      # iRMC S5
    - "iRMC*S6*"      # iRMC S6 (최신)

capabilities:
  redfish_version: "1.0+"            # iRMC S4 의 최소 버전
  power_subsystem: "conditional"      # iRMC S6+ 일부 지원 / 이전 false
  storage_strategy: "standard_with_simple_fallback"  # iRMC S2 시 SimpleStorage
  oem_strategy: "standard+oem"
  oem_namespace: "Oem.ts_fujitsu"     # Fujitsu OEM namespace 변형 — Oem.ts_fujitsu 또는 Oem.Fujitsu

collect:
  strategy: standard+oem
  systems_path: "/redfish/v1/Systems"
  chassis_path: "/redfish/v1/Chassis"
  managers_path: "/redfish/v1/Managers"
  oem_tasks: "redfish-gather/tasks/vendors/fujitsu/collect_oem.yml"   # M-E2 신설 dep
  storage_strategy: "standard_with_simple_fallback"
  power_strategy: "subsystem_with_legacy_fallback"

normalize:
  bmc_name: "iRMC"
  vendor_namespace: "Oem.ts_fujitsu"
  oem_normalize: "redfish-gather/tasks/vendors/fujitsu/normalize_oem.yml"

metadata:
  vendor: fujitsu
  generation: irmc
  generation_year: "2010-2024+"
  redfish_introduction: "DSP0268 v1.0+ (S4)"
  origin: "https://support.ts.fujitsu.com/IndexDownload.asp"
  lab_status: "부재 — 사용자 명시 2026-05-01"
  next_action: "lab 도입 후 별도 cycle — generation 별 capability 보정"
  generation_matrix:
    "S2": "IPMI 우선 / Redfish 미지원 또는 v1.0 부분 (2010-2014)"
    "S4": "DSP0268 v1.0+ / 표준 / OEM Oem.ts_fujitsu (2014-2019)"
    "S5": "DSP0268 v1.6+ / OEM 강화 (2019-2022)"
    "S6": "DSP0268 v1.10+ / PowerSubsystem 일부 (2022+)"
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `verify_harness_consistency.py` 통과
- [ ] adapter `metadata.origin` + 4 source URL 명시

### adapter score 매칭

```bash
python scripts/ai/score-adapter-match.py --vendor fujitsu --model "PRIMERGY RX2540 M5"
# 예상: fujitsu_irmc.yml (priority=70) 선택

python scripts/ai/score-adapter-match.py --vendor fujitsu --model "PRIMEQUEST 3800B"
# 예상: fujitsu_irmc.yml 선택 (PRIMEQUEST model_patterns 추가)
```

### Additive only

- [ ] 기존 priority=70 변경 0
- [ ] capabilities 내 storage / power 가 "conditional" / fallback 명시 — generation 별 분기

---

## risk

- (MED) iRMC S2 는 Redfish 미지원 펌웨어 다수 — 사이트 도입 시 IPMI fallback 또는 graceful degradation
- (MED) Oem.ts_fujitsu vs Oem.Fujitsu namespace 변형 — 펌웨어 별 차이. M-E2 OEM tasks 에서 두 fallback 처리

## 완료 조건

- [ ] fujitsu_irmc.yml 갱신 (firmware_patterns 4 generation + capabilities + metadata + PRIMEQUEST 추가)
- [ ] M-E2 OEM tasks dep 명시
- [ ] commit: `feat: [M-E1 DONE] Fujitsu iRMC S2/S4/S5/S6 generation 분기 + PRIMEQUEST model_patterns`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W3 → M-E2 (Fujitsu OEM tasks).

## 관련

- M-A3 (Fujitsu vault — dep)
- M-E2, M-E3 (Fujitsu 영역)
- rule 12 R2 / rule 96 R1-A
