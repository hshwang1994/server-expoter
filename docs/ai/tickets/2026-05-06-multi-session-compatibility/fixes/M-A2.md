# M-A2 — status 의도 결정 (사용자 결정 포인트)

> status: [PENDING] | depends: M-A1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "이게 로직이 정상작동돼지않는듯함. 부분 성공이라고 하더라도 error 에는 로그가 찍히는데 success로 빠지는경우가 있음 이것은 왜이런지 확인해줘 의도된건지?"

→ 의도된 동작인지 / 버그인지 **사용자가 결정**.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | (M-A1 분석 결과 입력 → 사용자 결정 → M-A3 변경 spec) |
| 영향 vendor | 9 vendor 모두 (envelope.status 호출자 계약) |
| 함께 바뀔 것 | (사용자 결정에 따라) build_status.yml 인라인 / status_rules.yml dynamic / schema/sections.yml 등 |
| 리스크 top 3 | (1) status enum 변경 = 호출자 시스템 파싱 영향 (rule 13 R5 envelope 13 필드 변경) / (2) 회귀 영향 큼 / (3) M-A1 분석 누락 시 잘못된 결정 |
| 진행 확인 | 사용자 결정 후 M-A3 진입 |

## 현재 상태

(M-A1 [DONE] 후 분석 결과 첨부 예정)

## 사용자 결정 4 포인트

### (1) 시나리오 B 처리

**시나리오 B**: 섹션 status 모두 success, errors[] 에 warning 있음

| option | overall status | 영향 |
|---|---|---|
| **B-1 (현재 동작)** | success | 호환성 영향 0. 호출자가 envelope.errors[] 별도 검사 필요 |
| **B-2 (사용자 의도?)** | partial | 호출자 시스템이 success 만 OK 로 판정한다면 partial 도 이상 신호로 인식 |
| **B-3 (신 enum)** | success_with_warnings | envelope status enum 4종 도입 (rule 13 R5 변경 필요) |

**사용자 결정 필요**: B-1 / B-2 / B-3 중 택일

### (2) errors[] severity 구분

현재 `_errors_fragment` 는 단일 type. severity 구분 없음.

| option | 변경 |
|---|---|
| **(a) 유지** | 변경 없음. 모든 error 동등 처리 |
| **(b) 도입** | error / warning / info 3종 — overall status 판정에서 warning 은 무시 |

**사용자 결정 필요**: (a) / (b) 중 택일

### (3) status_rules.yml DEAD CODE 처리

| option | 변경 |
|---|---|
| **(a) 살림** | build_status.yml 에서 include_vars 로 동적 로딩. status_rules.yml 정본화 |
| **(b) 삭제** | DEAD CODE 정리. 인라인 Jinja2 만 유지 |
| **(c) 유지 (현재)** | 운영자 참고용 + 향후 reserved 그대로 |

**사용자 결정 필요**: (a) / (b) / (c) 중 택일

### (4) overall status enum 정의

현재 envelope.status enum: `success | partial | failed`

| option | 변경 |
|---|---|
| **(a) 3 enum 유지** | rule 13 R5 envelope 변경 없음 |
| **(b) 4 enum 도입** | success / success_with_warnings / partial / failed (B-3 와 연결) |

**사용자 결정 필요**: (a) / (b) 중 택일

## 변경 spec

본 ticket = 사용자 결정 포인트 정리만. M-A3 에서 결정 결과 코드 반영.

산출물:
- 본 M-A2.md 에 사용자 답변 4개 기록
- M-A3 변경 spec 자동 도출 (결정 → 변경 매트릭스)

## 결정 매트릭스

| 결정 조합 | M-A3 변경 spec |
|---|---|
| B-1 + (a) + (c) + (a) | 변경 없음. 의도된 동작 명시 (build_status.yml comment + docs/20 schema 문서) |
| B-2 + (a) + (a/b/c) + (a) | build_status.yml 판정 로직 변경: errors[] non-empty → overall=partial |
| B-3 + (b) + (a) + (b) | envelope status enum 확장 + status_rules.yml 활성 + severity 도입 (큰 변경) |

## risk

- (HIGH) B-3 + (b) 조합 = envelope schema 변경 (rule 13 R5 + 92 R5 사용자 명시 승인)
- (MED) B-2 = 모든 vendor baseline 회귀 (status 가 success → partial 로 변경되는 케이스 다수)
- (LOW) status_rules.yml 정리 = DEAD CODE 처리만

## 완료 조건

- [ ] M-A1 분석 결과 첨부 / 확인
- [ ] 사용자 4 결정 답변 기록
- [ ] 결정 매트릭스 → M-A3 변경 spec 자동 도출
- [ ] M-A3.md 갱신 (변경 spec 채움)
- [ ] commit: `docs: [M-A2 DONE] status 의도 결정 — 사용자 답변 4 / M-A3 spec 도출`

## 다음 세션 첫 지시 템플릿

```
M-A2 status 의도 결정 진입. M-A1 결과 확인 + 사용자 답변 4 받음.

사용자 결정:
- (1) 시나리오 B 처리: B-1 / B-2 / B-3 → ___
- (2) errors severity: (a) / (b) → ___
- (3) status_rules.yml: (a) / (b) / (c) → ___
- (4) status enum: (a) 3 / (b) 4 → ___

→ 결정 매트릭스 따라 M-A3 변경 spec 도출
```

## 관련

- rule 13 R5 (envelope 13 필드 — status 변경 시 호출자 계약)
- rule 92 R5 (schema 변경 사용자 명시)
- rule 70 R8 (ADR trigger — 표면/rule 변경 시)
