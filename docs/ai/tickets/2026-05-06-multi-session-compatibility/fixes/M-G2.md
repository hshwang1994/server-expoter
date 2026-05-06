# M-G2 — rule / skill / agent / hook 후보 정리 + 적용

> status: [PENDING] | depends: M-G1 | priority: P3 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-G1 학습 추출 결과를 실제 하네스 보강 (rule / skill / agent / hook 추가/갱신) 으로 적용.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `.claude/rules/`, `.claude/skills/`, `.claude/agents/`, `scripts/ai/hooks/`, `docs/ai/decisions/ADR-*.md` (rule 70 R8 trigger 시) |
| 리스크 | MED (rule 변경은 표면 카운트 변경 → ADR 의무) |
| 진행 확인 | M-G1 [DONE] 보강 후보 list |

## 작업 spec

### (A) Rule 보강 (M-G1 후보 따라)

각 rule 변경 시:
1. rule 본문 변경 (Default / Allowed / Forbidden + Why + 재검토)
2. `.claude/policy/surface-counts.yaml` 갱신 (변동 있으면)
3. ADR 작성 (rule 70 R8 trigger 시 — rule 본문 의미 변경 / 표면 카운트 / 보호 경로)
4. `verify_harness_consistency.py` PASS

### (B) Skill 신규 / 갱신

각 skill:
1. `.claude/skills/<skill-name>/SKILL.md` 작성 (frontmatter + 본문)
2. surface-counts.yaml 의 skills 카운트 갱신
3. SKILL.md 형식 hook (`pre_commit_skill_format.py`) PASS

### (C) Agent 신규 / 갱신

각 agent:
1. `.claude/agents/<agent-name>.md` 작성 (frontmatter — name, description, tools, model)
2. surface-counts.yaml 의 agents 카운트 갱신
3. agent 정합성 hook PASS

### (D) Hook 신규

각 hook:
1. `scripts/ai/hooks/<hook-name>.py` 작성 (self-test 포함)
2. `.claude/settings.json` (해당 시) 또는 `verify_harness_consistency.py` 의 EXPECTED_REFERENCES 갱신
3. self-test PASS

### (E) ADR 작성 (rule 70 R8 trigger 시)

| trigger | ADR 필요 |
|---|---|
| rule 본문 의미 변경 | YES |
| 표면 카운트 (rules/skills/agents/policies) 변경 | YES |
| 보호 경로 정책 변경 | YES |

ADR 4 섹션: 컨텍스트 / 결정 / 결과 / 대안 비교

### (F) 검증

- `python scripts/ai/verify_harness_consistency.py`
- `python scripts/ai/verify_vendor_boundary.py`
- 모든 신규 hook self-test (`--self-test`)
- skill / agent 의 SKILL.md / agent.md 형식 hook PASS

## M-G1 예상 보강 list (Session-0 예측 — M-G1 산출물로 확정)

| 항목 | 신규/갱신 | 영향 |
|---|---|---|
| rule 26 R6 (multi-session-guide) | 갱신 — orchestrator 메타 | rule 본문 의미 변경 → ADR |
| rule 50 R2 (vendor 추가) | 갱신 — 단계 10 (사이트 fixture 향후 trigger) | rule 본문 변경 → ADR |
| skill: multi-session-orchestrator | 신규 | surface 카운트 +1 → ADR |
| skill: verify-status-logic | 신규 | surface 카운트 +1 |
| skill: 또는 docs/21_vault-operations.md | docs 신규 | 문서만 |
| agent: ticket-orchestrator | 신규 (cycle 분해 자동화) | surface 카운트 +1 → ADR |
| hook: pre_commit_ticket_consistency.py | 신규 | hooks 카운트 +1 |
| script: scripts/ai/measure_compatibility_matrix.py | 신규 | 측정 자동화 (rule 28 #11) |

→ M-G1 [DONE] 결과로 본 list 확정.

## 회귀 / 검증

- 모든 정적 검증 PASS
- pytest 회귀 (영향 가능 시)
- ADR 4 섹션 정합성

## risk

- (HIGH) rule 본문 변경 = 모든 작업의 정본 영향. M-G1 추출 정확성 의무
- (MED) 표면 카운트 변경 = ADR 의무 (rule 70 R8)
- (LOW) skill / agent / hook 신규는 surface 카운트 기록만

## 완료 조건

- [ ] M-G1 보강 후보 모두 적용 (rule / skill / agent / hook / docs)
- [ ] ADR 작성 (trigger 해당 시)
- [ ] surface-counts.yaml 갱신
- [ ] verify_harness_consistency PASS
- [ ] cycle 종료 — INDEX.md 의 "현재 상태" → [DONE]
- [ ] SESSION-HANDOFF.md "마지막 commit / 다음 세션 첫 지시" 채움
- [ ] commit: `harness: [M-G2 DONE] cycle 2026-05-06 학습 적용 — rule N / skill N / agent N / hook N`
- [ ] NEXT_ACTIONS.md 갱신 (cycle 종료 entry)

## 다음 세션 첫 지시 템플릿

```
M-G2 cycle 학습 적용 진입.

선행: M-G1 [DONE]

읽기 우선순위:
1. fixes/M-G2.md
2. M-G1 산출물 (HARNESS-RETROSPECTIVE.md)
3. .claude/rules/ + skills/ + agents/ 기존 패턴
4. .claude/policy/surface-counts.yaml
5. rule 70 R8 (ADR trigger)

작업:
1. M-G1 보강 후보 별 적용
2. ADR 작성 (trigger 해당 시)
3. surface-counts.yaml 갱신
4. verify_harness_consistency PASS
5. cycle 종료 entry — NEXT_ACTIONS.md
```

## 관련

- rule 70 R7 (cycle 자문) + R8 (ADR 의무 trigger)
- skill: write-cold-start-ticket (본 cycle 메타)
- 이전 cycle 적용 패턴: cycle-017 보강 (commit b5f523d2 — B1~B8 + D + E 일괄)
