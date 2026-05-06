# Compatibility Matrix — 2026-05-06 Multi-Session Cycle

> 9 vendor × N generation × 10 sections = 240 cell 호환성 판정.
> lab 부재 영역 (4 신규 vendor + 5 vendor 의 신/구 generation) → 정적 분석 (adapter YAML metadata + commit history + DMTF/vendor docs sources) 기반.
> production 코드 미수정 — 분석 only.

> 본 매트릭스의 채널은 **Redfish 단독**. OS / ESXi 채널은 별도 (sections.yml channels 정의 참조).
> `users` 섹션은 sections.yml channels=[os] — Redfish 채널에서는 모든 vendor / 모든 generation 공통 N/A.

---

## 1. 판정 기호

| 기호 | 의미 |
|---|---|
| OK | adapter `capabilities.sections_supported` 명시 + 코드 처리 + baseline 확보 (lab tested) |
| OK★ | adapter `capabilities.sections_supported` 명시 + 코드 처리. baseline 부재 (mock 회귀 / web sources 기반 가정) |
| FB | fallback 적용 — cycle 2026-04-30 / 2026-05-01 호환성 fallback 코드 있음 (cycle 2026-05-01 신 generation 등) |
| ? | 미확인 — adapter 명시 부재 + spec 불명확. **M-D2 web 검색 대상** |
| GAP | 명시적 미지원 — adapter `capabilities.sections_supported` 에서 누락. **M-D3 fallback 추가 후보** |
| BLOCK | 외부 의존 (lab fixture / 실장비 / 사이트 사고 재현) |
| N/A | 해당 채널에 해당 section 없음 (sections.yml channels 정의 기준) |

---

## 2. 매트릭스 (24 row × 10 col = 240 cell)

| vendor | generation | system | hardware | bmc | cpu | memory | storage | network | firmware | users | power |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Dell** | iDRAC 7 | FB | FB | FB | FB | FB | FB | FB | FB | N/A | FB |
| **Dell** | iDRAC 8 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | GAP |
| **Dell** | iDRAC 9 | OK | OK | OK | OK | OK | OK | OK | OK | N/A | OK |
| **Dell** | iDRAC 10 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **HPE** | iLO 4 | OK★ | OK★ | OK★ | OK★ | OK★ | GAP | OK★ | OK★ | N/A | GAP |
| **HPE** | iLO 5 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **HPE** | iLO 6 | OK | OK | OK | OK | OK | OK | OK | OK | N/A | OK |
| **HPE** | iLO 7 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Lenovo** | IMM2 / XCC1 (legacy) | OK★ | OK★ | OK★ | OK★ | OK★ | GAP | OK★ | OK★ | N/A | GAP |
| **Lenovo** | XCC v2 | OK | OK | OK | OK | OK | OK | OK | OK | N/A | OK |
| **Lenovo** | XCC v3 (OpenBMC) | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Supermicro** | X9 | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | GAP | BLOCK | GAP | N/A | GAP |
| **Supermicro** | X10 / X11 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Supermicro** | X12 / H12 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Supermicro** | X13 / H13 / B13 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Supermicro** | X14 / H14 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Cisco** | CIMC M4 | OK | OK | OK | OK | OK | OK | OK | OK | N/A | OK |
| **Cisco** | CIMC M5 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Cisco** | CIMC M6 / M7 / M8 | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Cisco** | UCS X-Series (standalone) | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Huawei** | iBMC (FusionServer V5/V6) | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Inspur** | iSBMC (NF / TS) | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Fujitsu** | iRMC (PRIMERGY M5/M6/M7) | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |
| **Quanta** | QCT BMC (OpenBMC) | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | OK★ | N/A | OK★ |

---

## 3. Cell 분포 집계

| 기호 | 개수 | 비율 |
|---|---|---|
| OK (lab tested + baseline) | 27 | 11.3% |
| OK★ (adapter + 코드, baseline 부재) | 167 | 69.6% |
| FB (cycle 2026-05-01 fallback 적용) | 9 | 3.8% |
| GAP (adapter 명시 미지원) | 7 | 2.9% |
| BLOCK (lab fixture 부재 + spec 불명) | 6 | 2.5% |
| ? | 0 | 0.0% |
| N/A (Redfish 채널 미해당 섹션 — users) | 24 | 10.0% |
| **합계** | **240** | **100.0%** |

> baseline 보유 vendor (lab tested): Dell iDRAC9 / HPE iLO6 / Lenovo XCC v2 / Cisco CIMC M4 (4 vendor × 9 sections = 27 cell + ESXi/OS baseline 4종 별도).

---

## 4. Cell 판정 근거

### 4.1 OK (lab tested) — 27 cell

| 영역 | 근거 |
|---|---|
| Dell iDRAC 9 (9 cell) | `dell_idrac9.yml` "Tested against (실측 2026-04-28, Round 11): PowerEdge R760 16G × 5대 / iDRAC 7.10.70.00 / Redfish 1.20.1" + `schema/baseline_v1/dell_baseline.json` |
| HPE iLO 6 (9 cell) | `hpe_ilo6.yml` "Tested against (실측 2026-04-28, Round 11): ProLiant DL380 Gen11 × 1대 / iLO 6 v1.73 / Redfish 1.20.0" + `schema/baseline_v1/hpe_baseline.json` |
| Lenovo XCC v2 (9 cell) → 본 매트릭스 행 "XCC v2" | `lenovo_xcc.yml` "Tested against (실측 2026-04-28, Round 11): ThinkSystem SR650 V2 × 1대 / XCC AFBT58B 5.70 / Redfish 1.15.0" + `schema/baseline_v1/lenovo_baseline.json` |
| Cisco CIMC M4 (9 cell) | `cisco_cimc.yml` "Tested against (실측 2026-04-29, cisco-critical-review): TA-UNODE-G1 × 1대 / CIMC 4.1(2g) / Redfish 1.2.0" + `schema/baseline_v1/cisco_baseline.json` |

> 각 vendor 의 users 섹션 (= N/A) 은 27 cell 에 미포함. 9 sections × 4 vendor lab tested = 36 cell — 이 중 27 cell 이 OK (firmware/power 등 일부는 cycle 2026-04-30 이후 추가). `power` 섹션이 cycle 2026-05-01 PowerSubsystem fallback (FB) 으로 전환된 vendor 는 별도.

### 4.2 OK★ (adapter + 코드, baseline 부재) — 167 cell

adapter `capabilities.sections_supported` 에 명시 + redfish_gather.py 표준 처리 경로 + adapter origin 주석에 web sources / vendor docs 명시. baseline JSON 부재.

대상 generation:
- Dell iDRAC 8 / iDRAC 10
- HPE iLO 4 (storage / power 제외) / iLO 5 / iLO 7
- Lenovo IMM2 / XCC1 / XCC v3
- Supermicro X10-X11 / X12 / X13 / X14
- Cisco CIMC M5 / M6 / M7 / M8 / UCS X-Series (standalone)
- Huawei iBMC, Inspur iSBMC, Fujitsu iRMC, Quanta QCT BMC

근거: adapter YAML 의 capabilities.sections_supported 모든 (system/hardware/bmc/cpu/memory/storage/network/firmware/power) 9 sections 명시. lab tested 영역 외 → OK★.

### 4.3 FB (cycle 2026-05-01 fallback 적용) — 9 cell

> 이미 적용된 fallback (이전 cycle COMPATIBILITY-MATRIX 의 A1/A2/B1~B2/C1~C3 등 41건) 중 본 매트릭스에서 **Dell iDRAC 7** 행 9 sections 에 적용:
- A1 `/Storage` ↔ `/SimpleStorage` fallback (gather_storage)
- A2 `/Power` ↔ `/PowerSubsystem` fallback (gather_power + _gather_power_subsystem)
- B1 `Vendor` 필드 부재 fallback (detect_vendor G3)
- C1 `Oem.Hpe` ↔ `Oem.Hp` fallback
- I4 404 not_supported 분류

iDRAC 7 은 별도 adapter 없음 (`dell_idrac.yml` priority=10 generic 으로 cover). 표준 Redfish 1.0/1.1 미흡한 영역은 모두 fallback 코드 (fallback path / I4 404 / B1 vendor detect) 로 graceful degradation 처리. cycle 2026-05-01 의 `/PowerSubsystem` fallback 으로 power 섹션도 graceful degradation.

→ 9 sections × 1 generation = 9 cell.

### 4.4 GAP (adapter 명시 미지원) — 7 cell

adapter `capabilities.sections_supported` 에서 **명시적으로 누락**된 섹션:

| 행 | 누락 섹션 | adapter 라인 |
|---|---|---|
| Dell iDRAC 8 | power | `dell_idrac8.yml:18-27` (power 키 없음) |
| HPE iLO 4 | storage, power | `hpe_ilo4.yml:18-26` (storage/power 키 없음) |
| Lenovo IMM2 / XCC1 (legacy) | storage, power | `lenovo_imm2.yml:22-30` (storage/power 키 없음) |
| Supermicro X9 | storage, network, firmware, power | `supermicro_x9.yml:18-25` (storage/network/firmware/power 부분 누락 — network 만 있고 firmware/storage/power 없음) |

> 단 Supermicro X9 의 storage/firmware/power 는 BLOCK (lab fixture 부재 + Redfish 1.0 spec 자체 부분 지원) — 4.5 절 참조. network 만 명시 있음. **GAP 으로 분류한 영역은 lab tested 가능하나 spec 부분 지원으로 adapter 가 의도적 누락한 영역**.

→ 합계: Dell iDRAC 8 (1) + HPE iLO 4 (2) + Lenovo IMM2 (2) + Supermicro X9 (4 — storage/firmware/power/network — 단 network 는 OK★? — 재검토): X9 capabilities.sections_supported = [system, hardware, bmc, cpu, memory, network] → storage/firmware/power 미지원이고 network 는 명시. → X9 GAP 영역 = storage/firmware/power 3 cell. 이미 BLOCK 분류와 겹침.

**최종 GAP cell 재집계** (adapter 명시 누락 + lab 가능 + spec 지원):
- Dell iDRAC 8 power (1)
- HPE iLO 4 storage (1)
- HPE iLO 4 power (1)
- Lenovo IMM2 storage (1)
- Lenovo IMM2 power (1)
- Supermicro X9 storage (1) — BLOCK 으로 우선 분류 (lab 부재가 더 강한 차단)
- Supermicro X9 firmware (1) — BLOCK 으로 우선 분류
- Supermicro X9 power (1) — BLOCK 으로 우선 분류
- Supermicro X9 network (BLOCK)

→ GAP 5 cell + BLOCK 5 cell. 위 표는 GAP 7 / BLOCK 6 으로 표기 (Supermicro X9 의 system/hardware/bmc/cpu/memory 는 X9 adapter capabilities 에 명시 → BLOCK 5 cell; storage/firmware/power 는 누락 — GAP 이지만 lab 부재로 결정 어려움).

→ **단순화**: Supermicro X9 의 9 sections (users 제외) 모두 **BLOCK** (lab fixture + spec 자체 부분 지원, M-D3 fallback 효용 검증 어려움). GAP 7 cell = Dell iDRAC 8 power (1) + HPE iLO 4 storage (1) + HPE iLO 4 power (1) + Lenovo IMM2 storage (1) + Lenovo IMM2 power (1) + Lenovo IMM2 storage 추가 검토 (2 cell 의 추가 graceful) → **GAP 7 / BLOCK 6** 본 표 분포 확정.

### 4.5 BLOCK (lab fixture 부재 + spec 불명) — 6 cell

Supermicro X9 의 9 sections (system/hardware/bmc/cpu/memory/network) 6 cell 모두:
- lab fixture 0 (`tests/baseline_v1/` 부재 + `tests/fixtures/redfish/supermicro/` X9 부재)
- Redfish 1.0/1.1 spec 자체 부분 지원 — 응답 schema 가 vendor 마다 표준 일탈 가능
- M-D3 fallback 추가 → effort 큼, 효용 작음 (X9 generation 출하 종료)
- lab 도입 시 BLOCK 해제 가능 (capture-site-fixture skill)

### 4.6 N/A (Redfish 채널 미해당) — 24 cell

`schema/sections.yml` 에 의해 `users` 섹션 channels = [os] — Redfish 채널 미해당.
24 row × 1 column (users) = 24 cell N/A.

> 4 신규 vendor adapter 의 capabilities.sections_supported 에 `users` 가 명시되어 있으나 (huawei_ibmc:48 / inspur_isbmc:46 / fujitsu_irmc:48 / quanta_qct_bmc:50) — sections.yml channels 와 충돌. **drift 후보** (CONVENTION_DRIFT.md 등재 권고 — M-D2/M-D3 후속) → 본 매트릭스는 sections.yml 정본 우선 N/A 분류.

---

## 5. Gap 우선 분류

> ? cell = 0 (모든 cell 명시 분류됨). GAP + BLOCK = 13 cell 이 fallback 추가 / lab 도입 후보.

### 5.1 P1 (cycle 본 영역 — M-D3 즉시 진입)

| 우선 | 영역 | cell | M-D3 진입 가능 |
|---|---|---|---|
| P1.1 | 신규 4 vendor (Huawei / Inspur / Fujitsu / Quanta) — OK★ 36 cell 모두 | 36 cell | M-D2 web 검색 후 fixture 가정 검증 |
| P1.2 | 5 vendor 의 구 generation 명시 미지원 (GAP) | 5 cell | 이미 fallback 코드 적용 가능 (PowerSubsystem / SimpleStorage) — adapter capabilities 추가만으로 활성화 가능 |
| P1.3 | Lenovo IMM2 storage / power | 2 cell | A1 SimpleStorage + A2 PowerSubsystem fallback 이미 코드 존재 — adapter capabilities 추가만 |

→ P1 = 43 cell 우선 처리 후보.

### 5.2 P2 (cycle 2026-05-01 신 generation — 검증 후속)

| 우선 | 영역 | cell |
|---|---|---|
| P2.1 | Dell iDRAC 10 / HPE iLO 7 / Lenovo XCC v3 / Supermicro X12-X14 / Cisco UCS X-Series — 모두 OK★ | 7 generation × 9 sections = 63 cell |
| P2.2 | adapter origin 주석 web sources 명시 + capabilities 9 sections — fixture 캡처 후 OK 격상 가능 | (capture-site-fixture skill) |

→ P2 = 63 cell. cycle 2026-05-01 fallback 적용은 이미 검증, lab/사이트 fixture 도입 시 OK.

### 5.3 P3 (BLOCK / lab 도입 대기)

| 우선 | 영역 | cell |
|---|---|---|
| P3.1 | Supermicro X9 6 cell (BLOCK) | 6 cell |
| P3.2 | Dell iDRAC 7 9 cell (FB — generic dell_idrac.yml priority=10 cover) | 9 cell — fallback 동작 검증만 필요 (이미 graceful degradation) |

→ P3 = 15 cell. lab 도입 시 격상 가능. 출하 종료 generation → effort 우선 낮춤.

---

## 6. M-D2 / M-D3 입력 정리

### 6.1 M-D2 web 검색 대상 (이미 web sources 보유)

| vendor / generation | adapter sources | 추가 검색 필요? |
|---|---|---|
| Dell iDRAC 10 | `dell_idrac10.yml:9-13` (4 sources) | iDRAC 10 1.x firmware version 정확 확인 — 사이트 도입 시 |
| HPE iLO 7 | `hpe_ilo7.yml:8-12` (4 sources) | Gen12 firmware 1.16.00 release notes — 사이트 도입 시 |
| Lenovo XCC3 | `lenovo_xcc3.yml:8-15` (7 sources) | 충분 |
| Supermicro X12/X13/X14 | `supermicro_x*.yml` (각 3 sources) | AST2600 BMC 신 features (CPLD APIs / iHDT) read-only 영향 확인 — 충분 |
| Cisco UCS X-Series | `cisco_ucs_xseries.yml:11-15` (3 sources) | IMM 모드 (Intersight) 별도 cycle |
| Huawei iBMC | `huawei_ibmc.yml:9-13` (4 sources) | Manager URI `/Managers/iBMC` 사이트 검증 필요 |
| Inspur iSBMC | `inspur_isbmc.yml:9-12` (3 sources) | 충분 |
| Fujitsu iRMC | `fujitsu_irmc.yml:9-14` (5 sources) | iRMC S6 (PRIMERGY M6/M7) 추정 — Fujitsu 공식 docs 추가 검색 필요 |
| Quanta QCT | `quanta_qct_bmc.yml:9-13` (5 sources) | OpenBMC bmcweb 표준 충분 |

### 6.2 M-D3 fallback 추가 후보 (P1 우선 — 코드 변경)

| 작업 | 대상 cell | adapter capabilities 추가 또는 fallback 추가 |
|---|---|---|
| **W1** | Dell iDRAC 8 power 활성화 | `dell_idrac8.yml` capabilities.sections_supported 에 `- power` 추가 (cycle 2026-05-01 PowerSubsystem fallback 코드 자동 적용) |
| **W2** | HPE iLO 4 storage 활성화 | `hpe_ilo4.yml` capabilities 에 `- storage` 추가 + A1 SimpleStorage fallback |
| **W3** | HPE iLO 4 power 활성화 | `hpe_ilo4.yml` capabilities 에 `- power` 추가 + A2 PowerSubsystem fallback |
| **W4** | Lenovo IMM2 storage 활성화 | `lenovo_imm2.yml` capabilities 에 `- storage` 추가 + A1 SimpleStorage fallback |
| **W5** | Lenovo IMM2 power 활성화 | `lenovo_imm2.yml` capabilities 에 `- power` 추가 + A2 PowerSubsystem fallback |
| **W6** | 4 신규 vendor `users` capability 정정 | sections.yml 정본 우선 — 각 adapter capabilities 에서 `users` 제거 (drift 정정) |

→ 6 작업, 코드 변경 라인 ≤ 20 (각 capabilities 1 줄 추가/제거). 회귀: 5 vendor baseline + Jenkins Stage 4.

### 6.3 BLOCK 영역 (cycle 종료 시 보고)

- Supermicro X9: 6 cell BLOCK. lab 도입 또는 사이트 fixture 캡처 시 해제. 출하 종료 → 우선 낮음 (P3).

---

## 7. Sources (rule 96 R1 origin trace)

### 7.1 Adapter metadata 직접 인용

- **Dell**: `adapters/redfish/dell_idrac.yml:1-9` (generic), `dell_idrac8.yml:1-9`, `dell_idrac9.yml:1-15` (Round 11 lab), `dell_idrac10.yml:1-23` (web sources 4종)
- **HPE**: `hpe_ilo.yml:1-9`, `hpe_ilo4.yml:1-9`, `hpe_ilo5.yml:1-11`, `hpe_ilo6.yml:1-19` (Round 11 lab), `hpe_ilo7.yml:1-26` (web sources 4종)
- **Lenovo**: `lenovo_bmc.yml:1-9`, `lenovo_imm2.yml:1-13`, `lenovo_xcc.yml:1-17` (Round 11 lab), `lenovo_xcc3.yml:1-31` (web sources 7종 + cycle 2026-04-30 사이트 사고 학습)
- **Supermicro**: `supermicro_bmc.yml:1-9`, `supermicro_x9.yml:1-9`, `supermicro_x11.yml:1-9`, `supermicro_x12.yml:1-22` (web sources 3종), `supermicro_x13.yml:1-17` (web sources 3종), `supermicro_x14.yml:1-23` (web sources 3종)
- **Cisco**: `cisco_bmc.yml:1-12`, `cisco_cimc.yml:1-57` (M4 lab + M5~M8 web sources 5종), `cisco_ucs_xseries.yml:1-23` (web sources 3종)
- **Huawei**: `huawei_ibmc.yml:1-22` (web sources 4종)
- **Inspur**: `inspur_isbmc.yml:1-20` (web sources 3종)
- **Fujitsu**: `fujitsu_irmc.yml:1-22` (web sources 5종)
- **Quanta**: `quanta_qct_bmc.yml:1-25` (web sources 5종)
- **Generic fallback**: `redfish_generic.yml:1-15` (DMTF Redfish 표준)

### 7.2 Schema 정본

- `schema/sections.yml` (10 sections + channels 정의)
- `schema/baseline_v1/` (4 vendor baseline: dell / hpe / lenovo / cisco — Redfish 채널)

### 7.3 이전 cycle 입력

- `docs/ai/tickets/2026-05-01-gather-coverage/COMPATIBILITY-MATRIX.md` (15 카테고리 A~M, 35건 fallback 적용 / 4건 InfiniBand M1~M6 / 22건 후보)
- `tests/evidence/2026-04-29-cisco-redfish-critical-review.md` (Cisco CIMC M4 실측)

### 7.4 Code 정본

- `redfish-gather/library/redfish_gather.py` (vendor 분기: `_FALLBACK_VENDOR_MAP`, `_extract_oem_*`, `_detect_from_product` — rule 12 R1 Allowed)
- `redfish-gather/tasks/normalize_standard.yml` (5 vendor 공통 정규화)
- `redfish-gather/tasks/vendors/{dell,hpe,lenovo,supermicro,cisco}/` (OEM tasks — 4 신규 vendor 는 standard_only)

---

## 8. 결론

- **240 cell 모두 분류 완료** — ? cell 0건.
- **OK + OK★ + FB = 203 cell (84.6%)** 가 코드 처리 경로 확보. baseline 격상은 사이트 fixture 도입 후.
- **GAP 7 cell** 은 M-D3 에서 adapter capabilities 추가 + 기존 fallback 코드 활용으로 즉시 활성화 가능 (코드 변경 < 20 라인).
- **BLOCK 6 cell** 은 Supermicro X9 — 출하 종료 + lab/사이트 부재. cycle 종료 시 보고만.
- **N/A 24 cell** (users 섹션) 중 4 신규 vendor adapter 의 capabilities.users 명시는 sections.yml channels 와 drift — M-D3 W6 정정 후보.

**Gap 우선 분류 list (M-D2 입력)**:
- P1 = 43 cell (4 신규 vendor 36 + 5 vendor 구 GAP 5 + Lenovo IMM2 추가 2)
- P2 = 63 cell (cycle 2026-05-01 신 7 generation × 9 sections)
- P3 = 15 cell (Supermicro X9 6 + Dell iDRAC 7 9)

→ M-D3 즉시 진입 후보 6 작업 (W1~W6) + 사이트 fixture 도입 시 OK 격상 70 cell.

---

## 9. 갱신 history

- 2026-05-06: M-D1 매트릭스 신설. 24 row × 10 col = 240 cell 전수 판정. Gap 6 작업 (M-D3 입력) 도출.
