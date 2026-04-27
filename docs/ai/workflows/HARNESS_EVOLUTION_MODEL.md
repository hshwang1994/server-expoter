# Harness Evolution Model — server-exporter

> 자기개선 루프 6단계 파이프라인 정본.

## 6단계

```
observer → architect → reviewer → governor → updater → verifier
```

| 단계 | Agent | 입력 | 출력 |
|---|---|---|---|
| 1. Observe | harness-observer | (trigger: cycle 시작) | drift 후보 + 1차 해석 |
| 2. Architect | harness-architect | observer 결과 | 변경 명세 (diff 수준) |
| 3. Review | harness-reviewer | architect 명세 | APPROVE / REVISE / REJECT |
| 4. Govern | harness-governor | reviewer APPROVE | Tier 1/2/3 분류 + 사용자 승인 (Tier 2) |
| 5. Update | harness-updater | governor 결정 | 실 파일 변경 + commit |
| 6. Verify | harness-verifier | updater 적용 | smoke test + verify_harness_consistency |

## 두 루프 분리

- 제품 루프 (wave-coordinator): 도메인 코드
- 하네스 루프 (harness-evolution-coordinator): 본 모델

서로 침범 금지 (rule 70 + 두 루프 분리 정책).

## Tier 정책

상세는 `docs/ai/policy/HARNESS_CHANGE_POLICY.md`.

- Tier 1: 자동허용 (docs / catalogs / cycle log)
- Tier 2: governor 심사 + 사용자 승인 (rules / agents / skills / policy)
- Tier 3: 절대 금지 (settings 권한 완화 / 보호 경로 제거)

## 호출 방법

- 수동: `/harness-cycle` (사용자 명시)
- 정기: 별도 cron (현재 미설정 — 운영 정책 결정 후)
- 사고 대응: `/harness-full-sweep` (전수조사)

## cycle 로그

매 cycle 종료 후 `docs/ai/harness/cycle-NNN.md` 작성.

내용:
- cycle 번호 / 일자 / trigger
- observer 발견 list
- architect 명세 list
- reviewer / governor 결정
- updater 적용 commit list
- verifier 결과
- 다음 cycle 시작점

## 관련

- agent: harness-evolution-coordinator + 6 sub
- rule: 28 (empirical-verification-lifecycle), 70 (docs-and-evidence)
- skill: harness-cycle, harness-full-sweep
- policy: HARNESS_CHANGE_POLICY.md
