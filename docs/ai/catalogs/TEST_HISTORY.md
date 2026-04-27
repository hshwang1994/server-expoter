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
