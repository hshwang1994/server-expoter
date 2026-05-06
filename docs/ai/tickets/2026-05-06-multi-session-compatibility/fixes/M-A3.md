# M-A3 — status 코드 변경 + 회귀

> status: [PENDING] | depends: M-A2 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-A2 사용자 결정 결과 → 코드 반영 + 회귀 테스트.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `common/tasks/normalize/build_status.yml` (필수). 결정에 따라 `status_rules.yml` / `schema/sections.yml` / `field_dictionary.yml` |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | 8 baseline JSON (status 변경 시) + 영향 vendor pytest fixture |
| 리스크 top 3 | (1) baseline 회귀 다수 fail 가능 / (2) envelope schema 변경 시 호출자 영향 / (3) DEAD CODE 정리 시 의도된 reserved 영향 |
| 진행 확인 | M-A2 결정 매트릭스 따라 spec 자동 도출. M-A2 [DONE] 후 진입 |

## 현재 상태

(M-A2 [DONE] 후 결정 결과 첨부 — 변경 spec 도출 매트릭스)

## 변경 spec (조건부 — M-A2 결정에 따라)

### Case A: B-1 + (a) + (c) + (a) — 의도된 동작 명시 only

- `common/tasks/normalize/build_status.yml` 상단에 의도 주석 추가
- `docs/20_json-schema-fields.md` (M-F1) 에 status 판정 규칙 명시
- 코드 변경 없음 → baseline 회귀 영향 0

### Case B: B-2 + (a) + (a/b/c) + (a) — errors non-empty → partial

```jinja2
- name: "normalize | build_status"
  ansible.builtin.set_fact:
    _out_status: >-
      {%- set sec_vals = _norm_sections.values() | list -%}
      {%- set supported_vals = sec_vals | reject('equalto','not_supported') | list -%}
      {%- set success_count  = supported_vals | select('equalto','success') | list | length -%}
      {%- set failed_count   = supported_vals | select('equalto','failed')  | list | length -%}
      {%- set has_errors     = (_collected_errors | default([])) | length > 0 -%}
      {%- if supported_vals | length == 0 -%}
      failed
      {%- elif failed_count == 0 and not has_errors -%}
      success
      {%- elif success_count == 0 -%}
      failed
      {%- else -%}
      partial
      {%- endif -%}
```

→ 모든 vendor baseline 재생성 가능 (대부분 success → partial 변경 — lab 부재 → mock fixture 기반).

### Case C: B-3 + (b) + (a) + (b) — 신 enum 도입

- envelope status enum 4종 → schema/sections.yml + field_dictionary.yml 변경 (rule 92 R5 사용자 명시)
- status_rules.yml 동적 로딩 활성화
- errors severity 도입 → `_errors_fragment` schema 변경 (3 채널 모두 영향)
- baseline 8건 모두 재생성

→ rule 70 R8 ADR 의무 (M-A4)

## 회귀 / 검증

- pytest 회귀: 영향 baseline 전수 (`pytest tests/ -v`)
- mock fixture 신규 추가:
  - `tests/fixtures/redfish/<vendor>/status_partial_with_errors.json` (시나리오 B)
  - `tests/fixtures/redfish/<vendor>/status_success_clean.json` (시나리오 A)
- 정적 검증:
  - `python scripts/ai/verify_harness_consistency.py`
  - `python scripts/ai/hooks/output_schema_drift_check.py` (Case C 시 schema 변경 검출)
  - YAML/Jinja2 syntax check

## risk

- (HIGH, Case C) envelope schema 변경 → 호출자 시스템 파싱 영향 (rule 13 R5 + rule 96 R1-B 호환성 외 영역). 사용자 명시 승인 필수
- (MED, Case B) 기존 baseline 회귀 fail (status success → partial). lab 검증 없는 mock 회귀에서는 OK
- (LOW, Case A) 변경 0 — 의도 주석만

## 완료 조건

- [ ] M-A2 결정 결과 확인
- [ ] 변경 spec 적용 (build_status.yml + 결정에 따른 보조 파일)
- [ ] mock fixture 신규 추가
- [ ] pytest 108/108 + 신규 fixture 회귀 PASS
- [ ] verify_harness_consistency / output_schema_drift_check PASS
- [ ] CURRENT_STATE.md 갱신
- [ ] commit: `<type>: [M-A3 DONE] status <Case A/B/C> 적용 + 회귀 N건`
- [ ] SESSION-HANDOFF.md / fixes/INDEX.md 갱신

## 다음 세션 첫 지시 템플릿

```
M-A3 status 코드 변경 진입.

M-A2 결정 결과:
- Case (A/B/C): ___
- 변경 spec: M-A3.md 의 "변경 spec" 절 해당 Case

작업:
1. build_status.yml 변경 (Case 따라)
2. mock fixture 추가
3. pytest + verify_* PASS
4. baseline 영향 분석 + 갱신 (Case B/C 시)
```

## 관련

- rule 13 R5 (envelope 13 필드)
- rule 92 R5 (schema 변경 사용자 명시)
- rule 96 R1-B (envelope 13 필드 변경 자제)
- rule 70 R8 (ADR trigger — Case C 시)
