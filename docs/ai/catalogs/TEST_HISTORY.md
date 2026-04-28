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
