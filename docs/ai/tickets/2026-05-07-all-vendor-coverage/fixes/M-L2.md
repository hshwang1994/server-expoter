# M-L2 — docs/ai/catalogs/VENDOR_ADAPTERS.md 갱신 (29 adapter 매트릭스)

> status: [PENDING] | depends: M-L1 | priority: P2 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "VENDOR_ADAPTERS.md 갱신 (28 → 29 adapter)." (cycle 진입)

cycle 진입 시 28 adapter — 본 cycle M-B1 (Supermicro X10) 신설로 29 adapter 예상. M-B3 ARS (선택적) 추가 시 30. catalog 갱신.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/ai/catalogs/VENDOR_ADAPTERS.md` (갱신 — 29+ adapter 매트릭스) |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | (없음 — 카탈로그) |
| 리스크 top 3 | (1) adapter 카운트 정확성 (28 → 29) / (2) priority 매트릭스 일관성 / (3) lab status 동기화 (M-K1 / M-K2 와) |
| 진행 확인 | M-L1 후 진입 |

---

## 갱신 본문 (docs/ai/catalogs/VENDOR_ADAPTERS.md)

```markdown
# VENDOR_ADAPTERS — Redfish adapter 매트릭스

> rule 28 R1 #3 측정 대상 (TTL 14일). cycle 2026-05-07 갱신 (M-L2).

## adapter 카운트

| 시점 | adapter 수 | 갱신 |
|---|---|---|
| cycle 2026-04-29 (production-audit) | 27 | 16 Redfish + 7 OS + 4 ESXi |
| cycle 2026-05-01 (gather-coverage) | 38 | +11 Redfish (idrac10/ilo7/xcc3/superdome_flex/x12/x13/x14/cisco_ucs_xseries/huawei_ibmc/inspur_isbmc/fujitsu_irmc/quanta_qct_bmc) |
| cycle 2026-05-06 (multi-session) | 39 | +1 (hpe_superdome_flex) |
| **cycle 2026-05-07 (all-vendor-coverage)** | **29~30 (Redfish 만)** | +1 supermicro_x10 신설 (M-B1) + (선택) supermicro_ars (M-B3) |

→ 본 카탈로그는 Redfish adapter 만. OS (7) / ESXi (4) 는 별도 적용.

## Redfish adapter 매트릭스 (29 adapter — cycle 2026-05-07 종료 시점)

### Dell (5 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| dell_idrac.yml | 10 | iDRAC7 (legacy) | 부재 |
| dell_idrac8.yml | 80 | iDRAC8 | 부재 |
| dell_idrac9.yml | 100 | iDRAC9 | 부재 |
| dell_idrac10.yml | 110 | iDRAC10 | **PASS** (사이트 5대) |

### HPE (6 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| hpe_ilo.yml | 10 | iLO (legacy) | 부재 |
| hpe_ilo4.yml | 80 | iLO4 | 부재 |
| hpe_ilo5.yml | 90 | iLO5 | 부재 |
| hpe_ilo6.yml | 100 | iLO6 | 부재 |
| hpe_ilo7.yml | 110 | iLO7 | **PASS** (사이트 1대) |
| hpe_superdome_flex.yml | 95 | Superdome Flex | 부재 |

### Lenovo (4 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| lenovo_bmc.yml | 10 | BMC (legacy) | 부재 |
| lenovo_imm2.yml | 80 | IMM2 | 부재 |
| lenovo_xcc.yml | 100 | XCC + XCC2 (firmware_patterns 분기) | 부재 |
| lenovo_xcc3.yml | 110 | XCC3 | **PASS** (사이트 1대) |

### Cisco (3 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| cisco_bmc.yml | 10 | BMC (legacy) | 부재 |
| cisco_cimc.yml | 80 | CIMC C-series 1.x ~ 4.x (firmware_patterns 분기) + S-series + B-series (model_patterns) | 부재 |
| cisco_ucs_xseries.yml | 120 | UCS X-series | **PASS** (사이트 1대) |

### Supermicro (7 adapter — M-B1 X10 신설 후)

| adapter | priority | generation | lab |
|---|---|---|---|
| supermicro_bmc.yml | 10 | BMC (legacy) | 부재 |
| supermicro_x9.yml | 70 | X9 | 부재 |
| supermicro_x10.yml | 75 | **X10 (cycle 2026-05-07 M-B1 신설)** | 부재 |
| supermicro_x11.yml | 80 | X11 + H11 (M-B3) | 부재 |
| supermicro_x12.yml | 90 | X12 + H12 | 부재 |
| supermicro_x13.yml | 100 | X13 + H13 | 부재 |
| supermicro_x14.yml | 110 | X14 + H14 | 부재 |

### (선택) Supermicro (8 adapter — M-B3 ARS 추가 시)

| adapter | priority | generation | lab |
|---|---|---|---|
| supermicro_ars.yml | 80 | ARS (ARM) | 부재 |

### Huawei (1 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| huawei_ibmc.yml | 70 | iBMC 1.x ~ 5.x (firmware_patterns) + Atlas (model_patterns) | 부재 (cycle 2026-05-01 명시) |

### Inspur (1 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| inspur_isbmc.yml | 70 | ISBMC | 부재 |

### Fujitsu (1 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| fujitsu_irmc.yml | 70 | iRMC S2 / S4 / S5 / S6 (firmware_patterns) + PRIMEQUEST (model_patterns) | 부재 |

### Quanta (1 adapter)

| adapter | priority | generation | lab |
|---|---|---|---|
| quanta_qct_bmc.yml | 70 | QCT BMC (S/D/T/J series) | 부재 |

### Generic fallback (1 adapter)

| adapter | priority | 용도 |
|---|---|---|
| redfish_generic.yml | 0 | 매치 안 되는 vendor — graceful degradation |

## priority 일관성 검증 (rule 12 R2)

각 vendor 내 priority 역전 0:

| vendor | priority 순서 |
|---|---|
| Dell | 10 < 80 < 100 < 110 |
| HPE | 10 < 80 < 90 < 95 < 100 < 110 (Superdome Flex 95) |
| Lenovo | 10 < 80 < 100 < 110 |
| Cisco | 10 < 80 < 120 |
| Supermicro | 10 < 70 < 75 < 80 < 90 < 100 < 110 |
| Huawei | 70 (단일) |
| Inspur | 70 (단일) |
| Fujitsu | 70 (단일) |
| Quanta | 70 (단일) |

→ 역전 0. ARS adapter 추가 시 80 (X11 동률 — model_patterns 분리 가능).

## OEM tasks 매트릭스 (M-J1)

| vendor | OEM tasks 디렉터리 | 상태 |
|---|---|---|
| Dell | redfish-gather/tasks/vendors/dell/ | [DONE] (이전 cycle) |
| HPE | redfish-gather/tasks/vendors/hpe/ | [DONE] (M-G1 Superdome 분기 보강) |
| Lenovo | redfish-gather/tasks/vendors/lenovo/ | [DONE] |
| Supermicro | redfish-gather/tasks/vendors/supermicro/ | [DONE] |
| Cisco | redfish-gather/tasks/vendors/cisco/ | **[NEW] cycle 2026-05-07 M-J1 신설** |
| Huawei | redfish-gather/tasks/vendors/huawei/ | **[NEW] cycle 2026-05-07 M-C2 신설** |
| Inspur | redfish-gather/tasks/vendors/inspur/ | **[NEW] cycle 2026-05-07 M-D1 신설** |
| Fujitsu | redfish-gather/tasks/vendors/fujitsu/ | **[NEW] cycle 2026-05-07 M-E2 신설** |
| Quanta | redfish-gather/tasks/vendors/quanta/ | **[NEW] cycle 2026-05-07 M-F1 신설** |

## 갱신 history

| cycle | adapter 변경 | OEM tasks 변경 |
|---|---|---|
| 2026-04-29 | 27 (production-audit) | Dell/HPE/Lenovo/Supermicro |
| 2026-05-01 | 38 (+11 신규 vendor / generation) | (변경 없음) |
| 2026-05-06 | 39 (+1 hpe_superdome_flex) | (변경 없음) |
| **2026-05-07** | **29 (+1 supermicro_x10) + (선택) ARS** | **+5 (Cisco/Huawei/Inspur/Fujitsu/Quanta 신설)** |
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `docs/ai/catalogs/VENDOR_ADAPTERS.md` 본문 갱신
- [ ] adapter 카운트 정확성 (29 또는 30)
- [ ] 9 vendor 모두 등재
- [ ] priority 매트릭스 일관성
- [ ] OEM tasks 매트릭스 9 vendor 등재 (5 신설 명시)

### 의미 검증

- [ ] 사이트 검증 4 vendor — "**PASS**" 표시
- [ ] 그 외 — "부재" 표시
- [ ] 갱신 history 4 cycle (04-29 / 05-01 / 05-06 / 05-07) 등재

---

## risk

- (LOW) adapter 카운트 정확성 — 본 cycle 종료 시 실측 (`ls adapters/redfish/ | wc -l`) 후 갱신

## 완료 조건

- [ ] docs/ai/catalogs/VENDOR_ADAPTERS.md 본문 갱신
- [ ] adapter 매트릭스 + priority 일관성 + OEM tasks 9 vendor
- [ ] commit: `docs: [M-L2 DONE] VENDOR_ADAPTERS.md 갱신 — 29 adapter + OEM tasks 9 vendor`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-L3 (COMPATIBILITY-MATRIX).

## 관련

- M-L1 (NEXT_ACTIONS)
- M-K1, M-K2 (origin / EXTERNAL_CONTRACTS)
- rule 28 R1 #3 (vendor adapter 매트릭스 측정 대상)
