# M-G1 — 본 cycle 학습 추출

> status: [PENDING] | depends: A~F all [DONE] | priority: P3 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "지금까지 작업한내용중에 추가 하네스에 학습시켜야하는것들이있으면 추가 하네스 개선해줘"

→ 본 cycle (multi-session-compatibility) 진행 중 발견된 학습 패턴 추출. cycle 종료 시점.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/ai/tickets/2026-05-06-multi-session-compatibility/HARNESS-RETROSPECTIVE.md` (신설) |
| 리스크 | LOW |
| 진행 확인 | A~F 모든 ticket [DONE] 후 진입 |

## 학습 추출 후보 (Session-0 예상)

### 멀티 세션 패턴

- **본 cycle 자체** — 메인 오케스트레이터 (Session-0) 가 ticket 만 작성, worker 세션이 실 작업
- 학습: rule 26 (multi-session-guide) 의 정신을 **단일 cycle 안 다중 worker** 로 확장
- skill 후보: `multi-session-orchestrator` (메인 세션 ticket 분해 자동화)

### lab 부재 vendor 추가 패턴

- F44~F47 (cycle-019 phase 2) + Superdome (본 cycle M-E) → lab 0 vendor 추가 패턴 확립
- 학습: priority=80, web sources only, capture-site-fixture skill 향후 갱신 의무
- rule 후보: rule 50 R2 단계 9 → 10 으로 확장 (web sources 의무 + 향후 사이트 fixture trigger)

### status 로직 의도 vs 사용자 기대 차이

- M-A1 분석 결과 (시나리오 B 의심 영역) → 의도된 동작 vs 버그 식별
- 학습: envelope 필드의 의미 명시 (M-F1 docs/20) 가 중요. drift 시 사용자 의심 발생
- skill 후보: `verify-status-logic` (build_status.yml 변경 시 시나리오 매트릭스 자동 검증)

### vault 자동 반영 검증 패턴

- M-C1~M-C3 → ansible include_vars 의 cache 메커니즘 명시
- 학습: vault 운영 가이드에 "다음 run 부터 자동 반영" 명시 필요
- docs 후보: `docs/21_vault-operations.md` 신설 또는 rotate-vault skill 보강

### 호환성 매트릭스 240 cell

- M-D1~M-D4 → 9 vendor × N gen × 10 sections = 240 cell 호환성 추적
- 학습: COMPATIBILITY-MATRIX 가 cycle 2026-05-01 35건 → cycle 2026-05-06 240 cell 확장
- 자동화 후보: `scripts/ai/measure_compatibility_matrix.py` (rule 28 측정 #11 외부 계약 lifecycle 추가)

### 24 ticket cold-start 형식

- 본 cycle ticket 24건 → 다음 세션 cold-start 가능
- 학습: write-cold-start-ticket skill 의 효과 검증
- 보강 후보: ticket 자동 정합성 검증 hook (`pre_commit_ticket_consistency.py`)

## 작업 spec — HARNESS-RETROSPECTIVE.md 구조

```markdown
# Harness Retrospective — 2026-05-06 multi-session-compatibility

## cycle 개요
- 시작: 2026-05-06 (Session-0 ticket 작성)
- 종료: (M-G1/G2 [DONE] 시점)
- ticket: 24건 (M-A1~G2)
- worker 세션: N개 (worker 별 commit list)

## 학습 패턴 N건

### 학습 1: <제목>
- **무엇이 일어났나** (관찰)
- **왜 발생** (원인)
- **무엇을 학습** (insight)
- **하네스 보강 후보** (rule / skill / agent / hook / docs)

### 학습 2: ...

(각 학습 별 4 절)

## rule 보강 후보

| rule | 변경 spec |
|---|---|
| rule 26 R6 | multi-session-orchestrator 메타 추가 |
| rule 50 R2 | 단계 10 (사이트 fixture 향후 trigger) |
| ... | ... |

## skill 보강 후보

| skill | 신규/갱신 |
|---|---|
| multi-session-orchestrator | 신규 |
| verify-status-logic | 신규 |
| ... | ... |

## agent 보강 후보

| agent | 신규/갱신 |
|---|---|
| ticket-orchestrator | 신규 (cycle 분해 자동화) |
| ... | ... |

## hook 보강 후보

| hook | 신규/갱신 |
|---|---|
| pre_commit_ticket_consistency.py | 신규 |
| ... | ... |

## docs 신설 후보

| docs | 의도 |
|---|---|
| docs/20_json-schema-fields.md | M-F1 산출물 |
| docs/21_vault-operations.md | M-C 결과 정본화 |
| ... | ... |

## 다음 cycle 권장

- ...
```

## 회귀 / 검증

- (문서만)

## risk

- (LOW) cycle 종료 시점에 학습 누락 — A~F ticket 의 산출물 모두 보강 의무

## 완료 조건

- [ ] HARNESS-RETROSPECTIVE.md 신설
- [ ] 학습 패턴 N건 (4 절씩)
- [ ] 보강 후보 5 종 (rule / skill / agent / hook / docs)
- [ ] 다음 cycle 권장
- [ ] commit: `docs: [M-G1 DONE] cycle 2026-05-06 학습 추출 N건`

## 다음 세션 첫 지시 템플릿

```
M-G1 cycle 학습 추출 진입.

선행: A~F 모든 ticket [DONE]

읽기 우선순위:
1. fixes/M-G1.md
2. 본 cycle 의 모든 ticket 산출물 (M-A1~F2)
3. SESSION-HANDOFF.md (worker 세션 진행 history)
4. commit log (본 cycle commit 들)

작업:
1. 학습 패턴 추출 (위 후보 6 + 추가)
2. HARNESS-RETROSPECTIVE.md 작성
3. M-G2 입력 — rule/skill/agent/hook/docs 보강 후보 list
```

## 관련

- rule 70 R7 (cycle 자문)
- skill: write-cold-start-ticket (본 cycle 메타 skill)
- 이전 RETROSPECTIVE: `docs/ai/tickets/2026-05-01-gather-coverage/HARNESS-RETROSPECTIVE-2026-05-01.md` (있으면 참조)
