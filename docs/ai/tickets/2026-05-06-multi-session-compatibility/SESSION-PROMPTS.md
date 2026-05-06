# Session Prompts — 2026-05-06 multi-session-compatibility

> **사용자 명시 (2026-05-06)**:
> - 단일 세션 순차 진행 — 각 ticket 끝나면 `/clear` → 다음 프롬프트 복붙
> - **자율 진행 권한**: 작업 중 부가 작업 발생 시 승인 없이 무조건 진행
> - 사용자 결정 항목도 AI 합리적 default 결정 후 SESSION-HANDOFF 에 명시
> - 모두 [DONE] 후 cycle 종료

---

## 자율 진행 권한 정책 (모든 세션 공통)

본 cycle 의 모든 worker 세션은 다음 권한을 보유:

1. **부가 작업 자율 진행** — ticket 진행 중 추가 발견되는 모든 작업은 승인 없이 진행
2. **사용자 결정 항목 default 진행** — 사용자 결정이 필요한 항목 (예: M-A2 status 의도, M-E1 Superdome 분류) 도 AI 가 합리적 default 결정 후 진행. 결정 사유는 SESSION-HANDOFF / decision-log 에 명시
3. **commit + push 자율** — 작업 완료 시 main 자율 commit + push (github + gitlab 동시 — rule 93 R1+R4)
4. **rule 24 6 체크리스트** 통과 후 [DONE] 선언
5. **commit 마커**: `<type>: [M-X## DONE] <요약>` (rule 26 R7 / rule 90)

**예외 (자율 진행 금지)**:
- force push (`--force` / `-f`) — rule 93 R1
- 새 vendor 추가 (rule 50 R2 — 본 cycle 의 M-E 는 사용자 명시 승인 받음)
- envelope 13 필드 추가/삭제/리네임 (rule 96 R1-B) — 호환성 cycle 외 영역

→ 본 cycle 은 **호환성 fallback 작성 cycle (Additive only)** — 위 예외 영역 진입 시에만 사용자 확인.

---

## 진행 순서 (24 ticket)

| # | ticket | 제목 | phase |
|---|---|---|---|
| 1 | M-A1 | status 로직 분석 | A 분석 |
| 2 | M-A2 | status 의도 결정 | A 결정 |
| 3 | M-A3 | status 코드 변경 + 회귀 | A 구현 |
| 4 | M-A4 | status ADR | A ADR |
| 5 | M-B1 | account_provision flow 분석 | B 분석 |
| 6 | M-B2 | 5+4 vendor 매트릭스 | B 검증 |
| 7 | M-B3 | 공통계정 mock 회귀 | B 회귀 |
| 8 | M-C1 | vault 동적 로딩 분석 | C 분석 |
| 9 | M-C2 | cache invalidation | C 검증 |
| 10 | M-C3 | vault 자동 반영 회귀 | C 회귀 |
| 11 | M-D1 | 240 cell 호환성 매트릭스 | D 매트릭스 |
| 12 | M-D2 | web 검색 gap (DMTF/vendor) | D 검색 |
| 13 | M-D3 | fallback 코드 추가 | D 구현 |
| 14 | M-D4 | 전 vendor 호환성 회귀 | D 회귀 |
| 15 | M-E1 | Superdome web 검색 | E 검색 |
| 16 | M-E2 | Superdome adapter | E 구현 |
| 17 | M-E3 | ai-context vendors | E 보강 |
| 18 | M-E4 | vendor-boundary-map | E 보강 |
| 19 | M-E5 | README / docs | E 보강 |
| 20 | M-E6 | Superdome 회귀 | E 회귀 |
| 21 | M-F1 | docs/20_json-schema-fields | F 문서 |
| 22 | M-F2 | 3채널 비교 | F 문서 |
| 23 | M-G1 | cycle 학습 추출 | G 학습 |
| 24 | M-G2 | rule/skill/agent 적용 | G 학습 |

**근거**: 의존 그래프 + 사용자 의심 영역 (status) 우선 + 코드 변경은 분석 후 + cycle 학습은 마지막.

---

## 공통 cold-start 가이드 (모든 세션 진입 시)

```
1. docs/ai/tickets/2026-05-06-multi-session-compatibility/INDEX.md (cycle 진입점)
2. SESSION-HANDOFF.md (이전 세션 마지막 commit / 진행 상태)
3. DEPENDENCIES.md (의존 그래프)
4. fixes/INDEX.md (24 ticket 상태표)
5. fixes/M-X##.md (본 ticket — 작업 spec 정본)
```

각 ticket 의 본문 (cold-start 형식) 에 모든 필수 정보 포함. 본 SESSION-PROMPTS.md 는 진입 트리거만.

---

## 공통 종료 절차 (모든 세션 [DONE] 시)

```
1. fixes/M-X##.md status [PENDING] → [DONE] + commit sha 기록
2. fixes/INDEX.md 의 status / worker / commit 컬럼 갱신
3. SESSION-HANDOFF.md 의 "마지막 commit / 시점 / 다음 세션 첫 지시" 갱신
4. NEXT_ACTIONS.md 갱신 (필요 시)
5. 정적 검증: pytest / verify_harness_consistency / verify_vendor_boundary
6. commit: <type>: [M-X## DONE] <요약>
7. git push origin main (github + gitlab 동시)
```

---

# 세션별 프롬프트 (24개)

각 프롬프트는 `/clear` 후 새 세션에 복붙.

---

## Session 1 — M-A1 (status 로직 분석)

```
2026-05-06 multi-session-compatibility cycle worker 진입.

cold-start:
1. docs/ai/tickets/2026-05-06-multi-session-compatibility/SESSION-PROMPTS.md (자율 진행 권한 + 종료 절차)
2. INDEX.md
3. SESSION-HANDOFF.md (이전 세션)
4. fixes/INDEX.md
5. fixes/M-A1.md (본 ticket — 정본)

본 ticket: M-A1 — status 로직 분석 (read-only)

작업:
- common/tasks/normalize/build_status.yml + status_rules.yml + build_errors.yml 분석
- "errors 있는데 success" 시나리오 B 재현 가능한 fixture 식별
- _errors_fragment trigger 위치 전수 검색 (3채널)
- 사용자 결정 4 포인트 정리 (M-A2 입력)

자율 진행: 본 cycle 의 자율 진행 권한 적용 (SESSION-PROMPTS.md 참조). 부가 작업 발견 시 승인 없이 진행.

완료 조건: M-A1.md 의 "완료 조건" 5 항목.

다음 세션: M-A2 (status 의도 결정)
```

---

## Session 2 — M-A2 (status 의도 결정)

```
2026-05-06 cycle Session 2 진입. 이전 ticket M-A1 [DONE].

cold-start: SESSION-PROMPTS.md + SESSION-HANDOFF.md + fixes/INDEX.md + fixes/M-A2.md

본 ticket: M-A2 — status 의도 결정

자율 진행 권한: 사용자 결정 4 포인트도 AI 합리적 default 결정 후 진행.

추천 default (lab 부재 + Additive only cycle):
- (1) 시나리오 B: B-1 (현재 동작 유지) — envelope shape 변경 없음, 호환성 외 영역
- (2) errors severity: (a) 유지 — 단순
- (3) status_rules.yml: (c) 유지 — DEAD CODE 정리도 영향 없음
- (4) status enum: (a) 3 enum 유지 — rule 13 R5 envelope shape 보존

근거: 본 cycle 은 호환성 fallback (Additive only). status 의미 변경은 별도 cycle (사용자 명시 승인) 영역. 의도된 동작 명시만으로 사용자 의심 해소 가능.

만약 M-A1 분석에서 시나리오 B 가 명백한 버그로 판명되면 → B-2 default 로 변경 (errors non-empty → partial).

작업:
- M-A1 분석 결과 확인
- 4 결정 default 기록 + 근거
- M-A3 변경 spec 도출
- decision-log 에 결정 사유 기록

완료: M-A2.md 완료 조건. 다음: M-A3
```

---

## Session 3 — M-A3 (status 코드 변경 + 회귀)

```
2026-05-06 cycle Session 3 진입. 이전 M-A2 [DONE].

cold-start: SESSION-PROMPTS.md + SESSION-HANDOFF.md + fixes/M-A3.md

본 ticket: M-A3 — M-A2 결정 결과 코드 반영 + 회귀

자율 진행: M-A2 default (Case A) 시 → 변경 spec = build_status.yml 의도 주석 추가 + docs/20 (M-F1) 의 status 절 명시. 코드 변경 0 → 회귀 영향 0.

만약 M-A2 가 Case B/C 결정 → M-A3.md 변경 spec 따라 진행 + mock fixture + pytest 회귀.

작업:
- M-A2 결정 Case 확인
- 변경 spec 적용
- 정적 검증 PASS
- mock fixture 추가 (Case B/C)

완료: M-A3.md 완료 조건. 다음: M-A4
```

---

## Session 4 — M-A4 (status ADR)

```
2026-05-06 cycle Session 4 진입. 이전 M-A3 [DONE].

cold-start: SESSION-PROMPTS.md + SESSION-HANDOFF.md + fixes/M-A4.md

본 ticket: M-A4 — ADR (rule 70 R8 trigger 시)

자율 진행: M-A3 Case 별 ADR 의무 판정.
- Case A (의도 주석만) → ADR 불필요. M-A4 SKIP 명시 + close
- Case B (build_status 로직 변경) → CONDITIONAL — envelope shape 동일이면 SKIP, 변경 시 ADR
- Case C (envelope enum 확장) → ADR 의무 (표면 카운트 / rule 13 R5 변경)

작업:
- trigger 판정
- (YES 시) docs/ai/decisions/ADR-2026-05-XX-status-logic.md 작성 (4 섹션)
- (NO 시) M-A4 SKIP commit

완료: M-A4.md 완료 조건. 다음: M-B1
```

---

## Session 5 — M-B1 (account_provision flow 분석)

```
2026-05-06 cycle Session 5 진입. 이전 M-A4 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-B1.md + redfish-gather/library/redfish_gather.py:2157 + redfish-gather/tasks/account_service.yml + redfish-gather/tasks/load_vault.yml

본 ticket: M-B1 — Redfish 공통계정 flow 분석 (read-only)

자율 진행: F49/F50 phase1~4 commit history (13bcbd5a / 7144073e / e6d69538 / 3fa39dec) 자율 분석. flow 다이어그램 (rule 41 Mermaid) 자율 작성.

작업:
- (A) account_service_provision flow Mermaid (AS-IS=F49 / TO-BE=F50 phase4)
- (B) 5 vendor × 단계 매트릭스
- (C) infraops_account_provision 통일 동작
- (D) 신규 4 vendor 추정 + M-D2 web 검색 trigger

완료: M-B1.md 완료 조건. 다음: M-B2
```

---

## Session 6 — M-B2 (5+4 vendor 매트릭스 검증)

```
2026-05-06 cycle Session 6 진입. 이전 M-B1 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-B2.md + M-B1 산출물

본 ticket: M-B2 — F49/F50 9 vendor 매트릭스 정적 검증

자율 진행: 17 row 매트릭스 자율 채움. 신규 4 vendor 는 M-D2 web 검색 결과 의존 → "lab 0 / web 검색 후속" 명시. Gap 4 카테고리 별 list 자율 도출.

작업:
- 17 row 매트릭스 채움
- Gap 4 카테고리 list (M-D3 입력)
- 정적 검증 PASS

완료: M-B2.md 완료 조건. 다음: M-B3
```

---

## Session 7 — M-B3 (공통계정 mock 회귀)

```
2026-05-06 cycle Session 7 진입. 이전 M-B2 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-B3.md + M-B2 산출물

본 ticket: M-B3 — 공통계정 mock fixture 16건 + pytest 회귀

자율 진행: 신규 4 vendor fixture 는 M-D2 web 검색 결과 미정 → "M-D2 [DONE] 후 갱신" placeholder 또는 임시 표준 endpoint 응답으로 작성. 5 vendor mock 은 commit history + 기존 baseline 패턴 따라 자율 작성.

작업:
- mock fixture 16건 (헤더 origin 주석)
- pytest parametrize 회귀 (test_account_service.py)
- pytest PASS + verify_* PASS

완료: M-B3.md 완료 조건. 다음: M-C1
```

---

## Session 8 — M-C1 (vault 동적 로딩 분석)

```
2026-05-06 cycle Session 8 진입. 이전 M-B3 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-C1.md + redfish-gather/tasks/load_vault.yml + ansible.cfg

본 ticket: M-C1 — vault 동적 로딩 분석 (read-only)

자율 진행: load_vault.yml 의 include_vars 메커니즘 + cache 영역 매트릭스 자율 작성. 사용자 답변 (자동 반영 YES, 다음 run 부터) 자율 명시.

작업:
- (A) flow Mermaid
- (B) cache 매트릭스 5 row
- (C) 시나리오 5 (primary password / 새 account / role 변경 / vault rekey / single run 중 변경)
- 사용자 답: YES (다음 run) + single run 중은 NO

완료: M-C1.md 완료 조건. 다음: M-C2
```

---

## Session 9 — M-C2 (cache invalidation 검증)

```
2026-05-06 cycle Session 9 진입. 이전 M-C1 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-C2.md + M-C1 산출물

본 ticket: M-C2 — cache invalidation 정밀 검증

자율 진행: M-C1 의심 영역 5종 (fact_cache / host vars / multi-account / vault decrypt / BMC 권한 cache) 자율 검증. F50 phase4 BMC 권한 cache 와 vault 자동 반영 분리 명시.

작업:
- (A) cache 매트릭스 확정
- (B) 시나리오 5 검증 결과
- (C) 사용자 답변 정리 (YES + 근거)
- BMC vs vault layer 분리

완료: M-C2.md 완료 조건. 다음: M-C3
```

---

## Session 10 — M-C3 (vault 자동 반영 회귀)

```
2026-05-06 cycle Session 10 진입. 이전 M-C2 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-C3.md + M-C2 산출물

본 ticket: M-C3 — mock vault fixture + pytest 회귀

자율 진행: tests/fixtures/vault/dell_v1/v2/v3.yml 자율 작성 (평문 OK, fixture 영역). pytest 5건 자율 추가.

작업:
- mock fixture 3종 (v1/v2/v3) + (선택) encrypted 1
- tests/redfish-probe/test_vault_dynamic_load.py 5건
- pytest PASS

완료: M-C3.md 완료 조건. 다음: M-D1
```

---

## Session 11 — M-D1 (240 cell 호환성 매트릭스)

```
2026-05-06 cycle Session 11 진입. 이전 M-C3 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-D1.md + adapters/redfish/*.yml (27) + schema/baseline_v1/

본 ticket: M-D1 — 9 vendor × N gen × 10 sections 매트릭스 (240 cell)

자율 진행: COMPATIBILITY-MATRIX.md (cycle root) 신설. 24 row × 10 col 매트릭스 자율 채움. 기호 (OK / OK★ / FB / ? / GAP / BLOCK / N/A) 적용. Gap 영역 list (M-D2 입력) 자율 도출.

작업:
- docs/ai/tickets/2026-05-06-multi-session-compatibility/COMPATIBILITY-MATRIX.md 신설
- 240 cell 판정
- Gap list + 우선 분류 (P1/P2/P3)

완료: M-D1.md 완료 조건. 다음: M-D2
```

---

## Session 12 — M-D2 (web 검색 gap)

```
2026-05-06 cycle Session 12 진입. 이전 M-D1 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-D2.md + M-D1 매트릭스 + docs/ai/catalogs/EXTERNAL_CONTRACTS.md

본 ticket: M-D2 — web 검색 gap 영역 (DMTF / vendor docs)

자율 진행: WebSearch / WebFetch 자율 사용 (사용자 명시 "보안 필요없음 / 모든 권한"). agent: web-evidence-collector (model: opus) delegate 가능. M-D1 Gap list 모든 cell 자율 검색.

작업:
- M-D1 Gap list 의 각 cell 검색
- sources 1+ 명시 (rule 96 R1-A)
- EXTERNAL_CONTRACTS.md / COMPATIBILITY-MATRIX.md 갱신
- M-D3 fallback 후보 list

완료: M-D2.md 완료 조건. 다음: M-D3
```

---

## Session 13 — M-D3 (fallback 코드 추가)

```
2026-05-06 cycle Session 13 진입. 이전 M-D2 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-D3.md + M-D2 fallback 후보 list + redfish_gather.py _endpoint_with_fallback (B5)

본 ticket: M-D3 — fallback 코드 추가 (Additive only)

자율 진행: M-D2 의 모든 fallback 후보 자율 적용. **Additive only 의무** (rule 92 R2 + 사용자 명시) — 기존 path 유지 + 새 fallback target 추가만. 변경 규모 큰 경우 vendor / section 별 sub commit 분할.

작업:
- 모든 fallback 후보 코드 적용
- origin 주석 (rule 96 R1)
- 정적 검증 PASS (verify_vendor_boundary / adapter_origin_check / cross_channel_consistency / envelope_change)
- 회귀 fixture 식별 (M-D4 입력)

완료: M-D3.md 완료 조건. 다음: M-D4
```

---

## Session 14 — M-D4 (전 vendor 호환성 회귀)

```
2026-05-06 cycle Session 14 진입. 이전 M-D3 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-D4.md + M-D3 변경 list

본 ticket: M-D4 — 호환성 회귀 + baseline 검증

자율 진행: mock fixture N건 자율 추가 (M-D3 변경 모든 영역). pytest parametrize 회귀. 8 baseline 회귀 PASS 확인 — Additive only 검증.

작업:
- mock fixture N건 (origin 주석)
- pytest parametrize 회귀
- baseline 8건 PASS
- envelope_change_check 통과

완료: M-D4.md 완료 조건. 다음: M-E1
```

---

## Session 15 — M-E1 (HPE Superdome web 검색)

```
2026-05-06 cycle Session 15 진입. 이전 M-D4 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-E1.md + adapters/redfish/hpe_*.yml

본 ticket: M-E1 — HPE Superdome web 검색

자율 진행: WebSearch / WebFetch 자율 사용. Superdome Flex / Flex 280 / 2 / X / Integrity 5 모델 자율 조사.

추천 default 결정 (사용자 결정 (a)/(b)):
- **(a) HPE sub-line** — Manufacturer string 이 "HPE" 동일 가능성 높음. adapter 위치 = `adapters/redfish/hpe_superdome*.yml`. 기존 hpe vendor entry 확장.
- 만약 web 검색 결과 Manufacturer 가 별도 string ("HPE Superdome") 이면 (b) 별도 vendor 결정.

작업:
- (A) Manufacturer / (B) 모델 매트릭스 / (C) endpoint / (D) OEM / (E) 펌웨어
- (F) 결정 (a)/(b) — default (a)
- sources URL list (rule 96 R1-A)
- EXTERNAL_CONTRACTS.md HPE Superdome entry
- M-E2 adapter spec 도출

완료: M-E1.md 완료 조건. 다음: M-E2
```

---

## Session 16 — M-E2 (Superdome adapter 작성)

```
2026-05-06 cycle Session 16 진입. 이전 M-E1 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-E2.md + M-E1 결정 (a)/(b) + adapters/redfish/huawei_ibmc.yml (lab 부재 패턴)

본 ticket: M-E2 — Superdome adapter 3종 작성 (priority=70~90)

자율 진행: M-E1 결정 따라 adapter 위치 + adapter YAML 자율 작성. _FALLBACK_VENDOR_MAP / bmc_names 갱신 (필요 시).

작업:
- adapter YAML 3종 (Flex 280 / Flex / Legacy)
- origin 주석 + tested_against + lab=부재
- score-adapter-match 검증
- 정적 검증 PASS

완료: M-E2.md 완료 조건. 다음: M-E3
```

---

## Session 17 — M-E3 (ai-context vendors)

```
2026-05-06 cycle Session 17 진입. 이전 M-E2 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-E3.md + .claude/ai-context/vendors/hpe.md

본 ticket: M-E3 — ai-context Superdome entry

자율 진행: M-E1 결정 (a) 시 hpe.md 갱신 / (b) 시 superdome.md 신규.

작업:
- M-E1 결정 따라 ai-context 갱신/신규

완료: M-E3.md 완료 조건. 다음: M-E4
```

---

## Session 18 — M-E4 (vendor-boundary-map 갱신)

```
2026-05-06 cycle Session 18 진입. 이전 M-E3 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-E4.md + .claude/policy/vendor-boundary-map.yaml

본 ticket: M-E4 — vendor-boundary-map.yaml Superdome entry

자율 진행: M-E1/E2 결정 따라 yaml 갱신. verify_vendor_boundary PASS.

작업:
- vendor-boundary-map.yaml 갱신
- verify_vendor_boundary PASS

완료: M-E4.md 완료 조건. 다음: M-E5
```

---

## Session 19 — M-E5 (README / docs 갱신)

```
2026-05-06 cycle Session 19 진입. 이전 M-E4 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-E5.md + README.md + docs/13_redfish-live-validation.md + docs/19_decision-log.md

본 ticket: M-E5 — Superdome 추가를 README / docs 반영

자율 진행: 4 문서 자율 갱신.

작업:
- README.md 멀티벤더 list (Superdome 명시)
- docs/13_redfish-live-validation.md Round entry
- docs/19_decision-log.md cycle 2026-05-06 entry
- (선택) CLAUDE.md 벤더 표

완료: M-E5.md 완료 조건. 다음: M-E6
```

---

## Session 20 — M-E6 (Superdome 회귀 mock)

```
2026-05-06 cycle Session 20 진입. 이전 M-E5 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-E6.md + tests/fixtures/redfish/

본 ticket: M-E6 — Superdome mock fixture + pytest 회귀

자율 진행: mock fixture 6종 + pytest 5+건 자율 작성. ProLiant Additive only 검증 포함.

작업:
- tests/fixtures/redfish/hpe_superdome/*.json 6종
- tests/redfish-probe/test_superdome_compat.py 5+건
- pytest PASS + baseline 8건 PASS

완료: M-E6.md 완료 조건. 다음: M-F1
```

---

## Session 21 — M-F1 (docs/20_json-schema-fields 신설)

```
2026-05-06 cycle Session 21 진입. 이전 M-E6 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-F1.md + common/tasks/normalize/build_output.yml + schema/sections.yml + schema/field_dictionary.yml + M-A1 분석 결과 + M-A2 결정

본 ticket: M-F1 — docs/20_json-schema-fields.md 신설 (envelope 13 + sections 10 + 65 entries)

자율 진행: 10 절 모두 자율 작성. M-A 의 status 판정 규칙 / M-C 의 vault 자동 반영 / M-D 의 호환성 매트릭스 등 본 cycle 학습 반영.

작업:
- docs/20_json-schema-fields.md 신설
- field_dictionary 65 entries 전수 list
- M-A1/A2 결과 반영

완료: M-F1.md 완료 조건. 다음: M-F2
```

---

## Session 22 — M-F2 (3채널 비교)

```
2026-05-06 cycle Session 22 진입. 이전 M-F1 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-F2.md + M-F1 산출물 + schema/baseline_v1/ + os-gather/, esxi-gather/, redfish-gather/ tasks

본 ticket: M-F2 — Redfish/OS/ESXi 3채널 JSON 키 비교

자율 진행: 5절 (sections 매트릭스 / 같은 키 다른 의미 / 채널 고유 키 / 정규화 차이 / status 차이) 자율 작성.

작업:
- M-F1 docs/20 의 채널별 차이 절 확장 또는 부록

완료: M-F2.md 완료 조건. 다음: M-G1
```

---

## Session 23 — M-G1 (cycle 학습 추출)

```
2026-05-06 cycle Session 23 진입. 이전 M-F2 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-G1.md + 본 cycle 모든 산출물 + commit log

본 ticket: M-G1 — cycle 학습 추출 + 보강 후보

자율 진행: 학습 패턴 자율 추출 (멀티 세션 / lab 부재 / status 의도 / vault 자동반영 / 240 cell / 24 ticket cold-start). HARNESS-RETROSPECTIVE.md 자율 작성.

작업:
- HARNESS-RETROSPECTIVE.md 신설
- 학습 패턴 N건 (4 절씩)
- rule/skill/agent/hook/docs 보강 후보
- 다음 cycle 권장

완료: M-G1.md 완료 조건. 다음: M-G2
```

---

## Session 24 — M-G2 (rule/skill/agent 적용 + cycle 종료)

```
2026-05-06 cycle Session 24 진입. 이전 M-G1 [DONE].

cold-start: SESSION-PROMPTS.md + fixes/M-G2.md + M-G1 보강 후보 + .claude/rules/, skills/, agents/, scripts/ai/hooks/

본 ticket: M-G2 — 하네스 보강 적용 + cycle 종료

자율 진행: M-G1 모든 보강 후보 자율 적용. ADR (rule 70 R8 trigger 시) 자율 작성. surface-counts.yaml 갱신. cycle 종료 entry NEXT_ACTIONS.

작업:
- 모든 rule / skill / agent / hook 적용
- ADR 작성 (trigger 해당 시)
- surface-counts.yaml 갱신
- INDEX.md 의 "현재 상태" → [DONE]
- HARNESS-RETROSPECTIVE.md 의 cycle 종료 시점 갱신
- NEXT_ACTIONS.md cycle 종료 entry
- verify_harness_consistency PASS
- 최종 commit + push

완료: cycle 종료 — 본 cycle 의 모든 24 ticket [DONE].
```

---

## Cycle 종료 후 (Session 25 — 선택)

cycle 종료 후 사용자 다음 cycle 진입 시:

```
2026-05-06 multi-session-compatibility cycle 종료 확인.

상태 점검:
1. docs/ai/NEXT_ACTIONS.md (cycle 종료 entry)
2. docs/ai/tickets/2026-05-06-multi-session-compatibility/HARNESS-RETROSPECTIVE.md (학습)
3. surface-counts.yaml (변동 카운트)
4. pytest 108 + N 회귀 PASS

다음 cycle 진입:
- 사용자 사이트 BMC 도입 시 → capture-site-fixture skill (사이트 fixture 캡처)
- 정기 self-improvement → harness-evolution-coordinator
- F44~F47 vault / baseline / OEM tasks (lab 도입 시)
- F22 / F33 사고 재현 후속 (외부 의존)
```

---

## 비상 시 (작업 막힘)

worker 세션 진행 중 막힘:

1. **외부 의존 발견** (lab / 사용자 결정 / 환경 한계) → 해당 ticket status [BLOCKED:사유] 명시 + 다음 ticket 으로 skip
2. **rule 위반 의심** → SESSION-HANDOFF.md 에 의심 사유 명시 + 사용자 명시 승인 요청 (예외 영역만)
3. **회귀 fail** → M-D3 / M-A3 같은 코드 변경 ticket 의 Additive only 위반 의심 → 해당 변경 revert + 재진입

→ **정지 금지** — 막힘 발견 시 다음 ticket 으로 자율 진행. 막힌 ticket 은 SESSION-HANDOFF 에 명시.

---

## 관련

- INDEX.md
- SESSION-HANDOFF.md
- DEPENDENCIES.md
- fixes/INDEX.md
- fixes/M-A1.md ~ M-G2.md (24 cold-start ticket)
- rule 26 (multi-session-guide) — 본 cycle 은 단일 세션 순차 진행 모드 (사용자 명시)
- rule 93 R1+R4 (자율 push)
- 자율 진행 권한 (사용자 명시 2026-05-06)
