# tests/e2e_browser — Playwright Browser E2E

> 도입: 2026-04-29 cycle-014. server-exporter의 호출자 / Jenkins UI / Grafana 적재 결과를 브라우저에서 검증.

## 사전 조건

```bash
# 1. test deps 설치
python -m pip install -r requirements-test.txt

# 2. Playwright Chromium 브라우저 다운로드 (~150MB, 최초 1회)
python -m playwright install chromium

# 3. lab 자격증명 (gitignored)
ls vault/.lab-credentials.yml
```

자격증명 파일이 없으면 `lab` marker 테스트는 자동 skip (conftest.py).

## 실행

```bash
# 전체 Browser E2E
pytest tests/e2e_browser/ -v

# Jenkins UI만
pytest tests/e2e_browser/ -v -m jenkins

# BMC UI만
pytest tests/e2e_browser/ -v -m bmc

# 헤드 모드 (브라우저 창 보기)
pytest tests/e2e_browser/ -v --headed

# 트레이스 캡처 (디버그)
pytest tests/e2e_browser/ -v --tracing on
```

## 시나리오 list

| 파일 | 시나리오 | 상태 |
|---|---|---|
| `test_jenkins_master.py` | 마스터 dashboard 도달 | [PASS] 활성 |
| `test_jenkins_master.py` | 로그인 + jobs list | [PASS] 활성 (cycle-015 cloviradmin/Goodmit0802!) |

## Marker 정의

| Marker | 의미 |
|---|---|
| `lab` | `vault/.lab-credentials.yml` 필요 (auto-skip 미존재 시) |
| `jenkins` | Jenkins master Web UI |
| `bmc` | BMC Web UI (iDRAC / iLO / XCC / CIMC) |
| `slow` | 30초 이상 |

## CI 통합 (예정)

Jenkins agent (10.100.64.154/155)에서 실행 시:
- Chromium binary cache 필요 (150MB) → `~/.cache/ms-playwright/`
- xvfb-run 또는 `--headed=False` (default)

## 비고

- 본 디렉터리는 기존 `tests/e2e/` (pytest baseline E2E)와 별개. 기존은 backend JSON 검증 / 본 디렉터리는 Browser UI.
- 사용자 권한 부여 (cycle-015): SSH 사용자 (cloviradmin) = Jenkins UI 사용자. Browser E2E login 활성.
