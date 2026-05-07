# M-H2 — HPE 미검증 generation (iLO legacy / iLO4 / iLO5 / iLO6) 보강

> status: [PENDING] | depends: — | priority: P1 | worker: W4 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "사이트 검증 안 된 HPE iLO generation 도 코드 path 깔자."

HPE 사이트 검증: iLO7 만. iLO (legacy) / iLO4 / iLO5 / iLO6 미검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/hpe_ilo.yml`, `hpe_ilo4.yml`, `hpe_ilo5.yml`, `hpe_ilo6.yml` (origin + capability), `tests/fixtures/redfish/hpe_ilo/`, `hpe_ilo4/`, `hpe_ilo5/`, `hpe_ilo6/` (mock) |
| 영향 vendor | HPE (lab 부재 — iLO7 외) |
| 함께 바뀔 것 | M-I1 / M-I2 (storage / power 변형 매트릭스 입력) |
| 리스크 top 3 | (1) iLO4 SmartStorage path (legacy) — 다른 generation 과 분기 큼 / (2) Additive 위반 시 iLO7 영향 / (3) Oem.Hp / Oem.Hpe 변형 (legacy) |
| 진행 확인 | HPE vault 이미 존재 — cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| generation | URL | 매트릭스 |
|---|---|---|
| iLO (legacy 1/2/3) | HPE archive docs | Redfish 미지원 (IPMI only) |
| iLO4 | `https://hewlettpackard.github.io/ilo-rest-api-docs/ilo4/` | DSP0268 v1.0+ (2014+) |
| iLO5 | `https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/` | DSP0268 v1.4+ (2017+) |
| iLO6 | `https://hewlettpackard.github.io/ilo-rest-api-docs/ilo6/` | DSP0268 v1.10+ (2022+) |
| iLO7 | (사이트 검증 — out of scope) | DSP0268 v1.13+ |

→ 매트릭스:
- **iLO (legacy 1/2/3)**: Redfish 미지원 — graceful (precheck protocol fail)
- **iLO4**: SmartStorage path (`/Systems/{id}/SmartStorage`) — 표준 Storage path 미지원
- **iLO5**: SmartStorage + 표준 Storage path dual
- **iLO6**: 표준 Storage path 우선 + SmartStorage fallback
- **iLO7**: 표준 Storage path only

→ Power 매트릭스:
- iLO4-5: Power deprecated only
- iLO6: Power + PowerSubsystem dual
- iLO7: PowerSubsystem only

---

## 구현

### 1. hpe_ilo.yml (legacy) origin

```yaml
metadata:
  vendor: hpe
  generation: ilo_legacy
  generation_year: "2002-2014"
  redfish_introduction: "미지원 (IPMI only)"
  origin: "HPE archive docs"
  lab_status: "부재"
  next_action: "lab 도입 후 별도 cycle — graceful degradation 시나리오"
  protocol_support: "IPMI only — Redfish 미지원 generation"
```

### 2. hpe_ilo4.yml capability

```yaml
capabilities:
  redfish_version: "1.0+"
  power_subsystem: false
  storage_strategy: "smart_storage_only"   # iLO4 의 legacy SmartStorage path
  oem_strategy: "standard+oem"
  oem_namespace: "Oem.Hp"                  # iLO4 시기 'Oem.Hp' (Hewlett-Packard) — iLO5+ 'Oem.Hpe'

metadata:
  vendor: hpe
  generation: ilo4
  generation_year: "2014-2017"
  redfish_introduction: "DSP0268 v1.0+"
  origin: "https://hewlettpackard.github.io/ilo-rest-api-docs/ilo4/"
  oem_namespace_variant: "Oem.Hp (iLO4 시기) → Oem.Hpe (iLO5+) fallback 의무"
```

### 3. hpe_ilo5.yml + hpe_ilo6.yml capability

```yaml
# iLO5
capabilities:
  redfish_version: "1.4+"
  power_subsystem: false
  storage_strategy: "smart_storage_with_standard_dual"
  oem_namespace: "Oem.Hpe"

# iLO6
capabilities:
  redfish_version: "1.10+"
  power_subsystem: "conditional"   # PowerSubsystem 도입 (Power deprecated path 와 dual)
  storage_strategy: "standard_with_smart_storage_fallback"
  oem_namespace: "Oem.Hpe"
```

### 4. mock fixture (4 디렉터리)

```
tests/fixtures/redfish/hpe_ilo/      # legacy — Redfish 미지원 시뮬 (service_root 부재)
tests/fixtures/redfish/hpe_ilo4/     # SmartStorage only + Oem.Hp variant
tests/fixtures/redfish/hpe_ilo5/     # SmartStorage + standard dual
tests/fixtures/redfish/hpe_ilo6/     # standard + PowerSubsystem dual
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check` 통과
- [ ] `verify_harness_consistency.py` 통과

### Additive only

- [ ] hpe_ilo7.yml 변경 0
- [ ] tests/fixtures/redfish/hpe_ilo7/ 변경 0
- [ ] sites_검증 envelope shape 변경 0

### 동적 검증

- [ ] iLO4 mock → SmartStorage path 만 사용 검증
- [ ] iLO5 mock → SmartStorage + standard dual 검증
- [ ] iLO6 mock → standard storage 우선 + SmartStorage fallback 검증
- [ ] Oem.Hp / Oem.Hpe fallback 분기 (HPE OEM tasks 본문에 이미 있음)

---

## risk

- (MED) iLO4 의 SmartStorage path 응답 형식이 iLO5+ standard storage 와 차이 큼 — adapter capabilities collect strategy 분기 의무
- (LOW) Oem.Hp legacy 변형 — HPE OEM tasks (`redfish-gather/tasks/vendors/hpe/collect_oem.yml`) 에 이미 fallback 분기 있는지 검증 (없으면 추가)

## 완료 조건

- [ ] 4 adapter (hpe_ilo / iLO4 / iLO5 / iLO6) metadata + capability 보강
- [ ] mock fixture 4 디렉터리 (시간 가용 시 priority: iLO5 > iLO4 > iLO6 > iLO legacy)
- [ ] iLO7 영향 0 검증
- [ ] commit: `feat: [M-H2 DONE] HPE 미검증 generation (iLO/4/5/6) capability + origin + mock`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W4 → M-H3 (Lenovo bmc/IMM2/XCC).

## 관련

- M-I1 / M-I2 (storage / power 매트릭스 입력)
- rule 92 R2 (Additive)
- rule 96 R1-A
