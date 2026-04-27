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
