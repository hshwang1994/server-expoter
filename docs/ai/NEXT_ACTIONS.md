# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-28 (cycle-009 후 갱신)

## 완료 항목 (cycle-009 — fallback envelope HIGH fix 2건 + T2-A7 rule 5요소 보강 7개)

- [x] **HIGH 버그 fix #1** — `os-gather/site.yml` Windows PLAY 3 `always` fallback envelope 2 필드 → 13 필드 (rule 13 R5 / rule 20 R1 정합)
- [x] **HIGH 버그 fix #2** — `esxi-gather/site.yml` `always` fallback의 미정의 변수 `_ip` → `_e_ip` 정정 (fallback 시 ip null 출력되던 문제)
- [x] **MED fix** — 3채널 fallback envelope `collection_method` 값 build_meta와 일관성 (OS `ansible`→`agent`, ESXi `vmware`→`vsphere_api`, Redfish `redfish`→`redfish_api`)
- [x] **T2-A7 rule 24** — completion-gate 5요소 보강 (R1~R9, 정적 검증 / 버그 0건 / 문서 4종 / 후속 식별 / Git push / Schema 회귀 / 종결어 금지 / "남은 작업" 답변 / 보고 포맷)
- [x] **T2-A7 rule 26** — multi-session-guide 5요소 보강 (R1~R8, 진입 조건 / 오너십 / commit pathspec / 공용 파일 / 동기화 / CONTINUATION / 마커 / 종료 갱신)
- [x] **T2-A7 rule 41** — mermaid-visualization 5요소 보강 (R1~R18, 타입 / 가시성 / 색상 / 형상 / ID / 라벨 / 30노드 / 성공실패 / AS-IS / vendor / 문맥 / 범례 / 호환 / sequence / state / gantt / er / ASCII)
- [x] **T2-A7 rule 50** — vendor-adapter-policy 5요소 보강 (R1~R6, 정규화 정본 / 9단계 / 점수 / branch / 경계 / generic fallback)
- [x] **T2-A7 rule 60** — security-and-secrets 5요소 보강 (R1~R8, encrypt / 회전 / redaction / verify / 자격증명 / stacktrace / 입력 / 스캔)
- [x] **T2-A7 rule 70** — docs-and-evidence-policy 5요소 보강 (R1~R7, 갱신 매핑 / fingerprint / 작성 원칙 / 정본 보호 / 보존 판정 / archive / cycle 자문)
- [x] **T2-A7 rule 90** — commit-convention 5요소 보강 (R1~R6, type 8 / 길이 / 금지어 / 본문 / 강제 수준 / AI 동등)

## 완료 항목 (cycle-008 — P2 MED/LOW 11건 일괄, 사용자 "새 vendor 제외 모두" 명시 승인)

- [x] **redfish_gather.py docstring Cisco 추가** (LOW)
- [x] **redfish_gather.py:727 `int(vcap_int / 1048576)` → `vcap_int // 1048576` 정수 나눗셈 통일** (LOW)
- [x] **callback_plugins/json_only.py `_emit()` silent pass 보강** — `JSON_ONLY_DEBUG=1` 환경변수로 stderr 경고 활성화 (호출자 호환성 유지)
- [x] **adapter_loader 동률 정렬 문서화** — Python list.sort stable + 파일명 알파벳 tie-break + 동률 발견 시 vvv 경고
- [x] **HPE iLO5/6 priority 차등 (T3-02)** — iLO 6=100, iLO 5=90, iLO 4=50, generic=10
- [x] **Lenovo generic fallback adapter 추가 (T3-03)** — `lenovo_bmc.yml` priority=10
- [x] **Cisco generic fallback adapter 추가** — `cisco_bmc.yml` priority=10 (Lenovo와 동일 패턴)
- [x] **lenovo_imm2.yml tested_against 펌웨어 명시** (rule 96 R1 origin 강화)
- [x] **cisco_cimc.yml 세대 차등 검토 결정 명시** — M5/M6 실장비 검증 부족으로 차등 분리 보류, generic fallback만 추가
- [x] **Cisco OEM gather_system 분기 silent 의도 명시** — adapter strategy=standard_only + Round 11 실측 OEM 비어있음 + bmc_names에 'cisco':'CIMC' 추가
- [x] **redfish_gather.py 추가 함수 분리** — gather_system 103→57줄 (vendor OEM helper 4종 + dispatch dict), detect_vendor 64→37줄 (`_fetch_service_root` + `_resolve_first_member_uri`), main 67→45줄 (`_make_section_runner` + `_collect_all_sections` + `_compute_final_status`)
- [x] **os-gather/tasks/linux/gather_system.yml 분리** — 346→322줄, `build_identifier_diagnostics.yml` 별도 task

## 완료 항목 (cycle-007 — 4축 검수 + HIGH 4 일괄)

- [x] **#1 redfish_gather.py `gather_storage()` 190줄 분리** — 5 함수 분리 (logic 동일, signature 동일, pytest 95/95 PASS)
- [x] **#2 rule 22 R7 텍스트 정정** — 5 공통 fragment 변수 명명 (`_data_fragment` + `_sections_{supported,collected,failed}_fragment` + `_errors_fragment`) 8 파일 일괄 갱신
- [x] **#3 precheck_bundle.py `run_module()` 181줄 + adapter_loader.py `LookupModule.run()` 115줄 분리** — 6+5 헬퍼 함수 추출
- [x] **#4 precheck_bundle.py `requests` 의존 제거** — urllib stdlib 단일 경로 통일 + 에러 분류 강화

## 완료 항목 (full-sweep 잔여 — 이전 세션)

- [x] **T2-B2**: `verify_harness_consistency.py` FORBIDDEN_WORDS default 활성화 (`--no-forbidden-check`로 비활성)
- [x] **T2-C2**: `precheck_bundle.py` Stage 1 (reachable) ↔ Stage 2 (port_open) 분리 + ConnectionRefusedError 시 host alive 판정
- [x] **T2-C8**: `os-gather/files/get_last_login.sh` 공유 snippet + lookup file 통합 (gather_users.yml 294 → 239 lines)
- [x] T2-C1 분석: precheck timeout (3/6/8s) ↔ 본 수집 timeout (rule 30 R3 30/10/30s) 의도된 차이로 변경 SKIP

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

## P1 — 사용자 결정 대기 (외부 의존)

### 옵션 / 회귀 위험 큰 항목
- [ ] **DRIFT-006 옵션 (2)**: `redfish_gather.py` vendor-agnostic 리팩토링 — `oem_extractor` 매핑을 adapter capabilities로 위임. 영향 vendor 전부 회귀 + Round 권장. 별도 cycle.

### 외부 의존
- [ ] **새 vendor 추가** (Huawei iBMC / NEC / Inspur 등) — PO 결정 + 실장비
- [ ] **Round 11 실장비 검증** — 새 펌웨어 / 새 모델 (probe-redfish-vendor) — 실장비 + Round 일정

## P2 — 잔여 (외부 의존 / 사용자 결정 / 운영)

### 운영 / 정책 (사용자 결정)
- [ ] **incoming-review hook 실 환경 테스트** — 다음 git merge 시 `docs/ai/incoming-review/<날짜>-<sha>.md` 자동 생성 확인
- [ ] **harness-cycle 정기 주기 결정** — 매주 / 격주 / 수동만 (사용자 결정)

### Vendor 차등 — 실장비 검증 후 진행
- [ ] **adapters/redfish/cisco_cimc.yml 세대 차등 (M4/M5/M6 차등 분리)** — M5/M6 실장비 검증 후 진행 (현재 M4만 Round 11 검증됨)

### Schema / Baseline (실측 evidence 필요, AI 자체 불가)
- [ ] **T2-D2** cisco_baseline.json `data.users` `null` → `[]` (rule 13 R4 — 실측 evidence 필요)

### Rule 재구조화 (대규모, 별도 cycle 필요)
- [ ] **DRIFT-006 옵션 (2)**: redfish_gather.py vendor-agnostic 리팩토링 — _OEM_EXTRACTORS dispatch는 cycle-008에서 적용. 다음 단계는 dispatch 자체를 adapter capabilities로 위임. 영향 vendor 전부 회귀 + Round 권장

## 결정 필요 (사용자, cycle-007 진입 시점)

| 항목 | 옵션 | 비고 |
|---|---|---|
| T2-D2 (cisco_baseline.json data.users) | `null` → `[]` | rule 13 R4 — 실측 evidence 필요 |
| T3-04 (adapter version 추적) | 의미 있는 버전 / 무시 | 추적 메커니즘 |
| T3-05 (redfish BMC IP N+1) | 첫 멤버만 / 병렬 / 유지 | 성능 vs 단순성. cycle-008에서 `_resolve_first_member_uri` helper 추출했지만 정책 자체는 "첫 멤버만" 유지 |
| T3-06 (governance 결정 ADR 필수) | 의무 / 선택 | trace 강도 |
| 새 vendor 추가 일정 | Huawei / NEC / Inspur | PO + 실장비 |
| Round 11 검증 | 새 펌웨어 / 새 모델 | 실장비 + 일정 |
| harness-cycle 정기 주기 | 자동 trigger 도입? | 운영 정책 |

## 해결됨 (cycle-007 / cycle-008)

- T3-01 (precheck requests 의존) → cycle-007에서 stdlib only로 해결
- T3-02 (HPE iLO5/6 priority 동률) → cycle-008에서 차등 (90/100) 적용
- T3-03 (Lenovo generic fallback) → cycle-008에서 lenovo_bmc.yml 추가 (Cisco도 같이)

## 정본 reference

- `docs/ai/CURRENT_STATE.md` (cycle-008 후 갱신)
- `docs/ai/harness/cycle-006.md` (직전 cycle 보고서)
- `docs/ai/harness/full-sweep-2026-04-28.md` (full-sweep 보고서)
- `docs/ai/impact/2026-04-27-vendor-boundary-57.md` (vendor 경계 분석)
- `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 6건)
- `docs/ai/decisions/ADR-2026-04-27-harness-import.md` (Plan 1~3 ADR)
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md` (cycle-003 첫 스캔)
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
