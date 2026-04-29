# Full Lab Sweep (2026-04-29) — runner artifacts

> 정본 보고서: `../2026-04-29-full-lab-sweep.md`

## 재실행 방법

자격증명은 환경변수로 주입 (commit 안 됨):

```bash
export LAB_SSH_PASS='<password>'   # cloviradmin SSH + Jenkins 로그인 동일
python tests/evidence/2026-04-29-full-lab-sweep/_runner_ssh_check.py            # 1. SSH 연결 확인
python tests/evidence/2026-04-29-full-lab-sweep/_runner_jenkins_discover.py     # 2. Jenkins 발견
python tests/evidence/2026-04-29-full-lab-sweep/_runner_jenkins_auth.py         # 3. 인증 + jobs 목록
python tests/evidence/2026-04-29-full-lab-sweep/_runner_jenkins_jobinfo.py      # 4. job 파라미터
python tests/evidence/2026-04-29-full-lab-sweep/_runner_jenkins_nodes.py        # 5. agent label
python tests/evidence/2026-04-29-full-lab-sweep/_runner_status_check.py         # 6. (수동) 빌드 상태
python tests/evidence/2026-04-29-full-lab-sweep/_runner_trigger_sweep.py        # 7. 3 채널 trigger + 결과 수집
python tests/evidence/2026-04-29-full-lab-sweep/_runner_envelope_verify.py      # 8. 13 필드 검증
python tests/evidence/2026-04-29-full-lab-sweep/_runner_problem_analysis.py     # 9. per-host 문제 분석
```

## 산출물 (commit 대상)

- `_inventory.json` — 18대 lab inventory + 4대 차단 사유
- `_jobinfo.json` — 3 gather job 파라미터 + 마지막 빌드
- `_nodes.json` — Jenkins agent label 매핑
- `_console_redfish.txt`, `_console_os.txt`, `_console_esxi.txt` — 빌드 console 전체
- `_sweep_summary.json` — 빌드 결과 요약
- `_envelope_verification.json` — per-host 13 필드 정합 결과
- `_problem_analysis.json`, `_problem_summary.txt` — per-host status / errors / sections
- `_inspect.txt` — sections enum 인스펙션 (DRIFT-012 근거)
- `_trigger_log.txt` — trigger 진행 로그

## 종속

- Python 3.11+
- `paramiko` (SSH)
- 환경변수 `LAB_SSH_PASS`
- Jenkins master `10.100.64.152` (운영) 도달 가능

## 보안

자격증명은 모두 환경변수. 본 디렉터리에 hardcoded 값 없음 (`grep -rn "Goodmit" .` 0건).
