# M-B2 — Supermicro 6 generation capability 정합 + origin 주석 강화

> status: [PENDING] | depends: M-B1 | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. Supermicro 6 generation 모두 코드 path 깔자." (2026-05-07)

Supermicro adapter 7개 (BMC + X9 + X10 (M-B1 신설) + X11 + X12 + X13 + X14) capability 정합 + origin 주석 강화. priority 일관성 검증 + web sources 출처 명시 (rule 96 R1-A).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/supermicro_bmc.yml`, `supermicro_x9.yml`, `supermicro_x10.yml`, `supermicro_x11.yml`, `supermicro_x12.yml`, `supermicro_x13.yml`, `supermicro_x14.yml` (7개) |
| 영향 vendor | Supermicro (lab 부재 — 사이트 BMC 0대) |
| 함께 바뀔 것 | adapter score 정렬 + EXTERNAL_CONTRACTS.md (M-K2) |
| 리스크 top 3 | (1) 기존 priority 변경 시 score 정렬 결과 변화 (Additive only) / (2) capability 변경 시 collect strategy 영향 / (3) origin 주석 부족 시 rule 96 R1-A 위반 |
| 진행 확인 | M-B1 X10 신설 후 진입 |

---

## 7 generation 매트릭스 (cycle 진입 시점)

| adapter | priority | redfish_version | power_subsystem | storage_strategy | oem_strategy |
|---|---|---|---|---|---|
| supermicro_bmc.yml | 10 (legacy generic) | 1.0+ | false | simple_storage | none |
| supermicro_x9.yml | 70 | 1.0 | false | simple_storage | none |
| supermicro_x10.yml | **75** (M-B1 신설) | 1.0+ | false | simple_storage | none |
| supermicro_x11.yml | 80 | 1.4+ | false | standard | weak |
| supermicro_x12.yml | 90 | 1.6+ | true (PowerSubsystem 도입 — DSP0268 v1.13+) | standard | weak |
| supermicro_x13.yml | 100 | 1.8+ | true | standard | weak |
| supermicro_x14.yml | 110 | 1.10+ | true | standard | weak |

→ Additive only — 본 ticket 은 origin 주석 + capability 정합 (semantic 변경 0).

---

## Web sources (rule 96 R1-A 의무)

각 adapter metadata 절에 다음 source 추가 (또는 갱신):

| generation | URL | 확인일 |
|---|---|---|
| BMC (legacy) | `https://www.supermicro.com/manuals/superserver/IPMI/` | 2026-05-07 |
| X9 (2012-2014) | `https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X9.pdf` | 2026-05-07 |
| X10 (2014-2018) | `https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X10.pdf` | 2026-05-07 |
| X11 (2017-2020) | `https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X11.pdf` | 2026-05-07 |
| X12 (2020-2022) | `https://www.supermicro.com/manuals/superserver/IPMI/X12_BMC_RedfishRefGuide.pdf` | 2026-05-07 |
| X13 (2022-2024) | `https://www.supermicro.com/manuals/superserver/X13/X13_BMC_RedfishRefGuide.pdf` | 2026-05-07 |
| X14 (2024+) | `https://www.supermicro.com/manuals/superserver/X14/X14_BMC_RedfishRefGuide.pdf` | 확인 필요 |

→ X12 부터 PowerSubsystem 도입 (DSP0268 v1.13+) — 본 cycle 의 M-I2 power section 변형 매트릭스 입력.

---

## 구현 절차

### 각 adapter metadata 갱신 (7개 동일 패턴)

각 adapter 의 `metadata` 절에 다음 4 키 추가/갱신 (rule 96 R1 origin 주석):

```yaml
metadata:
  vendor: supermicro
  generation: <bmc | x9 | x10 | x11 | x12 | x13 | x14>
  generation_year: "<예: 2014-2018>"
  redfish_introduction: "<예: DSP0268 v1.6+>"
  origin: "<위 표 URL>"
  lab_status: "부재 — 사용자 명시 2026-05-07 Q2 (Supermicro 사이트 BMC 0대)"
  next_action: "lab 도입 후 별도 cycle — capability 보정 (rule 50 R2 단계 10)"
  power_subsystem_introduction: "<X12+ true / X11- false>"  # M-I2 입력
  storage_strategy_evolution: "<X10- simple_storage / X11+ standard>"  # M-I1 입력
  tested_against: ["<펌웨어 버전 list>"]  # web sources 기반
```

### capability 정합 검증

기존 capabilities 절이 위 매트릭스와 일치하는지 검증:

- BMC / X9 / X10: `power_subsystem: false`, `storage_strategy: simple_storage`
- X11: `power_subsystem: false`, `storage_strategy: standard`
- X12 / X13 / X14: `power_subsystem: true`, `storage_strategy: standard`

불일치 시 capability 갱신 (Additive only — 기존 collect strategy 변경 0).

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `verify_harness_consistency.py` 통과
- [ ] `verify_vendor_boundary.py` 통과
- [ ] 각 adapter `metadata.origin` 존재 (rule 96 R1 의무) — 7개 모두

### 의미 검증

- [ ] priority 일관성: 10 < 70 < 75 < 80 < 90 < 100 < 110 (역전 없음 — rule 12 R2)
- [ ] capability 매트릭스 위 표와 일치
- [ ] origin URL 모두 vendor 공식 docs 또는 DMTF spec

### Additive only

- [ ] adapter 점수 매칭 결과 사이트 검증 4 vendor 영향 0
- [ ] capability 의 collect strategy 변경 0 (semantic 보존)

---

## risk

- (LOW) X14 (2024+) 펌웨어 정보 web sources 가용성 약함 — 확인 필요. 누락 시 X13 와 동일 패턴 가정 + lab 도입 후 보정
- (LOW) X11 BMC 일부 펌웨어 (BMC 1.x) 는 standard storage path 미지원 — model_patterns 별도 분기 가능. 사이트 도입 시 보정

## 완료 조건

- [ ] 7 adapter 모두 metadata 갱신 (origin / lab_status / next_action / power_subsystem_introduction / storage_strategy_evolution / tested_against)
- [ ] priority 일관성 검증
- [ ] verify_harness_consistency.py + verify_vendor_boundary.py 통과
- [ ] commit: `feat: [M-B2 DONE] Supermicro 7 generation capability 정합 + origin 주석 강화 (rule 96 R1-A)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 → M-B3 (AMD/ARM 변형).

## 관련

- M-B1 (X10 신설)
- rule 12 R2 (priority 일관성)
- rule 96 R1+R1-A (origin 주석 / web sources)
- M-I1 / M-I2 (storage / power 변형 — 본 ticket 매트릭스 입력)
