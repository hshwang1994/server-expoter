# M-L3 — docs/ai/catalogs/COMPATIBILITY-MATRIX.md 갱신 (rule 28 R1 #12)

> status: [PENDING] | depends: M-L2 | priority: P2 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "COMPATIBILITY-MATRIX.md 갱신 (vendor × generation × section 매트릭스 — rule 28 R1 #12)." (cycle 진입)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/ai/catalogs/COMPATIBILITY-MATRIX.md` (갱신) |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | (없음 — 카탈로그) |
| 리스크 top 3 | (1) 매트릭스 비대화 (9 vendor × N gen × 10 sections) / (2) cycle 진입 baseline (본 cycle COMPATIBILITY-MATRIX.md) 와 동기화 / (3) M-I1, M-I2 변형 매트릭스 입력 |
| 진행 확인 | M-L2 후 진입 |

---

## 갱신 본문 (docs/ai/catalogs/COMPATIBILITY-MATRIX.md)

본 cycle 진입 시 작성한 `docs/ai/tickets/2026-05-07-all-vendor-coverage/COMPATIBILITY-MATRIX.md` 를 정본 catalog 위치 (`docs/ai/catalogs/COMPATIBILITY-MATRIX.md`) 로 이동 + cycle 종료 후 [DONE] 상태 반영.

### 차이점:
- ticket 매트릭스 (cycle 시작 baseline) → catalog 매트릭스 (cycle 종료 결과)
- 본 cycle 산출 결과 반영 (Supermicro X10 신설 / OEM tasks 5 신설 / Cisco vendor task / 가별 vault 보강)

### 갱신 절:

```markdown
# COMPATIBILITY-MATRIX — 9 vendor × N generation × 10 sections (rule 28 R1 #12)

> 측정 대상 #12 (TTL 14일). cycle 2026-05-07 갱신 (M-L3).

## 사이트 검증 4 vendor × 1 generation (cycle 2026-05-07)

| vendor | generation | 사이트 BMC | adapter | vault | OEM tasks | baseline |
|---|---|---|---|---|---|---|
| Dell | iDRAC10 | 5대 | dell_idrac10.yml (priority=110) | dell.yml (encrypted) | tasks/vendors/dell/ | dell_baseline.json |
| HPE | iLO7 | 1대 | hpe_ilo7.yml (priority=110) | hpe.yml | tasks/vendors/hpe/ (M-G1 Superdome 분기 추가) | hpe_baseline.json |
| Lenovo | XCC3 | 1대 | lenovo_xcc3.yml (priority=110) | lenovo.yml | tasks/vendors/lenovo/ | lenovo_baseline.json |
| Cisco | UCS X-series | 1대 | cisco_ucs_xseries.yml (priority=120) | cisco.yml | **tasks/vendors/cisco/ (M-J1 신설)** | cisco_baseline.json |

## 9 vendor × N generation × 10 sections 매트릭스 (cycle 2026-05-07 종료 시점)

[자세한 매트릭스 — 본 cycle 진입 시 작성한 ticket 의 COMPATIBILITY-MATRIX.md 본문 + 본 cycle 산출 반영]

### sections 변형 매트릭스 (M-I1, M-I2, M-I3 결과)

#### Storage (M-I1)

| strategy | 적용 vendor / generation |
|---|---|
| pldm_rde_only | Dell iDRAC10, iDRAC9 6.x+ |
| pldm_rde_with_standard_fallback | Dell iDRAC9 5.x |
| smart_storage_only | HPE iLO4 |
| smart_storage_with_standard_dual | HPE iLO5 |
| standard_with_smart_storage_fallback | HPE iLO6 |
| standard | HPE iLO7, Lenovo XCC/XCC2/XCC3, Cisco UCS X-series, Supermicro X11+, Huawei iBMC 2.x+, Inspur, Fujitsu iRMC S4+, Quanta |
| simple_storage_only | Dell iDRAC7, Lenovo IMM2, Cisco CIMC 1.x-2.x, Supermicro X9-X10, Huawei iBMC 1.x |
| (graceful fail — Redfish 미지원) | HPE iLO legacy, Fujitsu iRMC S2, Cisco BMC legacy |

#### Power (M-I2)

| strategy | 적용 vendor / generation |
|---|---|
| subsystem_only | Dell iDRAC10, HPE iLO7, Cisco UCS X-series |
| subsystem_with_legacy_dual | Dell iDRAC9 5.x+, HPE iLO5/6, Lenovo XCC3, Supermicro X12-X14 |
| subsystem_with_legacy_fallback | Cisco CIMC 4.x, Huawei iBMC 3.x+, Fujitsu iRMC S6+ |
| legacy_only | 그 외 모든 generation |

#### bmc / firmware OEM namespace (M-I3 / M-J1)

| vendor | namespace 우선 | namespace fallback |
|---|---|---|
| Dell | Oem.Dell | (없음) |
| HPE | Oem.Hpe | Oem.Hp (iLO4) |
| Lenovo | Oem.Lenovo | (없음) |
| Cisco | Oem.Cisco | Oem.Cisco_RackUnit |
| Supermicro | Oem.Supermicro | (없음) |
| Huawei | Oem.Huawei | (없음) |
| Inspur | Oem.Inspur | Oem.Inspur_System |
| Fujitsu | Oem.ts_fujitsu | Oem.Fujitsu |
| Quanta | Oem.Quanta_Computer_Inc | Oem.QCT |

## cycle 산출 차이 (2026-05-07 진입 → 종료)

| 항목 | 진입 | 종료 | 증감 |
|---|---|---|---|
| adapter (Redfish) | 28 | 29 (+supermicro_x10) | +1 |
| vault encrypted (Redfish) | 5 | 9 (+huawei/inspur/fujitsu/quanta) | +4 |
| vendor OEM tasks | 4 | 9 (+cisco/huawei/inspur/fujitsu/quanta) | +5 |
| mock fixture (vendor 별) | 4 | 13+ (cycle 종료 시 일부 [SKIP] 가능) | +9 |
| baseline_v1 (Redfish) | 4 (사이트 검증) | 4 | 0 (lab 부재 vendor SKIP — rule 13 R4) |
| EXTERNAL_CONTRACTS entry | 일부 | 9 vendor × N gen | 대폭 |

## 다음 측정 시점 (rule 28 R1 #12 TTL 14일)

- 다음 측정: 2026-05-21 또는 trigger (adapter capabilities 변경 / 새 vendor / 펌웨어 업그레이드) 발생 시
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `docs/ai/catalogs/COMPATIBILITY-MATRIX.md` 본문 갱신
- [ ] 사이트 검증 4 + lab 부재 25+ row 등재
- [ ] M-I1 / M-I2 / M-I3 매트릭스 입력 통합

### 의미 검증

- [ ] cycle 산출 차이 명시 (진입 → 종료)
- [ ] 다음 측정 시점 (TTL 14일) 명시

---

## risk

- (LOW) 매트릭스 비대화 — 9 vendor × N gen × 10 sections 큼. ticket 매트릭스 + catalog 매트릭스 양쪽 갱신

## 완료 조건

- [ ] docs/ai/catalogs/COMPATIBILITY-MATRIX.md 본문 갱신
- [ ] cycle 산출 차이 명시
- [ ] commit: `docs: [M-L3 DONE] COMPATIBILITY-MATRIX.md 갱신 — cycle 2026-05-07 산출 반영`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-L4 (docs/13 갱신).

## 관련

- M-L1, M-L2, M-K2 (catalog 갱신)
- M-I1, M-I2, M-I3 (매트릭스 입력)
- rule 28 R1 #12 (COMPATIBILITY-MATRIX 측정 대상 — TTL 14일)
- 정본: 본 cycle 진입 시 ticket COMPATIBILITY-MATRIX.md
