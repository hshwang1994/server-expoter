# Output Schema / Fields / Baseline 정합

## 적용 대상
- `schema/sections.yml`, `schema/field_dictionary.yml`, `schema/fields/**`, `schema/baseline_v1/**`, `schema/examples/**`
- `common/tasks/normalize/build_*.yml`
- `callback_plugins/json_only.py`

## 현재 관찰된 현실

- 10 sections (system / hardware / bmc / cpu / memory / storage / network / firmware / users / power)
- field_dictionary.yml: 28 Must + Nice + Skip
- baseline_v1: vendor별 회귀 기준선
- Jenkins Stage 3 (Validate Schema) + Stage 4 (E2E Regression)이 FAIL 게이트
- Flyway 같은 DB schema는 없음 — 본 schema가 동등 역할

## 목표 규칙

### R1. 3종 동반 갱신

- **Default**: schema 변경은 다음 3종 동시 갱신:
  1. `schema/sections.yml` (섹션 list)
  2. `schema/field_dictionary.yml` (필드 정의)
  3. `tests/baseline_v1/{vendor}_baseline.json` (영향 vendor 전수)
- **Allowed**: 1 vendor만 영향 받는 vendor-specific 필드는 그 vendor baseline만 갱신
- **Forbidden**: sections.yml만 수정하고 field_dictionary 미갱신, 또는 그 반대
- **Why**: 한쪽만 수정하면 Jenkins Stage 3 (정합 검증) FAIL

### R2. Must 필드는 모든 vendor

- **Default**: field_dictionary.yml의 Must 분류 필드는 모든 vendor baseline에 존재해야 함
- **Allowed**: vendor-specific 필드는 Nice
- **Forbidden**: 새 필드를 Must로 분류하면서 일부 vendor baseline 누락
- **Why**: Must는 호출자가 모든 응답에서 보장 받는 필드. 누락 시 호출자 시스템 파싱 실패 가능

### R3. Schema 버전 사용자 확인

- **Default**: sections.yml + field_dictionary.yml 버전 변경은 사용자 명시 확인 (rule 92 R5와 동일 정신)
- **Forbidden**: AI가 임의로 버전 번호 결정
- **Why**: 다른 작업자/세션에서 같은 버전 사용 가능 → 충돌

### R4. Baseline 갱신 절차

- **Default**: `update-vendor-baseline` skill 사용. 실장비 검증 후 baseline 갱신:
  1. probe_redfish.py로 실장비 응답 수집
  2. 정규화된 결과를 baseline_v1/{vendor}_baseline.json에 저장
  3. tests/evidence/<날짜>-<vendor>.md에 검증 환경 기록
  4. Round 검증 docs/19_decision-log.md에 추가
- **Forbidden**: AI가 임의로 baseline 수정 (실측 없이)
- **Why**: baseline은 회귀 기준선. 실측 없는 수정은 회귀를 무력화

### R5. JSON envelope 6 필드

- **Default**: callback_plugins/json_only.py 출력은 정확히 6 필드: `status / sections / data / errors / meta / diagnosis`
- **Forbidden**: envelope 필드 추가/삭제 (호출자 호환성 깨짐)
- **Why**: rule 31 callback URL 무결성 + 호출자 시스템 계약

### R6. Build_*.yml 빌더 패턴 일관성

- **Default**: 새 builder 추가 시 기존 패턴 따름:
  - 입력: fragment 변수 (`_data_fragment` 등)
  - 출력: 누적 변수 (`_collected_data` 등) 또는 최종 envelope 필드
  - set_fact로만 변수 생성 (다른 task의 결과를 직접 참조 안 함)
- **Forbidden**: 빌더 안에서 외부 시스템 호출 (gather에서 이미 끝남)

## 금지 패턴

- 3종 중 일부만 갱신 — R1
- Must 필드 vendor 누락 — R2
- AI 임의 schema 버전 — R3
- 실측 없이 baseline 수정 — R4
- envelope 6 필드 변경 — R5
- 빌더에서 외부 호출 — R6

## 리뷰 포인트

- [ ] sections.yml + field_dictionary.yml + baseline 3종 동반 갱신
- [ ] 새 Must 필드가 모든 vendor에 존재
- [ ] schema 버전 사용자 승인
- [ ] baseline 갱신이 실측 기반인가 (evidence 첨부)
- [ ] envelope 6 필드 유지

## 테스트 포인트

- `python scripts/ai/hooks/output_schema_drift_check.py` (exit 0)
- Jenkins Stage 3 (Validate Schema) 통과
- Jenkins Stage 4 (E2E Regression) 통과
- 영향 vendor baseline 회귀

## 관련

- rule: `20-output-json-callback`, `21-output-baseline-fixtures`, `22-fragment-philosophy`
- skill: `update-output-schema-evidence`, `update-vendor-baseline`, `plan-schema-change`, `verify-json-output`
- agent: `schema-mapping-reviewer`, `schema-reviewer`, `schema-migration-worker`, `output-schema-refactor-worker`, `baseline-validation-worker`
- 정본: `docs/09_output-examples.md`, `docs/16_os-esxi-mapping.md`
