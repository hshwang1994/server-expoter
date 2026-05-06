# M-A4 — status ADR (rule 70 R8 trigger 시)

> status: [PENDING] | depends: M-A3 | priority: P2 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-A3 결과 rule 70 R8 trigger (rule 본문 변경 / 표면 카운트 변경 / 보호 경로 변경) 발생 시 ADR 작성.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/ai/decisions/ADR-2026-05-XX-status-logic.md` (신설) |
| 영향 vendor | (문서만) |
| 리스크 | LOW |

## ADR trigger 매트릭스 (rule 70 R8)

| M-A3 Case | trigger | ADR 의무 |
|---|---|---|
| Case A (의도 주석) | 없음 | **NO** (rule 본문 변경 없음, 표면 카운트 변동 없음) |
| Case B (errors non-empty → partial) | rule 13 R5 envelope 정본 변경 가능 | **CONDITIONAL** (envelope shape 동일하면 NO) |
| Case C (신 enum + severity) | rule 13 R5 envelope 변경 + 표면 카운트 (schema 항목 수) | **YES** |

→ M-A3 [DONE] 후 본 ticket 진입 가능 여부 판정.

## ADR 4 섹션 (rule 70 R8)

### 컨텍스트 (Why)

- 사용자 의심 영역 (M-A1 분석 시나리오 B)
- 호출자 시스템 계약 영향
- 기존 동작 / 새 동작 비교

### 결정 (What)

- M-A2 사용자 결정 결과 (B-1/B-2/B-3 + (a)/(b) ...)
- 변경된 envelope shape (있으면)
- 변경된 rule (있으면)

### 결과 (Impact)

- 호출자 호환성
- baseline 회귀 결과
- 표면 카운트 변동

### 대안 비교 (Considered)

- M-A2 결정 매트릭스의 다른 option 들과 비교
- 왜 본 결정 선택?

## 완료 조건

- [ ] M-A3 [DONE] 확인
- [ ] rule 70 R8 trigger 판정 (ADR 의무 YES/NO/CONDITIONAL)
- [ ] (YES 시) ADR 작성 — 4 섹션 모두
- [ ] (NO 시) "ADR 불필요" 본 ticket 에 명시 + close
- [ ] commit: `docs: [M-A4 DONE] status ADR (Case <A/B/C>)` 또는 `[M-A4 SKIP] ADR 불필요`

## 다음 세션 첫 지시 템플릿

```
M-A4 status ADR 진입.

M-A3 결과: Case ___ (A/B/C)
ADR trigger: ___ (YES/NO/CONDITIONAL)

YES 시: docs/ai/decisions/ADR-2026-05-XX-status-logic.md 작성
NO 시: M-A4 SKIP 명시 후 close
```

## 관련

- rule 70 R8 (ADR 의무 trigger 3종)
- rule 13 R5 (envelope 정본)
