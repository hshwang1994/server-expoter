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
- **설명**: 하네스 도입 문서들 (`rule 13`, `Plan 1 design`, `CLAUDE.md`, 일부 catalog)에서 `Field Dictionary 28 Must`로 표기했으나, 실측 결과 **Must 29 + Nice 8**.
- **영향**: 문서/문서 간 불일치. 실 운영에 영향 없음 (코드는 정상).
- **제안**: 차기 cycle / harness-cycle에서 일괄 갱신 (Tier 2 — rule 23 R1 4요소 승인 후).
- **상태**: resolved (2026-04-27 cycle-003)
- **관련**: rule 13 (output-schema-fields), `docs/ai/catalogs/SCHEMA_FIELDS.md`

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

## DRIFT-004 (2026-04-27)

- **발견 위치**: `schema/sections.yml` ↔ `schema/field_dictionary.yml`
- **분류**: convention-violation
- **설명**: cycle-004 W3-C `output_schema_drift_check.py` 정밀화 후 검출. `sections.yml`의 `users` 섹션 (channels: [os], OS gather에서 사용자 list 수집)이 `field_dictionary.yml`의 `fields:` 등록 prefix에 없음.
- **영향**: 운영자/외부 시스템이 `data.users[].name`, `data.users[].uid`, `data.users[].groups` 등 필드 의미를 field_dictionary에서 찾을 수 없음. 출력 자체는 정상.
- **제안**: cycle-005에서 `field_dictionary.yml`에 `users[].*` 항목 추가 — schema 변경이라 rule 92 R5 사용자 승인 필요.
- **상태**: open (사용자 결정 대기)
- **관련**: rule 13 R1 / R2, `schema/sections.yml`, `schema/field_dictionary.yml`, `tests/baseline_v1/{vendor}_baseline.json` 사용자 항목

## DRIFT-005 (2026-04-27, 후보)

- **발견 위치**: `redfish-gather/library/redfish_gather.py:103-109` ↔ `common/vars/vendor_aliases.yml`
- **분류**: convention-violation (Source-of-Truth 중복)
- **설명**: cycle-004 W2 vendor 경계 57건 분석에서 확인. `_VENDOR_ALIASES` dict (Python module)와 `vendor_aliases.yml` (Ansible) 두 곳에서 동일 매핑 정의. 신규 alias 추가 시 두 곳 동시 갱신 필요 → drift 잠재.
- **영향**: 운영 영향 없음 (현재 동기화 상태). 향후 vendor alias 추가 시 한 곳만 수정하면 redfish 검출 누락 가능.
- **제안**: cycle-005에서 옵션 결정 — (1) `_VENDOR_ALIASES` → YAML import / (2) 동기화 주석 + verify_harness_consistency 게이트 추가 / (3) 무시.
- **상태**: open (사용자 결정 대기)
- **관련**: rule 12 R1, rule 50 R2 (새 vendor 추가 9단계 — 동기화 단계 추가 후보), `docs/ai/impact/2026-04-27-vendor-boundary-57.md`

## DRIFT-006 (2026-04-27, 후보)

- **발견 위치**: `redfish-gather/library/redfish_gather.py:221-450, 705-706, 747` (vendor 분기 17건)
- **분류**: convention-violation
- **설명**: cycle-004 W2 vendor 경계 57건 분석에서 확인. Python module 안에 `if vendor == 'hpe':` / `oem = _safe(data, 'Oem', 'Dell', 'DellSystem')` 같은 vendor 분기 17건. rule 12 R1상 분기는 `redfish-gather/tasks/vendors/` 또는 adapter YAML capabilities에만 허용.
- **영향**: 운영 영향 없음 (현재 정상 동작). 새 vendor 추가 시 adapter YAML만 변경해서는 OEM 추출 안 됨 → 라이브러리 수정 필요.
- **제안**: cycle-005에서 옵션 결정 — (1) adapter origin 주석에 OEM 매핑 명시 (rule 96 강화) / (2) 라이브러리 vendor-agnostic 리팩토링 (`oem_extractor` 매핑을 capabilities에서 받음) / (3) rule 12 R1에 redfish_gather.py 예외 명시.
- **상태**: open (사용자 결정 대기)
- **관련**: rule 12 R1, rule 50 R2 (새 vendor 추가), `docs/ai/impact/2026-04-27-vendor-boundary-57.md`
