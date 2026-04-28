# server-exporter 현재 상태

## 일자: 2026-04-28 (cycle-011 — 보안 정책 자체 해제 + AI 자동화 권한 부여)

## 요약

server-exporter AI 하네스 **Plan 1+2+3 + cycle-001 ~ cycle-011 + full-sweep (Tier 1+2) 완료**. cycle-011에서 사용자 명시 결정으로 **보안 정책 자체 해제** — rule 60 + 관련 정책/hook/agent 11개 일괄 제거. AI 자동화 권한 확대.

cycle-011 변경 (이번 세션):

- **rule 60 (security-and-secrets) 삭제**: rules 29 → 28
- **policy/security-redaction-policy.yaml 삭제**: policies 10 → 9 (protected-paths.yaml은 stub로 잔존)
- **scripts/ai/hooks/pre_commit_policy.py 삭제**: hooks 19 → 18 + git hooks 재설치
- **scripts/ai/policy_loader.py 삭제**
- **agents/security-reviewer + vault-rotator 삭제**: agents 51 → 49
- **.claude/settings.json 보안 deny 38건 모두 제거** + `disableBypassPermissionsMode` 제거 + `defaultMode: bypassPermissions` + sandbox `allowUnsandboxedCommands: true`
- **PreToolUse pre_edit_guard hook 삭제**
- **rule 00 보호 경로 절** "참고용 (정책 강제 해제됨)"으로 갱신
- **ADR 작성**: `ADR-2026-04-28-security-policy-removal.md` (rule 70 R8 적용 두 번째 사례 — 3 trigger 모두 해당)
- **검증**: verify_harness_consistency PASS (28/43/49/9), verify_vendor_boundary PASS

cycle-010 변경 (이전 세션): 2026-04-28 cycle-010 (사용자 "권장하는 작업 모두 수행 + 후속 작업 마무리" 명시 승인)에서 cycle-009의 NEXT_ACTIONS 사용자 결정 대기 매트릭스 3건 (T3-04/05/06) 일괄 처리 + 신규 governance rule 1건 (R8 신설):

cycle-010 변경 (이번 세션):

- **T3-04 (04-A 채택)** — 27개 adapter (redfish 16 + os 7 + esxi 4) 의 `version: "1.0.0"` placeholder 1줄 일괄 삭제. `adapter_loader.py` / `module_utils/adapter_common.py` 참조 0건 검증. `tested_against` (rule 96 R1)이 펌웨어 검증 추적 충실
- **T3-05 (05-A 유지)** — redfish_gather.py BMC IP 수집 break-on-first-IP 패턴 (평균 1~2회 호출)이 실 N+1 아니므로 현재 유지. cycle-008 `_resolve_first_member_uri` helper로 가독성 개선됨. NEXT_ACTIONS T3-05 close
- **T3-06 (06-B 채택)** — `rule 70` R8 신설 (ADR 의무 trigger 3종): rule 본문 의미 변경 / 표면 카운트 변경 / 보호 경로 정책 변경. `ADR-2026-04-28-rule12-oem-namespace-exception.md` 소급 작성 (DRIFT-006 governance trace 보강 — R8 적용 첫 사례)
- **검증**: `verify_harness_consistency.py` PASS (29/43/51/10), `verify_vendor_boundary.py` PASS (0건), 27 adapter YAML 파싱 PASS + version 키 0/27, PROJECT_MAP fingerprint 갱신 (adapters)

cycle-009 변경 (이전 세션):

- **3-channel `site.yml` fallback envelope 13 필드 일관성**:
  - **HIGH 버그 fix #1**: `os-gather/site.yml` PLAY 3 (Windows) `always` fallback이 2 필드 (`status` / `errors`) 만 → 13 필드 envelope 보강 (rule 13 R5 / rule 20 R1 정합)
  - **HIGH 버그 fix #2**: `esxi-gather/site.yml` `always` fallback의 `_ip` 변수명 오류 → `_e_ip` 정정 (fallback 시 ip null 출력되던 문제 해결)
  - **MED fix**: `collection_method` 값 build_meta와 일관성 (OS: `ansible`→`agent`, ESXi: `vmware`→`vsphere_api`, Redfish: `redfish`→`redfish_api`)
- **T2-A7 — rule 7개 5요소 보강**: `rule 24` (completion-gate), `rule 26` (multi-session-guide), `rule 41` (mermaid-visualization), `rule 50` (vendor-adapter-policy), `rule 60` (security-and-secrets), `rule 70` (docs-and-evidence-policy), `rule 90` (commit-convention) 본문 R-번호 + Default/Allowed/Forbidden/Why/재검토 5요소 구조 적용 (rule 00 표기 구조 컨벤션 정합)

cycle-008 변경 (이전 세션):

- **redfish_gather.py — 함수 분리 추가**: `gather_system` 103→57줄 (vendor OEM helper 4종 `_extract_oem_{hpe,dell,lenovo,supermicro}` 추출 + `_OEM_EXTRACTORS` dispatch dict), `detect_vendor` 64→37줄 (`_fetch_service_root` + `_resolve_first_member_uri` 추출), `main` 67→45줄 (`_make_section_runner` + `_collect_all_sections` + `_compute_final_status` 추출). rule 10 R3 정합
- **os-gather/tasks/linux/gather_system.yml**: 346→322줄. `build_identifier_diagnostics.yml` 별도 task로 분리 (rule 10 R3)
- **adapters/redfish/**: HPE iLO5 priority 100→90 차등 (T3-02), `lenovo_bmc.yml` generic fallback 신규 (T3-03 일관성), `cisco_bmc.yml` generic fallback 신규 (일관성), `lenovo_imm2.yml` tested_against 펌웨어 명시 (rule 96 R1), `cisco_cimc.yml` 세대 차등 검토 결정 명시 (M5/M6 미검증으로 보류)
- **callback_plugins/json_only.py `_emit()`**: silent `pass` → `JSON_ONLY_DEBUG=1` 환경변수로 stderr 경고 활성화 (호출자 호환성 유지하면서 디버그 가시성)
- **lookup_plugins/adapter_loader.py**: score 동률 정렬 문서화 (Python list.sort stable + 파일명 알파벳 tie-break) + 동률 발견 시 vvv 경고
- **redfish_gather.py docstring**: Cisco 추가 (LOW), `int(vcap_int / 1048576)` → `vcap_int // 1048576` 정수 나눗셈 통일 (LOW), `bmc_names`에 `'cisco': 'CIMC'` 추가, gather_system Cisco silent OEM 의도 주석 추가

cycle-007 (이전):

- **cycle-007 #2**: rule 22 R7 ↔ 코드 drift 정합 — 5 공통 fragment 변수 명명 (`_data_fragment` + `_sections_{supported,collected,failed}_fragment` + `_errors_fragment`) 정정. rule + CLAUDE.md + ai-context + agent + skill 8 파일 동시 갱신
- **cycle-007 #1**: `redfish_gather.py` `gather_storage()` 190줄 → 5 함수 분리 (`_gather_simple_storage`, `_gather_standard_storage`, `_extract_storage_controller_info`, `_extract_storage_drives`, `_extract_storage_volumes`). rule 10 R3 정합
- **cycle-007 #3**: `precheck_bundle.py` `run_module()` 181줄 → 5 함수 분리 + `lookup_plugins/adapter_loader.py` `LookupModule.run()` 115줄 → 5 함수 분리
- **cycle-007 #4**: `precheck_bundle.py` `requests` 선택적 의존 제거 → urllib stdlib 단일 경로 통일 + 에러 분류 강화 (HTTPError / socket.timeout / URLError / SSLError)

- **cycle-007 #2**: rule 22 R7 ↔ 코드 drift 정합 — 5 공통 fragment 변수 명명 (`_data_fragment` + `_sections_{supported,collected,failed}_fragment` + `_errors_fragment`) 정정. rule + CLAUDE.md + ai-context + agent + skill 8 파일 동시 갱신
- **cycle-007 #1**: `redfish_gather.py` `gather_storage()` 190줄 → 5 함수 분리 (`_gather_simple_storage`, `_gather_standard_storage`, `_extract_storage_controller_info`, `_extract_storage_drives`, `_extract_storage_volumes`). rule 10 R3 정합
- **cycle-007 #3**: `precheck_bundle.py` `run_module()` 181줄 → 5 함수 분리 + `lookup_plugins/adapter_loader.py` `LookupModule.run()` 115줄 → 5 함수 분리
- **cycle-007 #4**: `precheck_bundle.py` `requests` 선택적 의존 제거 → urllib stdlib 단일 경로 통일 + 에러 분류 강화 (HTTPError / socket.timeout / URLError / SSLError)

cycle-006 (이전):

- **T2-B2 적용**: `verify_harness_consistency.py` FORBIDDEN_WORDS 검사 default 활성화 (rule 00 약속 충족 — `--no-forbidden-check`로 비활성)
- **T2-C2 적용**: `precheck_bundle.py` Stage 1 (reachable) ↔ Stage 2 (port_open) 분리 + ConnectionRefusedError 시 host alive 판정 (rule 27 R2 정합)
- **T2-C8 적용**: `os-gather/files/get_last_login.sh` 공유 snippet 추가 + Python/Raw 양 경로에서 lookup file 통합 (gather_users.yml 294 → 239 lines, rule 10 R3 정합)
cycle-006 (이전):

- **DRIFT-004 resolved**: `users[]` 섹션 6 필드 등록 (Must +3 / Nice +2 / Skip +1) → 분포 46 entries, output_schema_drift 정합
- **DRIFT-005 resolved**: `_BUILTIN_VENDOR_MAP` → `_FALLBACK_VENDOR_MAP` 이름 변경 + 3-tier path resolution + nosec silence
- **DRIFT-006 resolved**: rule 12 R1에 Allowed (cycle-006 추가) 절 — Redfish API spec OEM namespace는 외부 계약 직접 의존이라 의도된 예외. 17 라인 nosec silence
- **W2 (b) resolved**: os-gather Jinja2 OEM list silence + 동기화 책임 명시
- **vendor_boundary 0건 달성**: cycle-005 26 → cycle-006 0

cycle-005 (이전):
- 도구 정밀화 (scan #2 재설계 + scan #4 specificity + vendor_boundary docstring) + DRIFT-007 catalog 정합 + alias 동기화 게이트

- **DRIFT-007 catalog 정합**: validate_field_dictionary.py 기준 실측 분포 "Must 28 / Nice 7 / Skip 5 = 40 entries"로 5 위치 일괄 정정 (cycle-002 정정값 자체가 잘못된 grep 카운트였음 — 헤더 주석 noise)
- **scan #2 재설계**: set_fact 다음 indent 블록 lookahead로 누적 변수 직접 수정만 검출 → 107 → 0건
- **scan #4 specificity 분석**: 같은 priority여도 distribution_patterns / version_patterns / firmware_patterns로 분리되면 silence → 7 → 0건
- **verify_vendor_boundary docstring 인식**: Python triple-quote 페어링으로 docstring 라인 skip → 33 → 26건
- **verify_harness_consistency 동기화 게이트**: `_BUILTIN_VENDOR_MAP` ↔ vendor_aliases.yml drift advisory (DRIFT-005 옵션 (2) 사전 적용)
- **scan_suspicious_patterns.py: 11 패턴 모두 0건** (server-exporter 코드 rule 95 R1 100% 정합)

## 완료된 Plan / Cycle

| Plan / Cycle | 내용 | commit |
|---|---|---|
| Plan 1 (Foundation) | settings.json + 19 hooks + supporting scripts + policy + role + ai-context + templates + commands + 29 rules + CLAUDE.md Tier 0 | d87af96, 31526c3, ee82f1b, 031b32e |
| Plan 2 (Skills + Agents) | 43 skills + 51 agents | 183a79e, 2b3268f |
| Plan 3 (docs/ai 골격) | catalogs / decisions / policy / workflows / harness / handoff / impact / references | cc3067d, 50343f3 |
| cycle-001 (dry-run) | 자기개선 루프 dry-run | (cc3067d 일부) |
| cycle-002 (실측 + DRIFT 발견) | 실측 catalog 갱신 + 3 DRIFT 발견 + verify 강화 | 4b5ec30 |
| cycle-003 (DRIFT 정리 + 도구) | DRIFT-001/002/003 resolved + scan_suspicious_patterns.py 신규 + 13 adapter origin 발견 | 69abb8a |
| cycle-004 (전수조사) | 도구 3종 정밀화 + 13 adapter origin 일괄 + _safe_int + 변수 silence + DRIFT-004/005/006 등재 | fef5789..6142eea |
| cycle-005 (AI 자체 가능 일괄) | DRIFT-007 catalog 정합 + scan #2/#4 재설계 + vendor_boundary docstring + alias 동기화 게이트 → scan 11 패턴 0건 | 72b2613..2b4900d |
| cycle-006 (DRIFT 4종 일괄) | DRIFT-004 (users 등록) + DRIFT-005 (alias 통합) + DRIFT-006 (rule 12 예외 절) + W2 (b) silence → vendor_boundary 0건 | 86c91bc |
| full-sweep 2026-04-28 (Tier 1+2) | docs/rule/잔재어휘 정합 + code/schema 결함 + adapter origin/policy/settings | 1eb6abe / dd88aac / c1d6f9b |
| full-sweep 잔여 (T2-B2/C2/C8) | forbidden default 활성화 + precheck Stage 분리 + gather_users 함수 통합 | ad87006 |
| cycle-007 (4축 검수 + HIGH 4 일괄) | rule 22 R7 drift 정합 + redfish_gather.py 5 함수 분리 + precheck/adapter_loader 함수 분리 + requests 의존 제거 | 6a473bd |
| cycle-008 (P2 MED/LOW 일괄) | redfish_gather 추가 함수 분리 (gather_system/detect_vendor/main) + linux gather_system identifier_diagnostics 분리 + HPE priority 차등 + Lenovo/Cisco bmc fallback + json_only debug + adapter_loader 동률 문서화 | 756e1e77 |
| **cycle-009 (fallback envelope + rule 5요소)** | **3-channel fallback envelope 13 필드 일관성 (HIGH fix 2건 + MED fix 1건) + T2-A7 rule 7개 5요소 보강 (24/26/41/50/60/70/90)** | (이번 세션) |

## 검증 결과 (cycle-009 후)

```
[정적]
verify_harness_consistency.py        : PASS (rules 29 / skills 43 / agents 51 / policies 10)
validate_claude_structure.py         : OK
check_project_map_drift.py           : PASS (site.yml 3 fingerprint 갱신)
scan_suspicious_patterns.py          : clean (11 패턴 0건)
verify_vendor_boundary.py            : PASS — 0건
output_schema_drift_check.py         : 정합 (sections=10, fd_paths=46, fd_section_prefixes=10)
ansible-playbook --syntax-check       : PASS — 3 채널 (WSL)
pytest tests/                         : PASS — 95/95
```

도메인 코드:
- cycle-006 도메인 코드 변경: redfish_gather.py (이름 변경 + path resolution + nosec silence) + Jinja2 silence + field_dictionary +6 entries
- pytest 95 PASS — 영향 vendor 회귀 0건
- **모든 harness 도구 0건 — 100% 정합 달성**

## 카탈로그 (실측, 2026-04-27 cycle-004 후)

| 카테고리 | 카운트 | 변화 |
|---|---|---|
| rules | 29 | 변화 없음 |
| skills | 43 | 변화 없음 |
| agents | 51 | 변화 없음 |
| policies | 10 | 변화 없음 |
| roles | 6 | 변화 없음 |
| ai-context | 12 | 변화 없음 |
| templates | 8 | 변화 없음 |
| commands | 5 | 변화 없음 |
| hooks (Python) | 19 + supporting 8 | 변화 없음 |
| references (외부 docs) | 14 | 변화 없음 |
| **adapters** | **27** (cycle-008 lenovo_bmc + cisco_bmc 신규 추가, 모두 origin 주석 보유) | 100% rule 96 R1 정합 |
| **DRIFT 등재** | **6** (resolved 3 + open 3) | DRIFT-004/005/006 신규 |

## 채널별 / Vendor 상태

| 채널 | 상태 | adapter | origin 주석 |
|---|---|---|---|
| os-gather | ok | 7 | 100% (cycle-004) |
| esxi-gather | ok | 4 | 100% (cycle-004) |
| redfish-gather | ok | 14 | 100% (cycle-003 12 + cycle-004 1 redfish_generic + 1 registry) |

| Vendor | adapter | baseline | origin |
|---|---|---|---|
| Dell | 3 (idrac8/9/generic) | 있음 | 기존 + 검증 |
| HPE | 4 (ilo4/5/6/generic, iLO5/6 priority 차등 cycle-008) | 있음 | 기존 + 검증 |
| Lenovo | 3 (xcc/imm2/bmc — bmc fallback cycle-008 추가) | 있음 | 기존 + 검증 |
| Supermicro | 3 (x11/x9/bmc) | 일부 | 기존 + 검증 |
| Cisco | 2 (cimc/bmc — bmc fallback cycle-008 추가, 세대 차등은 M5/M6 미검증으로 보류) | 일부 | 기존 + 검증 |

## DRIFT 현황

| ID | 분류 | 상태 |
|---|---|---|
| DRIFT-001 | catalog-stale (Field Dictionary 28→29 Must, cycle-003 정정 자체 stale) | resolved (cycle-003), DRIFT-007에서 재정정 |
| DRIFT-002 | catalog-stale (Stage 4 일반화) | resolved (cycle-003) |
| DRIFT-003 | catalog-stale (vendor-bmc-guides adapter 이름) | resolved (cycle-003) |
| DRIFT-004 | convention-violation (`users` 섹션 field_dictionary 미등록) | **resolved (cycle-006)** — users[] 6 항목 등록 |
| DRIFT-005 | convention-violation (`_BUILTIN_VENDOR_MAP` 중복) | **resolved (cycle-006)** — _FALLBACK_VENDOR_MAP + path resolution + nosec |
| DRIFT-006 | convention-violation (redfish_gather.py vendor 분기 17건) | **resolved (cycle-006)** — rule 12 R1 Allowed 절 + 17 라인 nosec |
| DRIFT-007 | catalog-stale (Must 28/Nice 7/Skip 5 실측 — cycle-002 grep 헤더 noise 오인) | resolved (cycle-005) |

**모든 등재 DRIFT resolved.** cycle-007 진입 시 새 DRIFT 발견은 그 시점 catalog 추가.

## Round 11 reference 종합 수집 (2026-04-28)

> 사용자 제공 27대 실장비에 대한 종합 raw 정보 수집. 향후 schema 추가 / 매핑 검증 / vendor 온보딩 / 회귀 비교 reference.

- **신규 디렉터리**: `tests/reference/{redfish,os,esxi,agent,scripts,local}/`
- **수집 도구 4개**:
  - `crawl_redfish_full.py` — Redfish ServiceRoot부터 모든 link 재귀
  - `gather_os_full.py` — paramiko SSH (Linux) + pywinrm (Windows) + ansible setup
  - `gather_esxi_full.py` — paramiko + pyvmomi + esxcli
  - `gather_agent_env.py` — paramiko, REQUIREMENTS 검증용
- **자격**: `tests/reference/local/targets.yaml` (gitignored)
- **수집 결과 (완료, 2026-04-28 17:15)**:
  - Redfish 11대 시도 → 9 OK (Dell 5 + HPE + Lenovo + Cisco 15.2) / 1 SKIP (Dell 32 vendor 의심) / 2 환경 이슈 (Cisco 15.1 BMC 다운 + 15.3 도달 불가)
  - OS 7대 시도 → 6 OK (Linux distro 5 + bare-metal) / 1 환경 이슈 (Win10 WinRM)
  - ESXi 3대 → pyvmomi 3 OK, SSH 1만 (.1/.3 SSH 비활성)
  - Agent/Master 4대 → 모두 OK (각 39 명령)
- **최종 통계**: **15964 파일 / 126MB** (redfish 108MB / os 5.8MB / esxi 11MB / agent 399K)
- **사고 7건** (F1~F7): F1 자격 정정 (RESOLVED) / F2 vendor 의심 / F3 BMC 환경 / F4 WinRM 환경 / F5 SSH 비활성 / F6 sudo 대기 (RESOLVED) / F7 SKIP/옵션 추가 (RESOLVED)
- **회귀 영향**: 없음 (별도 디렉터리, fixtures/baseline 무수정, harness consistency PASS, vendor boundary PASS)
- **Evidence**: `tests/evidence/2026-04-28-reference-collection.md`
- **decision-log**: `docs/19_decision-log.md` §13 Round 11
- **follow-up**: F2 (사용자 확인) / F3 (장비 가동) / F4 task #10 (Win10 WinRM) / F5 (ESXi SSH 활성화) / F6 (sudo 처리 개선)

## 다음 작업 (cycle-007 후보)

> `docs/ai/NEXT_ACTIONS.md` 참조. 2026-04-28 full-sweep 보고서: `docs/ai/harness/full-sweep-2026-04-28.md`

### 사용자 결정 / 외부 의존
- T2-D2: `schema/baseline_v1/cisco_baseline.json` `data.users: null` → `[]` (rule 13 R4 — 실측 evidence 필요)
- T2-A7: rule 24 / 26 / 41 / 50 / 60 / 70 / 90 본문 R-번호 + Default/Allowed/Forbidden/Why 5요소 보강 (큰 재구조화)
- T3-01~T3-06 (full-sweep Tier 3): precheck `requests` 의존 / iLO5/6 priority / Lenovo generic / adapter 버전 / BMC IP 최적화 / ADR 필수 정책
- 새 vendor 추가 (PO 결정)
- Round 11 검증 (실장비)

### AI 자체 가능 (cycle-007)
- scan_suspicious_patterns.py #2 재설계 (set_fact 다음 라인 분석)
- scan_suspicious_patterns.py #4 specificity 분석 (priority 동률 + match.distribution_patterns 결합)
- verify_vendor_boundary.py Python `"""` docstring 인식 추가
- verify_harness_consistency.py에 `_VENDOR_ALIASES` ↔ `vendor_aliases.yml` 동기화 게이트
- verify_harness_consistency.py FORBIDDEN_WORDS default 모드 검사 활성화 (T2-B2)

## 정본 reference

- `CLAUDE.md` (Tier 0 정본, 보강됨)
- `GUIDE_FOR_AI.md`, `REQUIREMENTS.md`, `README.md`
- `docs/01_jenkins-setup` ~ `docs/19_decision-log`
- 직전 cycle: `docs/ai/harness/cycle-004.md`
- vendor 경계 분석: `docs/ai/impact/2026-04-27-vendor-boundary-57.md`
- DRIFT 카탈로그: `docs/ai/catalogs/CONVENTION_DRIFT.md`
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
