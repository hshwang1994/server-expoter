# ECC Adoption Summary — server-exporter

> ECC (Everything Claude Code) 채택 현황. server-exporter는 신규 하네스 도입 단계.

## 도입 현황

| 카테고리 | 상태 | 비고 |
|---|---|---|
| `.claude/rules/` | Plan 1 진행 중 | clovirone 풀스펙 포팅 (30 rules 목표) |
| `.claude/skills/` | Plan 2 예정 | 약 38 skills 목표 |
| `.claude/agents/` | Plan 2 예정 | 약 49 agents 목표 |
| `.claude/policy/` | Plan 1 완료 | 10 YAML |
| `.claude/role/` | Plan 1 완료 | 6 (gather/output-schema/infra/qa/po/tpm) |
| `.claude/ai-context/` | Plan 1 진행 중 | 6 디렉터리 |
| `.claude/templates/` | Plan 1 예정 | 10 (prototype-skeleton 제외) |
| `.claude/commands/` | Plan 1 예정 | 5 |
| `scripts/ai/hooks/` | Plan 1 완료 | 19 Python hooks + install-git-hooks.sh |
| `scripts/ai/` supporting | Plan 1 완료 | 8 (policy_loader / detect_session_context / verify_* / check_*) |
| `docs/ai/` | Plan 3 예정 | 운영 메타 문서 |

## 출처 / 영감

- `clovirone-base/.claude/` — Java/Spring/Vue/MyBatis/multi-customer/plugin 도메인 풀스펙 하네스
- 풀스펙 포팅 정책 (어휘/경로/도메인 substitution)
- 자기개선 루프 6단계 (observer → architect → reviewer → governor → updater → verifier)

## 도입 결정 근거

설계서 `docs/superpowers/specs/2026-04-27-harness-refactor-design.md` §1~2 참조.
3 세션 분할: Plan 1 (Foundation) / Plan 2 (Skills + Agents) / Plan 3 (Docs/AI + Verification).

## 운영 부담 모니터링

- 자기개선 루프 7 agents (architect/coordinator/governor/observer/reviewer/updater/verifier) 실 사용 빈도 — 1 cycle 직접 돌려본 후 keep/drop 재결정 (ADR로 기록).
- skill/agent 본문이 server-exporter 도메인을 충분히 반영하는지 — 각 skill/agent에 server-exporter 실 파일 경로 1개 이상 인용 의무.
