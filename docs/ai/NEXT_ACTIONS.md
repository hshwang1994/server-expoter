# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-05-06 (post-cycle P2 — pre_commit_docs20_sync_check hook 신설 [DONE])

### 본 phase (M-G1 P2 후보 22건 중 1건 처리)

| 후보 | 상태 | 결과 |
|---|---|---|
| **hook: pre_commit_docs20_sync_check.py** | **[DONE]** | rule 13 R7 advisory hook 신설 — pytest 11 테스트 PASS / self-test 6/6 PASS / install-git-hooks.sh chain 등록 / surface-counts hooks 21→22 |

### 다음 phase 권장 (M-G1 P2 후보 21건 잔존)

순위 (운영 안정화 영향순):
1. `hook: pre_commit_status_logic_check.py` — build_status.yml 변경 시 시나리오 mock (M-A 학습 직접 반영)
2. `hook: pre_commit_ticket_consistency.py` — docs/ai/tickets/ 변경 시 cold-start 6 절 검증 (다음 cycle 자료 보전)
3. `rule 13 R8` — status 로직 변경 시 시나리오 매트릭스 update (M-A 학습 형식화)
4. `skill: verify-status-logic` — M-A 학습 lookup 표준화

### 잔존 후보 (이전 cycle 표 그대로 유지)

다음 21 후보 (rule 8 + skill 5 + agent 1 + hook 4 + docs 2 + script 1):

| 후보 | 우선 | trigger |
|---|---|---|
| rule 26 R10 (다중 worker 4 정본) | P2 | 단일 cycle N-worker 패턴 정착 |
| rule 50 R2 단계 10 (lab 부재 fixture trigger) | P2 | F44~F47 + Superdome lab 도입 후 |
| rule 96 R1-C (lab 부재 NEXT_ACTIONS 자동 등록) | P2 | lab 부재 vendor 추가 후속 |
| rule 13 R8 (status 로직 변경 시 시나리오 매트릭스 update) | P2 | M-A 학습 적용 |
| rule 28 #12 (COMPATIBILITY-MATRIX TTL 14일) | P2 | 매트릭스 자동 측정 도입 시 |
| rule 27 R6 (vault 자동 반영 단서 3개) | P3 | M-C 학습 적용 |
| rule 92 R2 보강 (Additive 검증 절차) | P3 | 운영 안정화 후 |
| skill: cycle-orchestrator | P2 | 다음 cycle orchestration 자동화 |
| skill: add-vendor-no-lab | P2 | lab 부재 vendor 추가 자동화 |
| skill: verify-status-logic | P2 | M-A 학습 |
| skill: rotate-vault 보강 | P3 | M-C 학습 |
| skill: write-cold-start-ticket 보강 | P3 | 본 cycle 24 ticket 라이브러리화 |
| agent: ticket-decomposer | P2 | cycle-orchestrator sub |
| hook: pre_commit_ticket_consistency.py | P2 | docs/ai/tickets/ 변경 시 cold-start 6 절 검증 |
| hook: pre_commit_status_logic_check.py | P2 | build_status.yml 변경 시 시나리오 mock |
| hook: post_commit_compatibility_matrix_check.py | P3 | adapter capabilities 변경 시 매트릭스 advisory |
| hook: pre_commit_additive_only_check.py | P3 | 코드 변경 diff Additive 검증 |
| docs/21_vault-operations.md | P2 | M-C 결과 정본화 |
| docs/22_compatibility-matrix.md | P3 | M-D1 240 cell 정본화 |
| script: scripts/ai/measure_compatibility_matrix.py | P3 | rule 28 #12 측정 자동화 |

### rule 13 R7 재검토 trigger 모니터링

- 본 hook 도입 → advisory 운영 1~2 cycle 관찰
- false-positive 0 / 정본 4종 staged 시 docs/20 동반 의무 100% 준수 확인 시 **blocking 격상** 검토

### lab 도입 후 별도 cycle 권장 (이전 그대로)

(생략 — 이전 entry 동일)

---

## 일자: 2026-05-06 (cycle multi-session-compatibility — Session-5 종료, **24/24 ticket [DONE/SKIP]**)

### cycle 종료 — 23 ticket [DONE] + 1 [SKIP]

| 영역 | 진행 | 결과 |
|---|---|---|
| A. status 로직 | M-A1/A2/A3 [DONE], M-A4 [SKIP] (rule 70 R8 trigger NO) | Case A — 의도 주석 강화 + pytest 13건 추가 |
| B. account_service | M-B1/B2/B3 [DONE] | 9 vendor 매트릭스 + Gap 0 / BLOCK 1 + mock 8건 |
| C. vault 자동 반영 | M-C1/C2/C3 [DONE] | YES (다음 run 부터) — cacheable 0 / fact_caching 0 + mock 9건 |
| D. 호환성 매트릭스 | M-D1/D2/D3/D4 [DONE] | 240 cell 매트릭스 + W1~W6 9 라인 변경 (Additive only) + 회귀 PASS |
| E. Superdome 추가 | M-E1/E2/E3/E4/E5/E6 [DONE] | hpe_superdome_flex.yml (priority=95, lab 부재) + ai-context + boundary-map + docs + 회귀 13건 |
| F. JSON 스키마 docs | M-F1/F2 [DONE] | docs/20 신설 (825 라인) — envelope 13 + sections 10 + field_dictionary 65 + 3채널 비교 |
| G. 하네스 학습 | M-G1/G2 [DONE] | HARNESS-RETROSPECTIVE 8 학습 + rule 13 R7 신설 + ADR + 22 후보 다음 cycle 권장 |

### cycle 통계

- pytest: 108 → **324 PASS** (+30 본 cycle: M-B3 8 + M-C3 9 + M-E6 13)
- adapter: 38 → **39** (+1 hpe_superdome_flex)
- docs/20: 신설 825 라인
- rule: 28 → **28** (R7 신설 1, ADR 작성)
- commit: 11건 (Session-0~5)

### M-G2 P1 적용 완료

- **rule 13 R7 신설**: envelope 정본 변경 시 docs/20 갱신 의무 → **ADR-2026-05-06-rule13-r7-docs20-sync.md** 작성

### M-G1 P2/P3 후속 cycle 권장 (다음 cycle)

다음 22 후보 (rule 8 + skill 5 + agent 1 + hook 5 + docs 2 + script 1):

| 후보 | 우선 | trigger |
|---|---|---|
| rule 26 R10 (다중 worker 4 정본) | P2 | 단일 cycle N-worker 패턴 정착 |
| rule 50 R2 단계 10 (lab 부재 fixture trigger) | P2 | F44~F47 + Superdome lab 도입 후 |
| rule 96 R1-C (lab 부재 NEXT_ACTIONS 자동 등록) | P2 | lab 부재 vendor 추가 후속 |
| rule 13 R8 (status 로직 변경 시 시나리오 매트릭스 update) | P2 | M-A 학습 적용 |
| rule 28 #12 (COMPATIBILITY-MATRIX TTL 14일) | P2 | 매트릭스 자동 측정 도입 시 |
| rule 27 R6 (vault 자동 반영 단서 3개) | P3 | M-C 학습 적용 |
| rule 92 R2 보강 (Additive 검증 절차) | P3 | 운영 안정화 후 |
| skill: cycle-orchestrator | P2 | 다음 cycle orchestration 자동화 |
| skill: add-vendor-no-lab | P2 | lab 부재 vendor 추가 자동화 |
| skill: verify-status-logic | P2 | M-A 학습 |
| skill: rotate-vault 보강 | P3 | M-C 학습 |
| skill: write-cold-start-ticket 보강 | P3 | 본 cycle 24 ticket 라이브러리화 |
| agent: ticket-decomposer | P2 | cycle-orchestrator sub |
| hook: pre_commit_ticket_consistency.py | P2 | docs/ai/tickets/ 변경 시 cold-start 6 절 검증 |
| hook: pre_commit_status_logic_check.py | P2 | build_status.yml 변경 시 시나리오 mock |
| hook: pre_commit_docs20_sync_check.py | P2 | rule 13 R7 자동 검증 |
| hook: post_commit_compatibility_matrix_check.py | P3 | adapter capabilities 변경 시 매트릭스 advisory |
| hook: pre_commit_additive_only_check.py | P3 | 코드 변경 diff Additive 검증 |
| docs/21_vault-operations.md | P2 | M-C 결과 정본화 |
| docs/22_compatibility-matrix.md | P3 | M-D1 240 cell 정본화 |
| script: scripts/ai/measure_compatibility_matrix.py | P3 | rule 28 #12 측정 자동화 |

### lab 도입 후 별도 cycle 권장

1. **사이트 fixture 캡처**: capture-site-fixture skill 적용
   - Supermicro X9 6 cell BLOCK 해소
   - Lenovo XCC v3 OpenBMC 1.17.0 reverse regression fixture
   - Superdome Flex multi-partition 전수 수집 (Systems Members[0] 단일 진입 패턴 확장)
   - 신규 4 vendor 사이트 실측 fixture (Huawei/Inspur/Fujitsu/Quanta)
2. **자동화 cycle**: rule 28 #12 + COMPATIBILITY-MATRIX 자동 측정 도구
3. **호출자 계약 안정성**: docs/20 정본화 후 호출자 시스템 통합 가이드

### 이전 cycle 작업 (참고)

## 일자: 2026-05-06 (cycle multi-session-compatibility — Session-0 ticket 작성 완료)

### 본 phase 완료 (Session-0 = 메인 오케스트레이터)

사용자 명시 (2026-05-06):
> "lab 접속 가능 장비 없음 → 프로젝트 코드를 모든 vendor / 모든 장비에 호환되도록 작성. 실 검증은 향후. 다른 세션에서 작업하되 모두 상세 티켓화. 누락 0. 세션 간 동기화 가능하게."

- **PROJECT_MAP fingerprint 갱신** (F49/F50 호환성 commit 4건 반영)
- **사용자 9 작업 항목 → 24 ticket 분해** (cold-start 형식, 다음 세션 컨텍스트 0 진입 가능)
- **ticket 디렉터리**: `docs/ai/tickets/2026-05-06-multi-session-compatibility/`
  - INDEX.md (cycle 진입점)
  - SESSION-HANDOFF.md (세션 종료/다음 첫 지시)
  - DEPENDENCIES.md (의존성 그래프 + 진행 가능 ticket 식별)
  - fixes/INDEX.md (24 ticket 분류 + 진행 상태)
  - fixes/M-A1~M-G2.md (24 cold-start ticket)

### 24 ticket 분류

| 영역 | ticket | 사용자 의도 |
|---|---|---|
| **A. status 로직 검증** | M-A1~A4 (4) | "errors 있는데 success" 케이스 — 의도 vs 버그 식별 + 결정 |
| **B. Redfish 공통계정** | M-B1~B3 (3) | F49/F50 5+4 vendor 매트릭스 검증 + 회귀 |
| **C. Vault 자동 반영** | M-C1~C3 (3) | 패스워드 변경 시 자동 반영 메커니즘 검증 + 회귀 |
| **D. 전 vendor 호환성 fallback** | M-D1~D4 (4) | 9 vendor × N gen × 10 sections 매트릭스 240 cell + fallback 추가 |
| **E. HPE Superdome 추가** | M-E1~E6 (6) | rule 50 R2 9단계 + web 검색 (Flex / Flex 280 / 2 / X / Integrity) |
| **F. JSON 스키마 의미 문서** | M-F1~F2 (2) | docs/20_json-schema-fields.md 신설 + 3채널 비교 |
| **G. 하네스 학습** | M-G1~G2 (2) | cycle 학습 추출 + rule/skill/agent/hook 보강 |

### 진행 가능 ticket (worker 세션 즉시 착수)

DEPENDENCIES.md 참조. 의존 없는 6 ticket 동시 진행 가능 (서로 다른 파일 영역):
- M-A1, M-B1, M-C1 (분석 read-only)
- M-D1 (호환성 매트릭스 작성)
- M-E1 (Superdome web 검색)
- M-F1 (docs/20 신설)

### 사용자 결정 필요

| 결정 | ticket | 내용 |
|---|---|---|
| status 로직 의도 | M-A2 | "errors 있는데 success" → success / partial / success_with_warnings ? |
| Superdome 분류 | M-E1 | (a) HPE sub-line / (b) 별도 vendor |
| schema 변경 (있다면) | M-D / M-F | sections.yml + field_dictionary.yml 버전 결정 (rule 92 R5) |

### 외부 의존 (lab 도입 시)

- 모든 ticket 의 실 lab 검증 (mock fixture + 정적 검증으로 본 cycle 종료)
- Round 검증 docs/13_redfish-live-validation.md
- vault 실 회전 검증 (mock 시뮬만 cycle 내 진행)

### 다음 cycle 권장

- **worker 세션 1~6 진입** — DEPENDENCIES.md 의 진행 가능 ticket 부터 병렬
- **Phase 1 (분석 — 6 ticket 동시)** → **Phase 2 (사용자 결정 M-A2)** → **Phase 3 (구현)** → **Phase 4 (회귀)** → **Phase 5 (cycle 종료 M-G1/G2)**
- HARNESS-RETROSPECTIVE.md 작성 (cycle 종료 시 — M-G1 산출물)

---

## 일자: 2026-05-01 (cycle-019 phase 3 — 잔여 ticket 상태 close)

### 본 phase 완료 (사용자 명시 "남은 티켓 모두 수행 / 더이상 작업할게없나")

- **PROJECT_MAP drift 정정** (cycle-015 _grafana 제거 / cycle-019 +11 adapter 반영) — commit `9bf9d196`
- **fixes/INDEX.md status 정정** — F02/F20/F21 [DONE] 정정 (commit 36c40db9 적용 누락 분류)
- **22 호환성 ticket 전수 분류** (정확한 status):
  - **[DONE]**: 9건 (P1 3 + 호환성 일괄 3 + 묶음 3 — 모든 코드 적용 완료)
  - **[VERIFIED-COMPATIBLE]**: 5건 (F01/F10/F12/F34/F35/F40) — 코드 자동 호환
  - **[TRACKING-ONLY]**: 5건 (F09/F16/F17/F24/F41/F42) — 정기 추적
  - **[BLOCKED:lab-fixture]**: 3건 (F04/F15/F38)
  - **[BLOCKED:incident]**: 2건 (F22/F33)
  - **[BY-DESIGN]**: 1건 (F39)
  - **[BLOCKED:rhel10-adoption]**: 1건 (F43)
  - **[BLOCKED:schema-out-of-scope]**: 1건 (F37)
- **결론**: 호환성 ticket 전체 41% (9/22) 코드 적용 완료, 23% (5/22) 자동 호환 검증, 36% (8/22) 외부 의존

### 잔여 (외부 의존 — AI 환경 외)

| 분류 | 건수 | 진입 조건 |
|---|---|---|
| lab fixture 캡처 후 코드 적용 | 3건 (F04/F15/F38) | HPE iLO5 구 펌웨어 / Supermicro X9 / Windows Mellanox WinOF host |
| 사고 재현 후 코드 적용 | 2건 (F22/F33) | WinRM TLS 1.3 / Redfish Session lockout |
| RHEL 10 lab 도입 시 | 1건 (F43) | RHEL 10 운영 도입 결정 |
| schema 신설 결정 | 1건 (F37) | hba_ib 섹션 신설 (호환성 외 영역) |
| 정기 추적 (분기/연간) | 5건 | DMTF release / vendor EOL / CVE / community.vmware / errata |

### 신규 vendor 4종 (F44~F47) 잔여

- **vault 생성** — `vault/redfish/{huawei,inspur,fujitsu,quanta}.yml` (lab/사이트 도입 시 ansible-vault encrypt)
- **baseline 생성** — `schema/baseline_v1/{vendor}_baseline.json` (lab 도입 시)
- **사이트 fixture 캡처** — capture-site-fixture skill (도입 시)
- **OEM tasks** — `redfish-gather/tasks/vendors/{vendor}/` (사이트 fixture 확보 후 OEM extraction 보강)
- **Round 검증** — docs/13_redfish-live-validation.md

### 다음 cycle 권장

- harness-evolution-coordinator 정기 self-improvement (rule 28 측정 11종 drift 검사) — cycle-018 이후 공백
- 사용자 사이트 신 generation BMC 도입 신호 시 → 해당 ticket 즉시 진입

---

## 일자: 2026-05-01 (cycle-019 phase 2 — F44~F47 신규 vendor 4종 도입 완료)

### 본 phase 완료 (사용자 명시 "신규 밴더 추가 승인하겠다")

- **rule 50 R2 9단계 중 1/2/6/7/9 진행** — vault SKIP (사용자 명시 phase 1)
- **adapter 4 신규**: huawei_ibmc / inspur_isbmc / fujitsu_irmc / quanta_qct_bmc (priority=80, lab 부재)
- **vendor_aliases / _FALLBACK_VENDOR_MAP / _BMC_PRODUCT_HINTS / bmc_names** 동기화 (4 위치)
- **ai-context vendors/** 4 신규 (huawei.md / inspur.md / fujitsu.md / quanta.md)
- **vendor-boundary-map.yaml** 4 vendor + 신 generation 7 adapter 매핑 갱신
- **decision-log** docs/19_decision-log.md cycle-019 entry
- 표면: adapter 34 → 38 / vendor 정규화 5 → 9
- pytest 101 → 108 (+7 신규 회귀)

### 잔여 (외부 의존)

- **vault 생성** (lab/사이트 도입 시) — `vault/redfish/{huawei,inspur,fujitsu,quanta}.yml` ansible-vault encrypt
- **baseline 생성** (lab 도입 시) — `schema/baseline_v1/{vendor}_baseline.json`
- **사이트 fixture 캡처** — capture-site-fixture skill (도입 시)
- **OEM tasks** — `redfish-gather/tasks/vendors/{vendor}/` (사이트 fixture 확보 후 OEM extraction 보강)
- **Round 검증 / live-validation** — docs/13_redfish-live-validation.md

---

## 일자: 2026-05-01 (cycle-019 phase 1 — 7-loop + 10R extended audit P1 22건 일괄 수행 완료)

### 본 phase 완료 (사용자 명시 "예정돼있는 티켓 모두 수행해.")

- **호환성 fallback P1 22건 일괄 적용**:
  - F41 dell_idrac10.yml (PowerEdge 17G) / F47 hpe_ilo7.yml (Gen12) / F55 lenovo_xcc3.yml (V4 / OpenBMC)
  - F61 supermicro_x12/x13/x14.yml 3종 (AST2600) / F69 cisco_ucs_xseries.yml (X210c/X410c)
  - F56 lenovo_xcc.yml 좁힘 (V2/V3) / F68 cisco_cimc.yml 매트릭스 확장 (M4~M8)
  - F83 GET-only docstring 명시 / F84 TLS 1.2/1.3 SSLContext 명시
  - F48 NetworkPorts/Ports fallback 회귀 7건 신규
  - F80 EXTERNAL_CONTRACTS DMTF 매트릭스 / F91/F97/F104/F125/F126 advisory 5건 등재
- adapter 표면: 27 → 34 (+7)
- pytest 94 → 101 (신규 7건 — F48/F84 회귀)
- 모든 정적 검증 PASS

### 본 cycle 미수행 (외부 의존)

- **F74~F77 신규 vendor (Huawei / Inspur / Fujitsu / Quanta)** — rule 50 R2 9단계 사용자 명시 승인 필요. lab 부재 + 운영 도입 신호 없음. fixes/F44~F47.md ticket 만 보존.
- **F81 ThermalSubsystem fallback** — 향후 thermal 섹션 진입 시 적용 (호환성 영역 외)
- **F138 DMTF Redfish-Service-Validator 도입** — 검토 권장 (외부 도구)
- **사이트 fixture 캡처** — 사용자 사이트 신 generation BMC 도입 시 capture-site-fixture skill 적용

### 다음 cycle 권장

- 사용자 사이트 신 generation BMC 도입 신호 시 → F74~F77 9단계 진행 또는 F##.md ticket 즉시 진입
- 정기 harness self-improvement cycle (rule 28 측정 11종 drift 검사)

---

## 일자: 2026-05-01 (cycle-018 — 정기 자기개선 cycle 완료)

### 본 cycle 완료 (사용자 명시 "계획된 작업 모두 수행해라" → "진행해라")

- 6단계 파이프라인 (observer → architect → reviewer → governor → updater → verifier) 1회 진입 완료
- drift 4건 + 부수 2건 fix (12 파일 변경)
- 표면 카운트 변동 0 (rules=28 / skills=48 / agents=59 / policies=10 / hooks=21 그대로)
- ADR 불필요 (rule 70 R8 trigger 미해당)
- pytest 94/94 PASS / 6종 검증 모두 PASS

### 핵심 fix
- SessionStart "Baseline 0개" 버그 해결 (`collect_repo_facts.py` 경로 fix)
- field_dictionary 8 doc stale 정정 (46 → 65 entries, 분류 체계 유지)
- adapter 3 doc stale 정정 (25 → 27)
- `_vendor_count()` 명명 명확화 (docstring)
- untracked 잔재 9건 + vault_decrypt_check.py `.gitignore` 등록 (Goodmit0802! 평문 leak 차단)

### 다음 cycle 권장
- **harness-evolution-coordinator 다음 정기 cycle** — 본 cycle은 doc drift 위주. 다음은 코드 영역 (rule 28 측정 #11 외부 계약 / Fragment 토폴로지) drift 검사 필요
- **vault_decrypt_check.py 평문 password 제거** — fallback `"Goodmit0802!"` 삭제 후 `os.environ.get('VAULT_PASSWORD')` 강제. 그 후 git add 가능 (현재 .gitignore로 leak만 차단)
- (기존 P2/P3 잔여 — 변동 없음, 외부 의존)

---

## 이전 일자: 2026-05-01 (P1 follow-up cycle — F5/F13/F23 회귀 보강 + F23 적용 완료)

### 본 cycle 완료 (사용자 명시 "남아있는 작업 모두 수행해라")

- **F5 power EnvironmentMetrics fallback** — 코드 이미 적용 확인 (`_gather_power_subsystem` 1772-1791) + 회귀 5건 신규
- **F13 Cisco CIMC AccountService 'not_supported'** — 코드 이미 적용 확인 (`account_service_provision` 2081-2103) + 회귀 4건 신규
- **F23 OS gather not_supported 점진 전환** — Linux/Windows `gather_users.yml` 에 `_sections_unsupported_fragment` wiring + 회귀 9건 신규

### 검증 PASS
- pytest 94/94 (76 + 신규 18)
- harness consistency / vendor boundary / py_compile / YAML / project_map_drift

### 다음 cycle 권장 (P2 — 외부 의존)

(이전 cycle 의 P2 / P3 list 그대로 유지 — 아래 표 이전.)

---

## 일자: 2026-05-01 (하네스 보강 cycle 종료 — B1~B8 + D + E 모두 적용)

### 본 cycle 완료 (사용자 명시 "하네스 보강 작업 모두 수행해라 남겨두지말고 모두")

- **B1** rule 96 R1-A web sources 의무 신설 (lab 부재 영역 → 4종 sources 1개 이상)
- **B2** rule 25 R7-A-1 사용자 실측 > spec 신설 (Lenovo XCC reverse regression 학습)
- **B3** rule 96 R1-B envelope 13 필드 변경 자제 + envelope_change_check.py hook
- **B4** write-cold-start-ticket skill (SESSION-HANDOFF + INDEX + coverage 자동 구성)
- **B5** redfish_gather.py `_endpoint_with_fallback` 헬퍼 (Storage/Power/Thermal 패턴 추상화)
- **B6** adapter_origin_check.py hook (rule 96 R1 자동 검증)
- **B7** capture-site-fixture skill (사이트 사고 fixture sanitize 절차)
- **B8** cross_channel_consistency_check.py hook (3채널 envelope shape 일관성)
- **D-A1** web-evidence-collector agent (model: opus)
- **D-A3** lab-tracker agent (model: opus)
- **D-S1** web-evidence-fetch skill
- **D-S2** lab-inventory-update skill

### 표면 카운트 변동
- agents: 57 → 59
- skills: 43 → 48
- hooks: 18 → 21
- rules: 28 (본문 강화만)
- policies: 10
- decisions: ADR-2026-05-01-harness-full-permissions (cycle-011 시작 시점부터 존재)

### 검증 PASS
- verify_harness_consistency / verify_vendor_boundary / 3 신규 hook self-test / py AST 모두 PASS

### 다음 cycle 권장
- **harness-evolution-coordinator 6단계 정기 cycle 1회 진입** (observer → architect → reviewer → governor → updater → verifier) — cycle-016 이후 자기개선 cycle 공백
- **gather-coverage P1 3건** 진행 (F5 power EnvironmentMetrics / F13 Cisco AccountService not_supported / F23 OS unsupported 분류 점진 전환)
- **사이트 fixture 캡처** — capture-site-fixture skill 실 적용 (HPE Gen12 / Lenovo XCC3 / Dell iDRAC8 첫 적용)

---

## 일자: 2026-05-01 (gather coverage 전수 조사 cycle — 25건 fix 후보 등재)

### 본 cycle 완료 (2026-05-01 사용자 명시 "검색-티켓저장 반복")

- Phase A: INDEX + CYCLE-04-30 + CYCLE-05-01 + COVERAGE-MAIN 티켓
- Phase B Round 1: DMTF 표준 13 영역 (8건 fix 후보)
- Phase B Round 2: 5 vendor × BMC 세대 호환성 (7건 추가)
- Phase B Round 3: 사고/함정 + OS/ESXi (10건 추가)
- Phase D: 종합 매트릭스 + push

총 25건 fix 후보 발견 (P0=처리완료 / P1=3건 권장 / P2=9건 검증 / P3=11건 선제자제).

### 다음 cycle 권장 P1 작업 (3건)

| # | 영역 | 작업 | 파일 |
|---|---|---|---|
| F5 | power | gather_power의 PowerSubsystem fallback에 EnvironmentMetrics 추가 (system-level metric 보존) | `redfish_gather.py` `_gather_power_subsystem` |
| F13 | users | Cisco CIMC AccountService 'not_supported' 분류 — cycle 2026-05-01 인프라 활용 | adapter cisco_cimc.yml + redfish_gather.py |
| F23 | os | OS gather (hba_ib 등) 미지원 케이스 `_sections_unsupported_fragment` 분류 점진 전환 | os-gather/tasks/linux/gather_*.yml |

### P2 작업 (9건 — lab 검증/사고 재현 후)

자세한 list: docs/ai/tickets/2026-05-01-gather-coverage/COVERAGE-MAIN.md 참조

### P3 작업 (11건 — 사고 재현 시까지 보류)

자세한 list: docs/ai/tickets/2026-05-01-gather-coverage/coverage/MATRIX-R3.md 참조

### 티켓 위치

- 전체 메인: `docs/ai/tickets/2026-05-01-gather-coverage/INDEX.md`
- 종합 매트릭스: `docs/ai/tickets/2026-05-01-gather-coverage/COVERAGE-MAIN.md`
- Round 별 결과: `coverage/MATRIX-R{1,2,3}.md`
- 기존 cycle: `CYCLE-2026-04-30.md` + `CYCLE-2026-05-01.md`

---

## 일자: 2026-05-01 (404 'failed'→'not_supported' 분류 cycle 완료 — follow-up)

### 본 cycle 완료 (2026-05-01 사용자 명시 "모든 채널 / 모든 섹션" 진행)

- `9eb11fe4` redfish 404 분류 + PowerSubsystem fallback (DMTF 2020.4 호환)
- `a483811b` 3채널 fragment 인프라 (`_all_sec_unsupported` + build_sections)
- `5df5a9e1` 회귀 테스트 9건
- (본 commit) FAILURE_PATTERNS + NEXT_ACTIONS 갱신

검증: pytest 76/76 PASS / verify_harness_consistency PASS / py_compile 모두 OK.

### Follow-up (사이트 검증 + 점진 전환)

| 항목 | 작업 | 우선 |
|---|---|---|
| Site-A Dell envelope 재확인 | `power` / `network_adapters` 가 `'not_supported'` 분류로 emit + errors[] noise 사라짐 | P0 |
| HPE Gen12 / Lenovo XCC3 1.17.0 PowerSubsystem fallback 효과 | envelope `data.power.power_supplies` 채워지는지 | P0 |
| OS gather 미지원 분류 전환 | `gather_hba_ib.yml` (lspci 부재 시), Windows WMI namespace 미지원 시 — `_sections_unsupported_fragment` 활용 | P1 |
| ESXi gather 미지원 분류 | esxcli/vSphere API 미지원 케이스 fragment 분류 | P1 |
| Thermal 섹션 신규 검토 | `schema/sections.yml`에 thermal 추가? DMTF 2020.4 영향 | P2 |
| HPE iLO 5 BaseNetworkAdapters fallback | 일부 펌웨어 호환성 — 사고 재현 후 | P2 |
| SSH/WinRM/vSphere 호환성 — 사고 재현 후 별도 cycle | rule 92 R2 정신상 선제 변경 자제 | P3 |

### 본 cycle 적용 정적 검증

- pytest tests/unit/ — 76/76 PASS (신규 9건 추가)
- verify_harness_consistency — PASS
- py_compile — 1 파일 PASS (redfish_gather.py)
- YAML syntax — 5 파일 PASS (init/merge/build_sections/build_status/normalize_standard)
- 사이트 검증은 사용자 빌드에서만 가능 (Jenkins agent + 실 BMC)

---

## 이전 일자: 2026-04-30 (HTTP 406 호환 fix cycle 후 follow-up)

### 본 cycle 완료 (2026-04-30 site-A 사고 root cause fix 4 commit)

- Commit 1 (4715bb5b): precheck/redfish HTTP 헤더 명시 + 405/406 허용
- Commit 2 (7b0afc0c): `_compute_final_status` 401/403 강제 failed (Dell vault fallback 정상화)
- Commit 3 (2c543e1c): `diagnosis.details.detail` 노출 + Jenkinsfile_portal verbosity 토글
- Commit 4: vendor_aliases 보강 (HPE/Lenovo/Cisco/Dell/Supermicro 변형) + governance 문서

### Follow-up (사용자 측 사이트에서만 가능)

| 항목 | 작업 | 우선 |
|---|---|---|
| Site-A 1.17.0 펌웨어 BMC fixture 캡처 | `tests/fixtures/redfish/hpe_ilo_fw1_17/` ServiceRoot 응답 추가 → 회귀 차단 | P1 |
| Site-A `verbosity=2` 빌드 1회 실행 | 다른 BMC 잠재 사고 자동 발굴 | P1 |
| Dell vault fallback 실제 작동 검증 | Site-A에서 multi-account vault 1번 시도 (Commit 2 효과) | P1 |
| SSH/WinRM/vSphere 같은 호환성 함정 점검 | 사고 재현 후 별도 cycle (rule 92 R2 정신상 선제 변경 자제) | P2 |

### 본 cycle 적용 정적 검증

- `pytest tests/unit/` — 67/67 PASS (회귀 + 신규 9건 추가)
- `python scripts/ai/verify_harness_consistency.py` — PASS
- `python -m py_compile` — 3 파일 PASS
- 사이트 검증은 사용자 빌드에서만 가능 (Jenkins agent + 실 BMC)

---

## 이전 일자: 2026-04-30 (vendor-detect-robustness G1~G7 전체 + multi-account 보강 완료 — 잔여 결정 항목)

### G1~G7 전체 적용 완료 (2026-04-30)

`docs/ai/CURRENT_STATE.md` 참조. ad-hoc unit 22/22 PASS, pytest 216/216 PASS.

### 사용자 결정 대기 (정책 변경)

| 항목 | 영향 | 결정 |
|---|---|---|
| multi-account `_rf_attempt_ok` 강화 (`status == 'success'` 만 OK) | primary `partial` 결과 시 fallback 시도. 정상 partial 운영 (일부 섹션 not_supported 환경) 영향 가능 | 진행/보류 |
| account 순서 재정렬 (recovery 우선) | 운영 환경에 따라 fallback 우선 시도 — vault 정책 변경 | 진행/보류 |
| BMC lockout 정책 (현재 1초 backoff) 늘리기 | 5 accounts × 1s = 5s 추가 빌드 시간. 더 길게 (3~5초) 안전 | 진행/보류 |

### 실측 검증 필요 (lab 환경)

- **Lenovo 실 장비**: G1+G2+G3+G6 적용 후 vendor=null 해소 확인. `tests/redfish-probe/probe_redfish.py --vendor lenovo` 또는 Jenkins console log
- **구 BMC TLS**: G4 적용 후 "Redfish 미지원" 오판정 해소 확인 (해당 lab 장비 있을 시)
- **Dell `Dellidrac1!` 401**: G3+G6+backoff 적용 후 multi-account fallback 동작 확인. Jenkins console log에서 try_one_account.yml 출력으로 어느 account에서 succeed/fail 판단

### Commit/push 결정 대기

- 본 cycle 변경은 main 브랜치 직접 작업 — rule 93 R4 사용자 명시 승인 필요
- 변경 4 파일 + docs 4 파일

---

## 이전 일자: 2026-04-30 (residual-sweep — squash merge 직후 잔여 7건 fix)

## 잔여 (residual-sweep 후속)

| 항목 | 분류 | 차단 사유 |
|---|---|---|
| **OPS-RESIDUAL-1** Win10 (10.100.64.120) WinRM HTTPS 활성화 후 라이브 검증 | 운영 작업 (lab) | WinRM HTTPS off / NTLM MD4 미지원 — 16건 코드 fix는 raw PowerShell 기반으로 적용됨, 실 검증 lab 한계 |
| **OPS-RESIDUAL-2** Dell 10.50.11.162 BMC 응답 실패 재확인 | 외부 의존 (BMC) | residual-sweep 시 status=failed — 일시적 lab condition 추정. 다음 운영 검증 시 재확인 |
| **OPS-RESIDUAL-3** ESXi vsphere config.network routeConfig path 펌웨어 검증 | LOW | 현재 config.network 단계로 fallback (consoleVnic/vnic.spec). 실측 시 routeConfig 직접 path 미동작 펌웨어 7.0.3에서 확인. 다른 펌웨어/모델 (8.0u3 등) 시 추가 path 등록 가능 |

본 cycle 추가 검증 완료:
- 18 hosts (3 ESXi + 6 Linux + 9 Redfish) status=success rate 17/18 (94.4%)
- pytest 178/178 PASS / vendor boundary PASS / harness consistency PASS
- evidence: `tests/evidence/2026-04-30-residual-sweep/FINAL_REPORT.md`

---

## 일자: 2026-04-29 (account-fallback-validation 종료 시점 — 사용자 명시 lab 권한 위임 8 채널 실 검증)

## 잔여 (account-fallback-validation 후속)

| 항목 | 분류 | 차단 사유 |
|---|---|---|
| **OPS-AS-DELL-1** Dell iDRAC9 AccountService `find_empty_slot` None 반환 진단 | HIGH (P2 흐름 핵심) | `redfish_gather.py` 1413-1448 `account_service_get` 의 errors 가시성 부족 — 빈 슬롯 14개 raw probe 확인됨에도 코드 검색 None. `_rf_account_service_meta` 에 `errors[]` 노출 + ansible -vv debug 진단 필요. evidence: `tests/evidence/2026-04-29-account-fallback-validation.md` G1 |
| **OPS-AS-CISCO-1** Cisco CIMC 다른 펌웨어/모델 multi-slot 노출 검증 | LOW | lab CIMC 1대 (10.100.15.2) `Members@odata.count = 1` (admin 1슬롯만). 다른 Cisco 모델/펌웨어가 multi-slot 노출하면 코드 `not_supported` 분기 재검토. 외부 의존 — 추가 lab 부재. evidence: 위 G2 |
| **OPS-AS-SMC-1** Supermicro 실 BMC lab 확보 + AccountService 검증 | MED | 외부 의존 — `.lab-credentials.yml` 에 Supermicro BMC 미정의. 본 검증에서 skip |
| **OPS-AS-LAB-CLEANUP** lab Lenovo (slot 4) + HPE (slot 3) 의 infraops 정리 | LOW | lab BMC 에 영속 생성됨 (idempotent 검증 OK). production 배포 후 lab 회수 시 cleanup 필요 또는 운영 그대로 유지 — 사용자 결정 |
| **DOC-DECISION-LOG** docs/19_decision-log.md 본 검증 결과 추가 | MED | evidence 1건 → decision-log Round XX 항목 |

## 일자: 2026-04-29 (production-audit 종료 시점 — 4 agent 전수조사 + HIGH 30+건 일괄 fix)

## 잔여 (production-audit 후속)

| 항목 | 분류 | 차단 사유 |
|---|---|---|
| **OPS-AUDIT-1** Goodmit0802! 자격증명 회전 | 사용자 결정 (보안) | 자격증명이 git history (이전 commits)에 잔존 — 회전 후 filter-branch / repo rewrite 결정 필요 |
| **OPS-AUDIT-2** Supermicro 실장비 fixture 확보 | 외부 의존 (실장비 + lab 권한) | 3 adapter 정의 (`supermicro_bmc/x9/x11.yml`)에 0 fixture / 0 baseline |
| **OPS-AUDIT-3** ESXi 8.0u3 baseline 생성 | 외부 의존 (실장비) | **재확인 (production-audit 후속)**: tests/reference/esxi/10_100_64_{1,2,3}/ 3종 모두 ESXi 7.0.3 — 8.0u3 reference 미존재. 실 ESXi 8.0u3 장비 + lab 권한 확보 후 진행 |
| **OPS-AUDIT-4** Linux raw_fallback pytest 커버 | ✅ **완료 (production-audit 후속)** | `schema/baseline_v1/rhel810_raw_fallback_baseline.json` + `TestRhel810RawFallback` 7 테스트 (gather_mode/sections/memory_basis/correlation/array fields) 추가 |
| **OPS-AUDIT-5** Cisco UCS C-series (cisco_bmc) 실장비 검증 | 외부 의존 | cisco_bmc.yml은 fallback adapter — TA-UNODE-G1 외 일반 CIMC 검증 필요 |
| **OPS-AUDIT-6** RAID6/10/50/60 fixture 추가 | 외부 의존 (실장비) | 현재 RAID0/1/5만 baseline. 8+ drive RAID6 검증 필요 |
| **OPS-AUDIT-7** HPE iLO4 / iLO6 / Dell iDRAC8 / Lenovo IMM2 baseline | 외부 의존 | adapter 정의는 있으나 baseline 없음 |
| **OPS-HPE-REVIEW-1** HPE iLO 6 baseline 재수집 (10.50.11.231) | 운영 작업 (Jenkins job) | 2026-04-29 hpe-critical-review fix 5건 적용 후. 현재 baseline 은 cycle-016 Phase M/N 이전 stale — 재수집 시 본 fix 효과 (bios_date / ilo_version / cpu.architecture / hostname / is_primary / 빈 문자열 정규화) 모두 반영. evidence: `tests/evidence/2026-04-29-hpe-redfish-critical-review.md` |
| **OPS-HPE-REVIEW-2** Dell baseline 재검토 | 운영 작업 (실 Dell 장비) | `_hoist_oem_extras` 적용으로 Dell `hardware.bios_date` 도 채워짐 (이전: null). 실 Dell 검증 후 baseline 갱신 |
| **OPS-CISCO-REVIEW-1** Cisco baseline 재수집 (10.100.15.2) | 운영 작업 (사용자 결정) | 2026-04-29 cisco-critical-review fix 5건 (H1 dns_servers / H2 default_gateways / H3 PSU power_capacity_w / H4 power_control.power_capacity_watts / L1 firmware N/A 필터) 적용 후. dynamic 필드 (`power_consumed_watts/avg/max`, `bmc.datetime`) 정책 결정 (nullify vs realtime) 후 재캡처. evidence: `tests/evidence/2026-04-29-cisco-redfish-critical-review.md` |
| **OPS-CISCO-REVIEW-2** Cisco baseline `data.bmc` Phase M/N 신규 8 필드 보강 | 운영 작업 | `cisco_baseline.json` `data.bmc` 가 cycle-016 Phase M/N 이전 stale (datetime / datetime_offset / mac_address / dns_name / uuid / last_reset_time / timezone / power_state 부재). 코드 fix 후 baseline 재수집 시 자연 반영 — OPS-CISCO-REVIEW-1 와 묶어 진행 |
| **OPS-DELL-VAULT-1** Dell BMC vault 자격증명 회전 (10.50.11.162) | 운영 작업 (보안) | 2026-04-29 cisco-critical-review 4 vendor 회귀 검사 결과 — vault `dell.yml` (root/GoodskInfra1!) 로 BMC 인증 시 `HTTP 401`. ServiceRoot 무인증 GET 은 정상 (Vendor=Dell 응답) → BMC 자격증명 만료/잠금/변경 추정. `rotate-vault` skill 사용. evidence: `tests/evidence/2026-04-29-cisco-redfish-critical-review.md` 4 vendor 회귀 검증 표 |
| **OPS-LENOVO-PSU1** Lenovo 10.50.11.232 PSU1 hardware 점검 | 운영 작업 (실 hardware) | 2026-04-29 회귀 검사에서 발견 — PSU1 `Health=Critical`, `InputRanges[0].OutputWattage=null` (정격 미응답). 실 PSU 고장 또는 커넥터 분리. PSU 교체 또는 커넥터 점검 필요. envelope 정상 (코드 fix 동작 OK — PSU2 `power_capacity_w=750` 정상 채움) |

## 일자: 2026-04-29 (cycle-016 종료 시점 — 사용자 11 항목 점검 + 실 Jenkins 빌드 5회 + summary grouping 완성)

## ⏳ 현재 상태 (한 줄)

cycle-016 — 사용자 요구사항 11/11 검증 완료. 실 Jenkins 빌드 5회 (#39 #41 #43 #44 #45) — RHEL 9.6 OS gather 정상 동작 확인 (storage/network summary.groups + grand_total_gb 정상). Redfish 빌드는 lab vault 자격 미정합으로 status=failed 이지만 JSON envelope + 메시지 명확성 검증 완료. cycle-015 잔여 (OPS-3 / OPS-9 / OPS-11 / AI-16~18) + cycle-016 신규 (AI-19~22) 보유.

## cycle-016 핵심 결과

| 항목 | 결과 |
|---|---|
| 사용자 요구사항 11항목 검증 | 11/11 PASS (실 Jenkins 빌드 + 코드 검증) |
| OS Linux/Windows summary grouping | 9 파일 namespace pattern 실장 |
| ESXi summary 보강 | 3 파일 (storage / network / system) |
| Redfish summary namespace 변환 | normalize_standard.yml |
| baseline + examples 자동 주입 | 7 vendor + 3 example |
| 실 Jenkins 빌드 5회 (#39 ~ #45) | 모두 pipeline SUCCESS, OS 빌드 status=success |
| Jinja2 inline 코멘트 회귀 fix | 9 위치 제거 |
| 실패 메시지 명확성 | build_failed_output.yml default fallback 컨텍스트 포함 |
| pytest | 147/147 PASS |

## cycle-016 처리 완료 항목 (AI-* 7건)

| 항목 | 결과 |
|---|---|
| **AI-16** BMC Web UI E2E (Playwright) | ✅ `tests/e2e_browser/test_bmc_webui.py` Chromium PASS |
| **AI-17** baseline evidence | ✅ `tests/evidence/cycle-016/README.md` (정본 baseline_v1 안정성 위해 evidence 별도 보존) |
| **AI-18** RHEL 8.10 raw fallback | ✅ Build #49 (gather_mode=python_incompatible / Py3.6.8 분기) |
| **AI-19** Linux baremetal dmidecode | ✅ Build #48 (Dell R760 Ubuntu 24.04, slot 권한 후속만 잔여) |
| **AI-20** Redfish vault sync + AccountService | ✅ Build #50 (lab_root recovery / fallback_used=true / dryrun=true 메타) |
| **AI-21** ESXi 빌드 | ✅ Build #47 #51 (Cisco TA-UNODE-G1 + namespace fix 검증 grand_total=16556) |
| **AI-22** Windows 빌드 | ⚠️ Build #46 UNSTABLE → reopen as OPS 이슈 (10.100.64.135 포트 closed) |

## cycle-016 후속 (Phase G — 사용자 "남은 작업 모두 수행" 요청 처리)

| 항목 | 결과 |
|---|---|
| HPE/Lenovo/Cisco vault sync (lab recovery) | ✅ commit `61230ad5` |
| Dell × 4 BMC 빌드 (#52~#55) | ✅ 4/4 status=success / 멀티 spec (256GB / 12.8TB multi-tier) |
| HPE BMC 빌드 (#56) | ✅ status=success / 512GB / 7152GB |
| Lenovo BMC 빌드 (#57) | ✅ status=success / 512GB / 7152GB |
| Cisco BMC 1 빌드 (#58) | ⚠️ status=failed (TA-UNODE-G1 non-standard, "Redfish 미지원" 명확 한국어 메시지) |
| Linux distro 3 (RHEL 9.2 / Ubuntu / Rocky) #59~#61 | ✅ 3/3 status=success |
| ESXi 3 host 전수 #62 #63 | ✅ namespace fix 검증 (grand_total_gb=16556) |
| Windows #64 재시도 | ⚠️ 동일 UNSTABLE (lab 간헐) |
| AccountService dryrun=false 실 실행 (agent SSH 직접) | ✅ `account_service:{dryrun:false, method:"noop"}` 메타 노출 |
| baremetal dmidecode `become: true` (#66) | ✅ **DDR5 16GB × 8 = 128GB summary 완전 수집** |

## 진짜 잔여 (AI 환경 외 — 사용자 / 운영팀 / 외부 결정 의존)

- **OPS-9** repo private 전환 (사용자 결정)
- **OPS-3** 운영팀 vault credential 회전 timing — AccountService 실 호출 권한 부여 (현재 dryrun toggle 만 검증)
- **OPS-11 partial** Cisco BMC 10.100.15.3 ping fail (lab 부재) — 1번 (10.100.15.1)은 회복됐으나 Redfish 미지원
- **AI-22 reopen** Win Server 2022 (10.100.64.135) 빌드 시점 winrm probe 간헐 실패 — lab firewall/WinRM 서비스 안정성 OPS 조사
- **AI-25 후속** dell_baseline.json 정본 갱신 — 현재 baseline IP (10.50.11.162) 와 lab 실 IP 불일치. lab 실 IP 정본 채택 시 정합성 검토 후 갱신

## cycle-015 핵심 결과

| 항목 | 결과 |
|---|---|
| lab 자격증명 + inventory (gitignored) | 28 호스트 5 그룹 |
| LAB_INVENTORY catalog | 신규 (sanitized) |
| 21 호스트 연결성 검증 | 21/21 ICMP + TCP protocol PASS |
| rule 96 DRIFT-011 발견 | Dell 32 AMI / Cisco 2 TA-UNODE-G1 (사용자 라벨 vs Manufacturer 불일치) |
| Win Server 2022 firewall | 모든 포트 closed → OPS-10 |
| Cisco BMC 1, 3 일시 장애 | 503 / timeout → OPS-11 |
| Playwright + Chromium 설치 | 완료 |
| Browser E2E smoke | 1/1 PASS (Jenkins master dashboard 도달) |
| 표면 카운트 | catalogs +1 / decisions +1 / 신규 dir 2 |

## cycle-014 핵심 결과 (이전 세션)

## cycle-014 핵심 결과

| 항목 | 결과 |
|---|---|
| 4 vendor 코드 경로 (precheck → detect → adapter → collect → rescue) | PASS (4/4 vendor detect 성공, adapter 자동 선택 OK) |
| HIGH Jinja2 회귀 fix | commit `bf247266` main push 완료 |
| vault primary 자격 (4 vendor infraops) | HTTP 401 → OPS-3 회전 필요 |
| vault recovery 자격 (USERID/root/admin/?) | HTTP 401 → OPS-3 회전 필요 |
| account_service 자동 생성 검증 | 미진입 (recovery 자격 fail로 trigger 안 됨) — cycle-015 이월 |
| Supermicro 검증 | baseline 부재 — 별도 cycle |

## cycle-013 종료 시점

## 다음 세션 시작 시 확인 순서 (cold start)

1. **main 갭** — `git fetch origin && git log --oneline origin/main..HEAD` 으로 cycle-013 commit (`0150fa2e`) main 머지 여부 확인 (현재 ahead 1, behind 1)
2. **운영자 빌드 결과 확인** — OPS-1 Jenkins 시범 결과 받았는지 (envelope `meta.auth.fallback_used` 값)
3. **자율 매트릭스 잔여** — 본 매트릭스의 AI-8 (main pull + 정리)만 잔여 (rule 93 R2 사용자 명시 승인 필요)

## 자율 진행 closed (cycle-013 완료)

| # | 작업 | 결과 | commit |
|---|---|---|---|
| AI-1 | schema/examples 11 path 보강 | validate_field_dictionary 11 WARN → 0 WARN | `0150fa2e` |
| AI-2 | PROJECT_MAP fingerprint 재계산 | drift 6 → 0 + 본문 stale 4건 정정 | `0150fa2e` |
| AI-3 | JENKINS_PIPELINES.md 갱신 | vault binding 절 신규 (server-gather-vault-password) | `0150fa2e` |
| AI-4 | SCHEMA_FIELDS.md 갱신 | Must 31 / Nice 20 / Skip 6 = 57 (1건 over count 정정) | `0150fa2e` |
| AI-5 | VENDOR_ADAPTERS.md 헤더 갱신 | recovery_accounts 메타 절 신규 | `0150fa2e` |
| AI-6 | cycle-012.md 신규 | governance 보존 | `0150fa2e` |
| AI-7 | ADR vault-encrypt-adoption | rule 70 R8 trigger 미해당 advisory governance trace | `0150fa2e` |

## 자율 진행 잔여 (다음 세션 AI)

| # | 작업 | 전제 | 차단 사유 |
|---|---|---|---|
| AI-8 | main pull 후 cycle-013 commit 정리 + CURRENT_STATE 종료 갱신 | rule 93 R2 사용자 명시 승인 | main 머지 / 브랜치 전환은 사용자 결정 |

## 사용자 개입 필요 (자율 불가, 명시 승인 후 진행)

| # | 작업 | 이유 | 진입 후 AI 가능 작업 |
|---|---|---|---|
| OPS-1 | Jenkins 빌드 시범 1회 (target_type=redfish, 임의 BMC) | UI 클릭 + lab 환경 | console log 받으면 envelope 분석 + 회귀 fixture 추가 |
| ~~OPS-2~~ | ~~PR 머지 결정~~ | — | **closed 2026-04-29** — PR #1 머지 완료 (`b74c1103`) |
| **OPS-3 (cycle-015에서 7/9 BMC sync 확인)** | cycle-015 lab credentials를 vault primary로 흡수 가능 — Dell × 5 + HPE + Lenovo 모두 200 OK 확인 (`bmc-auth-probe-2026-04-29.json`) | 운영팀 결정 (vault re-encrypt timing) | encrypt 후 cycle-016 정식 진입 |
| **OPS-9 (cycle-015 신규)** | repo private 전환 시 자격증명 정책 결정 — (a) ansible-vault encrypt 흡수 / (b) gitignored 평문 영구 | 사용자 결정 (private 전환 시점) | (a) 결정 시 vault encrypt 자동 / (b) 결정 시 현 상태 유지 |
| ~~OPS-10~~ | ~~Win Server 2022 firewall 해제~~ | — | **closed cycle-015** — 사용자 직접 + IP 정정 (132 → 10.100.64.135) |
| **OPS-11 (cycle-015 신규, 잔여)** | Cisco BMC 1, 3 가용성 재확인 — 503/timeout | 다음 일과시간 / lab 운영자 | 정상 시 baseline 갱신 |
| ~~OPS-12~~ | ~~Dell 32 (실제 AMI) 물리 호스트 식별~~ | — | **closed cycle-015** — 사내 부재 확인 → 호스트 제거 (DRIFT-011 resolved) |
| ~~OPS-13~~ | ~~Cisco BMC 2 TA-UNODE-G1 식별~~ | — | **closed cycle-015** — 사내 부재 확인 → 호스트 제거 (DRIFT-011 resolved) |
| ~~OPS-14~~ | ~~Jenkins 사용자 / API token 정책~~ | — | **partially obviated cycle-015** — cloviradmin이 Jenkins 사용자로도 작동 (Browser E2E PASS) |
| ~~OPS-15~~ | ~~Grafana endpoint 합의~~ | — | **closed cycle-015** — Jenkinsfile_grafana 제거 (사용자 명시) |
| OPS-4 | P1 lab 회귀 — vendor 5종 1차 / 2차 fallback 시나리오 | 실 BMC + lab cycle | 결과 받으면 evidence + baseline 갱신 |
| OPS-5 | P2 dryrun OFF 전환 (Dell + HPE 먼저) | rule 92 R5 + BMC 잠금 위험 | 결정 받으면 `_rf_account_service_dryrun: false` 토글 + lab 검증 |
| OPS-6 | baseline_v1/* 7개 실측 갱신 (P3/P4 신 필드 정합) | rule 13 R4 — 실측 기반만 | probe_redfish.py 결과 받으면 baseline 갱신 + Stage 4 회귀 |
| OPS-7 | settings.local.json 편집 — AI self-modification 차단 (cycle-011 잔여) | settings.json만으로 풀림 확인됨 | 운영자 직접 편집 |
| OPS-8 | main에 cycle-013 commit 정리 (PR 또는 직접) | rule 93 R2 머지 사용자 명시 승인 | 승인 받으면 main 정리 + CURRENT_STATE 종료 갱신 (AI-8) |
| AI-9 | 25개 stale reference cleanup (cycle-011 advisory 잔여) | 즉시 — cycle-013 11건 처리 후 약 38건 잔존 | 별도 cycle (영향 범위 큼) — rule 60 / pre_commit_policy / vault-rotator 본문 참조 정리 |
| AI-10 | docs/ai/harness/ archive 진입 (cycle-001~005 → archive/) | rule 70 R6 정본 catalog 비대화 차단 | 별도 cycle — 사용자 archive 정책 명시 후 |
| AI-11 | docs/ai/impact/ 6 보고서 archive (구조·정책 전환 reasoning 보존) | rule 70 R6 첫 질문 YES | 별도 cycle |
| **cycle-016** | OPS-3 후 4 vendor primary 인증 성공 검증 + recovery only 시나리오 + account_service 진입 + dryrun=true→false | OPS-3 완료 | redfish 공통계정 자동 생성 검증 (cycle-012 P2 코드의 실 BMC 동작). cycle-015 lab credentials의 6 vendor password 흡수 |
| Supermicro 추가 | baseline_v1 추가 + Supermicro BMC IP 명시 + 5번째 vendor 검증 | OPS-12 (Dell 32 AMI 식별)에 따라 — AMI = Supermicro면 즉시 가능 | 5 vendor 완전 검증 |
| ~~AI-12~~ | ~~Dell × 5 Round 11 baseline~~ | — | **partially DONE cycle-015** — endpoint coverage 검증 PASS (`dell-round11-endpoint-coverage.json`). baseline JSON 정식 갱신은 cycle-016 |
| ~~AI-13~~ | ~~Linux raw fallback Round (RHEL 8.10)~~ | — | **DONE cycle-015** — rule 10 R4 실증 (`linux-probe-2026-04-29.json`) |
| ~~AI-14~~ | ~~Browser E2E 활성 시나리오~~ | — | **DONE cycle-015** — Jenkins login PASS (`test_master_login_then_dashboard`) |
| ~~AI-15~~ | ~~deep_probe Dell 32 / Cisco 2~~ | — | **obviated cycle-015** — 두 호스트 모두 제거 |
| AI-16 | Browser E2E — Cisco CIMC / iDRAC Web UI | OPS-11 가용성 회복 후 | UI 진입 + 펌웨어 / sensor / power 패널 |
| **AI-17 (cycle-015 신규)** | Dell × 5 + HPE + Lenovo baseline_v1 정식 갱신 | cycle-015 endpoint coverage 통과 → JSON 작성 가능 | probe_redfish.py 정식 실행 + baseline_v1 갱신 + Stage 4 회귀 (cycle-016) |
| **AI-18 (cycle-015 신규)** | RHEL 8.10 raw fallback ansible-playbook 실행 (정식 site.yml) | Jenkins agent SSH 또는 직접 ansible 설치 후 | 실 envelope 13 필드 응답 검증 |

## 사용자 결정 명시 필요 (Phase 진입 전)

| # | 항목 | 후보 | AI 추천 |
|---|---|---|---|
| DEC-1 | OS/ESXi secondary 자격 사용 시 envelope `meta.auth.fallback_used: true` 노출 정책 | 노출 / 비노출 | 노출 (이미 P1 commit에 적용됨) |
| DEC-2 | P5 sub-phase 우선순위 (Linux NTP+firewall+listening 완료 / Windows runtime 완료 / ESXi vSwitch 완료) | 다음 sub-phase = ESXi multipath / license? | 본 cycle은 sub-phase a+b 완료 — c (multipath/license) 별도 cycle |
| DEC-3 | Cisco AccountService 미지원 처리 — 운영자 수동 복구 절차 매뉴얼 | 작성 / 보류 | docs/ 별도 매뉴얼 |

## cycle-013 요약 (이번 세션 완료)

`0150fa2e` cycle-013 catalog 5종 + cycle-012 보고서 + ADR + examples 11 path

**자율 매트릭스 7건 (AI-1~AI-7) closed**:
- catalog 4종 (PROJECT_MAP / JENKINS_PIPELINES / SCHEMA_FIELDS / VENDOR_ADAPTERS) 갱신
- cycle-012.md 보고서 + ADR-2026-04-29-vault-encrypt-adoption advisory 신규
- schema/examples 11 path 보강 (validate 11 WARN → 0)

**발견 + 정정**: cycle-012 commit 메시지 / 헤더 주석 1건 over count (Nice 21 → 20, 58 → 57). 모든 catalog 정합.

**검증**: harness consistency / vendor boundary / project_map_drift / validate_field_dictionary 모두 PASS.

## cycle-012 요약 (이전 세션 완료)

`f0f621ce` P0 / `fe0be36c` P1 / `0448d00d` P2+P4(Redfish) / `fbb0f357` P3+P4 normalize / `92b935c3` P5 Linux / `b6d24fd3` P4 OS/ESXi + P5 Windows / `8e536447` schema 12 entries / `c37138ca` docs / `29fee49a` vault encrypt + credential 'server-gather-vault-password'

**검증**: 145 e2e PASS / harness 28-43-49-9 / vendor boundary / field_dictionary Must31-Nice21-Skip6=58
**plan**: `C:\Users\hshwah\.claude\plans\1-snazzy-haven.md`
**handoff**: `docs/ai/handoff/2026-04-29-cycle-012.md`
**branch**: `feature/3channel-expansion`

---

## 완료 항목 (cycle-011 — 보안 정책 자체 해제)

## 완료 항목 (cycle-011 — 보안 정책 자체 해제)

- [x] **rule 60 + 정책 / hook / agent 11개 일괄 제거** (사용자 명시 결정 옵션 A)
- [x] **settings.json 보안 deny 38건 + disableBypassPermissionsMode 제거** + defaultMode bypassPermissions + sandbox allowUnsandboxedCommands
- [x] **git hooks 재설치** (pre_commit_policy 제거)
- [x] **rule 00 보호 경로 절 갱신** (참고용으로 변경)
- [x] **ADR 작성** (rule 70 R8 두 번째 적용)
- [x] **surface-counts.yaml 갱신** (28/43/49/9)
- [x] **verify_harness_consistency / verify_vendor_boundary** PASS
- [x] **SSH/WinRM 자동화 재시도** — Win Server 2022 (10.100.64.135) 28/28 PASS, 4.14 MB raw archive 수집 → `tests/reference/os/win2022/10_100_64_135/`
- [x] **evidence 작성** — `tests/evidence/2026-04-28-win2022-validation.md`
- [x] **Round 12 자동 재수집** — Linux 6/6 + ESXi 3/3 (SSH 활성화 후 모두 OK) + Redfish 9/11 + Agent 4/4
- [-] **Win10 (10.100.64.120)** — 사용자 결정으로 **제외** (자격 미해결)
- [-] **WinServer2022 (10.100.64.132)** — 사용자 결정으로 **제외** (WinRM 비활성)
- [-] **Dell 10.100.15.32** — 사용자 결정으로 **제외** (vendor mismatch / AMI Redfish Server)
- [ ] **Cisco 10.100.15.1 Redfish 활성화** — 웹 UI는 200 OK, but `/redfish/v1/` → 503. CIMC에서 Redfish service 별도 enable 필요 (Cisco UCS Manager 또는 CIMC CLI: `scope cimc; scope https; set redfish-enabled yes; commit`)
- [ ] **Cisco 10.100.15.3 라우팅 확인** — 사용자 PC에서는 웹 접근 OK, but Agent 154 (Jenkins)에서는 모든 포트 unreachable. 네트워크 라우팅 / 방화벽 정책 확인 필요
- [ ] **settings.local.json** — AI self-modification 차단으로 사용자 직접 편집 필요 (settings.json만으로 자동화 풀림 확인됨)
- [ ] **25개 stale reference cleanup** — advisory, 후속 incremental

## 완료 항목 (cycle-010 — T3-04/05/06 일괄 + rule 70 R8 신설)

- [x] **T3-04 (04-A 채택)** — 27 adapter `version: "1.0.0"` placeholder 일괄 삭제 (참조 0건 검증)
- [x] **T3-05 (05-A 유지)** — redfish_gather.py BMC IP 수집 현재 유지. break-on-first-IP가 실 N+1 아니므로 NEXT_ACTIONS close
- [x] **T3-06 (06-B 채택)** — `rule 70 R8` 신설 (ADR 의무 trigger 3종: rule 본문 의미 변경 / 표면 카운트 변경 / 보호 경로 정책 변경)
- [x] **소급 ADR 작성** — `ADR-2026-04-28-rule12-oem-namespace-exception.md` (DRIFT-006 governance trace 보강 — R8 적용 첫 사례)
- [x] **검증 5종 PASS** — verify_harness_consistency / verify_vendor_boundary / 27 adapter YAML 파싱 / project_map_drift --update / version 키 0/27
- [x] **증거 문서 4종 갱신** — CURRENT_STATE / NEXT_ACTIONS / TEST_HISTORY / harness/cycle-010.md

## 완료 항목 (cycle-009 — fallback envelope HIGH fix 2건 + T2-A7 rule 5요소 보강 7개)

- [x] **HIGH 버그 fix #1** — `os-gather/site.yml` Windows PLAY 3 `always` fallback envelope 2 필드 → 13 필드 (rule 13 R5 / rule 20 R1 정합)
- [x] **HIGH 버그 fix #2** — `esxi-gather/site.yml` `always` fallback의 미정의 변수 `_ip` → `_e_ip` 정정 (fallback 시 ip null 출력되던 문제)
- [x] **MED fix** — 3채널 fallback envelope `collection_method` 값 build_meta와 일관성 (OS `ansible`→`agent`, ESXi `vmware`→`vsphere_api`, Redfish `redfish`→`redfish_api`)
- [x] **T2-A7 rule 24** — completion-gate 5요소 보강 (R1~R9, 정적 검증 / 버그 0건 / 문서 4종 / 후속 식별 / Git push / Schema 회귀 / 종결어 금지 / "남은 작업" 답변 / 보고 포맷)
- [x] **T2-A7 rule 26** — multi-session-guide 5요소 보강 (R1~R8, 진입 조건 / 오너십 / commit pathspec / 공용 파일 / 동기화 / CONTINUATION / 마커 / 종료 갱신)
- [x] **T2-A7 rule 41** — mermaid-visualization 5요소 보강 (R1~R18, 타입 / 가시성 / 색상 / 형상 / ID / 라벨 / 30노드 / 성공실패 / AS-IS / vendor / 문맥 / 범례 / 호환 / sequence / state / gantt / er / ASCII)
- [x] **T2-A7 rule 50** — vendor-adapter-policy 5요소 보강 (R1~R6, 정규화 정본 / 9단계 / 점수 / branch / 경계 / generic fallback)
- [x] **T2-A7 rule 60** — security-and-secrets 5요소 보강 (R1~R8, encrypt / 회전 / redaction / verify / 자격증명 / stacktrace / 입력 / 스캔)
- [x] **T2-A7 rule 70** — docs-and-evidence-policy 5요소 보강 (R1~R7, 갱신 매핑 / fingerprint / 작성 원칙 / 정본 보호 / 보존 판정 / archive / cycle 자문)
- [x] **T2-A7 rule 90** — commit-convention 5요소 보강 (R1~R6, type 8 / 길이 / 금지어 / 본문 / 강제 수준 / AI 동등)

## 완료 항목 (cycle-008 — P2 MED/LOW 11건 일괄, 사용자 "새 vendor 제외 모두" 명시 승인)

- [x] **redfish_gather.py docstring Cisco 추가** (LOW)
- [x] **redfish_gather.py:727 `int(vcap_int / 1048576)` → `vcap_int // 1048576` 정수 나눗셈 통일** (LOW)
- [x] **callback_plugins/json_only.py `_emit()` silent pass 보강** — `JSON_ONLY_DEBUG=1` 환경변수로 stderr 경고 활성화 (호출자 호환성 유지)
- [x] **adapter_loader 동률 정렬 문서화** — Python list.sort stable + 파일명 알파벳 tie-break + 동률 발견 시 vvv 경고
- [x] **HPE iLO5/6 priority 차등 (T3-02)** — iLO 6=100, iLO 5=90, iLO 4=50, generic=10
- [x] **Lenovo generic fallback adapter 추가 (T3-03)** — `lenovo_bmc.yml` priority=10
- [x] **Cisco generic fallback adapter 추가** — `cisco_bmc.yml` priority=10 (Lenovo와 동일 패턴)
- [x] **lenovo_imm2.yml tested_against 펌웨어 명시** (rule 96 R1 origin 강화)
- [x] **cisco_cimc.yml 세대 차등 검토 결정 명시** — M5/M6 실장비 검증 부족으로 차등 분리 보류, generic fallback만 추가
- [x] **Cisco OEM gather_system 분기 silent 의도 명시** — adapter strategy=standard_only + Round 11 실측 OEM 비어있음 + bmc_names에 'cisco':'CIMC' 추가
- [x] **redfish_gather.py 추가 함수 분리** — gather_system 103→57줄 (vendor OEM helper 4종 + dispatch dict), detect_vendor 64→37줄 (`_fetch_service_root` + `_resolve_first_member_uri`), main 67→45줄 (`_make_section_runner` + `_collect_all_sections` + `_compute_final_status`)
- [x] **os-gather/tasks/linux/gather_system.yml 분리** — 346→322줄, `build_identifier_diagnostics.yml` 별도 task

## 완료 항목 (cycle-007 — 4축 검수 + HIGH 4 일괄)

- [x] **#1 redfish_gather.py `gather_storage()` 190줄 분리** — 5 함수 분리 (logic 동일, signature 동일, pytest 95/95 PASS)
- [x] **#2 rule 22 R7 텍스트 정정** — 5 공통 fragment 변수 명명 (`_data_fragment` + `_sections_{supported,collected,failed}_fragment` + `_errors_fragment`) 8 파일 일괄 갱신
- [x] **#3 precheck_bundle.py `run_module()` 181줄 + adapter_loader.py `LookupModule.run()` 115줄 분리** — 6+5 헬퍼 함수 추출
- [x] **#4 precheck_bundle.py `requests` 의존 제거** — urllib stdlib 단일 경로 통일 + 에러 분류 강화

## 완료 항목 (full-sweep 잔여 — 이전 세션)

- [x] **T2-B2**: `verify_harness_consistency.py` FORBIDDEN_WORDS default 활성화 (`--no-forbidden-check`로 비활성)
- [x] **T2-C2**: `precheck_bundle.py` Stage 1 (reachable) ↔ Stage 2 (port_open) 분리 + ConnectionRefusedError 시 host alive 판정
- [x] **T2-C8**: `os-gather/files/get_last_login.sh` 공유 snippet + lookup file 통합 (gather_users.yml 294 → 239 lines)
- [x] T2-C1 분석: precheck timeout (3/6/8s) ↔ 본 수집 timeout (rule 30 R3 30/10/30s) 의도된 차이로 변경 SKIP

## 완료 항목 (cycle-006)

- [x] **DRIFT-004**: `users[]` 섹션 6 필드 등록 (Must +3 / Nice +2 / Skip +1) → 분포 46 entries
- [x] **DRIFT-005**: `_BUILTIN_VENDOR_MAP` → `_FALLBACK_VENDOR_MAP` 이름 변경 + 3-tier path resolution + nosec silence
- [x] **DRIFT-006**: rule 12 R1에 Allowed (cycle-006 추가) 절 + 17 라인 `# nosec rule12-r1` silence
- [x] **W2 (b)**: os-gather Jinja2 OEM list silence + 동기화 책임 명시 + verify_vendor_boundary nosec 패턴
- [x] **vendor_boundary 0건 달성** (cycle-005 26 → 0)
- [x] CONVENTION_DRIFT.md DRIFT-004/005/006 모두 resolved
- [x] cycle-006 보고서 + CURRENT_STATE / NEXT_ACTIONS 갱신

## 완료 항목 (cycle-005)

- [x] **DRIFT-007 catalog 정합** — Must 28 / Nice 7 / Skip 5 = 40 entries 실측 확정 (cycle-002 grep 헤더 noise 오인 정정)
  - CLAUDE.md / rule 13 / SCHEMA_FIELDS.md / field_dictionary.yml 헤더 / SKILL.md 일괄 갱신
  - SCHEMA_FIELDS.md 측정 명령 grep → YAML 파싱 변경
- [x] **scan #2 재설계** — set_fact 다음 indent 블록 lookahead로 누적 변수 침범만 검출 (107 → 0건)
- [x] **scan #4 specificity 분석** — distribution_patterns / version_patterns / firmware_patterns 분리 검사 (7 → 0건)
- [x] **verify_vendor_boundary docstring 인식** — Python triple-quote 영역 skip (33 → 26건)
- [x] **verify_harness_consistency 동기화 게이트** — `_BUILTIN_VENDOR_MAP` ↔ `vendor_aliases.yml` advisory (DRIFT-005 옵션 (2) 사전)

## 완료 항목 (cycle-004)

- [x] 도구 3종 정밀화 (verify_vendor_boundary 인코딩 fix + scan / output_schema_drift_check 정밀화)
- [x] 13 adapter origin 주석 일괄 추가 (rule 96 R1)
- [x] redfish_gather.py `_safe_int` helper + 6 블록 refactor
- [x] detect_vendor.yml default 가드 + 변수 상태 13건 silence
- [x] vendor 경계 57건 분석 보고서
- [x] DRIFT-004/005/006 등재

## P1 — 사용자 결정 대기 (외부 의존)

### 옵션 / 회귀 위험 큰 항목
- [ ] **DRIFT-006 옵션 (2)**: `redfish_gather.py` vendor-agnostic 리팩토링 — `oem_extractor` 매핑을 adapter capabilities로 위임. 영향 vendor 전부 회귀 + Round 권장. 별도 cycle.

### 외부 의존
- [ ] **새 vendor 추가** (Huawei iBMC / NEC / Inspur 등) — PO 결정 + 실장비
- [ ] **Round 11 실장비 검증** — 새 펌웨어 / 새 모델 (probe-redfish-vendor) — 실장비 + Round 일정

## P2 — 잔여 (외부 의존 / 사용자 결정 / 운영)

### 운영 / 정책 (사용자 결정)
- [ ] **incoming-review hook 실 환경 테스트** — 다음 git merge 시 `docs/ai/incoming-review/<날짜>-<sha>.md` 자동 생성 확인
- [ ] **harness-cycle 정기 주기 결정** — 매주 / 격주 / 수동만 (사용자 결정)

### Vendor 차등 — 실장비 검증 후 진행
- [ ] **adapters/redfish/cisco_cimc.yml 세대 차등 (M4/M5/M6 차등 분리)** — M5/M6 실장비 검증 후 진행 (현재 M4만 Round 11 검증됨)

### Schema / Baseline (실측 evidence 필요, AI 자체 불가)
- [ ] **T2-D2** cisco_baseline.json `data.users` `null` → `[]` (rule 13 R4 — 실측 evidence 필요)

### Rule 재구조화 (대규모, 별도 cycle 필요)
- [ ] **DRIFT-006 옵션 (2)**: redfish_gather.py vendor-agnostic 리팩토링 — _OEM_EXTRACTORS dispatch는 cycle-008에서 적용. 다음 단계는 dispatch 자체를 adapter capabilities로 위임. 영향 vendor 전부 회귀 + Round 권장

## 결정 필요 (사용자)

| 항목 | 옵션 | 비고 |
|---|---|---|
| T2-D2 (cisco_baseline.json data.users) | `null` → `[]` | rule 13 R4 — 실측 evidence 필요 |
| 새 vendor 추가 일정 | Huawei / NEC / Inspur | PO + 실장비 |
| Round 11 검증 | 새 펌웨어 / 새 모델 | 실장비 + 일정 |
| harness-cycle 정기 주기 | 자동 trigger 도입? | 운영 정책 |

## 해결됨 (cycle-007 / cycle-008 / cycle-010)

- T3-01 (precheck requests 의존) → cycle-007에서 stdlib only로 해결
- T3-02 (HPE iLO5/6 priority 동률) → cycle-008에서 차등 (90/100) 적용
- T3-03 (Lenovo generic fallback) → cycle-008에서 lenovo_bmc.yml 추가 (Cisco도 같이)
- T3-04 (adapter version 추적) → cycle-010에서 04-A 삭제 채택 (placeholder 1줄 일괄 제거)
- T3-05 (redfish BMC IP N+1) → cycle-010에서 05-A 유지 결정 (break-on-first-IP가 실 N+1 아님)
- T3-06 (governance ADR 의무) → cycle-010에서 06-B 채택 (rule 70 R8 신설 + 조건부 trigger 3종)

## 정본 reference

- `docs/ai/CURRENT_STATE.md` (cycle-008 후 갱신)
- `docs/ai/harness/cycle-006.md` (직전 cycle 보고서)
- `docs/ai/harness/full-sweep-2026-04-28.md` (full-sweep 보고서)
- `docs/ai/impact/2026-04-27-vendor-boundary-57.md` (vendor 경계 분석)
- `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 6건)
- `docs/ai/decisions/ADR-2026-04-27-harness-import.md` (Plan 1~3 ADR)
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md` (cycle-003 첫 스캔)
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
