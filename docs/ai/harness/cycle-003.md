# Harness Cycle 003 — DRIFT 정리 + 도구 보강 + 실측

## 일자: 2026-04-27

## Trigger

cycle-002에서 발견한 3 DRIFT의 Tier 2 정리 + AI가 자체 처리 가능한 후속 작업 모두 수행 (사용자 명시 요청).

## 1. Observer (관측)

cycle-002 결과 list:
- DRIFT-001 (28→29 Must) — open
- DRIFT-002 (Stage 4 일반화) — open
- DRIFT-003 (vendor-bmc-guides adapter 이름) — planned
- output_schema_drift_check 정밀화 — pending
- rule 95 R1 자동 검출 도구 — pending
- network/firmware/users/power 섹션 상세 SCHEMA_FIELDS — pending
- EXTERNAL_CONTRACTS vendor별 endpoint 실측 — pending

## 2. Architect (변경 명세)

### Tier 2 (DRIFT 정리)
- `rule 13` 본문 "28 Must" → "29 Must + 8 Nice" + Stage 4 pipeline별 차이 명시
- `rule 80` 본문 R1 + R1-A로 Stage 4 pipeline별 표 분리
- `CLAUDE.md` 2곳 정정 (28 Must / Jenkins 4-Stage 일반화)
- `vendor-bmc-guides.md` HPE / Lenovo / Supermicro adapter 이름 정정

### Tier 1 (도구 보강 / catalog 보강)
- `scripts/ai/scan_suspicious_patterns.py` 신규 (rule 95 R1 11 패턴 자동 검출)
- `SCHEMA_FIELDS.md`에 network / firmware / users / power 섹션 채널 추가
- `EXTERNAL_CONTRACTS.md`에 redfish_gather.py 실측 endpoint / field 추가
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md` 첫 impact 보고서 (스캔 결과)
- DRIFT-001 / 002 / 003 상태 → resolved

## 3. Reviewer

본 cycle은 catalog-stale 정정 + 도구 추가. 도메인 코드 / 운영 영향 없음. 자가 검수 금지 (rule 25 R7) — 차기 reviewer가 검토.

## 4. Governor (Tier 분류)

| 적용 | Tier | 사유 |
|---|---|---|
| rule 13 / 80 본문 정정 | 2 | rule 변경 — 사용자 명시 위임 ("남은 AI 작업 모두") |
| CLAUDE.md 정정 | 2 | Tier 0 정본 — 사용자 명시 위임 |
| vendor-bmc-guides.md 정정 | 1 | reference docs 갱신 |
| scan_suspicious_patterns.py 신규 | 1 | 도구 추가 (advisory, 운영 영향 없음) |
| catalogs 보강 | 1 | docs 갱신 |
| DRIFT 상태 갱신 | 1 | catalog 갱신 |

## 5. Updater (적용)

본 cycle 적용 commit (이번 메시지에서):
- `.claude/rules/13-output-schema-fields.md` 본문 정정
- `.claude/rules/80-ci-jenkins-policy.md` R1 + R1-A 추가
- `CLAUDE.md` 2곳 정정
- `docs/ai/references/redfish/vendor-bmc-guides.md` adapter 이름 정정
- `scripts/ai/scan_suspicious_patterns.py` 신규
- `docs/ai/catalogs/SCHEMA_FIELDS.md` 섹션 상세 추가
- `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` redfish_gather.py 실측 추가
- `docs/ai/catalogs/CONVENTION_DRIFT.md` DRIFT 3건 상태 → resolved
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md` 신규
- `docs/ai/harness/cycle-003.md` (본 파일)

## 6. Verifier (검증)

```
$ python scripts/ai/verify_harness_consistency.py
=== 하네스 일관성 검증 ===
rules: 29, skills: 43, agents: 51, policies: 10
통과: 모든 참조 정합 확인

$ python scripts/ai/scan_suspicious_patterns.py
=== 의심 패턴 스캔 결과 (advisory) ===
[#11] Adapter origin 주석 누락 (rule 96 R1) — 13건
      → 다음 cycle 정리 후보 (TIER 2 — 사용자 결정)
```

## 결과

**Tier 2 + Tier 1 변경 PASS**.

DRIFT-001/002/003 모두 resolved 상태. 차기 cycle-004는:
- 13 adapter origin 주석 추가 (rule 96 R1 — 사용자 결정 후)
- output_schema_drift_check 매칭 로직 정밀화
- scan_suspicious_patterns.py false positive 줄이기

## 다음 cycle 시작점

- 새 vendor 추가 / Round 11 검증 (PO / 실장비 결정)
- adapter origin 주석 13개 일괄 추가
- 도구 정밀화 (scan / drift_check)

## 정본 reference

- workflow: `docs/ai/workflows/HARNESS_EVOLUTION_MODEL.md`
- catalog: `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 모두 resolved)
- impact: `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md`
- skill: `harness-cycle`
