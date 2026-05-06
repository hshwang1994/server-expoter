# H-D7 — JSON 출력 스키마 키 사전 딥 리라이트

> status: [DONE] | depends: H-C, H-E (권장) | priority: P1/P2

## 사용자 의도

검증 / 결정 / 호출자 reference 가 정확하고 사람이 읽기 쉬워야 함.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 파일 | `docs/20_json-schema-fields.md` |
| 영향 독자 | 검증 / 결정 추적 / 호출자 시스템 개발자 |
| 핵심 | envelope 13 + sections 10 + field 65 |

## 변경 항목

1. 도입부 — 누가 / 언제 / 왜 보는지
2. 본문 구조 재정렬 (시간순 / 호출자 시야 / 검증 흐름 우선)
3. 표 컬럼 의미 명확화
4. 내부 cycle 번호 / Round 표기를 "이력" 푸터로 분리
5. 약어 풀이
6. 다음 단계 안내

## 검증

- [ ] cross-reference 유효
- [ ] 호출자 계약 영향 0 (필드 의미 변경 0)
- [ ] decision-log 의 경우: 사용자 인용 보존

## 진행 상태

[DONE]
