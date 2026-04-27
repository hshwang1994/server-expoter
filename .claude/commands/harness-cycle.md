---
description: server-exporter 하네스 자기개선 1 cycle 트리거. 6단계 파이프라인 (observer → architect → reviewer → governor → updater → verifier).
argument-hint: "[focus area] 예: rules, skills, agents, all"
---

# /harness-cycle

server-exporter AI 하네스 자기개선 1 cycle을 수동 트리거.

## 6단계 파이프라인

| 단계 | Agent | 역할 |
|---|---|---|
| 1. Observe | `harness-observer` | 측정 + 1차 해석 (rule 28 측정 대상 재측정 + drift 검출) |
| 2. Architect | `harness-architect` | 변경 명세 (diff 수준) — 구현 안 함, 설계만 |
| 3. Review | `harness-reviewer` | 명세 검수 (자가 승인 금지, rule 25 R7) |
| 4. Govern | `harness-governor` | Tier 1/2/3 분류 + 사용자 에스컬레이션 결정 |
| 5. Update | `harness-updater` | 승인된 명세 적용 (Tier 1 자동 / Tier 2 사용자 승인 후) |
| 6. Verify | `harness-verifier` | verify_harness_consistency.py + smoke test |

## 호출 시점

- 매주 정기 (advisory)
- 측정 대상 drift 누적 (rule 28)
- 사용자 피드백 수렴 후
- skill/rule 신설 후 일관성 검증

## 입력

- `focus area`: `rules` / `skills` / `agents` / `policy` / `all`

## 출력

- `docs/ai/harness/cycle-NNN.md` — 본 cycle 로그
- 변경된 파일 commit (Tier 1만 자동, Tier 2는 사용자 승인 후)
- 다음 cycle 시작점 표기

## 두 루프 분리

- 제품 루프 (wave-coordinator) ↔ 하네스 루프 (본 cycle)
- 서로 대상 파일 침범 금지

## 정본

- skill: `.claude/skills/harness-cycle/SKILL.md` (Plan 2에서 작성)
- workflow: `docs/ai/workflows/HARNESS_EVOLUTION_MODEL.md` (Plan 3에서 작성)
- governance: `docs/ai/workflows/HARNESS_GOVERNANCE.md`
