# M-H3 — Lenovo 미검증 generation (BMC / IMM / IMM2 / XCC / XCC2) 보강

> status: [PENDING] | depends: — | priority: P1 | worker: W4 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "사이트 검증 안 된 Lenovo generation 도 코드 path 깔자."

Lenovo 사이트 검증: XCC3 만. BMC (legacy) / IMM / IMM2 / XCC / XCC2 미검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/lenovo_bmc.yml`, `lenovo_imm2.yml`, `lenovo_xcc.yml` (origin + capability), `tests/fixtures/redfish/lenovo_*/` (mock) |
| 영향 vendor | Lenovo (lab 부재 — XCC3 외) |
| 함께 바뀔 것 | M-I1 / M-I2 (storage / power 변형) |
| 리스크 top 3 | (1) Lenovo generation 명명 — IBM 시기 BMC, IBM xSeries IMM, IMM2 → Lenovo XCC / XCC2 / XCC3 / (2) cycle 2026-04-30 사이트 사고 — XCC accept-only header / (3) Additive 위반 시 XCC3 영향 |
| 진행 확인 | Lenovo vault 이미 존재 — cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| generation | URL | 매트릭스 |
|---|---|---|
| BMC (IBM 시기) | IBM xSeries archive docs | Redfish 미지원 (대부분) |
| IMM (IBM Integrated Management Module) | IBM IMM archive | Redfish 미지원 또는 v1.0 부분 |
| IMM2 | `https://lenovopress.lenovo.com/.../imm2-redfish` | DSP0268 v1.0+ (2014+) |
| XCC | `https://lenovopress.lenovo.com/.../xcc-redfish` | DSP0268 v1.4+ (2017+) |
| XCC2 | `https://lenovopress.lenovo.com/.../xcc2-redfish` | DSP0268 v1.10+ (2022+) |
| XCC3 | (사이트 검증 — out of scope) | DSP0268 v1.13+ |

→ Lenovo 사이트 사고 (cycle 2026-04-30 reverse regression):
- 사이트 BMC 펌웨어 1.17.0 — Accept + OData-Version + User-Agent 추가 시 reject
- "Accept만" 으로 hotfix (rule 25 R7-A1 — 사용자 실측 > spec)
- 본 매트릭스에 적용: XCC2 / XCC 일부 펌웨어도 동일 정책 가능 — header 정책 보수적

---

## 구현

### 1. lenovo_bmc.yml (legacy IBM BMC) origin

```yaml
metadata:
  vendor: lenovo
  generation: bmc_legacy
  generation_year: "2007-2014 (IBM xSeries)"
  redfish_introduction: "미지원 또는 v1.0 부분"
  origin: "IBM xSeries archive"
  lab_status: "부재"
  protocol_support: "IPMI only — Redfish 미지원 또는 부분"
  history_note: "IBM 시기 (Lenovo 인수 전) — Manufacturer aliases 에 'IBM' 포함 (vendor_aliases.yml)"
```

### 2. lenovo_imm2.yml capability

```yaml
capabilities:
  redfish_version: "1.0+"
  power_subsystem: false
  storage_strategy: "standard_with_simple_fallback"  # IMM2 일부 펌웨어 SimpleStorage
  oem_strategy: "standard+oem"
  oem_namespace: "Oem.Lenovo"

metadata:
  vendor: lenovo
  generation: imm2
  generation_year: "2014-2017"
  redfish_introduction: "DSP0268 v1.0+"
  origin: "https://lenovopress.lenovo.com/.../imm2-redfish"
  history_note: "IBM IMM2 → Lenovo IMM2 (2014 인수 후)"
```

### 3. lenovo_xcc.yml + 신규 lenovo_xcc2 (XCC2 capability — XCC3 와 분기)

```yaml
# lenovo_xcc.yml (XCC 1세대)
capabilities:
  redfish_version: "1.4+"
  power_subsystem: false
  storage_strategy: "standard"
  oem_namespace: "Oem.Lenovo"

# 신규: lenovo_xcc2.yml (cycle 2026-05-07 추가 검토 — 또는 lenovo_xcc.yml 안 firmware_patterns 으로 분기)
# 권장: lenovo_xcc.yml 안 firmware_patterns 분기 (Additive — 새 adapter 신설 회피)

# lenovo_xcc.yml match.firmware_patterns 확장:
match:
  firmware_patterns:
    - "XCC*1.*"      # XCC 1세대 (2017-2020)
    - "XCC*2.*"      # XCC2 (2020-2022)
    # XCC3 는 lenovo_xcc3.yml 에서 처리 (priority=110)
```

### 4. mock fixture (4 디렉터리)

```
tests/fixtures/redfish/lenovo_bmc/    # legacy IBM BMC
tests/fixtures/redfish/lenovo_imm2/   # IMM2 (2014-2017)
tests/fixtures/redfish/lenovo_xcc/    # XCC 1세대 + XCC2 variants
tests/fixtures/redfish/lenovo_xcc2/   # XCC2 별도 (선택)
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check` 통과
- [ ] `verify_harness_consistency.py` 통과

### Additive only

- [ ] lenovo_xcc3.yml 변경 0 (사이트 검증)
- [ ] tests/fixtures/redfish/lenovo_xcc3/ 변경 0
- [ ] cycle 2026-04-30 hotfix (Accept-only header) 정책 영향 0

### 동적 검증

- [ ] IMM2 mock → standard storage + SimpleStorage fallback
- [ ] XCC mock → standard storage + Power deprecated only
- [ ] XCC2 mock (firmware_patterns 분기) → 적절한 capability 사용

---

## risk

- (MED) Lenovo XCC2 펌웨어가 사이트 사고 1.17.0 (XCC3) 와 동일 header 정책 — 보수적 header 정책 의무
- (LOW) IBM 시기 BMC mock — 대부분 Redfish 미지원 시뮬

## 완료 조건

- [ ] lenovo_bmc / lenovo_imm2 / lenovo_xcc metadata + capability 보강
- [ ] lenovo_xcc.yml firmware_patterns 분기 (XCC + XCC2)
- [ ] mock fixture 4 디렉터리 (시간 가용 시 priority: XCC > IMM2 > XCC2 > BMC)
- [ ] XCC3 영향 0 검증
- [ ] commit: `feat: [M-H3 DONE] Lenovo 미검증 generation (BMC/IMM2/XCC/XCC2) capability + origin + mock`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W4 → M-H4 (Cisco BMC/CIMC/B-series).

## 관련

- M-I1 / M-I2 (storage / power 매트릭스)
- rule 25 R7-A1 (사용자 실측 > spec — header 정책)
- rule 92 R2 (Additive)
- rule 96 R1-A
