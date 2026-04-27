# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-28 (cycle-005 후 갱신)

## 완료 항목 (cycle-005)

- [x] **DRIFT-007 catalog 정합** — Must 28 / Nice 7 / Skip 5 = 40 entries 실측 확정 (cycle-002 grep 헤더 noise 오인 정정)
  - CLAUDE.md / rule 13 / SCHEMA_FIELDS.md / field_dictionary.yml 헤더 / SKILL.md 일괄 갱신
  - SCHEMA_FIELDS.md 측정 명령 grep → YAML 파싱 변경
- [x] **scan #2 재설계** — set_fact 다음 indent 블록 lookahead로 누적 변수 침범만 검출 (107 → 0건)
- [x] **scan #4 specificity 분석** — distribution_patterns / version_patterns / firmware_patterns 분리 검사 (7 → 0건)
- [x] **verify_vendor_boundary docstring 인식** — Python triple-quote 영역 skip (33 → 26건)
- [x] **verify_harness_consistency 동기화 게이트** — `_BUILTIN_VENDOR_MAP` ↔ `vendor_aliases.yml` advisory (DRIFT-005 옵션 (2) 사전)

## 완료 항목 (cycle-004)

- [x] 도구 3종 정밀화 (verify_vendor_boundary 인코딩 fix + scan / output_schema_drift_check 정밀화)
- [x] 13 adapter origin 주석 일괄 추가 (rule 96 R1)
- [x] redfish_gather.py `_safe_int` helper + 6 블록 refactor
- [x] detect_vendor.yml default 가드 + 변수 상태 13건 silence
- [x] vendor 경계 57건 분석 보고서
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

## P2 — cycle-006 AI 자체 가능 (잔여 작업 거의 없음)

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
