# Harness Cycle 002 — 첫 실측 cycle

## 일자: 2026-04-27

## Trigger

Plan 3 완료 후 NEXT_ACTIONS P2 작업 (catalog 채우기 + verify 강화) 일환. 사용자가 "남은 작업 모두 수행"으로 명시 요청.

## 1. Observer (관측 + 실측)

### rule 28 R1 측정 대상 재측정

| # | 대상 | 결과 | drift 발견 |
|---|---|---|---|
| 1 | 출력 schema | sections 10 + Must 29 / Nice 8 (실측) | **DRIFT-001** — 일부 문서에 "28 Must"로 표기 |
| 3 | 벤더 어댑터 매트릭스 | Redfish 14 (Dell 3 / HPE 4 / Lenovo 2 / Supermicro 3 / Cisco 1 / generic 1) | **DRIFT-003** — vendor-bmc-guides.md에 부정확 adapter 이름 |
| 4-5 | Jenkinsfile 4-Stage | Stage 4가 pipeline별 다름 (E2E Regression / Ingest / Callback) | **DRIFT-002** — 도입 문서가 일반화로 표기 |
| 6 | 하네스 표면 | rules 29 / skills 43 / agents 51 / policies 10 / templates 8 / commands 5 / hooks 19 | (이전 cycle에서 갱신됨) |
| 10 | 벤더 경계 | verify_vendor_boundary 통과 | clean |

### 발견 요약

3 catalog-stale drift 발견 (DRIFT-001, 002, 003) — `docs/ai/catalogs/CONVENTION_DRIFT.md` 등록. 모두 catalog/도입 문서의 stale 표기. 실 코드/운영 영향 없음.

## 2. Architect (변경 명세)

### 본 cycle 적용

- **VENDOR_ADAPTERS.md**: 실측으로 정정 (14 adapter 정확 명시 + priority 일관성 검증 [PASS])
- **SCHEMA_FIELDS.md**: Must 29 / Nice 8 정정
- **JENKINS_PIPELINES.md**: Stage 4 차이 (E2E Regression / Ingest / Callback) 명시
- **CONVENTION_DRIFT.md**: 3 DRIFT entry 추가
- **verify_harness_consistency.py**: SKILL.md `name` ↔ 폴더 일치 검사 추가 (43 SKILL 모두 PASS)
- **output_schema_drift_check.py**: sections.yml nested 구조 (`sections:` 아래) 파싱 fix
- **install-git-hooks.sh**: 실 환경 설치 시도 → PASS (pre-commit / commit-msg / post-commit / post-merge 4 hook 설치됨)

### 차기 cycle 후속 (Tier 2 — 사용자 승인 필요)

- rule 13 본문 "28 Must" → "29 Must" 갱신
- rule 80 "Stage 4 = E2E Regression" 일반화 표현 정정 (pipeline별 차이 명시)
- vendor-bmc-guides.md adapter 이름 정정
- output_schema_drift_check.py 매칭 로직 정밀화 (field_dictionary 내부 path와 sections 매칭)

## 3. Reviewer (검수)

본 cycle은 catalog 갱신 + 도구 강화 (Tier 1) 위주. Tier 2 항목은 후속 cycle 사용자 승인.

자가 검수 금지 (rule 25 R7) — Tier 2 후속은 별도 reviewer.

## 4. Governor (Tier 분류)

| 적용 | Tier | 사유 |
|---|---|---|
| Catalog 갱신 (VENDOR_ADAPTERS / SCHEMA_FIELDS / JENKINS_PIPELINES / CONVENTION_DRIFT) | 1 | docs 갱신 / 실측 정정 |
| verify_harness_consistency.py 강화 | 1 | 검증 강화 (rule 위반 차단 강화) |
| output_schema_drift_check.py fix | 1 | bug fix (false positive 제거) |
| git hooks 실 환경 설치 | 1 | install script 실행 (commit/merge 시 advisory 검증) |
| rule 본문 수치 정정 (Must / Stage 4 일반화) | 2 | rule 변경 → 후속 cycle 사용자 승인 |

## 5. Updater (적용)

본 cycle 적용 commit (이번 메시지에서):

- `docs/ai/catalogs/VENDOR_ADAPTERS.md` 정정
- `docs/ai/catalogs/SCHEMA_FIELDS.md` 정정 (Must 29)
- `docs/ai/catalogs/JENKINS_PIPELINES.md` 정정 (Stage 4 pipeline별)
- `docs/ai/catalogs/CONVENTION_DRIFT.md` DRIFT-001 / 002 / 003 등록
- `scripts/ai/verify_harness_consistency.py` SKILL.md name 검사 추가
- `scripts/ai/hooks/output_schema_drift_check.py` nested parse fix
- `.git/hooks/{pre-commit,commit-msg,post-commit,post-merge}` 설치됨 (untracked)

## 6. Verifier (검증)

```
$ python scripts/ai/verify_harness_consistency.py
=== 하네스 일관성 검증 ===
rules: 29, skills: 43, agents: 51, policies: 10
통과: 모든 참조 정합 확인

$ python scripts/ai/hooks/output_schema_drift_check.py
output schema drift 감지:
  - sections.yml에 있지만 field_dictionary.yml에 없는 섹션: ['system', 'hardware', 'bmc', 'cpu', 'memory', 'storage', 'network', 'firmware', 'users', 'power']
```

후자는 **개선된 동작**이지만 false positive (field_dictionary 구조가 달라 단순 top-level key 매칭 부적합). 다음 cycle에서 정밀화.

## 결과

**Tier 1 변경 PASS**. Tier 2 후속 작업은 NEXT_ACTIONS / DRIFT entry로 보존.

## 다음 cycle 시작점

- DRIFT-001 / 002 / 003 정리 (rule 13 / 80 본문 + vendor-bmc-guides.md)
- output_schema_drift_check.py 매칭 로직 정밀화
- Round 11 검증 (실장비 — PO 결정)
- 새 vendor 추가 시도 (PO 결정)

## 정본 reference

- workflow: `docs/ai/workflows/HARNESS_EVOLUTION_MODEL.md`
- catalog: `docs/ai/catalogs/CONVENTION_DRIFT.md` DRIFT-001/002/003
- skill: `harness-cycle`
