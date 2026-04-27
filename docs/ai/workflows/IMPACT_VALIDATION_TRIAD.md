# Impact Validation Triad — server-exporter

> rule 91 → 95 → 92 triad — 변경 영향 검증 3단계.

## 3단계

```
1. Rule 91 (task-impact-gate) — 변경 전 영향 미리보기
   ↓
2. Rule 95 (production-code-critical-review) — 의심 패턴 11종 자동 스캔
   ↓
3. Rule 92 (dependency-and-regression-gate) — 회귀 영역 자동 식별 + 검사
```

## 1. Rule 91 (사전 영향 미리보기)

skill `task-impact-preview` 자동 호출. 5 섹션:
1. 영향 모듈
2. 영향 vendor
3. 함께 바뀔 것 (테스트 / 문서 / adapter / 외부 계약)
4. 리스크 top 3
5. 진행 확인

후속:
- LOW → 직진
- MED + 옵션 2+ → compare-feature-options
- HIGH → write-impact-brief + 사용자 승인
- Critical → 사용자 명시 승인 없이 진입 금지

## 2. Rule 95 (구현 중 의심 검증)

production 코드를 한 줄이라도 읽거나 인용하는 모든 작업에서 **의심 패턴 11종** 자동 스캔:

1. Ansible default(omit) 누락
2. set_fact 재정의로 fragment 침범 (rule 22)
3. Jinja2 정규식 dead code
4. adapter score 동률 처리
5. is none / is undefined / length == 0 혼동
6. 빈 callback message
7. int() cast 미방어
8. Single-vendor 분기 silent
9. adapter_loader self-reference
10. mutable / immutable 혼동
11. 외부 시스템 계약 drift (rule 96)

의심 발견 시 `@pytest.mark.xfail` 추가 + FAILURE_PATTERNS.md entry.

## 3. Rule 92 (구현 후 회귀)

회귀 영역 자동 포함 (R9):
- 공통 fragment (`common/tasks/normalize/`)
- 공통 라이브러리 (`common/library/`, `redfish-gather/library/`)
- adapter 추가/수정
- callback (`callback_plugins/json_only.py`)
- 출력 schema (sections.yml / field_dictionary.yml)
- Jenkinsfile* (모든 3종)
- vault 회전

체크리스트 (R3):
- 영향 vendor baseline 회귀 통과
- 3-channel syntax-check
- 출력 envelope 6 필드 유지
- 외부 호출 timeout

## 진입점

각 단계 진입점:
- 1: `task-impact-preview` skill
- 2: `write-quality-tdd` skill 또는 `review-existing-code`
- 3: `prepare-regression-check` skill + Jenkins Stage 4

## 관련

- rule 91, 92, 95, 96
- skill: task-impact-preview, write-quality-tdd, prepare-regression-check, review-existing-code, debug-external-integrated-feature
- agent: change-impact-analyst, fragment-engineer, vendor-boundary-guardian, qa-regression-worker
