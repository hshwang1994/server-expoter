# H-E3 — 3 채널 공통 필드

> status: [DONE] | depends: — | priority: P1/P2

## 사용자 의도

"스키마 폴더내의 파일" 도 사람이 읽기 편하게.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 파일 | `schema/fields/common.yml` |
| 영향 독자 | 호출자 시스템 개발자 / 신규 작업자 |
| 핵심 | description 다듬기 |

## 변경 항목

1. 헤더 코멘트 평이하게 (이미 1차 완료)
2. 각 entry 의 description / display_name / help_ko 표현이 사람이 읽기에 자연스러운지 확인
3. **의미 변경 금지** — 호출자 계약 / 정본 코드 영향 0
4. 변경은 뉘앙스 / 약어 풀이 / 자연스러운 문장만

## 검증

- [ ] `python -c "import yaml; yaml.safe_load(open(...))"` PASS
- [ ] entry 수 / key 이름 / type / enum / priority 변경 0
- [ ] tests/validate_field_dictionary.py 통과 (있다면)

## 진행 상태

[DONE]
