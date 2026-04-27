---
description: server-exporter 하네스 전수조사 + 일괄 개선 (1회성 대형). 시니어 엔지니어 인수 모드.
argument-hint: "(없음)"
---

# /harness-full-sweep

server-exporter 하네스 전 영역 전수조사 + Tier 1/2 일괄 수정 (Tier 3 제외).

## 호출 시점

**사용자 명시 요청 시에만**. 자동 트리거 금지.
- "하네스 전체 점검해줘"
- "인수 리뷰"
- "전수조사"
- "full sweep"

## 점검 영역 (병렬 Agent)

| Agent | 영역 |
|---|---|
| `harness-observer` × 9 (병렬) | skills / agents / rules / docs / scripts / hooks / settings / templates / role / ai-context |
| `harness-architect` | 발견된 모든 drift를 명세화 |
| `harness-reviewer` | 자기 검수 금지 (별도 reviewer가 수정 명세 검수) |
| `harness-governor` | Tier 분류 |
| `harness-updater` | Tier 1·2 일괄 적용 |
| `harness-verifier` | 통합 검증 |

## Tier 분류

| Tier | 예시 | 적용 |
|---|---|---|
| 1 | docs 초안 / stale 정정 | 자동 |
| 2 | rules / agents / skills 변경 | governor 심사 |
| 3 | settings 권한 완화 / 보호 경로 제거 | 사용자 에스컬레이션 (스킵) |

## 출력

- `docs/ai/harness/full-sweep-YYYY-MM-DD.md` — 보고서
- 일괄 commit (Tier별 분할)

## 정본

- skill: `.claude/skills/harness-full-sweep/SKILL.md` (Plan 2)
- workflow: `docs/ai/workflows/HARNESS_GOVERNANCE.md` (Plan 3)
