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

## DRIFT-008 (2026-04-28, resolved 2026-04-28 full-sweep)

- **발견 위치** (full-sweep, 영역 2 HIGH-2):
  - `.claude/rules/00-core-repo.md:16` — `Field Dictionary 28 Must`
  - `.claude/rules/23-communication-style.md:63` — 어휘 치환표
  - `.claude/role/output-schema/README.md:4,8,51` (3곳)
  - `.claude/ai-context/output-schema/convention.md:42,45` (2곳)
  - `.claude/ai-context/common/repo-facts.md:47`
  - `.claude/ai-context/common/coding-glossary-ko.md:16`
  - `.claude/skills/update-output-schema-evidence/SKILL.md:39`
  - `docs/ai/catalogs/PROJECT_MAP.md:34`
  - `docs/ai/catalogs/SCHEMA_FIELDS.md:23-29,38`
- **분류**: catalog-stale (cycle-006 schema users[] 6 항목 추가 후 미반영)
- **설명**: cycle-006 (2026-04-28)에서 schema users[] 섹션 6 항목 추가 + field_dictionary "31 Must / 9 Nice / 6 Skip = 46 entries" 갱신. CLAUDE.md / rule 13 본문은 갱신됐으나 위 11곳 (rule / role / ai-context / skill / catalog) 미반영. cycle-006 직후 full-sweep에서 발견.
- **수정 (full-sweep, Tier 1)**: 11곳 모두 `31 Must / 9 Nice / 6 Skip = 46 entries`로 일괄 정정
- **상태**: resolved (2026-04-28 full-sweep)
- **관련**: rule 13 R1 (3종 동반 갱신), rule 70 (catalog 갱신 trigger), full-sweep 보고서

## DRIFT-009 (2026-04-28, resolved 2026-04-28 full-sweep)

- **발견 위치**: `.claude/rules/23-communication-style.md:87,90,137` (`5체크`) ↔ `.claude/rules/24-completion-gate.md:3,53,70,85,90` + `CLAUDE.md:455` (`6 체크`)
- **분류**: convention-violation (rule 본문 모순)
- **설명**: rule 23 R4 본문이 "5체크"로 명시됐으나 정본 (rule 24 + CLAUDE.md)은 "6 체크". 사용자가 rule 23 따르면 한 항목 누락 위험.
- **수정 (full-sweep, Tier 2-A1)**: rule 23 R4 → "6체크"로 정정 (rule 24 = 정본)
- **상태**: resolved (2026-04-28 full-sweep)
- **관련**: rule 24 (정본), CLAUDE.md Step 7

## DRIFT-010 (2026-04-28, resolved 2026-04-28 full-sweep)

- **발견 위치** (full-sweep 영역 6 HIGH-1):
  - `common/tasks/normalize/init_fragments.yml:42-46`
  - `common/tasks/normalize/build_empty_data.yml:24-28`
  - `common/tasks/normalize/build_failed_output.yml:79-80`
- **분류**: convention-violation (rule 13 R5 envelope 정합 위반)
- **설명**: storage 섹션 빈값 정의 3 빌더에 `logical_volumes: []` 누락. `schema/sections.yml:51-56`은 `storage.empty_value` 명시. field_dictionary는 `storage.logical_volumes[]` 8 Must 필드 정의. 현재 baseline은 gather 코드가 채워주고 있어 우연히 통과 중. precheck 실패 또는 Redfish 외 채널이면 호출자 파싱 NG 가능.
- **수정 (full-sweep, Tier 2-D1)**: 3 빌더에 `logical_volumes: []` 추가
- **상태**: resolved (2026-04-28 full-sweep)
- **관련**: rule 13 R5, rule 22 R1 (3 파일 동기화 의무)

## DRIFT-011 (2026-04-29, open)

- **발견 위치**:
  - `inventory/lab/redfish.json:11` — 사용자 라벨 `_vendor: dell` (BMC 10.100.15.32 — GPU 호스트)
  - `inventory/lab/redfish.json:6-8` — 사용자 라벨 `_vendor: cisco` (BMC 10.100.15.1, 15.2, 15.3)
  - `tests/evidence/cycle-015/connectivity-2026-04-29.md` 5절
- **분류**: external-contract-drift (rule 96 R1)
- **설명**: cycle-015 첫 lab 권한 직후 연결성 검증에서 `GET /redfish/v1/` 무인증 응답 (rule 27 R3 1단계) 결과 사용자 라벨 vs Redfish Manufacturer 불일치 2건 발견:
  1. **10.100.15.32** (사용자: "dell, GPU 카드 설치") → `Vendor='AMI', Product='AMI Redfish Server', RedfishVersion=1.11.0` — AMI MegaRAC = Supermicro / Asrock / whitebox 가능. 현재 adapter 매칭으로는 `redfish_generic.yml` 또는 `supermicro_bmc.yml` 후보 (Dell adapter 매칭 안 됨 → 기존 baseline 회귀 영향 0).
  2. **10.100.15.2** (사용자: "cisco") → `Product='TA-UNODE-G1', RedfishVersion=1.2.0` — 표준 Cisco UCS Product 아님 (UCS C-series는 보통 `Product='UCS C220 M5'` 형식). TA-UNODE는 Tetration / TelePresence / 3rd party 가능성.
- **영향**: 본 실장비 회귀 진입 전 식별 필요. 현재는 이론상의 vendor 라벨 vs 실 Manufacturer drift라 baseline 갱신 시 잘못된 vendor adapter 적용 위험.
- **제안**:
  1. 호스트 물리 라벨 확인 (사용자 lab 직접 확인)
  2. `deep_probe_redfish.py`로 Manufacturer / Model / Oem namespace 상세 추출
  3. `inventory/lab/redfish.json` `_vendor` 라벨 정정
  4. `EXTERNAL_CONTRACTS.md`에 AMI Redfish 1.11.0 / TA-UNODE-G1 entry 추가
- **상태**: **resolved (cycle-015 사용자 명시 결정)** — 두 호스트 모두 사내 lab 부재 확인. `inventory/lab/redfish.json` + `vault/.lab-credentials.yml`에서 제거. OPS-12 / OPS-13 closed.
- **관련**: rule 96 R1 (외부 계약 origin 주석), rule 27 R3 (Vault 2단계 — 1단계가 본 drift 검출), rule 50 R1 (vendor 정규화 정본 vendor_aliases.yml), `tests/evidence/cycle-015/connectivity-2026-04-29.md`


## DRIFT-012 (2026-05-01, resolved cycle-017)

- **발견 위치**: `.claude/skills/cross-review-workflow.md` (단일 .md 파일 형식)
- **분류**: skill 디렉터리 형식 일관성
- **설명**: cycle 2026-05-01 중반 (commit `a1a3bf6b`) cross-review-workflow skill 을 단일 `.md` 파일로 추가. 기존 47 skill 은 모두 `<name>/SKILL.md` 디렉터리 형식. `verify_harness_consistency.py` 검증기는 디렉터리만 카운트해서 단일 파일은 누락. 일관성 깨짐.
- **resolved (cycle-017)**:
  - `.claude/skills/cross-review-workflow.md` → `.claude/skills/cross-review-workflow/SKILL.md` 디렉터리 변환
  - frontmatter (name + description) 추가
  - `verify_harness_consistency.py` 통과 (rules 28 / skills 48 / agents 59 / policies 10)
- **관련**: rule 70 R5, `verify_harness_consistency.py:138-156` (SKILL.md frontmatter name ↔ 폴더명 일치 검사)

## DRIFT-013 (2026-05-01, resolved cycle-017)

- **발견 위치**: cycle 2026-04-30 Lenovo XCC 1.17.0 reverse regression
- **분류**: 사용자 실측 vs spec drift
- **설명**: cycle 2026-04-30 첫 fix (`Accept` + `OData-Version` + `User-Agent` 추가) 가 lab 검증 OK 였으나 사이트 BMC 펌웨어 1.17.0 reject. "표준 권장 = 모든 BMC 호환" 가정 실패. 사용자 명시 hotfix ("Accept만") 적용 후 정상화.
- **resolved (cycle-017)**:
  - rule 25 R7-A-1 신설 — "사용자 실측 > spec" 본문 화
  - capture-site-fixture skill 신설 — 사이트 사고 fixture sanitize + commit
  - lab-tracker agent (opus) — lab 보유/부재 추적
  - web-evidence-collector agent (opus) + web-evidence-fetch skill — lab 부재 영역 web sources 의무 (rule 96 R1-A)
- **관련**: rule 25 R7-A-1, rule 96 R1-A, ADR-2026-05-01-harness-reinforcement

## DRIFT-014 (2026-05-11, resolved cycle hpe-ilo7-gen12-match-fix)

- **발견 위치**: `adapters/redfish/hpe_ilo7.yml` L36 ↔ 일부 Gen12 BMC firmware 보고 형식
- **분류**: external-contract-drift (rule 96 R1)
- **설명**: 직전 cycle `hpe-csus-add` mock 검증 부수 발견 — iLO 7 adapter 의 `firmware_patterns = ["iLO.*7", "^\\d+\\.\\d+\\.\\d+"]` 가 3-part version (예 "1.16.00") 만 가정. 일부 Gen12 BMC 는 facts.firmware 추출 path (Manager.FirmwareVersion 만) 에 따라 2-part short version "1.10" 만 보고 → `firmware_patterns` 매치 실패 → -9999 disqualify (`module_utils/adapter_common.py` L260-267) → iLO 7 (priority=120) 대신 iLO 4 (priority=50) 가 잘못 선택. mock S1 시나리오 재현 확인.
- **영향**:
  - Gen12 BMC 응답 path drift 시 SmartStorage legacy (iLO 4 strategy) + Oem.Hp namespace 시도 → Gen12 Oem.Hpe.* 정보 수집 실패
  - 사이트 실 BMC firmware 형식 미확정 (lab 부재 — web sources `1.16.00` / `1.12.00` 3-part 가정만 알려짐)
- **resolved (cycle hpe-ilo7-gen12-match-fix)**:
  - `hpe_ilo7.yml` firmware_patterns 확장 (Additive only, rule 92 R2): `["iLO.*7", "^\\d+\\.\\d+\\.\\d+", "^1\\.1[0-9]"]`
  - `^1\.1[0-9]` (1.10~1.19) 명시 — iLO 4 `^1\.[0-9]` / iLO 6 `^1\.[5-9]` 한자리 minor 와 충돌 0
  - mock 5 시나리오 회귀 (S1=iLO7 / S2=iLO7 / S3=iLO6 / S4=CSUS3200 / S5=SDFlex) 모두 PASS
  - `scripts/ai/verify_hpe_ilo7_fix.py` 신규 — 본 회귀 재현 도구
- **후속 (NEXT_ACTIONS, lab 도입 후)**:
  - 사이트 BMC facts.firmware 실측 형식 확정 → 1.20+ 2-part 변형 발견 시 firmware_patterns 추가 정정
  - reverse regression 검토 (rule 25 R7-A-1 — 사용자 실측 > spec)
- **관련**: rule 92 R2 (Additive only), rule 96 R1 (origin 주석), rule 25 R7-A-1, `module_utils/adapter_common.py` L260-267
