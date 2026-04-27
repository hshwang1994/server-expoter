# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-27 (cycle-004 후 갱신)

## 완료 항목 (cycle-004)

- [x] 도구 3종 정밀화
  - [x] `verify_vendor_boundary.py` UnicodeEncodeError fix + `--full` 옵션 + `vendor_aliases.yml` EXCLUDE
  - [x] `scan_suspicious_patterns.py` #2 builder 제외 / #4 vendor 그룹화 / #9 docstring 제외 / silence 패턴
  - [x] `output_schema_drift_check.py` `fields:` dotted path → prefix 추출 + 따옴표/[] 처리 + envelope 화이트리스트
- [x] **13 adapter origin 주석 일괄 추가** (rule 96 R1)
- [x] **redfish_gather.py `_safe_int` helper + 6 블록 refactor** (10 cast 통일)
- [x] `detect_vendor.yml:35` `default('unknown')` 가드
- [x] **변수 상태 13건 의도 silence 주석** (#5 13 → 0건)
- [x] **vendor 경계 57건 분석 보고서** — `docs/ai/impact/2026-04-27-vendor-boundary-57.md`
- [x] cycle-004 보고서 + CURRENT_STATE / NEXT_ACTIONS / CONVENTION_DRIFT 갱신
- [x] DRIFT-004/005/006 등재

## P1 — cycle-005 사용자 결정 대기

### 사용자 명시 승인 필요 (rule 92 R5 schema / rule 12 R1 vendor 경계)
- [ ] **DRIFT-004**: `users` 섹션을 `schema/field_dictionary.yml`에 등록 — schema 변경 승인 필요
  - 추가 항목 후보: `users[].name`, `users[].uid`, `users[].gid`, `users[].groups`, `users[].shell`, `users[].home`
  - 영향 vendor: 모든 OS gather (Linux + Windows) baseline 갱신 의무
- [ ] **DRIFT-005**: `_VENDOR_ALIASES` (Python module) ↔ `vendor_aliases.yml` 중복 정리 — 옵션 (1)/(2)/(3) 결정
- [ ] **DRIFT-006**: `redfish_gather.py` vendor 분기 17건 — 옵션 (1)/(2)/(3) 결정 (`docs/ai/impact/2026-04-27-vendor-boundary-57.md`)
- [ ] **W2 (b)**: os-gather/tasks/{linux,windows}/gather_system.yml Jinja2 OEM list — vendor_aliases 참조 / 동기화 주석 / 무시 결정

### 사용자 명시 승인 추가 발견 (cycle-004 verifier WSL pytest)
- [ ] **DRIFT-007**: `field_dictionary.yml` 실측 ("Must 28 + Nice 7 + Skip 5") ↔ cycle-003 DRIFT-001 정정값 ("Must 29 + Nice 8") 불일치 — rule 13 / CLAUDE.md / SCHEMA_FIELDS.md 일괄 정정 필요

### 외부 의존
- [ ] **새 vendor 추가** (Huawei iBMC / NEC / Inspur 등) — PO 결정 + 실장비
- [ ] **Round 11 실장비 검증** — 새 펌웨어 / 새 모델 (probe-redfish-vendor) — 실장비 + Round 일정

## P2 — cycle-005 AI 자체 가능

### 도구 정밀화 (남은 false positive)
- [ ] `scan_suspicious_patterns.py` #2 재설계 — set_fact 다음 라인 분석으로 진짜 fragment 침범만 검출 (107건 → 잔여 ≤ 5건 목표)
- [ ] `scan_suspicious_patterns.py` #4 specificity 분석 — 같은 priority여도 distribution_patterns / version_patterns로 분리되면 silence (7건 → 잔여 ≤ 1건 — HPE iLO5 vs iLO6)
- [ ] `verify_vendor_boundary.py` Python `"""` docstring 인식 — 7건 false positive 추가 제거
- [ ] `verify_harness_consistency.py` 에 `_VENDOR_ALIASES` ↔ `vendor_aliases.yml` 동기화 게이트 추가 (DRIFT-005 (2) 옵션 시)

### 운영 / 정책
- [ ] **incoming-review hook 실 환경 테스트** — 다음 git merge 시 `docs/ai/incoming-review/<날짜>-<sha>.md` 자동 생성 확인
- [ ] **harness-cycle 정기 주기 결정** — 매주 / 격주 / 수동만 (사용자 결정)

## 결정 필요 (사용자, cycle-005 진입 시점)

| 항목 | 옵션 | 비고 |
|---|---|---|
| DRIFT-004 (users 섹션 등록) | 등록 / 보류 | rule 92 R5 schema 변경 |
| DRIFT-005 (`_VENDOR_ALIASES` 중복) | YAML import / 동기화 게이트 / 무시 | rule 50 R2 9단계 영향 |
| DRIFT-006 (vendor 분기 17건) | adapter origin OEM 매핑 / 라이브러리 리팩토링 / rule 12 예외 | 영향 큼 — 별도 cycle 권장 |
| W2 (b) Jinja2 OEM list | vendor_aliases 참조 / 동기화 주석 / 무시 | os-gather 영향 |
| 새 vendor 추가 일정 | Huawei / NEC / Inspur | PO + 실장비 |
| Round 11 검증 | 새 펌웨어 / 새 모델 | 실장비 + 일정 |
| harness-cycle 정기 주기 | 자동 trigger 도입? | 운영 정책 |

## 정본 reference

- `docs/ai/CURRENT_STATE.md` (cycle-004 후 갱신)
- `docs/ai/harness/cycle-004.md` (이번 cycle 보고서)
- `docs/ai/impact/2026-04-27-vendor-boundary-57.md` (vendor 경계 분석)
- `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 6건)
- `docs/ai/decisions/ADR-2026-04-27-harness-import.md` (Plan 1~3 ADR)
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md` (cycle-003 첫 스캔)
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
