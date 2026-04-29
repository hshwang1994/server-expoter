# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-29 (cycle-013 종료 시점 — cycle-012 자율 매트릭스 7건 closed + 정합 정정)

## ⏳ 현재 상태 (한 줄)

cycle-012 PR #1 머지 완료 (`b74c1103`). cycle-013에서 자율 매트릭스 7건 (AI-1~AI-7) 모두 closed + 분포 1건 over count 정정. **lab 검증 + main 정리 대기 중**.

## 다음 세션 시작 시 확인 순서 (cold start)

1. **main 갭** — `git fetch origin && git log --oneline origin/main..HEAD` 으로 cycle-013 commit (`0150fa2e`) main 머지 여부 확인 (현재 ahead 1, behind 1)
2. **운영자 빌드 결과 확인** — OPS-1 Jenkins 시범 결과 받았는지 (envelope `meta.auth.fallback_used` 값)
3. **자율 매트릭스 잔여** — 본 매트릭스의 AI-8 (main pull + 정리)만 잔여 (rule 93 R2 사용자 명시 승인 필요)

## 자율 진행 closed (cycle-013 완료)

| # | 작업 | 결과 | commit |
|---|---|---|---|
| AI-1 | schema/examples 11 path 보강 | validate_field_dictionary 11 WARN → 0 WARN | `0150fa2e` |
| AI-2 | PROJECT_MAP fingerprint 재계산 | drift 6 → 0 + 본문 stale 4건 정정 | `0150fa2e` |
| AI-3 | JENKINS_PIPELINES.md 갱신 | vault binding 절 신규 (server-gather-vault-password) | `0150fa2e` |
| AI-4 | SCHEMA_FIELDS.md 갱신 | Must 31 / Nice 20 / Skip 6 = 57 (1건 over count 정정) | `0150fa2e` |
| AI-5 | VENDOR_ADAPTERS.md 헤더 갱신 | recovery_accounts 메타 절 신규 | `0150fa2e` |
| AI-6 | cycle-012.md 신규 | governance 보존 | `0150fa2e` |
| AI-7 | ADR vault-encrypt-adoption | rule 70 R8 trigger 미해당 advisory governance trace | `0150fa2e` |

## 자율 진행 잔여 (다음 세션 AI)

| # | 작업 | 전제 | 차단 사유 |
|---|---|---|---|
| AI-8 | main pull 후 cycle-013 commit 정리 + CURRENT_STATE 종료 갱신 | rule 93 R2 사용자 명시 승인 | main 머지 / 브랜치 전환은 사용자 결정 |

## 사용자 개입 필요 (자율 불가, 명시 승인 후 진행)

| # | 작업 | 이유 | 진입 후 AI 가능 작업 |
|---|---|---|---|
| OPS-1 | Jenkins 빌드 시범 1회 (target_type=redfish, 임의 BMC) | UI 클릭 + lab 환경 | console log 받으면 envelope 분석 + 회귀 fixture 추가 |
| ~~OPS-2~~ | ~~PR 머지 결정 (squash 권장)~~ | ~~rule 93 R4 main 보호~~ | **closed 2026-04-29** — PR #1 머지 완료 (`b74c1103`) |
| OPS-3 | 평문 password 6종 회전 (Passw0rd1!/Goodmit0802!/Dellidrac1!/calvin/hpinvent1!/VMware1!) — Git history 잔존 | 운영팀 일정 + 실 장비 | 회전 후 vault에 새 password 반영 + encrypt + 새 PR |
| OPS-4 | P1 lab 회귀 — vendor 5종 1차 / 2차 fallback 시나리오 | 실 BMC + lab cycle | 결과 받으면 evidence + baseline 갱신 |
| OPS-5 | P2 dryrun OFF 전환 (Dell + HPE 먼저) | rule 92 R5 + BMC 잠금 위험 | 결정 받으면 `_rf_account_service_dryrun: false` 토글 + lab 검증 |
| OPS-6 | baseline_v1/* 7개 실측 갱신 (P3/P4 신 필드 정합) | rule 13 R4 — 실측 기반만 | probe_redfish.py 결과 받으면 baseline 갱신 + Stage 4 회귀 |
| OPS-7 | settings.local.json 편집 — AI self-modification 차단 (cycle-011 잔여) | settings.json만으로 풀림 확인됨 | 운영자 직접 편집 |
| OPS-8 | main에 cycle-013 commit 정리 (PR 또는 직접) | rule 93 R2 머지 사용자 명시 승인 | 승인 받으면 main 정리 + CURRENT_STATE 종료 갱신 (AI-8) |
| AI-9 | 25개 stale reference cleanup (cycle-011 advisory 잔여) | 즉시 — cycle-013 11건 처리 후 약 38건 잔존 | 별도 cycle (영향 범위 큼) — rule 60 / pre_commit_policy / vault-rotator 본문 참조 정리 |
| AI-10 | docs/ai/harness/ archive 진입 (cycle-001~005 → archive/) | rule 70 R6 정본 catalog 비대화 차단 | 별도 cycle — 사용자 archive 정책 명시 후 |
| AI-11 | docs/ai/impact/ 6 보고서 archive (구조·정책 전환 reasoning 보존) | rule 70 R6 첫 질문 YES | 별도 cycle |

## 사용자 결정 명시 필요 (Phase 진입 전)

| # | 항목 | 후보 | AI 추천 |
|---|---|---|---|
| DEC-1 | OS/ESXi secondary 자격 사용 시 envelope `meta.auth.fallback_used: true` 노출 정책 | 노출 / 비노출 | 노출 (이미 P1 commit에 적용됨) |
| DEC-2 | P5 sub-phase 우선순위 (Linux NTP+firewall+listening 완료 / Windows runtime 완료 / ESXi vSwitch 완료) | 다음 sub-phase = ESXi multipath / license? | 본 cycle은 sub-phase a+b 완료 — c (multipath/license) 별도 cycle |
| DEC-3 | Cisco AccountService 미지원 처리 — 운영자 수동 복구 절차 매뉴얼 | 작성 / 보류 | docs/ 별도 매뉴얼 |

## cycle-013 요약 (이번 세션 완료)

`0150fa2e` cycle-013 catalog 5종 + cycle-012 보고서 + ADR + examples 11 path

**자율 매트릭스 7건 (AI-1~AI-7) closed**:
- catalog 4종 (PROJECT_MAP / JENKINS_PIPELINES / SCHEMA_FIELDS / VENDOR_ADAPTERS) 갱신
- cycle-012.md 보고서 + ADR-2026-04-29-vault-encrypt-adoption advisory 신규
- schema/examples 11 path 보강 (validate 11 WARN → 0)

**발견 + 정정**: cycle-012 commit 메시지 / 헤더 주석 1건 over count (Nice 21 → 20, 58 → 57). 모든 catalog 정합.

**검증**: harness consistency / vendor boundary / project_map_drift / validate_field_dictionary 모두 PASS.

## cycle-012 요약 (이전 세션 완료)

`f0f621ce` P0 / `fe0be36c` P1 / `0448d00d` P2+P4(Redfish) / `fbb0f357` P3+P4 normalize / `92b935c3` P5 Linux / `b6d24fd3` P4 OS/ESXi + P5 Windows / `8e536447` schema 12 entries / `c37138ca` docs / `29fee49a` vault encrypt + credential 'server-gather-vault-password'

**검증**: 145 e2e PASS / harness 28-43-49-9 / vendor boundary / field_dictionary Must31-Nice21-Skip6=58
**plan**: `C:\Users\hshwah\.claude\plans\1-snazzy-haven.md`
**handoff**: `docs/ai/handoff/2026-04-29-cycle-012.md`
**branch**: `feature/3channel-expansion`

---

## 완료 항목 (cycle-011 — 보안 정책 자체 해제)

## 완료 항목 (cycle-011 — 보안 정책 자체 해제)

- [x] **rule 60 + 정책 / hook / agent 11개 일괄 제거** (사용자 명시 결정 옵션 A)
- [x] **settings.json 보안 deny 38건 + disableBypassPermissionsMode 제거** + defaultMode bypassPermissions + sandbox allowUnsandboxedCommands
- [x] **git hooks 재설치** (pre_commit_policy 제거)
- [x] **rule 00 보호 경로 절 갱신** (참고용으로 변경)
- [x] **ADR 작성** (rule 70 R8 두 번째 적용)
- [x] **surface-counts.yaml 갱신** (28/43/49/9)
- [x] **verify_harness_consistency / verify_vendor_boundary** PASS
- [x] **SSH/WinRM 자동화 재시도** — Win Server 2022 (10.100.64.135) 28/28 PASS, 4.14 MB raw archive 수집 → `tests/reference/os/win2022/10_100_64_135/`
- [x] **evidence 작성** — `tests/evidence/2026-04-28-win2022-validation.md`
- [x] **Round 12 자동 재수집** — Linux 6/6 + ESXi 3/3 (SSH 활성화 후 모두 OK) + Redfish 9/11 + Agent 4/4
- [-] **Win10 (10.100.64.120)** — 사용자 결정으로 **제외** (자격 미해결)
- [-] **WinServer2022 (10.100.64.132)** — 사용자 결정으로 **제외** (WinRM 비활성)
- [-] **Dell 10.100.15.32** — 사용자 결정으로 **제외** (vendor mismatch / AMI Redfish Server)
- [ ] **Cisco 10.100.15.1 Redfish 활성화** — 웹 UI는 200 OK, but `/redfish/v1/` → 503. CIMC에서 Redfish service 별도 enable 필요 (Cisco UCS Manager 또는 CIMC CLI: `scope cimc; scope https; set redfish-enabled yes; commit`)
- [ ] **Cisco 10.100.15.3 라우팅 확인** — 사용자 PC에서는 웹 접근 OK, but Agent 154 (Jenkins)에서는 모든 포트 unreachable. 네트워크 라우팅 / 방화벽 정책 확인 필요
- [ ] **settings.local.json** — AI self-modification 차단으로 사용자 직접 편집 필요 (settings.json만으로 자동화 풀림 확인됨)
- [ ] **25개 stale reference cleanup** — advisory, 후속 incremental

## 완료 항목 (cycle-010 — T3-04/05/06 일괄 + rule 70 R8 신설)

- [x] **T3-04 (04-A 채택)** — 27 adapter `version: "1.0.0"` placeholder 일괄 삭제 (참조 0건 검증)
- [x] **T3-05 (05-A 유지)** — redfish_gather.py BMC IP 수집 현재 유지. break-on-first-IP가 실 N+1 아니므로 NEXT_ACTIONS close
- [x] **T3-06 (06-B 채택)** — `rule 70 R8` 신설 (ADR 의무 trigger 3종: rule 본문 의미 변경 / 표면 카운트 변경 / 보호 경로 정책 변경)
- [x] **소급 ADR 작성** — `ADR-2026-04-28-rule12-oem-namespace-exception.md` (DRIFT-006 governance trace 보강 — R8 적용 첫 사례)
- [x] **검증 5종 PASS** — verify_harness_consistency / verify_vendor_boundary / 27 adapter YAML 파싱 / project_map_drift --update / version 키 0/27
- [x] **증거 문서 4종 갱신** — CURRENT_STATE / NEXT_ACTIONS / TEST_HISTORY / harness/cycle-010.md

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

## 결정 필요 (사용자)

| 항목 | 옵션 | 비고 |
|---|---|---|
| T2-D2 (cisco_baseline.json data.users) | `null` → `[]` | rule 13 R4 — 실측 evidence 필요 |
| 새 vendor 추가 일정 | Huawei / NEC / Inspur | PO + 실장비 |
| Round 11 검증 | 새 펌웨어 / 새 모델 | 실장비 + 일정 |
| harness-cycle 정기 주기 | 자동 trigger 도입? | 운영 정책 |

## 해결됨 (cycle-007 / cycle-008 / cycle-010)

- T3-01 (precheck requests 의존) → cycle-007에서 stdlib only로 해결
- T3-02 (HPE iLO5/6 priority 동률) → cycle-008에서 차등 (90/100) 적용
- T3-03 (Lenovo generic fallback) → cycle-008에서 lenovo_bmc.yml 추가 (Cisco도 같이)
- T3-04 (adapter version 추적) → cycle-010에서 04-A 삭제 채택 (placeholder 1줄 일괄 제거)
- T3-05 (redfish BMC IP N+1) → cycle-010에서 05-A 유지 결정 (break-on-first-IP가 실 N+1 아님)
- T3-06 (governance ADR 의무) → cycle-010에서 06-B 채택 (rule 70 R8 신설 + 조건부 trigger 3종)

## 정본 reference

- `docs/ai/CURRENT_STATE.md` (cycle-008 후 갱신)
- `docs/ai/harness/cycle-006.md` (직전 cycle 보고서)
- `docs/ai/harness/full-sweep-2026-04-28.md` (full-sweep 보고서)
- `docs/ai/impact/2026-04-27-vendor-boundary-57.md` (vendor 경계 분석)
- `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 6건)
- `docs/ai/decisions/ADR-2026-04-27-harness-import.md` (Plan 1~3 ADR)
- `docs/ai/impact/2026-04-27-suspicious-pattern-scan.md` (cycle-003 첫 스캔)
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
