# 호환성 매트릭스 (Compatibility Matrix)

> **이 문서는** server-exporter 가 어떤 벤더 / 어떤 세대 / 어떤 섹션을 어디까지 지원하는지를 한 장 표로 정리한 reference 다.
>
> 호출자 / 신규 작업자가 "Dell iDRAC 8 세대도 storage 수집 되는가?" 같은 질문을 빠르게 해소할 때 본다.
> 9개 벤더 × 여러 세대 × 10 섹션 조합 (총 240 셀 규모) 을 한눈에 비교할 수 있다.
>
> 매트릭스는 어댑터의 `capabilities` 와 실장비 baseline 결과를 기준으로 작성된다.

## 1. 목적

server-exporter 가 지원하는 vendor / generation / section 호환성을 한 장 매트릭스로 추적. 호출자 / 다음 작업자 / 다음 cycle 진입자가 lookup reference 로 사용.

호환성 매트릭스 입력:
- `adapters/redfish/{vendor}_*.yml` 의 `capabilities.sections_supported`
- `schema/baseline_v1/{vendor}_baseline.json` (실장비 검증 후)
- `tests/evidence/<날짜>-<vendor>.md` (Round 검증)
- web sources (rule 96 R1-A) — lab 부재 영역

## 2. 판정 기호

| 기호 | 의미 |
|---|---|
| `OK` | adapter `capabilities.sections_supported` 명시 + 코드 처리 + baseline 확보 (lab tested) |
| `OK★` | adapter `capabilities.sections_supported` 명시 + 코드 처리. baseline 부재 (mock 회귀 / web sources 기반 가정) |
| `FB` | fallback 적용 — cycle 2026-04-30 / 2026-05-01 호환성 fallback 코드 있음 |
| `GAP` | 명시적 미지원 — adapter `capabilities.sections_supported` 에서 누락 — fallback 추가 후보 |
| `BLOCK` | 외부 의존 (lab fixture / 실장비 / 사이트 사고 재현) |
| `N/A` | 해당 채널에 해당 section 없음 (sections.yml channels 정의 기준) |
| `?` | 미확인 — adapter 명시 부재 + spec 불명확. web sources 검색 대상 |

## 3. 매트릭스 (Redfish 단독 — 24 row × 10 col = 240 cell)

> OS / ESXi 채널은 별도. `users` 섹션은 sections.yml channels=[os] — Redfish 채널에서는 모든 vendor / 모든 generation 공통 N/A.

cycle 2026-05-06 M-D1 매트릭스 (정본 — `docs/ai/tickets/2026-05-06-multi-session-compatibility/COMPATIBILITY-MATRIX.md`):

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

## 4. Cell 분포 집계 (cycle 2026-05-06 M-D1 시점)

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

→ baseline 보유 vendor (lab tested): Dell iDRAC9 / HPE iLO6 / Lenovo XCC v2 / Cisco CIMC M4 (4 vendor × 9 sections = 27 cell + ESXi/OS baseline 4종 별도).

## 5. lab 부재 영역 식별 (rule 50 R2 단계 10 + rule 96 R1-A)

| 영역 | 부재 사유 | 보완 |
|---|---|---|
| Dell iDRAC 7 (9 FB cell) | EOL 펌웨어 | cycle 2026-05-01 P1 fallback 적용 |
| Dell iDRAC 8 (1 GAP — power) | iDRAC 8 power schema 불명확 | adapter capabilities 추가 후보 |
| HPE iLO 4 (2 GAP) | EOL 펌웨어 / partial PowerSubsystem | adapter capabilities 추가 후보 |
| Lenovo XCC1 (2 GAP) | legacy IMM2 | XCC1 generation 명시 + fallback 추가 |
| Supermicro X9 (6 BLOCK) | EOL 펌웨어 + lab fixture 부재 | NEXT_ACTIONS 등재 (lab 도입 cycle) |
| Supermicro X9 (3 GAP) | OEM 미지원 generation | adapter capabilities 추가 후보 |
| 신규 4 vendor (Huawei/Inspur/Fujitsu/Quanta) | lab 부재 + vault SKIP | rule 96 R1-A web sources + NEXT_ACTIONS 등재 |
| HPE Superdome Flex | lab 부재 + sub-line | adapter `hpe_superdome_flex.yml` priority=95 + web sources 14건 |

## 6. 갱신 절차

### 6.1 매트릭스 갱신 trigger (rule 28 #12)

| trigger | 갱신 위치 |
|---|---|
| `adapters/**/*.yml` capabilities 변경 | 본 docs/22 + cycle ticket COMPATIBILITY-MATRIX.md |
| 새 vendor 추가 (rule 50 R2) | 새 row 추가 |
| 펌웨어 업그레이드 (lab tested) | 해당 cell `OK★` → `OK` 격상 |
| `schema/sections.yml` 변경 (sections 10 영향) | column 수정 |
| `schema/baseline_v1/{vendor}_baseline.json` 추가 | 해당 row `OK★` → `OK` 격상 |

TTL 14일 — `scripts/ai/measure_compatibility_matrix.py` (P3 도입 예정) 자동 측정.

### 6.2 cycle 진입 시 매트릭스 read

cycle-orchestrator skill Phase 1 (분석 단계) 에서 본 docs/22 read → 영역별 GAP / BLOCK / FB cell 식별 → 영향 vendor / 영향 ticket 도출.

### 6.3 cell 격상 / 격하 절차

- `OK★` → `OK`: 실장비 검증 (rule 13 R4) 후 baseline 추가 (`schema/baseline_v1/{vendor}_baseline.json`)
- `GAP` → `FB`: cycle 호환성 fix 적용 (rule 92 R2 Additive 검증 절차)
- `BLOCK` → `OK★`: lab fixture 도입 (`capture-site-fixture` skill) + adapter capabilities 명시
- `?` → `OK★` / `GAP`: web sources (rule 96 R1-A) 로 명시 또는 미지원 결정

## 7. 호환성 fix 적용 history (cycle 별)

| cycle | fix 영역 | cell 변화 |
|---|---|---|
| cycle 2026-04-30 | F40 power Members[0] 단일 진입 | Lenovo XCC v3 power `?` → `OK★` |
| cycle 2026-05-01 | P1 22건 일괄 (신 generation BMC 7종 + 호환성 fallback) | iDRAC 7 / iDRAC 10 / iLO 7 / XCC v3 / X12-X14 / UCS X-Series — 모두 신규 row 추가 |
| cycle 2026-05-01 | F44~F47 신규 4 vendor | Huawei / Inspur / Fujitsu / Quanta — 모두 신규 row 추가 |
| cycle 2026-05-01 | F50 phase4 Lenovo XCC 권한 cache fix | XCC v3 auth recovery `BLOCK` → `OK★` |
| cycle 2026-05-06 | M-D2 W1~W6 9 라인 (Additive only) | (cell 불변 — 기존 path 유지 + 새 fallback path 추가) |
| cycle 2026-05-06 | M-E hpe_superdome_flex | 신규 row (HPE sub-line) |

## 8. 관련 문서

| 문서 | 용도 |
|---|---|
| `rule 28 #12` | COMPATIBILITY-MATRIX TTL 14일 정본 |
| `rule 50 R2 + 단계 10` | vendor 추가 9단계 + lab 부재 NEXT_ACTIONS |
| `rule 96 R1-A / R1-C` | web sources 의무 / lab 부재 NEXT_ACTIONS 자동 등록 |
| `skill: cycle-orchestrator` | Phase 1 매트릭스 read |
| `skill: add-vendor-no-lab` | lab 부재 vendor 추가 |
| `script: scripts/ai/measure_compatibility_matrix.py` | P3 자동 측정 (예정) |
| `docs/10_adapter-system.md` | Adapter 시스템 (점수 / capabilities) |
| `docs/13_redfish-live-validation.md` | Round 검증 (lab tested 격상 trigger) |
| `docs/14_add-new-gather.md` | gather 추가 일반 |
| `docs/19_decision-log.md` | 의사결정 trace |
| `docs/20_json-schema-fields.md` | envelope / sections / field_dictionary 정본 |
| `docs/21_vault-operations.md` | vault 자동 반영 / 회전 |
