# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-28 (cycle-006 후 갱신)

## 완료 항목 (cycle-006)

- [x] **DRIFT-004**: `users[]` 섹션 6 필드 등록 (Must +3 / Nice +2 / Skip +1) → 분포 46 entries
- [x] **DRIFT-005**: `_BUILTIN_VENDOR_MAP` → `_FALLBACK_VENDOR_MAP` 이름 변경 + 3-tier path resolution + nosec silence
- [x] **DRIFT-006**: rule 12 R1에 Allowed (cycle-006 추가) 절 + 17 라인 `# nosec rule12-r1` silence
- [x] **W2 (b)**: os-gather Jinja2 OEM list silence + 동기화 책임 명시 + verify_vendor_boundary nosec 패턴
- [x] **vendor_boundary 0건 달성** (cycle-005 26 → 0)
- [x] CONVENTION_DRIFT.md DRIFT-004/005/006 모두 resolved
- [x] cycle-006 보고서 + CURRENT_STATE / NEXT_ACTIONS 갱신

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

## P1 — cycle-007 사용자 결정 대기 (대부분 외부 의존)

### 옵션 / 회귀 위험 큰 항목
- [ ] **DRIFT-006 옵션 (2)**: `redfish_gather.py` vendor-agnostic 리팩토링 — `oem_extractor` 매핑을 adapter capabilities로 위임. 영향 vendor 전부 회귀 + Round 권장. 별도 cycle.

### 외부 의존
- [ ] **새 vendor 추가** (Huawei iBMC / NEC / Inspur 등) — PO 결정 + 실장비
- [ ] **Round 11 실장비 검증** — 새 펌웨어 / 새 모델 (probe-redfish-vendor) — 실장비 + Round 일정

## P2 — cycle-007 AI 자체 가능 (운영 정책 결정 대기 외 잔여 거의 없음)

### 운영 / 정책
- [ ] **incoming-review hook 실 환경 테스트** — 다음 git merge 시 `docs/ai/incoming-review/<날짜>-<sha>.md` 자동 생성 확인
- [ ] **harness-cycle 정기 주기 결정** — 매주 / 격주 / 수동만 (사용자 결정)

## 결정 필요 (사용자, cycle-007 진입 시점)

| 항목 | 옵션 | 비고 |
|---|---|---|
| T2-D2 (cisco_baseline.json data.users) | `null` → `[]` | rule 13 R4 — 실측 evidence 필요 |
| T2-A7 (rule 7개 5요소 보강) | 진행 / 보류 | rule 24/26/41/50/60/70/90 큰 재구조화 |
| T3-01 (precheck requests 의존) | stdlib only / 유지 | 의존 정책 |
| T3-02 (HPE iLO5/6 priority 동률) | 차등 / 유지 | adapter 매칭 일관성 |
| T3-03 (Lenovo generic fallback) | 추가 / 유지 | adapter 정책 일관성 |
| T3-04 (adapter version 추적) | 의미 있는 버전 / 무시 | 추적 메커니즘 |
| T3-05 (redfish BMC IP N+1) | 첫 멤버만 / 병렬 / 유지 | 성능 vs 단순성 |
| T3-06 (governance 결정 ADR 필수) | 의무 / 선택 | trace 강도 |
| 새 vendor 추가 일정 | Huawei / NEC / Inspur | PO + 실장비 |
| Round 11 검증 | 새 펌웨어 / 새 모델 | 실장비 + 일정 |
| harness-cycle 정기 주기 | 자동 trigger 도입? | 운영 정책 |

## 정본 reference

- `docs/ai/CURRENT_STATE.md` (cycle-006 후 + 2026-04-28 full-sweep 갱신)
- `docs/ai/harness/cycle-006.md` (직전 cycle 보고서)
- `docs/ai/harness/full-sweep-2026-04-28.md` (이번 full-sweep 보고서)
- `docs/ai/impact/2026-04-27-vendor-boundary-57.md` (vendor 경계 분석)
- `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 6건)
- `docs/ai/decisions/ADR-2026-04-27-harness-import.md` (Plan 1~3 ADR)
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md` (cycle-003 첫 스캔)
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
