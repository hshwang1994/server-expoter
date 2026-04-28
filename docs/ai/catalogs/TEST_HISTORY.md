# TEST_HISTORY — server-exporter

> 테스트 실행 / Round 검증 / Baseline 갱신 이력 (append-only, rule 70).

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
