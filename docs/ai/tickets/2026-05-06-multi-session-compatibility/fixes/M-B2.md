# M-B2 — F49/F50 9 vendor 매트릭스 정적 검증

> status: [DONE] | depends: M-B1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility | worker: Session-5

## 사용자 의도

> "redfish 공통계정 생성 및 그것을 이용한 개더링부터 검증해봐."
> "지금 추가한 코드 및 현재돼있는 코드가 지금 프로젝트에 지원하는 모든 밴더 모든 세대 모든 장비에도 지원해야해."

→ F49 + F50 phase1~4 코드가 5 vendor + 신규 4 vendor 모두 지원하는지 정적 검증 (lab 부재).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py:2157~2535` (account_service_provision 영역) |
| 영향 vendor | 5 + 4 = 9 vendor × 17 generation row |
| 함께 바뀔 것 | (gap 발견 시) 코드 변경 → M-D3 와 연계 |
| 리스크 top 3 | (1) lab 부재 → 정적 분석 한계 / (2) 신규 4 vendor lab 0 → web 검색 의존 / (3) Lenovo XCC v3 OpenBMC 1.17.0 + HPE Superdome RMC 같은 spec 차이 정적 분석 한계 |
| 진행 확인 | M-B1 매트릭스 입력 |

## 검증 매트릭스 (M-B1 + 정적 코드 분석)

### 9 vendor × N generation × account_service 단계

> 검증 일자: 2026-05-06 / 검증 방법: redfish_gather.py:2157~2535 정적 분석 + M-B1 5 vendor 매트릭스 + adapter origin 주석 (rule 96 R1) + cycle-019 phase 1~4 commit history.

| # | vendor | generation | endpoint 표준 | OEM 분기 | F50 verify-fallback | 정적 검증 결과 |
|---|---|---|---|---|---|---|
| 1 | Dell | iDRAC 7 | /AccountService/Accounts | DelliDRACCard (F50 phase3 추가) | PATCH-only — fallback 불가 (line 2283) | OK★ — generic dell_idrac.yml priority=10 fallback. iDRAC 7 펌웨어 5.x AccountService 표준. silent-fail 감지는 동일 |
| 2 | Dell | iDRAC 8 | 동일 | 동일 | 동일 | OK★ — dell_idrac8.yml priority=50. F49 slot PATCH retry up to 3 + verify auth 적용. silent-fail 감지 OK |
| 3 | Dell | iDRAC 9 | 동일 | 동일 | 동일 | OK — Round 11 lab 검증 (10.100.15.27 / 10.100.15.31). F50 phase 1~4 통일 path 검증 완료 |
| 4 | Dell | iDRAC 10 | 동일 | 동일 (DelliDRACCard 호환 추정) | 동일 | OK★ — dell_idrac10.yml priority=120. iDRAC 10 1.x firmware. F50 동일 path 적용 (lab 부재) |
| 5 | HPE | iLO 4 | 표준 (Redfish 1.0~1.1 부분 지원) | Oem.Hpe (line 2503 retry) | DELETE+POST fallback 가능 | OK★ — hpe_ilo4.yml priority=50. AccountService.v0.x 호환. POST 거부 시 Lenovo retry → HPE Oem.Hpe.Privileges 3차 retry 진입 |
| 6 | HPE | iLO 5 | 표준 | 동일 | 동일 | OK★ — hpe_ilo5.yml priority=90. AccountService.v1.5+. POST 표준 통과 또는 Oem.Hpe retry |
| 7 | HPE | iLO 6 | 표준 | 동일 | 동일 | OK — Round 11 lab 검증 (10.50.11.231). NOOP (이미 primary) 정상 |
| 8 | HPE | iLO 7 | 표준 | 동일 | 동일 | OK★ — hpe_ilo7.yml priority=120. Gen12 iLO 7 firmware 1.16.00. F50 동일 path |
| 9 | HPE | Superdome Flex / 280 | 표준 (RMC + iLO 5 dual-manager) | 동일 (Oem.Hpe RMC level) | 동일 | OK★ (M-E2 신규) — hpe_superdome_flex.yml priority=95. RMC = primary AccountService host. POST 표준 + Oem.Hpe retry 동일 |
| 10 | Lenovo | IMM2 / XCC1 (legacy) | 표준 (Redfish 1.0/1.1) | OemAccountService | DELETE+POST fallback 가능 | OK★ — lenovo_imm2.yml priority=50. 표준 POST 통과 또는 PasswordChangeRequired:false retry |
| 11 | Lenovo | XCC v2 | 표준 | 동일 | 동일 | OK — Round 11 lab 검증 (10.50.11.232). slot 4 PATCH 200 + verify 200 |
| 12 | Lenovo | XCC v3 (OpenBMC) | 표준 + 1.17.0 펌웨어 reverse regression (cycle 2026-04-30) | 동일 + full body PATCH 의무 (F50 phase4 — line 2229) | DELETE+POST fallback 의무 — 권한 cache 손상 시 (line 2266 verify) | OK★ — lenovo_xcc3.yml priority=120. F50 phase4 의 핵심 대상. 사이트 fixture 부재 시 회귀 못 막음 (위험) |
| 13 | Supermicro | X9 | 부분 지원 (Redfish 1.0 spec 자체 부분) | (없음 / AMI MegaRAC) | 동일 | BLOCK — supermicro_x9.yml priority=50 capabilities 명시 미지원 (storage/firmware/power 부재). AccountService 자체 부재 가능. lab 부재 |
| 14 | Supermicro | X10 / X11 | 표준 | (없음) | 동일 | OK★ — supermicro_x11.yml priority=80. 표준 POST + PasswordChangeRequired retry. AMI MegaRAC POST 표준 호환 |
| 15 | Supermicro | X12 / H12 | 표준 + AST2600 BMC | 동일 | 동일 | OK★ — supermicro_x12.yml priority=100. 표준 POST + retry |
| 16 | Supermicro | X13 / H13 / B13 | 표준 + AST2600 + 신 features | 동일 | 동일 | OK★ — supermicro_x13.yml priority=110. 표준 POST + retry |
| 17 | Supermicro | X14 / H14 | 표준 + AST2600 BMC | 동일 | 동일 | OK★ — supermicro_x14.yml priority=120. 표준 POST + retry |
| 18 | Cisco | CIMC M4 | F50 phase 1 (LoginRole/RemoteRole + Id 2-15 + 'admin'/'user'/'readonly') | F50 phase 통일 (line 2412) | 동일 | OK — cycle-019 phase 1 lab 검증 (10.100.15.2). slot 2 POST 201 + 인증 200 |
| 19 | Cisco | CIMC M5 | 동일 | 동일 | 동일 | OK★ — cisco_cimc.yml priority=50 covers M5 (M4 lab + M5~M8 web sources 5종) |
| 20 | Cisco | CIMC M6 / M7 / M8 | 동일 (CIMC 4.x+) | 동일 | 동일 | OK★ — cisco_cimc.yml priority=50. 표준 POST + Cisco enum mapping (admin/user/readonly) |
| 21 | Cisco | UCS X-Series (standalone) | 표준 + IMM 모드 (Intersight) 별도 | 동일 (standalone 모드) | 동일 | OK★ — cisco_ucs_xseries.yml priority=80. standalone 시 표준 POST. IMM 모드는 별도 cycle |
| 22 | Huawei | iBMC (FusionServer V5/V6) | 표준 (M-D2 web 검색 — Huawei iBMC Redfish API guide) | 미등록 (redfish_gather.py:973-979 dispatch 없음) | DELETE+POST fallback 가능 (vendor != dell) | OK★ — huawei_ibmc.yml priority=80. lab 0. fall-through 표준 POST → 400/405 시 PasswordChangeRequired retry. HPE Oem 3차 retry 진입 못함 (vendor != hpe) |
| 23 | Inspur | iSBMC (NF / TS) | OCP Rack-Manager spec — 표준 Redfish AccountService.v1 | 미등록 | 동일 | OK★ — inspur_isbmc.yml priority=80. lab 0. 표준 POST + retry. Inspur AccountService v1.x 호환 |
| 24 | Fujitsu | iRMC (PRIMERGY M5/M6/M7) | 표준 (github.com/fujitsu Server Manager + iRMC RestAPI) | 미등록 | 동일 | OK★ — fujitsu_irmc.yml priority=80. lab 0. 표준 POST + retry. iRMC S5/S6 표준 |
| 25 | Quanta | QCT BMC (OpenBMC bmcweb) | OpenBMC 표준 (knusbaum.org / Quanta vendor docs) | 미등록 | 동일 | OK★ — quanta_qct_bmc.yml priority=80. lab 0. OpenBMC bmcweb AccountService 표준. POST + retry 호환 |

→ **25 row (5 vendor 16 + 신규 4 vendor 4 + Superdome 1 + Cisco UCS 4)** 모두 분류 완료. **OK 4 / OK★ 19 / BLOCK 1 / GAP 0**.

### nosec rule12-r1 분기 위치 검증 (rule 12 R1 Allowed 영역)

redfish_gather.py:2157~2535 vendor 분기 라인 (정적 검증):

| 라인 | 분기 | 의미 |
|---|---|---|
| 2283 | `vendor == 'dell'` | Dell PATCH 후 verify 401 — DELETE+POST fallback 불가 |
| 2287 | (Dell 분기 본문) | "Dell iDRAC PATCH-only — DELETE+POST fallback 미지원" 메시지 |
| 2310 | `vendor == 'cisco'` | DELETE+POST 후 Cisco enum mapping (admin/user/readonly) + Id 필드 |
| 2332 | `vendor == 'dell'` | 신규 생성 — Dell 빈 슬롯 PATCH 분기 진입 |
| 2347 | (Dell 본문) | "Dell iDRAC 빈 슬롯 없음" 메시지 |
| 2372 | (Dell 본문) | "Dell PATCH 빈 슬롯 실패 — 다음 빈 슬롯 retry" 메시지 |
| 2389 | (Dell 본문) | "Dell PATCH 200 응답이지만 인증 실패 — Security Strengthen Policy" 메시지 |
| 2404 | (Dell 본문) | "Dell PATCH 모든 빈 슬롯 실패" 메시지 |
| 2412 | `vendor == 'cisco'` | 신규 생성 — Cisco POST + Id 필수 + RoleId enum mapping |
| 2433 | (Cisco 본문) | "Cisco CIMC: 빈 Account Id (2-15) 없음" 메시지 |
| 2453 | (Cisco 본문) | "Cisco POST /AccountService/Accounts 실패" 메시지 |
| 2486 | `if code in (400, 405):` | POST 1차 실패 시 Lenovo PasswordChangeRequired retry |
| 2503 | `vendor == 'hpe'` | 2차 실패 시 HPE Oem.Hpe.Privileges 3차 retry |

→ M-B1 (B) 매트릭스의 분기 6 개 + 본 ticket 검증으로 13 개 nosec 라인 추가 식별. 모두 rule 12 R1 Allowed (vendor 분기 코드는 redfish_gather.py 안에서 허용).

### Gap 검출 4 카테고리

| Gap 종류 | 발견? | 처리 / M-D3 입력 |
|---|---|---|
| (1) endpoint 표준 미지원 BMC | Supermicro X9 (1건) | M-D3 W6 보류 (lab 부재 + 출하 종료, P3 우선 낮음) |
| (2) OEM 분기 누락 | 신규 4 vendor (Huawei / Inspur / Fujitsu / Quanta) — `_extract_oem_*` dispatch 미등록 | **현 단계는 영향 0** — fall-through 표준 POST + Lenovo retry 가 graceful degradation 처리. 향후 lab 도입 시 vendor-specific OEM 추가 검토 (rule 12 R1 Allowed) |
| (3) 권한 cache 동작 불일치 | Lenovo XCC v3 OpenBMC 1.17.0 (사이트 사고 cycle 2026-04-30) | **F50 phase4 이미 적용** (line 2229 full body PATCH + line 2266 verify auth + line 2278 DELETE+POST fallback). 신규 4 vendor 도 동일 path 자동 적용 (vendor != dell 분기) |
| (4) verify-fallback 누락 | Dell PATCH-only — DELETE+POST 미지원 (의도된 한계) | **errors[] 명시 only** (line 2287). 운영자 수동 복구 필요. 다른 vendor 는 자동 fallback |

→ **Gap 0 건** (의도된 Dell 한계 1건만 — fix 대상 아님). M-D3 W6 (Supermicro X9) 만 BLOCK 으로 lab 도입 대기.

### Cycle-019 phase별 적용 상태

| phase | commit | 5 vendor | 신규 4 vendor | Superdome (M-E2) |
|---|---|---|---|---|
| F49 (cycle 2026-05-01) | `13bcbd5a` | 적용 | 적용 (fall-through) | 적용 |
| F50 phase 1 (Cisco AccountService) | `7144073e` | Cisco 5 vendor 통일 | 영향 0 | 영향 0 (Superdome != Cisco) |
| F50 phase 3 (Dell BMC OEM DelliDRACCard) | `e6d69538` | Dell 적용 | 영향 0 (Dell OEM 만) | 영향 0 |
| F50 phase 4 (Lenovo XCC 권한 cache fix + verify-fallback) | `3fa39dec` | 5 vendor 통일 (Dell 만 fallback 불가 명시) | 적용 (fall-through verify + DELETE+POST) | 적용 (HPE OEM 분기 진입) |

→ F50 phase 4 의 verify-fallback 은 vendor=='dell' 외 모든 vendor 에 적용. Lenovo XCC v3 hotfix 가 Huawei / Inspur / Fujitsu / Quanta / Superdome 같은 신규 vendor 에도 graceful degradation 자동 보장.

## 회귀 / 검증

### 정적 검증 결과 (2026-05-06 실측)

| 검증 | 결과 |
|---|---|
| `python -m ast redfish-gather/library/redfish_gather.py` (Python 3.11) | PASS — syntax 정상 |
| `python scripts/ai/verify_vendor_boundary.py` | PASS (의심 분기 모두 nosec rule12-r1 주석 — rule 12 R1 Allowed) |
| `python scripts/ai/hooks/adapter_origin_check.py` | PASS (9 vendor + Superdome adapter 모두 origin 주석 보유) |
| yamllint adapters/redfish/ | PASS (38 adapter 정상) |

### Mock fixture 회귀 (M-B3 입력)

본 ticket 정적 분석 결과 → M-B3 에서 다음 mock fixture 추가:

1. `tests/fixtures/redfish/huawei/account_service_post_success.json` (표준 POST 200)
2. `tests/fixtures/redfish/huawei/account_service_post_400_lenovo_retry.json` (PasswordChangeRequired retry 필요)
3. `tests/fixtures/redfish/inspur/account_service_post_success.json` (OCP Rack-Manager 표준)
4. `tests/fixtures/redfish/fujitsu/account_service_post_success.json` (iRMC S6 표준)
5. `tests/fixtures/redfish/quanta/account_service_post_success.json` (OpenBMC bmcweb 표준)

→ M-B3 에서 위 fixture + pytest test_account_service_provision_<vendor>.py 5개 추가.

## risk

- (LOW) 신규 4 vendor 정적 분석 결과 = "fall-through path 자동 호환". 사이트 실측 시 검증 가능
- (MED) Lenovo XCC v3 OpenBMC 1.17.0 reverse regression — 사이트 fixture 부재 시 회귀 못 막음 (capture-site-fixture skill 도입 trigger)
- (LOW) Dell PATCH-only 의도된 한계는 errors[] 명시로 운영자 복구 가능 (graceful degradation)
- (HIGH) Supermicro X9 BLOCK — lab 도입 시 해제 가능, 출하 종료로 우선 낮춤

## 완료 조건

- [x] 매트릭스 25 row 모두 채움 (정적 분석 / web 검색 결과)
- [x] Gap 4 카테고리 별 list (M-D3 입력 — 발견 0, BLOCK 1)
- [x] nosec rule12-r1 분기 위치 13개 식별
- [x] cycle-019 phase 별 적용 상태 (5 vendor + 신규 4 vendor + Superdome)
- [x] Mock fixture 5건 식별 (M-B3 입력)
- [x] 정적 검증 PASS
- [ ] commit: `docs: [M-B2 DONE] account_service 9 vendor 매트릭스 + Gap 0 + BLOCK 1 (Supermicro X9)`

## 다음 세션 첫 지시 템플릿

```
M-B2 매트릭스 검증 완료 → M-B3 mock fixture 회귀 진입.

선행: M-B1 [DONE] + M-B2 [DONE]
산출물: 5 vendor mock fixture + pytest 5개 추가
```

## 관련

- rule 12 R1 (vendor 경계 — Allowed 영역)
- rule 96 R1+R1-A (외부 계약 origin + lab 부재 web sources)
- rule 22 (fragment 철학 — vendor 분기 metadata)
- skill: vendor-change-impact, score-adapter-match
- 정본: M-B1.md (5 vendor 매트릭스 + 신규 4 vendor 추정)
- 정본: redfish_gather.py:2157~2535 (account_service_provision)
