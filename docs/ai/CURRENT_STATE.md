# server-exporter 현재 상태

## 일자: 2026-04-27

## 요약

server-exporter AI 하네스 Plan 1 (Foundation) 완료. clovirone-base 풀스펙 하네스를 server-exporter 도메인으로 1:1 포팅. 신규 약 100 파일 추가. 기존 코드/문서 무수정.

## Plan 1 Phase 완료 현황

| Phase | 산출물 | 파일 수 | commit |
|---|---|---|---|
| 1. Skeleton | settings.json + 19 hooks + 8 supporting scripts | 28 | d87af96 |
| 2. Policy/Meta | 10 policy + 6 role + 12 ai-context + 10 templates + 5 commands | 43 | 31526c3 |
| 3. Rules | 29 rules (00, 10-13, 20-22, 23-28, 30-31, 40-41, 50, 60, 70, 80, 90-93, 95-97) | 29 | ee82f1b |
| 4. Verify + CLAUDE.md | CLAUDE.md Tier 0 보강 + verify 통과 | 1 mod + baseline 갱신 | (이번 commit) |

## 채널별 상태

| 채널 | 상태 | 비고 |
|---|---|---|
| os-gather | ok | 기존 그대로 |
| esxi-gather | ok | 기존 그대로 |
| redfish-gather | ok | 기존 그대로 |

## 어댑터 매트릭스 (기존)

| Vendor | 어댑터 수 | 검증된 펌웨어 | Baseline |
|---|---|---|---|
| Dell | 3 (idrac8 / idrac9 / idrac generic) | 5.x / 6.x | 있음 |
| HPE | 4 (ilo5 / ilo6 / synergy / generic) | 2.x | 있음 |
| Lenovo | 2 (xcc / xcc_legacy) | XCC | 있음 |
| Supermicro | 3 (x12 / x11 / legacy) | 일부 | 일부 |
| Cisco | 1 (cimc) | 초기 | 일부 |
| generic | 1 (redfish_generic) | — | — |

## Schema 상태 (기존)

- sections.yml: 10 섹션
- field_dictionary.yml: 28 Must + Nice + Skip
- baseline_v1: 7+ vendor

## 다음 작업 (Plan 2)

- [ ] `.claude/skills/` — 약 38 skills
- [ ] `.claude/agents/` — 약 49 agents
- [ ] surface-counts.yaml 자동 갱신

## 다음 작업 (Plan 3)

- [ ] `docs/ai/` 운영 메타 문서 골격
  - CURRENT_STATE.md (본 파일, 추가 갱신)
  - NEXT_ACTIONS.md
  - catalogs/ (8종)
  - decisions/ (ADR)
  - policy/, workflows/, harness/, handoff/, impact/, incoming-review/, roadmap/, onboarding/
- [ ] 자기개선 루프 dry-run 검증
- [ ] verify_harness_consistency.py final 통과 (skills/agents 작성 후)

## 정본 reference

- `CLAUDE.md` Tier 0 정본
- `GUIDE_FOR_AI.md`, `REQUIREMENTS.md`, `README.md`
- `docs/01_jenkins-setup` ~ `docs/19_decision-log`
- 설계서: `docs/superpowers/specs/2026-04-27-harness-refactor-design.md`
- 실행 계획: `docs/superpowers/plans/2026-04-27-harness-refactor-plan-1-foundation.md`
