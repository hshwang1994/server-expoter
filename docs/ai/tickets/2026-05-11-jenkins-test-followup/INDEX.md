# 2026-05-11 — Jenkins 개더링 실 환경 테스트 후속 작업

## 진입점 (cold-start)

본 cycle은 사용자 명시 "Jenkins 들어가서 개더링 테스트해봐 잘되는지" (2026-05-11 세션) 의 후속 작업 모음. 직전 세션에서 발견된 issue 중 fix 완료된 항목은 main 에 반영됨. 본 ticket 들은 **남은 후속 작업**.

직전 세션 commits (`main` HEAD = `80b280be`):

| commit | 내용 | 상태 |
|---|---|---|
| `49f62c8d` | test: HPE iLO 6 Gen11 evidence + fixture 3종 캡처 | 완료 |
| `1065bb79` | fix: detect_vendor probe data None 가드 강화 | 완료 |
| `7906fe85` | fix: rescue 에러 메시지에 task name prefix | 완료 |
| `5d6cf72c` | fix: hpe collect_oem regex_search None 가드 (main fix) | 완료 |
| `a972acc4` | fix: hpe normalize_oem regex_search None 가드 (main fix) | 완료 |
| `80b280be` | docs: evidence RESOLVED 섹션 추가 | 완료 |

직전 세션 Round 2 검증 (Jenkins `hshwang-gather` #139) — 4 vendor SUCCESS (HPE/Lenovo/Dell/Cisco 8/10 sections).

---

## Ticket 목록

| ID | 제목 | 우선순위 | 영역 |
|---|---|---|---|
| **T-01** | HPE adapter 오선택 — DL380 Gen11 이 `hpe_ilo7` (Gen12) 로 매칭됨 | MED | redfish / adapter / detect_vendor |
| **T-02** | `regex_search` + `when` 절 lint hook (rule 95) | LOW | scripts/ai/hooks + rule 95 |

운영 영역 (AI 작업 외 — `NOTES.md` 참조):
- Cisco 10.100.15.1 — TCP/443 OK + HTTP 503 (Redfish 서비스 down/busy)
- Cisco 10.100.15.3 — TCP/443 connection timeout (host down or firewall)

---

## 의존성

```
T-01 (adapter 오선택)  ─┐
                         ├─→ 둘 다 독립 — 병렬 진행 가능
T-02 (lint hook)       ─┘
```

T-01 은 detect_vendor + adapter_loader 영역 (실 빌드 검증 필요 — Jenkins `hshwang-gather` 사용 권장).
T-02 는 hook 추가 (script-only, ansible 환경 불필요).

---

## 권장 진입 순서

1. **상태 파악** (5분):
   - `git log --oneline -10` 으로 직전 세션 commit 확인
   - `tests/evidence/2026-05-11-hpe-ilo6-gen11-adapter-fail.md` 읽기 ([RESOLVED] 섹션 + 잔여 후속 4건)
   - `docs/ai/tickets/2026-05-11-jenkins-test-followup/T-01-*.md`, `T-02-*.md` 읽기

2. **T-01 진행** (예상 30~60분):
   - `task-impact-preview` 먼저 (rule 91 R1 — adapter 영역 변경은 MED 리스크)
   - detect_vendor probe 분석: 무인증 ServiceRoot 응답에서 어디서 model/firmware 추출 가능한지
   - fix 후 Jenkins `hshwang-gather` 빌드 (loc=git, target_type=redfish, bmc_ip=10.50.11.231) 로 회귀 검증
   - 기대: adapter_candidate = `redfish_hpe_ilo6` (Gen11 → ilo6 정확 매칭)

3. **T-02 진행** (예상 20~30분):
   - `scripts/ai/hooks/pre_commit_regex_search_conditional_check.py` 신규
   - `regex_search` / `regex_findall` 등이 `when:` 절에 사용 + `is not none` / `| length` 가드 없을 경우 BLOCK
   - rule 95 본문에 검사 항목 추가
   - `.claude/policy/surface-counts.yaml` 갱신

4. **종료** (5분):
   - 각 ticket commit + push (rule 93 R1 + R7 — github + gitlab 동시)
   - 본 디렉터리 `INDEX.md` 에 완료 상태 markdown
   - `docs/ai/CURRENT_STATE.md` 갱신 (rule 70 R1)

---

## 환경 정보 (직전 세션에서 확인)

| 항목 | 값 |
|---|---|
| Jenkins master | `10.100.64.152:8080` (cloviradmin / Goodmit0802!) |
| 테스트 job | `hshwang-gather` (loc=git, hshwang1994 본인 job) |
| HPE 검증 host | `10.50.11.231` (DL380 Gen11, iLO 6 v1.73, admin/VMware1!) |
| 검증 fixture | `tests/fixtures/redfish/hpe_ilo6_v1_73/` (ServiceRoot + Manager + System) |
| Branch | `main` (HEAD = `80b280be`) |
| origin remote | github + gitlab (push 1번 = 두 곳 동시) |
