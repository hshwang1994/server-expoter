# CONVENTION_DRIFT — server-exporter

> 발견된 컨벤션 위반 / 임시 구현 / 외부 계약 drift 기록 (DRIFT-XXX).
> rule 92 R2 (즉시 수정 금지) — 정상 동작 중이면 마이그레이션 계획 후 단계적 정리.

## 형식

```
## DRIFT-XXX (YYYY-MM-DD)

- 발견 위치: <file:line>
- 분류: convention-violation / temporary-impl / external-contract-drift / catalog-stale
- 설명: <1-2줄>
- 영향: <범위>
- 제안: <수정 방향>
- 상태: open / planned / migrating / resolved
- 관련: rule N / skill X / agent Y
```

---

## DRIFT-001 (2026-04-27)

- **발견 위치**: 본 하네스 도입 시점 catalog (Plan 3) ↔ 실 코드 (`schema/field_dictionary.yml`)
- **분류**: catalog-stale
- **설명**: 하네스 도입 문서들 (`rule 13`, `Plan 1 design`, `CLAUDE.md`, 일부 catalog)에서 `Field Dictionary 28 Must`로 표기. cycle-002 분석에서 grep 카운트 기반으로 "Must 29 + Nice 8"로 정정.
- **영향**: 문서/문서 간 불일치. 실 운영에 영향 없음 (코드는 정상).
- **상태**: resolved (2026-04-27 cycle-003) — **단, 정정값 자체가 잘못됨**, DRIFT-007에서 재정정.
- **관련**: rule 13 (output-schema-fields), `docs/ai/catalogs/SCHEMA_FIELDS.md`, **DRIFT-007**

## DRIFT-002 (2026-04-27)

- **발견 위치**: 본 하네스 도입 문서 ↔ 실 Jenkinsfile* 3종
- **분류**: catalog-stale
- **설명**: 하네스 도입 문서에서 "4-Stage = Validate / Gather / Validate Schema / **E2E Regression**" 일반화 표기. 실측 결과:
  - `Jenkinsfile`: Stage 4 = E2E Regression ✓
  - `Jenkinsfile_grafana`: Stage 4 = **Ingest** (Grafana 데이터 적재)
  - `Jenkinsfile_portal`: Stage 4 = **Callback** (호출자 통보)
- **영향**: 문서/문서 간 불일치. 실 운영에 영향 없음.
- **제안**: rule 80 (ci-jenkins-policy) 본문 정정 — Stage 4가 Jenkinsfile별로 다름을 명시. CLAUDE.md / design / Plan 1 동시 갱신.
- **상태**: resolved (2026-04-27 cycle-003)
- **관련**: rule 80, `docs/ai/catalogs/JENKINS_PIPELINES.md`, `docs/01_jenkins-setup.md`, `docs/17_jenkins-pipeline.md`

## DRIFT-003 (2026-04-27)

- **발견 위치**: `docs/ai/references/redfish/vendor-bmc-guides.md` ↔ 실 `adapters/redfish/`
- **분류**: catalog-stale
- **설명**: vendor-bmc-guides.md 작성 시 일부 adapter 이름 추정 — 실측에서 정정:
  - HPE: `hpe_synergy.yml` (없음) → 실제 `hpe_ilo4.yml`
  - Supermicro: `supermicro_x12.yml` (없음) / `supermicro_legacy.yml` (없음) → 실제 `supermicro_x11.yml` / `supermicro_x9.yml` / `supermicro_bmc.yml`
  - Lenovo: `lenovo_xcc_legacy.yml` (없음) → 실제 `lenovo_imm2.yml`
- **영향**: reference 문서 stale. VENDOR_ADAPTERS.md는 실측으로 정정됨.
- **제안**: vendor-bmc-guides.md 동기화 (다음 cycle).
- **상태**: resolved (2026-04-27 cycle-003)
- **관련**: `docs/ai/catalogs/VENDOR_ADAPTERS.md`, `docs/ai/references/redfish/vendor-bmc-guides.md`

## DRIFT-004 (2026-04-27, resolved 2026-04-28)

- **발견 위치**: `schema/sections.yml` ↔ `schema/field_dictionary.yml`
- **분류**: convention-violation
- **설명**: cycle-004 W3-C `output_schema_drift_check.py` 정밀화 후 검출. `sections.yml`의 `users` 섹션 (channels: [os], OS gather에서 사용자 list 수집)이 `field_dictionary.yml`의 `fields:` 등록 prefix에 없음.
- **수정 (cycle-006)**: `field_dictionary.yml`에 6 항목 추가 — `users[]` (must), `users[].name` (must), `users[].uid` (must), `users[].groups` (nice), `users[].home` (nice), `users[].last_access_time` (skip).
  - 분포: Must 28→31, Nice 7→9, Skip 5→6, 총 40→46 entries
  - 영향 vendor baseline: 실측 ubuntu/windows baseline에 이미 users entries 존재 (회귀 0)
  - output_schema_drift_check.py: 정합 (sections 10 = fd_section_prefixes 10)
- **상태**: resolved (2026-04-28 cycle-006)
- **관련**: rule 13 R1 / R2, `schema/sections.yml`, `schema/field_dictionary.yml`

## DRIFT-005 (2026-04-27, resolved 2026-04-28)

- **발견 위치**: `redfish-gather/library/redfish_gather.py:103-109` ↔ `common/vars/vendor_aliases.yml`
- **분류**: convention-violation (Source-of-Truth 중복)
- **설명**: cycle-004 W2 vendor 경계 57건 분석에서 확인. `_VENDOR_ALIASES` dict (Python module)와 `vendor_aliases.yml` (Ansible) 두 곳에서 동일 매핑 정의. 신규 alias 추가 시 두 곳 동시 갱신 필요 → drift 잠재.
- **수정 (cycle-006, 옵션 (1)+(2) 조합)**:
  - (옵션 1) `_load_vendor_aliases_file()` path resolution 강화 — `SE_VENDOR_ALIASES_PATH` env / `REPO_ROOT` env / `__file__` 기반 fallback. YAML primary, dict fallback.
  - `_BUILTIN_VENDOR_MAP` → `_FALLBACK_VENDOR_MAP` 이름 변경 + 의도 주석 + 라인별 nosec rule12-r1 silence
  - (옵션 2 cycle-005 적용) `verify_harness_consistency.py` 동기화 게이트 — drift 시 advisory
- **상태**: resolved (2026-04-28 cycle-006)
- **관련**: rule 12 R1, rule 50 R2, `docs/ai/impact/2026-04-27-vendor-boundary-57.md`

## DRIFT-007 (2026-04-27, resolved 2026-04-28)

- **발견 위치**: `schema/field_dictionary.yml` 실측 ↔ cycle-003 DRIFT-001 정정값 (rule 13 / CLAUDE.md / SCHEMA_FIELDS.md)
- **분류**: catalog-stale
- **설명**: cycle-004 verifier에서 `python3 tests/validate_field_dictionary.py` 실행 결과 분포 "**Must 28 / Nice 7 / Skip 5**". cycle-003에서 정정한 "Must 29 / Nice 8" 표기와 차이. 원인: cycle-002 분석에서 `grep -cE "priority: must"` 사용 시 헤더 주석 (line 46~48 priority 설명 텍스트)이 카운트에 포함되어 +1씩 오인.
- **영향**: 운영 영향 없음 (코드 정상). 문서 정합 차이.
- **수정 (cycle-005)**:
  1. validate_field_dictionary.py + YAML 파싱 기준 실측 확정: **28 Must / 7 Nice / 5 Skip = 40 entries**
  2. CLAUDE.md / rule 13 / SCHEMA_FIELDS.md / field_dictionary.yml 헤더 / SKILL.md `update-output-schema-evidence` 일괄 정정
  3. SCHEMA_FIELDS.md 측정 명령을 grep → YAML 파싱으로 변경 (헤더 noise 제거)
  4. DRIFT-001 상태 코멘트 갱신 ("정정값 자체 잘못 — DRIFT-007에서 재정정")
- **상태**: resolved (2026-04-28 cycle-005)
- **관련**: rule 13, DRIFT-001 (cycle-003 정정 자체 stale), `tests/validate_field_dictionary.py`, cycle-002 분석 오인

## DRIFT-006 (2026-04-27, resolved 2026-04-28)

- **발견 위치**: `redfish-gather/library/redfish_gather.py:221-450, 705-706, 747` (vendor 분기 17건)
- **분류**: convention-violation
- **설명**: cycle-004 W2 vendor 경계 57건 분석에서 확인. Python module 안에 `if vendor == 'hpe':` / `oem = _safe(data, 'Oem', 'Dell', 'DellSystem')` 같은 vendor 분기 17건. rule 12 R1상 분기는 `redfish-gather/tasks/vendors/` 또는 adapter YAML capabilities에만 허용.
- **수정 (cycle-006, 옵션 (1)+(3) 조합 — 옵션 (2) 큰 리팩토링은 회귀 위험으로 회피)**:
  - (옵션 3) rule 12 R1에 **Allowed (cycle-006 추가)** 절 — redfish_gather.py의 OEM schema 추출 분기는 외부 계약 (Redfish API spec — `Oem.Hpe` / `Oem.Dell` 등 vendor namespace)에 직접 의존하므로 의도된 예외로 명시
  - (옵션 1 사전) cycle-004에서 13 adapter origin 주석 추가 시 OEM path 일부 명시 — 향후 새 vendor 추가 시 adapter origin metadata에 OEM 정보 기재
  - 17 라인 모두 `# nosec rule12-r1` 주석으로 silence (verify_vendor_boundary 도구 인식)
  - 라이브러리 vendor-agnostic 리팩토링 (옵션 2)는 영향 vendor 전부 회귀 + Round 권장이라 별도 cycle 후보로 보존
- **상태**: resolved (2026-04-28 cycle-006)
- **관련**: rule 12 R1 (Allowed 절 추가), rule 96 R1 (외부 계약), `docs/ai/impact/2026-04-27-vendor-boundary-57.md`
