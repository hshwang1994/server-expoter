# server-exporter 다음 작업 (NEXT_ACTIONS)

> 우선순위가 정해진 다음 작업 list. CURRENT_STATE의 후속.

## 일자: YYYY-MM-DD

## P0 — 즉시 (이번 세션)

- [ ] {작업} — {담당 role / agent} — {예상 시간}

## P1 — 다음 세션

- [ ] {작업} — {WHY: 사유} — {연관 rule/skill}

## P2 — 백로그

- [ ] {작업}

## 의존성 체인

```
P0[A] → P1[B]    # B는 A 완료 후 가능
P0[A] → P1[C]
P1[B] + P1[C] → P2[D]
```

## 결정 필요

| 항목 | 결정자 | 마감 | 영향 |
|---|---|---|---|
| | | | |

## 정본 reference

- `docs/ai/CURRENT_STATE.md` — 현재 상태
- `docs/ai/decisions/` — 결정 기록
- `REQUIREMENTS.md` — 요구사항
