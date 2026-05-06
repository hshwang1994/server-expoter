# M-A3 — status 코드 변경 + 회귀

> status: [DONE] | depends: M-A2 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility | session: Session-3 (2026-05-06)

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

M-A2 [DONE] (Session-2, 2026-05-06) — 결정 결과:

| 결정 | 선택 |
|---|---|
| (1) 시나리오 B 처리 | **B-1 (현재 동작 유지)** |
| (2) errors[] severity | **(a) 유지 (severity 도입 없음)** |
| (3) status_rules.yml | **(c) 유지 (현재)** |
| (4) status enum | **(a) 3 enum 유지** |

→ **Case A 채택** — 의도된 동작 명시 only (Additive). 코드 동작 변경 없음.

근거 종합: rule 92 R2 (Additive only) + rule 13 R5 (envelope 13 필드 보존) + rule 96 R1-B (호환성 외 영역 — schema 확장 별도 cycle) + M-A1 분석 (시나리오 B 가 명백한 의도된 동작 — 코드 주석 3 위치 명시).

상세 근거 + 결정 매트릭스: `M-A2.md` "사용자 결정 결과" 절 + "변경 spec (M-A3 도출)" 절.

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

- [x] M-A2 결정 결과 확인 (Case A — B-1+a+c+a)
- [x] 변경 spec 적용
  - [x] `common/tasks/normalize/build_status.yml` 헤더 주석 강화 (시나리오 4 매트릭스 + 의도된 설계 + 3 reference)
  - [x] `status_rules.yml` 변경 0 (DEAD CODE 명시 주석 + collection_result 절 build_status 인라인과 동등 정합 확인)
- [x] mock fixture 신규 추가: `tests/fixtures/outputs/status_success_with_warnings.json` (시나리오 B 재현)
- [x] 회귀 pytest 신규: `tests/unit/test_status_scenario_b_invariants.py` 13 테스트
- [x] pytest 291/291 PASS (기존 278 + 신규 13, 회귀 0)
- [x] verify_harness_consistency PASS (rules:28 / skills:48 / agents:59 / policies:10)
- [x] verify_vendor_boundary 사전 위반 3건 — 본 cycle M-A3 변경과 무관 (redfish_gather.py OEM Lenovo/HPE pre-existing)
- [x] YAML / JSON / Python AST PASS
- [x] baseline 회귀 영향 0 (코드 동작 변경 없음)
- [x] CURRENT_STATE.md 갱신
- [x] commit: `feat: [M-A3 DONE] status Case A 의도 주석 강화 + 회귀 13건`
- [x] SESSION-HANDOFF.md / fixes/INDEX.md / DEPENDENCIES.md 갱신

## 변경 사항 요약 (Session-3 / 2026-05-06)

### 변경 파일

| 파일 | 변경 | 의도 |
|---|---|---|
| `common/tasks/normalize/build_status.yml` | +35 / -2 (헤더 주석만) | 시나리오 4 매트릭스 + errors[] 분리 의미 + 3 reference 명문화 |
| `tests/fixtures/outputs/status_success_with_warnings.json` | 신규 | 시나리오 B 재현 (Linux OS gather memory dmidecode fallback + network lspci stderr) |
| `tests/unit/test_status_scenario_b_invariants.py` | 신규 | Jinja2 ↔ Python 재현 회귀 + invariants 13 테스트 |

### 코드 동작 변경

- 0 (의도 주석만 추가). envelope 13 필드 / status enum / sections / errors / data 모두 변경 없음
- rule 13 R5 envelope shape 보존 / rule 96 R1-B 호환성 외 schema 확장 회피

### 신규 회귀 테스트 13건

1. `test_fixture_exists_and_loads` — fixture 존재
2. `test_envelope_has_13_fields` — rule 13 R5 envelope 13 필드 invariant
3. `test_overall_status_is_success` — 시나리오 B 정본
4. `test_errors_non_empty_with_warnings` — errors[] non-empty
5. `test_errors_have_section_and_message` — errors[] schema (rule 22 R8)
6. `test_memory_warning_pattern_present` — gather_memory.yml:171-175 dmidecode fallback 패턴
7. `test_supported_sections_all_success` — supported 섹션 = success
8. `test_recomputed_status_matches_envelope` — Jinja2 ↔ Python 재현 일치
9. `test_errors_do_not_change_status` — errors 변동이 status 영향 없음
10. `test_scenario_a_clean_success` — 시나리오 A
11. `test_scenario_c_partial` — 시나리오 C
12. `test_scenario_d_all_failed` — 시나리오 D
13. `test_no_supported_sections_failed` — 엣지 (모두 not_supported)

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
