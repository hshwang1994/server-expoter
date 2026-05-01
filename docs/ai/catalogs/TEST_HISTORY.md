# TEST_HISTORY — server-exporter

> 테스트 실행 / Round 검증 / Baseline 갱신 이력 (append-only, rule 70).

## 2026-05-01 (cycle-019 phase 2 — F44~F47 신규 vendor 4종)

- 환경: 로컬 (Python 3.11.9 / pytest 9.0.2)
- 테스트 신규 7건: `tests/unit/test_new_vendors_f44_f47.py`
  - `test_f44_f47_vendor_aliases_yaml_has_4_new_entries` — vendor_aliases.yml 4 entry
  - `test_f44_f47_fallback_vendor_map_sync` — _FALLBACK_VENDOR_MAP sync 게이트
  - `test_f44_f47_bmc_product_hints_added` — _BMC_PRODUCT_HINTS 7 신 시그니처
  - `test_f44_f47_adapter_yaml_files_exist` — 4 adapter 파일 존재
  - `test_f44_f47_adapter_yaml_required_keys` — 4 필수 키 + priority=80
  - `test_f44_f47_adapter_match_includes_canonical_vendor` — match.vendor canonical
  - `test_f44_f47_ai_context_files_exist` — 4 ai-context 파일 + vault SKIP 명시
- pytest 결과: **108/108 PASS** (cycle-019 phase 1 101 → 108, +7)
- 정적 검증:
  - verify_harness_consistency PASS (vendor sync 게이트 통과)
  - verify_vendor_boundary PASS (nosec 주석 적절)
  - check_project_map_drift PASS (fingerprint 재갱신)
  - py_compile redfish_gather.py PASS
  - YAML 6 파일 syntax PASS
- baseline 회귀: skip (lab 부재 — 신규 vendor 4종 모두 lab/사이트 부재)

## 2026-05-01 (cycle-019 phase 1 — 7-loop + 10R extended audit P1 22건)

- 환경: 로컬 (Python 3.11.9 / pytest 9.0.2)
- 테스트 신규 7건: `tests/unit/test_redfish_tls_and_network_fallback.py`
  - F84: `test_f84_tls_context_min_version_1_2` / `test_f84_tls_context_max_version_1_3` / `test_f84_tls_context_unverified_self_signed` / `test_f84_tls_context_legacy_renegotiation_flag`
  - F48: `test_f48_network_adapters_uses_ports_when_no_networkports` / `test_f48_network_adapters_prefers_networkports_when_present` / `test_f48_network_adapters_skip_empty_placeholder`
- pytest 결과: **101/101 PASS** (cycle-018 94 → 101, +7)
- 정적 검증:
  - verify_harness_consistency PASS
  - verify_vendor_boundary PASS
  - check_project_map_drift PASS (fingerprint 갱신 — adapter 27 → 34)
  - py_compile redfish_gather.py PASS
  - YAML 9 파일 syntax PASS
  - adapter 4 필수 키 (match/capabilities/collect/normalize) 7 신규 모두 존재
- baseline 회귀: skip — 신 generation BMC adapter (F41/F47/F55/F61/F69) 는 lab 부재 영역. 기존 5 vendor lab fixture 영향 없음 (priority 역전 없음, 신 adapter 는 모두 priority ≥ 90 + model_patterns 차등).

## 형식

```
## YYYY-MM-DD (Round X / commit Y)

- 환경: <agent / vendor / 펌웨어>
- 명령: <pytest / ansible-playbook / redfish-probe ...>
- 결과: <PASS N / FAIL M>
- Baseline 갱신: <예/아니오 + 영향 vendor>
- Evidence: <tests/evidence/<날짜>-<주제>.md 링크>
```

---

## 2026-05-01 — P1 follow-up (F5/F13/F23 회귀 보강 + F23 적용)

- 환경: Windows 11 호스트 (Bash on Windows / pytest 9.0.2 / Python 3.11.9)
- 입력: 사용자 명시 "남아있는 작업 모두 수행해라"
- 적용:
  - **F5** `redfish_gather.py:_gather_power_subsystem` — 이미 적용된 EnvironmentMetrics fallback에 회귀 5건 신규 (`tests/unit/test_power_environment_metrics_f5.py`)
  - **F13** `redfish_gather.py:account_service_provision` — 이미 적용된 Cisco / 404 graceful 분류에 회귀 4건 신규 (`tests/unit/test_account_service_unsupported_f13.py`)
  - **F23** `os-gather/tasks/{linux,windows}/gather_users.yml` — `_sections_unsupported_fragment` wiring (Linux Python+Raw / Windows rc-aware) + 회귀 9건 신규 (`tests/unit/test_os_users_unsupported_f23.py`)
- 명령:
  - `python -m pytest tests/unit/ -q` → **94/94 PASS** (2.21s, 76 기존 + 18 신규)
  - `python -m py_compile redfish-gather/library/redfish_gather.py` → PASS
  - `python -c "import yaml; yaml.safe_load(...)"` (Linux/Windows gather_users + cisco_cimc.yml) → PASS
  - `python scripts/ai/verify_harness_consistency.py` → PASS (rules:28 skills:48 agents:59 policies:10)
  - `python scripts/ai/verify_vendor_boundary.py` → PASS
  - `python scripts/ai/check_project_map_drift.py --update` → 재baseline (os-gather + tests hash)
- Baseline 갱신: 없음 (코드 fragment 분류 변경 only — envelope 13 필드 동일)
- Evidence: 본 cycle은 코드 회귀 unit 위주. 사이트 검증 (Alpine/distroless 환경 빌드)은 외부 의존 — 후속.

### Additive 원칙 (rule 96 R1-B)
- envelope 13 필드 변경 0건
- schema/sections.yml 변경 0건
- `_sections_failed_fragment` → `_sections_unsupported_fragment` 라우팅만 (errors[] noise 차단)

---

## 2026-05-01 — 호환성 ticket 일괄 (F01~F43 22건)

- 환경: Windows 11 호스트 (Bash on Windows / pytest 9.0.2 / Python 3.11.9)
- 입력: 사용자 명시 "호환성 티켓 모두 수행하세요"
- 적용 (코드 변경 5건):
  - F05 `redfish_gather.py` — `_gather_power_subsystem` EnvironmentMetrics fallback (DMTF 2020.4)
  - F02 `normalize_standard.yml` — ProcessorType 필터 'CORE' enum 통과
  - F13/F08 `redfish_gather.py` — `account_service_provision` 404-only graceful 'not_supported' 분류
  - F20 `try_one_account.yml` — backoff sleep 1→5 (BMC lockout 회피)
  - F21 `ansible.cfg` — RHEL 9+ paramiko ssh-rsa legacy 호환
- 보류/검증만 (17건):
  - 이미 호환: F01, F09, F10, F12, F17, F22, F24, F34, F35, F40
  - lab 한계: F04, F11, F14, F15, F38
  - 추적: F33, F41, F42, F43, F16
  - graceful: F23, F07, F37, F39
- 명령:
  - `python -m py_compile redfish-gather/library/redfish_gather.py` → PASS
  - `python -c "import yaml; yaml.safe_load(...)"` (normalize_standard, try_one_account) → PASS
  - `python -m pytest tests/ -x` → **234/234 PASS** (29.41s)
  - `python scripts/ai/verify_harness_consistency.py` → PASS (rules:28 skills:48 agents:59 policies:10)
  - `python scripts/ai/verify_vendor_boundary.py` → PASS
  - `python scripts/ai/hooks/output_schema_drift_check.py` → PASS
  - `python scripts/ai/check_project_map_drift.py --update` → PASS
- 원칙: 호환성 cycle (rule 96 R1-B) — envelope 13 필드 변경 0건, Additive only
- Baseline 갱신: 없음 (호환성 fallback path 추가, 기존 200 응답 영향 없음)
- 후속: lab 한계 fix (F04/F11/F14/F15/F38) 사이트 fixture 확보 시 별도 cycle

---

## 2026-04-29 — Dell Redfish 비판적 검증 + envelope 값 미채움 7건 fix

- 환경: Windows 11 호스트 (Bash on Windows / pytest 9.0.2 / Python 3.11.9)
- 입력: 사용자 명시 "Dell Redfish 수집 안되는게 많고 값도 이상함. 키 늘리지 말고 버그 모두 fix"
- 분석: Round 11 reference (`tests/reference/redfish/dell/10_100_15_27`, R760, iDRAC 7.10.70.00) ↔ 코드 정적 비교
- 발견: 26건 (CRIT 2 / HIGH 11 / MED 5 / LOW 2 / 의도 6) → envelope 키 미채움/명확 버그 7건만 fix
- 변경 파일:
  - `redfish-gather/library/redfish_gather.py` (BUG-1, BUG-13, BUG-15, BUG-16, BUG-19 — 5건)
  - `redfish-gather/tasks/normalize_standard.yml` (BUG-12, BUG-13 fallback, BUG-14 fallback — 3건)
- 명령:
  - `python -m py_compile redfish-gather/library/redfish_gather.py` → PASS
  - `python -c "import yaml; yaml.safe_load(open('redfish-gather/tasks/normalize_standard.yml'))"` → PASS
  - `python -m pytest tests/ --tb=short` → **158 passed in 17.20s**
  - `python scripts/ai/verify_harness_consistency.py` → PASS (rules 28 / skills 43 / agents 49 / policies 9)
  - `python scripts/ai/verify_vendor_boundary.py` → PASS
- Baseline 갱신: **아니오** (rule 13 R4 — 실 BMC 재수집 후 Round 12 에서 갱신 예정. 영향 vendor: Dell 단독 — `hardware.bios_date` / `oem.estimated_exhaust_temp` 두 필드)
- Evidence: `tests/evidence/2026-04-29-dell-redfish-critical-review.md` (예정)
- 미수행 (envelope 키 추가 필요): BUG-2 controller metadata, BUG-3~10 PSU/Firmware/Drive/Volume/Memory/NIC 풍부 raw, BUG-11 BIOS Attributes 571
- 회귀 영향:
  - HPE/Lenovo/Supermicro/Cisco volumes — `boot_volume` 표준 우선화로 표준 BootVolume 응답 vendor 에서 명시 false/true 정확 반영 (이전 항상 None)
  - Dell volumes — boot_volume 동일 (표준 BootVolume None → Dell Oem fallback)
  - Dell hardware.bios_date — null → "MM/DD/YYYY" (실 환경 검증 시)
  - 모든 vendor cpu.logical_threads — per-processor TotalThreads 누락 펌웨어에서 fallback 활성

---

## 2026-04-29 — production-audit (4 agent 전수조사 + HIGH 30+건 일괄 fix)

- 환경: Windows 11 호스트 (Bash on Windows / pytest 9.0.2 / Python 3.11.9)
- 명령: `python -m pytest tests/ --tb=short`
- 결과: **148 passed in 17.53s** (이전 147 + remote_identifier_test guard 1)
- 추가 검증:
  - `verify_harness_consistency.py` PASS — rules 28 / skills 43 / agents 49 / policies 9
  - `verify_vendor_boundary.py` PASS — common/3-channel vendor 하드코딩 0건 (rule 12 R1)
  - `tests/validate_field_dictionary.py` PASS — 65 entries (Must 39 / Nice 20 / Skip 6)
  - `check_project_map_drift.py` — 4 drift 해소 후 PASS
- 변경 영역 (Phase 2):
  - common/tasks/normalize/ (skeleton 동기화)
  - 3 채널 site.yml (always block diagnosis dict)
  - schema/field_dictionary.yml (envelope top-level 8 entries)
  - esxi-gather/{site.yml,tasks/normalize_network.yml} (vendor normalize / DNS / netmask)
  - schema/baseline_v1/{cisco,windows}_baseline.json
  - os-gather/tasks/linux/{gather_cpu,gather_memory,gather_storage,gather_network}.yml
  - os-gather/tasks/windows/{gather_storage,gather_network,gather_runtime}.yml
  - redfish-gather/{library,tasks}/* (account_service / cross-channel typing / vendor merge)
  - common/library/precheck_bundle.py (IPv6 듀얼스택)
  - filter_plugins/diagnosis_mapper.py (None 가드)
  - Jenkinsfile + Jenkinsfile_portal (timeout / artifact / hard gate)
  - tests/scripts/* + scripts/ai/*.py (자격증명 환경변수화)
- Baseline 갱신: cisco_baseline.json (users null→[]) / windows_baseline.json (media_type 정규화)
- Evidence: 본 CURRENT_STATE.md + NEXT_ACTIONS.md 갱신

---

## 2026-04-29 — cycle-016 (사용자 11 항목 일괄 점검 + 실 Jenkins 빌드 5회 + summary grouping 완성)

- 환경: Windows 11 호스트 (PowerShell + Bash) + Jenkins master 10.100.64.152 (cloviradmin) + agent jenkins-agent
- Job: `hshwang-gather` (`https://github.com/hshwang1994/server-expoter` main pull)
- 명령: PowerShell `Invoke-WebRequest` + crumb + Basic Auth → `buildWithParameters` POST + console log fetch
- 결과:
  - **Build #39** target=redfish 10.100.15.27 → pipeline=SUCCESS / gather=failed (lab vault 자격 미정합) — JSON envelope 13 필드 + 한국어 메시지 + Stage 4 145 pytest pass
  - **Build #41** target=os 10.100.64.165 (RHEL 9.6) → 회귀 발견 `Template delimiters: '#' at 86`
  - **Build #42** 부분 fix 후 재발 → 추가 inline 코멘트 9개 제거
  - **Build #43** OS 첫 정상 가동 → status=success / network.summary.groups + storage.summary.groups 동작 확인 / system.runtime 채워짐
  - **Build #44** namespace pattern fix 후 → storage.summary.grand_total_gb=100 (이전 0 → 정상)
  - **Build #45** Redfish 회귀 검증 (코드 변경 영향 없음)
- pytest: 147 PASS (실 Jenkins agent + 로컬 모두 일치)
- harness consistency / vendor boundary / schema drift: 모두 PASS
- Baseline 갱신: 7 vendor + 3 example (`scripts/ai/inject_summary_to_baselines.py` 일괄)
- Evidence: `docs/ai/harness/cycle-016.md`
- commit: `0da258d5`, `88793df8`, `a2e3e75e`, `e18230b8`, `240106bc` main push 완료

---

## 2026-04-29 — cycle-014 (4 vendor BMC 실 검증 + HIGH Jinja2 fix + vault sync 발견)

- 환경: Windows 11 호스트 (paramiko 4.0.0) + Jenkins agent 10.100.64.154 (cloviradmin / Ubuntu 6.8 / ansible-core 2.20.3 — REQUIREMENTS.md 정합)
- 사용자 명시 권한: AI 모든 권한 (하네스 + 실 장비). 벤더당 1대 BMC 검증.
- 검증 BMC (baseline_v1 정본 IP):
  - Dell 10.50.11.162 (PowerEdge R740 / iDRAC 9)
  - HPE 10.50.11.231 (ProLiant DL380 Gen11 / iLO 6)
  - Lenovo 10.50.11.232 (ThinkSystem SR650 V2 / XCC)
  - Cisco 10.100.15.2 (TA-UNODE-G1 / CIMC)
  - Supermicro: baseline 부재로 별도 cycle
- 1차 (cycle-013 main `b605c68b`): 4 vendor 모두 fatal — `_precheck_ok` Jinja2 syntax error.
- **HIGH 회귀 fix** (commit `bf247266`): `common/tasks/precheck/run_precheck.yml:47` Jinja2 expression 안 `{# ... #}` 주석을 YAML 주석으로 분리.
- 2차 (fix 후): 4 vendor 정상 envelope 13 필드. precheck OK / detect_vendor OK / adapter 자동 선택 OK / collect 401 → rescue → 13 필드 envelope.
- curl 자격 검증 (자격 transcript 노출 0): ServiceRoot 4 vendor HTTP 200 / vault primary+recovery 모두 HTTP 401 → vault ↔ BMC sync 안 됨 (OPS-3 우선순위 격상).
- redfish 공통계정 자동 생성 (P2 account_service): recovery 자격 fail로 진입 미발생 (의도된 동작) → cycle-015 이월.
- Evidence: `tests/evidence/cycle-014/README.md` + 4 log + `docs/ai/harness/cycle-014.md`
- Git: main `bf247266` push 완료.

---

## 2026-04-29 — cycle-013 (cycle-012 PR 머지 + 자율 매트릭스 + 정합 정정)

- 환경: Windows 11 + Python 3.11.9 (호스트)
- 변경 영역:
  - **AI-1** schema/examples — redfish_success.json + os_partial.json 11 path 보강
  - **AI-2** PROJECT_MAP — fingerprint 갱신 + 본문 stale 4건 정정
  - **AI-3** JENKINS_PIPELINES — vault binding 절 신규
  - **AI-4** SCHEMA_FIELDS — Must 31 / Nice 20 / Skip 6 = 57 정정 (1건 over count)
  - **AI-5** VENDOR_ADAPTERS — recovery_accounts 메타 절 신규
  - **AI-6** harness/cycle-012.md — 신규 (cycle-012 보고서 보존)
  - **AI-7** decisions/ADR-2026-04-29-vault-encrypt-adoption — advisory governance trace
  - **field_dictionary.yml** 헤더 주석 1줄 정정 (Nice 21 → 20)
- 명령 (실측):
  - `python -c "import json; ..."` schema/examples 2 파일 → PASS
  - `python tests/validate_field_dictionary.py` → **PASS** (10 checks, 8 passed, 0 failed, **0 warnings** ← 11 WARN 해소)
  - `python scripts/ai/verify_harness_consistency.py` → PASS (rules: 28, skills: 43, agents: 49, policies: 9)
  - `python scripts/ai/verify_vendor_boundary.py` → PASS (vendor 하드코딩 0건)
  - `python scripts/ai/check_project_map_drift.py` → PASS (drift 0건, fingerprint 갱신 후)
- 결과: 정적 검증 4/4 PASS. 도메인 코드 변경 없음 (catalog/문서만), 회귀 영향 없음.
- Baseline 갱신: 없음.
- Git: feature/3channel-expansion 3 commit (`0150fa2e` / `57745bd1` / `b1d8014c`) push 완료. main 머지는 OPS-8 (rule 93 R2 사용자 명시 승인) 대기.
- Evidence: `docs/ai/harness/cycle-012.md` (cycle-012 보존), `docs/ai/harness/cycle-013.md` (본 cycle 보고서), `docs/ai/decisions/ADR-2026-04-29-vault-encrypt-adoption.md`, `docs/ai/handoff/2026-04-29-cycle-013.md`, `docs/ai/archive/README.md`

### Phase 3 추가 작업 (본 응답 후반)

- stale inline 47건 일괄 trace 표기 (rule 60 / pre_commit_policy / vault-rotator / security-reviewer / protected-paths)
- archive 진입: harness/cycle-001~005 (5) + impact/ 6 보고서 → docs/ai/archive/
- SECURITY_POLICY.md deprecated 헤더
- cycle-013 보고서 + handoff + archive README 신규
- 검증 4종 재확인: 모두 PASS

---

## 2026-04-29 — cycle-012 (3-channel gather 대형 확장 P0~P5 + 후속 PR 갱신)

- 환경: Windows 11 + Python 3.11.9 (호스트)
- 변경 영역:
  - **P0 Foundation** — Jenkinsfile 3종 + tests/e2e/test_envelope_failure_modes.py + .gitignore + scripts/bootstrap_vault_encrypt.sh + docs/01_jenkins-setup.md
  - **P1 Auth Multi-Candidate** — vault accounts list (8 파일) + redfish load_vault/collect_standard/try_one_account + os/esxi try_credentials + adapters 16개 recovery_accounts 메타
  - **P2 + P4 (Redfish)** — redfish_gather.py AccountService 4 메서드 + dryrun ON default + gather_network_adapters_chassis + account_service.yml
  - **P3 + P4 normalize** — Redfish summary + Linux memory summary + normalize_standard.yml HBA/IB 매핑
  - **P4 OS/ESXi** — gather_hba_ib.yml (Linux raw) + windows/gather_storage.yml Get-InitiatorPort + esxi/collect_network_extended.yml
  - **P5** — Linux/Windows gather_runtime.yml
  - **schema** — sections.yml 신 sub-key 명시 + field_dictionary.yml 12 entries Nice 추가 (총 58)
- 명령 (실측):
  - `python -c "import ast; ast.parse(...)"` → redfish_gather.py + test_envelope_failure_modes.py PASS
  - `python -c "import yaml; ..."` 38 modified/new YAML safe_load → PASS
  - `python -m pytest tests/e2e/test_envelope_failure_modes.py -v` → 50/50 PASS
  - `python -m pytest tests/e2e/` → **195 PASS** (145 기존 + 50 신규)
  - `python scripts/ai/verify_vendor_boundary.py` → PASS (rule 12 R1 nosec 처리)
  - `python scripts/ai/verify_harness_consistency.py` → PASS (rules: 28, skills: 43, agents: 49, policies: 9)
  - `python tests/validate_field_dictionary.py` → PASS (Must 31 / Nice 21 / Skip 6 = 58)
  - `ansible-playbook --syntax-check` → SKIP (Windows 메인 환경 제약, WSL 보류)
- 결과: 정적 검증 7/8 PASS + 1 SKIP (환경 제약). 회귀 195/195 PASS.
- Baseline 갱신: 없음 (rule 13 R4 — 실측 기반만 허용. P3/P4 신 필드는 Nice 분류로 baseline 회귀 영향 없음)
- Commit: `f0f621ce` P0 / `fe0be36c` P1 / `0448d00d` P2+P4(Redfish) / `fbb0f357` P3+P4 normalize / `92b935c3` P5(Linux). 후속 commit (P4 OS/ESXi + P5 Windows + schema + docs) 진행 중.
- Branch: `feature/3channel-expansion` (origin push 완료, PR 사용자 직접 생성 — 옵션 A1)
- Plan: `C:\Users\hshwa\.claude\plans\1-snazzy-haven.md`
- Evidence: 본 항목

---

## 2026-04-28 — cycle-010 (T3-04/05/06 일괄 + rule 70 R8 신설)

- 환경: Windows 11 + Python 3.11.9 (호스트)
- 변경 영역:
  - 27 adapter YAML — `version: "1.0.0"` placeholder 1줄 일괄 삭제 (T3-04)
  - `.claude/rules/70-docs-and-evidence-policy.md` — R8 (ADR 의무 trigger) 신설 + 금지 패턴 + 리뷰 포인트
  - `docs/ai/decisions/ADR-2026-04-28-rule12-oem-namespace-exception.md` — DRIFT-006 소급 ADR (R8 첫 적용)
  - `.claude/policy/project-map-fingerprint.yaml` — adapters fingerprint 갱신
  - 증거 문서 — CURRENT_STATE / NEXT_ACTIONS / TEST_HISTORY / harness/cycle-010.md
- 명령:
  - `grep -c "^version:" adapters/**/*.yml` → 27/27 = 0건
  - `python yaml.safe_load 27 adapter` → PASS, version 키 부재
  - `python scripts/ai/verify_harness_consistency.py` → PASS (rules: 29, skills: 43, agents: 51, policies: 10)
  - `python scripts/ai/verify_vendor_boundary.py` → PASS (vendor 하드코딩 0건)
  - `python scripts/ai/check_project_map_drift.py --update` → adapters fingerprint 갱신
  - `ansible-playbook --syntax-check` → SKIP (Windows 메인 환경 제약)
- 결과: 정적 검증 4/5 PASS + 1 SKIP (환경 제약)
- Baseline 갱신: 없음 (T3-04는 schema 영향 없음)
- Evidence: `docs/ai/harness/cycle-010.md`

---

## 2026-04-28 — cycle-008 (P2 MED/LOW 11건 일괄 정합)

- 환경: Windows 11 + Python 3.11.9 (호스트)
- 변경 영역:
  - redfish-gather/library/redfish_gather.py — 함수 분리 추가 (gather_system 103→57, detect_vendor 64→37, main 67→45 + OEM helper 4종 + section runner 3종)
  - os-gather/tasks/linux/gather_system.yml — 346→322줄, build_identifier_diagnostics.yml 분리
  - adapters/redfish/ — hpe_ilo5 priority 100→90, lenovo_bmc.yml 신규, cisco_bmc.yml 신규, lenovo_imm2 tested_against, cisco_cimc 세대 보류 명시
  - callback_plugins/json_only.py — `_emit()` JSON_ONLY_DEBUG 환경변수 가드
  - lookup_plugins/adapter_loader.py — 동률 정렬 문서화 + vvv 경고
- 명령:
  - `python -m pytest tests/ -q` → 95 PASS / 0 FAIL
  - `python scripts/ai/verify_vendor_boundary.py` → 통과 (0건, _OEM_EXTRACTORS dict의 4 라인에 nosec rule12-r1 추가)
  - `python scripts/ai/verify_harness_consistency.py` → PASS (rules 29 / skills 43 / agents 51 / policies 10)
  - `python scripts/ai/hooks/output_schema_drift_check.py` → 정합 (sections=10 fd_paths=46 fd_section_prefixes=10)
  - `python scripts/ai/check_project_map_drift.py --update` → fingerprint 갱신
  - `python -c "import ast; ast.parse(open('redfish-gather/library/redfish_gather.py').read())"` → OK
  - `python -c "import yaml; yaml.safe_load(open(... gather_system.yml ...))"` → OK
- 결과: 모든 검증 PASS
- Baseline 갱신: 없음 (회귀 영역 변경, 의미 변경 없음 — 회귀 95 PASS로 확인)
- Evidence: 본 commit (cycle-008) + CURRENT_STATE.md + NEXT_ACTIONS.md 갱신
- 회귀: 없음 (95 PASS 동일)

---

## 2026-04-27 — 하네스 도입 후 정적 검증

- 환경: Windows 11 + Python 3.11.9 (검증 기준 Agent 10.100.64.154 — Ansible 2.20.3 / Python 3.12.3)
- 명령:
  - `python -c "import ast; ast.parse(...)"` 모든 .py 파일 (27 + 51 = 78 Python 파일)
  - `python scripts/ai/verify_harness_consistency.py`
  - `python scripts/ai/hooks/commit_msg_check.py --self-test`
  - `python scripts/ai/hooks/session_start.py`
- 결과:
  - ast.parse: PASS (0 syntax error)
  - verify_harness_consistency: PASS (참조 위반 0 / 잔재 어휘 0)
  - commit_msg self-test: PASS (6/6 케이스)
  - session_start: 정상 동작 (구조 issue 0건, 측정 대상 출력)
- Baseline 갱신: 없음 (하네스 도입만)
- Evidence: docs/superpowers/specs + docs/superpowers/plans
- 회귀: server-exporter 도메인 코드 무수정 → 기존 베이스라인 회귀 영향 없음

### 미실행 (환경 제약 또는 Plan 3 비범위)

- ansible-playbook --syntax-check (실 ansible 환경 + collections 필요 — 검증 기준 Agent에서 별도 실행)
- 실장비 probe (Round 검증) — 다음 vendor onboarding 시
- Jenkins 4-Stage dry-run — Jenkins controller 환경 필요

---

## 2026-04-27~28 — cycle-002 ~ cycle-006 (정적 검증 누적)

- 환경: Windows 11 + Python 3.11.9 (verify_* 스크립트 OS 중립)
- 명령 / 결과 (각 cycle 보고서 `docs/ai/harness/cycle-00[2-6].md` 정본):
  - `verify_harness_consistency.py`: PASS (rules 29 / skills 43 / agents 51 / policies 10)
  - `verify_vendor_boundary.py`: 26건 → 0건 (cycle-005~006 정밀화 + nosec silence)
  - `check_project_map_drift.py`: PASS (fingerprint 일치)
  - `scan_suspicious_patterns.py`: PASS (rule 95 R1 11 패턴 0건)
  - `validate_claude_structure.py`: PASS
  - `output_schema_drift_check.py`: PASS (cycle-002~006 모두 sections=10 / fd_paths=46 / fd_section_prefixes=10)
  - `validate_field_dictionary.py`: PASS (cycle-006 이후 31 Must / 9 Nice / 6 Skip = 46)
- Baseline 갱신: 없음 (하네스 + schema 보강만 — 실장비 검증 없음)
- 회귀: 도메인 코드 영향 영역 (redfish_gather.py vendor 분기 silence) — 기능 미변경, baseline 회귀 SKIP

## 2026-04-28 — full-sweep 적용 (Tier 1+2)

- 환경: Windows 11 + WSL Python 3.11
- 명령:
  - `verify_harness_consistency.py` (sweep 전 PASS)
  - `verify_vendor_boundary.py` (sweep 전 PASS)
  - `check_project_map_drift.py` (sweep 전 PASS)
  - `scan_suspicious_patterns.py` (sweep 전 PASS)
- 결과: full-sweep 보고서 `docs/ai/harness/full-sweep-2026-04-28.md` 참조
- 회귀: docs/rule/policy/code 정합 변경 — 영향 vendor baseline 회귀 별도 결정 필요

## 2026-04-28 — full-sweep 잔여 (T2-B2 / T2-C2 / T2-C8) 적용

- 환경: Windows 11 + Python 3.11
- 명령:
  - `python scripts/ai/verify_harness_consistency.py`: PASS (rules 29 / skills 43 / agents 51 / policies 10 — 잔재 어휘 default 검사 활성화)
  - `python scripts/ai/verify_vendor_boundary.py`: PASS (vendor 하드코딩 0건)
  - `python scripts/ai/check_project_map_drift.py`: PASS (fingerprint 갱신 후 정합 — os-gather +files/, common precheck 변경)
  - `python scripts/ai/scan_suspicious_patterns.py`: PASS (rule 95 R1 11 패턴 0건)
  - `python scripts/ai/validate_claude_structure.py`: PASS
  - `python scripts/ai/hooks/output_schema_drift_check.py`: PASS (sections=10, fd_paths=46, fd_section_prefixes=10)
  - `python -c "import yaml; yaml.safe_load(...)"`: PASS (gather_users.yml + vendor-boundary-map.yaml)
  - `python -m py_compile`: PASS (precheck_bundle.py + verify_harness_consistency.py)
- 결과:
  - T2-B2 ▷ verify_harness_consistency.py FORBIDDEN_WORDS default 모드 활성화 (`--no-forbidden-check`로 비활성)
  - T2-C2 ▷ precheck_bundle.py Stage 1 (reachable: any TCP response) ↔ Stage 2 (port_open: target service port) 분리 + ConnectionRefusedError 구분
  - T2-C8 ▷ os-gather/files/get_last_login.sh 신규 + Python/Raw 양 경로에서 lookup file 통합 (gather_users.yml 294 → 239 lines)
  - T2-A7 / T3-01~T3-06 / T2-D2: NEXT_ACTIONS 사용자 결정 대기로 SKIP
- 미실행 (환경 제약):
  - `ansible-playbook --syntax-check 3-channel`: WSL ansible 미설치 — 검증 기준 Agent (10.100.64.154)에서 별도 실행
  - `pytest tests/`: WSL pytest 미설치 — 검증 기준 Agent에서 별도 실행
- Baseline 갱신: 없음 (도메인 변경: precheck Stage 분리 + gather_users 함수 통합 — 출력 envelope 13 필드 미변경)
- 회귀: precheck_bundle.py 변경은 진단 메시지만 영향 (failure_stage="port" 신설). gather_users.yml은 기능 동치 (shell snippet 위치 변경만). 영향 vendor baseline 회귀는 검증 기준 Agent에서 별도 실행 필요

## 2026-04-28 — Round 11 reference 종합 수집

- 환경: 사용자 PC (Windows + WSL Ubuntu, 검증 기준 Agent 외)
- 자격: tests/reference/local/targets.yaml (gitignored)
- 명령:
  - `python tests/reference/scripts/crawl_redfish_full.py` (Redfish 11대 시도)
  - `wsl python3 tests/reference/scripts/gather_os_full.py` (OS 7대 시도)
  - `wsl python3 tests/reference/scripts/gather_esxi_full.py` (ESXi 3대)
  - `wsl python3 tests/reference/scripts/gather_agent_env.py` (Agent 2대 + Master 2대)
- 결과:
  - **Redfish**: Dell 27 OK 2417 endpoint / 15MB / 596s, 나머지 BMC 진행 중
  - **OS**: Linux 6대 OK (각 ~106 명령), Win10 FAIL (F4)
  - **ESXi**: pyvmomi 3대 OK, SSH는 .2 1대만 (F5)
  - **Agent/Master**: 4대 모두 OK (각 39 명령)
- 누적 (BMC 진행 중 시점): 4420 파일 / 43MB
- 사고:
  - F1: Dell BMC user=root (admin 아님) — targets.yaml 정정 (사용자 확인)
  - F2: 10.100.15.32 ServiceRoot가 AMI Redfish Server — 실 vendor / 자격 사용자 확인 필요
  - F3: Cisco 10.100.15.1 HTTP 503 / 15.3 timeout — 장비 가동 상태 확인 필요
  - F4: Win10 WinRM 환경 (HTTPS 미활성 + Basic 미허용 + WSL Python 3.12 NTLM MD4 미지원)
  - F5: ESXi 10.100.64.1/.3 SSH 비활성
  - F6: Master 10.100.64.153 sudo ~120s 대기
- Baseline 갱신: **없음** (별도 디렉터리 — fixtures/baseline 무수정)
- 회귀: 영향 없음 (별도 디렉터리, 회귀 input 무수정)
- 환경 제약: 검증 기준 Agent (10.100.64.154) 외 WSL에서 직접 수집
- Evidence: tests/evidence/2026-04-28-reference-collection.md
- decision-log: docs/19_decision-log.md §13 Round 11
