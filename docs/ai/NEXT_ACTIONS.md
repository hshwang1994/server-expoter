# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-27 (cycle-003 후 갱신)

## 완료 항목 (이번 세션)

- [x] Plan 1 (Foundation) / Plan 2 (Skills + Agents) / Plan 3 (docs/ai)
- [x] References 14개 (외부 시스템 / 라이브러리 / 표준)
- [x] cycle-001 (dry-run) / cycle-002 (실측 + DRIFT 발견) / cycle-003 (DRIFT 정리 + 도구 보강)
- [x] verify_harness_consistency.py에 SKILL.md name 검사 추가
- [x] output_schema_drift_check.py nested parse fix
- [x] **scan_suspicious_patterns.py 신규** (rule 95 R1 11 패턴 자동 검출)
- [x] git hooks 실 환경 설치
- [x] clovirone-base/ 폴더 제거
- [x] 중복 templates 제거
- [x] **DRIFT-001/002/003 모두 resolved** (rule 13 / 80 / CLAUDE.md / vendor-bmc-guides 정정)
- [x] EXTERNAL_CONTRACTS.md에 redfish_gather.py 실측 endpoint / field 추가
- [x] SCHEMA_FIELDS.md에 10 섹션 채널 매핑 완성
- [x] 첫 impact 보고서 (scan_suspicious_patterns 결과)

## P1 — 차기 cycle (사용자 / 운영 결정 필요)

### Tier 2 (사용자 명시 승인)
- [ ] **13 adapter origin 주석 추가** — `scan_suspicious_patterns.py` 발견. 각 adapter에 vendor / firmware / tested_against / oem_path 주석 (rule 96 R1)
- [ ] **rule 80 cron 표현식 실측** — Jenkins console에서 trigger 블록 grep 후 catalog 갱신

### 사용자 / PO / 실장비 의존
- [ ] **새 vendor 추가 시도** — `add-new-vendor` skill 검증 (Huawei iBMC / NEC / Inspur 등) — PO 결정
- [ ] **Round 11 실장비 검증** — 새 펌웨어 / 새 모델 (probe-redfish-vendor) — 실장비 + Round 일정 결정

## P2 — 도구 정밀화 (다음 cycle AI 자체 가능)

- [ ] `output_schema_drift_check.py` 매칭 로직 정밀화 — field_dictionary 안 path와 sections 매칭
- [ ] `scan_suspicious_patterns.py` false positive 줄이기:
  - Pattern #2: `common/tasks/normalize/`는 builder라 제외 (rule 11 R1 허용)
  - Pattern #4: 같은 vendor 내 그룹화 후 동률 비교
  - Pattern #9: docstring 주석 라인 제외
- [ ] `verify_harness_consistency.py`에 agent frontmatter 검증 추가

## P2 — 운영 / 정책

- [ ] **incoming-review hook 실 환경 테스트** — 다음 git merge 시 `docs/ai/incoming-review/<날짜>-<sha>.md` 자동 생성 확인
- [ ] **harness-cycle 정기 주기 결정** — 매주 / 격주 / 수동만

## 결정 필요 (사용자)

| 항목 | 비고 |
|---|---|
| 13 adapter origin 주석 추가 일정 | rule 96 R1 정리 |
| 새 vendor 추가 일정 | PO 결정 + 실장비 |
| harness-cycle 정기 주기 | 자동 trigger 도입? |
| Round 11 검증 일정 | 운영 정책 |

## 정본 reference

- `docs/ai/CURRENT_STATE.md`
- `docs/ai/decisions/ADR-2026-04-27-harness-import.md`
- `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 모두 resolved)
- `docs/ai/harness/cycle-003.md`
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md`
