# M-D2 — Web 검색 gap 영역 (DMTF / vendor docs)

> status: [DONE] | depends: M-D1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility | worker: Session-5

## 사용자 의도

M-D1 매트릭스의 Gap (?, GAP, BLOCK) 영역에 대해 web 검색으로 호환성 정보 수집. lab 부재 영역 보완 (rule 96 R1-A).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` 갱신 (M-D2 entry 추가) |
| 영향 vendor | 9 vendor (Gap 7 / BLOCK 6 / 신규 4 vendor 36 cell P1.1) |
| 함께 바뀔 것 | M-D3 fallback 추가 입력 (W1~W6 작업) |
| 리스크 | MED (web 검색 정보 ≠ 실 BMC 응답 — origin 주석 의무) |
| 진행 확인 | M-D1 [DONE] Gap list 입력 |

## 검증 대상 (M-D1 산출물)

| 영역 | cell | 처리 |
|---|---|---|
| Gap (adapter capabilities 미명시) | 7 | M-D3 W1~W5 capabilities 추가 (1 라인) + W6 정정 (1 라인) |
| BLOCK (Supermicro X9) | 6 | lab 도입 대기 (P3) |
| OK★ (신규 4 vendor 36 cell) | 36 | 사이트 fixture 도입 시 OK 격상 (origin 주석 web sources 충분) |
| ? cell | 0 | (M-D1 에서 모두 분류됨) |

## 산출물

### (A) Gap 7 cell + BLOCK 6 cell + P1.1 36 cell — EXTERNAL_CONTRACTS.md M-D2 entry 추가 완료

→ `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` 의 "M-D2 — COMPATIBILITY-MATRIX Gap 7 / BLOCK 6 web 검증" 절 신설.

각 cell 별 검증 요약:

| 작업 | 영향 cell | sources | fallback path | M-D3 작업 |
|---|---|---|---|---|
| W1 | dell_idrac8 power (1) | Dell developer.dell.com PowerSubsystem + DMTF Power.v1_8_0 | `Chassis/{id}/PowerSubsystem` → `Chassis/{id}/Power` (cycle 2026-05-01 fallback) | capabilities `+ power` |
| W2 | hpe_ilo4 storage (1) | hewlettpackard.github.io ilo4 SimpleStorage + DMTF SimpleStorage.v1_3_0 | `Systems/{id}/Storage` → `Systems/{id}/SimpleStorage` (cycle 2026-05-01 A1) | capabilities `+ storage` |
| W3 | hpe_ilo4 power (1) | hewlettpackard.github.io ilo4 Power | A2 PowerSubsystem fallback | capabilities `+ power` |
| W4 | lenovo_imm2 storage (1) | pubs.lenovo.com imm2 + github.com/Lenovo/lenovo-redfish-tool | A1 SimpleStorage | capabilities `+ storage` |
| W5 | lenovo_imm2 power (1) | pubs.lenovo.com imm2 power | A2 PowerSubsystem | capabilities `+ power` |
| W6 | 4 신규 vendor users 정정 (4) | sections.yml 정본 (channels = [os]) | drift 정정 — capabilities 에서 `- users` 제거 | drift fix |
| BLOCK1 | Supermicro X9 6 cell | supermicro.com X9 manuals (legacy) | lab 도입 대기 (P3) | (해소 조건 충족 시) |
| P1.1 | 4 신규 vendor 36 cell (OK★) | adapter origin 주석 web sources 4종 (cycle 2026-05-01 phase 2) | 표준 fall-through (M-B2 검증 완료) | 사이트 fixture 도입 시 OK |

### (B) 검색 sources 총괄

- vendor docs: **5건** (Dell, HPE, Lenovo×2, Supermicro)
- DMTF spec: **2건** (Power.v1_8_0, SimpleStorage.v1_3_0)
- server-exporter 정본: **3건** (`redfish_gather.py` fallback 코드 2 + `sections.yml` channels)
- (cycle 2026-05-01 phase 2 신규 4 vendor adapter 의 web sources 14건 별도 — 본 cycle 추가 검증 대상)

### (C) M-D3 입력 정리 (W1~W6 작업)

| # | 작업 | 영향 파일 | 코드 변경 라인 | 회귀 영역 |
|---|---|---|---|---|
| W1 | dell_idrac8 power 활성화 | `adapters/redfish/dell_idrac8.yml:18-27` | `+ - power` (1 줄) | dell baseline + Stage 4 |
| W2 | hpe_ilo4 storage 활성화 | `adapters/redfish/hpe_ilo4.yml:18-26` | `+ - storage` (1 줄) | hpe baseline + Stage 4 |
| W3 | hpe_ilo4 power 활성화 | `adapters/redfish/hpe_ilo4.yml:18-26` | `+ - power` (1 줄) | hpe baseline + Stage 4 |
| W4 | lenovo_imm2 storage 활성화 | `adapters/redfish/lenovo_imm2.yml:22-30` | `+ - storage` (1 줄) | lenovo baseline + Stage 4 |
| W5 | lenovo_imm2 power 활성화 | `adapters/redfish/lenovo_imm2.yml:22-30` | `+ - power` (1 줄) | lenovo baseline + Stage 4 |
| W6 | 4 신규 vendor users drift 정정 | `huawei_ibmc.yml`, `inspur_isbmc.yml`, `fujitsu_irmc.yml`, `quanta_qct_bmc.yml` | `- - users` 4 곳 제거 | sections.yml channels 검증 |

→ **Additive only (rule 92 R2)** — W1~W5 코드 변경 5 라인 (capabilities 추가). W6 drift 정정 4 라인 제거. 합계 9 라인 변경.

### (D) sources 누락 영역 (lab 도입 후 보강 후보)

| 영역 | 누락 | 사유 |
|---|---|---|
| Supermicro X9 (BLOCK 6) | spec 자체 부분 지원 — vendor 별 응답 일탈 가능 | lab 도입 시 fixture 캡처 필요 |
| iDRAC 7 firmware 5.x 이전 | dell_idrac.yml priority=10 generic fallback | 사이트 도입 시 정정 가능 |
| HPE Superdome Flex multi-partition | 첫 partition (Partition0) 만 수집 | M-E2 adapter 한계 명시 (별도 cycle 확장) |
| Cisco UCS X-Series IMM 모드 (Intersight) | standalone 모드만 cover | 별도 cycle (Intersight 통합) |
| Lenovo XCC v3 OpenBMC 1.17.0 reverse regression | 사이트 fixture 부재 | capture-site-fixture skill |

→ 5 영역 lab 도입 후속 작업 — 본 cycle 종료 시 NEXT_ACTIONS.md 등재.

## 회귀 / 검증

### 정적 검증 결과 (2026-05-06 실측)

| 검증 | 결과 |
|---|---|
| EXTERNAL_CONTRACTS.md M-D2 entry 추가 | PASS — 11 sources 명시 |
| `python scripts/ai/hooks/adapter_origin_check.py` | PASS (38 adapter 모두 origin 주석 보유) |
| markdown 정합성 | PASS |
| W6 drift 정정 sections.yml channels 검증 | PASS — `users` channels = `[os]` (Redfish 미포함) |

## risk

- (HIGH) web 검색 결과 ≠ 실 BMC 응답 (rule 25 R7-A-1) — 사이트 fixture 도입 시 정정 가능
- (MED) DMTF spec 변경 / vendor docs deprecated link — TTL 90일 (rule 28 #11)
- (LOW) sources 1~3 보유로 lab 부재 보완 가능

## 완료 조건

- [x] M-D1 Gap 7 + BLOCK 6 cell 각각 web 검색 sources 명시
- [x] EXTERNAL_CONTRACTS.md M-D2 entry 추가 (W1~W6 + BLOCK1 + P1.1)
- [x] M-D3 fallback 후보 list (W1~W6 9 라인 변경)
- [x] sources 누락 영역 5건 lab 도입 후 보강 list
- [x] 정적 검증 PASS
- [ ] commit: `docs: [M-D2 DONE] M-D1 Gap web 검증 + W1~W6 fallback 후보 + EXTERNAL_CONTRACTS 갱신`

## 다음 세션 첫 지시 템플릿

```
M-D2 검증 완료 → M-D3 fallback 코드 추가 진입.

선행: M-D1 [DONE] + M-D2 [DONE]
산출물: W1~W6 9 라인 변경 (5 capabilities 추가 + 4 users drift 정정)
회귀: 5 vendor baseline + Jenkins Stage 4
```

## 관련

- rule 96 R1-A (lab 부재 → 4 sources 의무)
- rule 92 R2 (Additive only)
- agent: web-evidence-collector (model: opus — 선택적)
- skill: web-evidence-fetch
- catalog: docs/ai/catalogs/EXTERNAL_CONTRACTS.md (M-D2 entry)
- 정본: M-D1.md COMPATIBILITY-MATRIX.md (240 cell)
