# Harness Change Policy — server-exporter

> 하네스 자체 변경 (`.claude/`, `docs/ai/`, `scripts/ai/`) 거버넌스 정책.
> Tier 1/2/3 분류 + 승인 경로.

## Tier 분류

| Tier | 예시 | 승인 |
|---|---|---|
| **1 (자동허용)** | docs 초안 / stale 정정 / catalogs 갱신 / surface-counts 갱신 / cycle 로그 작성 | reviewer APPROVE 후 자동 |
| **2 (승인필요)** | rules / agents / skills / policy 추가/수정 / templates 추가 / commands 변경 | governor 심사 + 사용자 4요소 승인 (rule 23 R1) |
| **3 (절대금지)** | settings 권한 완화 / 보호 경로 제거 / 자가 검수 허용 / control plane 우회 | 사용자 명시 에스컬레이션만, 자동 적용 금지 |

## Tier 1 자동허용 절차

1. observer 발견 / architect 명세 / reviewer APPROVE
2. updater 적용
3. verifier 검증
4. cycle 로그 작성 (`docs/ai/harness/cycle-NNN.md`)

## Tier 2 승인 필요 절차

1. observer / architect / reviewer 절차 동일
2. governor가 사용자에게 4 요소 포맷 승인 요청 (rule 23 R1):
   - 무엇 (한 줄)
   - 왜
   - 영향 (파일 N개 / rules M건)
   - 결정 필요 (진행 / 조정 / 취소)
3. 사용자 명시 승인 후 updater 적용

## Tier 3 절대 금지

다음은 자동 cycle에서 절대 적용 안 함:
- `.claude/settings.json`의 deny → allow 변경
- 보호 경로 (`vault/**`, `schema/baseline_v1/**`, `Jenkinsfile*`) 제거
- 자가 검수 허용 (rule 25 R7 우회)
- bypassPermissions 활성화

이런 변경은 사용자가 직접 PR 생성 + 명시 승인 + 별도 ADR 필수.

## 두 루프 분리

- 제품 루프 (wave-coordinator): `os/esxi/redfish-gather`, `common`, `adapters`, `schema`, `tests`
- 하네스 루프 (harness-evolution-coordinator): `.claude/`, `docs/ai/`, `scripts/ai/`, `CLAUDE.md`

서로 침범 금지. 위반 시 cycle abort + 사용자 보고.

## 자가 검수 금지 (rule 25 R7)

각 단계의 결과를 동일 agent가 검수하지 말 것:
- architect 명세 → harness-reviewer (별도)
- updater 적용 → harness-verifier (별도)
- 도메인 워커 결과 → 별도 reviewer agent

## 관련 정본

- rule 70 (docs-and-evidence-policy)
- rule 25 (parallel-agents) R7
- agent: harness-evolution-coordinator + 6 sub
- workflow: `docs/ai/workflows/HARNESS_GOVERNANCE.md`
