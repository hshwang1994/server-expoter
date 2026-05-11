# ADR-2026-05-11: `regex_search` + `when` 절 None 가드 검사 hook 도입 + rule 95 R1 #12 추가

상태: Accepted
일자: 2026-05-11
결정자: hshwang1994 (사용자 명시 "필요한 작업은 모두 진행")
관련 ticket: `docs/ai/tickets/2026-05-11-jenkins-test-followup/T-02-regex-when-lint-hook.md`
관련 commit: (push 후 확정)
trigger: rule 70 R8 trigger 1 (rule 95 R1 본문 의미 변경)

## 컨텍스트 (Why)

cycle 2026-05-11 직전 세션 — Jenkins `hshwang-gather` build #133~#137 4회 fail 사고:
- HPE 10.50.11.231 (DL380 Gen11 iLO 6 v1.73) Redfish 수집 시 `status=failed` / `sections all 10 failed`
- envelope `errors[].message` = `"Conditional result (False) was derived from value of type 'NoneType' at '<unknown>'"`
- 1턴 식별 어려움 — `strategy: free` + `no_log: true` 로 정확한 task 위치 미식별

### 진짜 원인 (commit `5d6cf72c` / `a972acc4` post-mortem)

`redfish-gather/tasks/vendors/hpe/collect_oem.yml` L82 + `normalize_oem.yml` L39 / L45:

```yaml
when:
  - "(_rf_detected_model | default('')) | regex_search('(?i)Superdome|Flex|Compute Scale-up|CSUS')"
```

`regex_search` 가 미매치 시 **None** 반환. Ansible strict mode 에서 conditional 평가가 None 을 받으면 `Conditional result (False) was derived from value of type 'NoneType'` fail.

DL380 Gen11 model 은 Superdome / Flex / CSUS 패턴 미매치 → regex_search None → block fail → rescue → status=failed.

`| default('')` 는 regex_search **앞** 에 위치 — `_rf_detected_model` 자체 undefined 가드 (INPUT 가드) 만 제공. regex_search **출력** 의 None 은 가드 안 됨.

### 사고 재발 차단 필요

본 패턴은 다른 vendor task 에서도 재발 가능 (예: lenovo `collect_oem.yml`, dell vendor-specific tasks). 작업자 / AI 가 새 vendor task 작성 시 동일 함정 빠질 위험. **pre-commit hook 으로 영구 차단** 필요.

## 결정 (What)

### 1. `scripts/ai/hooks/pre_commit_regex_search_conditional_check.py` 신규

- **검사 대상**: staged YAML 파일 (`os-gather/`, `esxi-gather/`, `redfish-gather/`, `common/`, `adapters/` 영역)
- **검사 로직** (line-based heuristic):
  1. `when:` 블록 진입 감지 (block 형식 `when:` / inline 형식 `when: condition` 둘 다)
  2. `regex_search` / `regex_findall` / `regex_replace` 사용 라인 식별
  3. **POST-regex_* 가드 위치 검증** — 가드 토큰 (`is not none` / `is none` / `is sameas` / `| length` / `| bool` / `| default(` / ` in `) 이 regex_* 호출 **뒤** 위치에 있는지 검사
  4. `| default('')` 가 regex_search **앞** 에 있으면 INPUT 가드만 → 사고 패턴으로 분류 (BAD)
- **단계**: advisory (exit 0 — commit 허용 + stderr 경고). 1주 안정 후 `REGEX_WHEN_BLOCKING=1` 또는 hook 자체 BLOCKING 격상 검토
- **환경변수**:
  - `REGEX_WHEN_SKIP=1` — 본 hook skip
  - `REGEX_WHEN_BLOCKING=1` — advisory → blocking 격상

### 2. `.claude/rules/95-production-code-critical-review.md` R1 #12 추가

기존 "의심 패턴 11종" → "의심 패턴 12종":

> 12. **`regex_search` / `regex_findall` / `regex_replace` + `when` 절 None 가드 누락** — Ansible Jinja2 `regex_*` 가 미매치 시 None 반환 → strict mode conditional fail. 가드: `(var | regex_search('p')) is not none` / `| length > 0` / `| default(false) | bool`. 가드는 regex_* 호출 **뒤** 에 와야 함 — `| default('')` 가 regex_search **앞** 에 있으면 INPUT 만 가드 (출력은 여전히 None, 5d6cf72c 사고 사례). 자동 검출 hook: `scripts/ai/hooks/pre_commit_regex_search_conditional_check.py` (advisory — cycle 2026-05-11 도입).

### 3. `scripts/ai/hooks/install-git-hooks.sh` 등록

`pre-commit` chain 마지막에 `pre_commit_regex_search_conditional_check.py` 추가 + 환경변수 안내 `REGEX_WHEN_SKIP` / `REGEX_WHEN_BLOCKING` 추가.

### 4. `.claude/policy/surface-counts.yaml` 갱신

`hooks: 28 → 29`

## 결과 (Impact)

### 즉시 효과
- self-test 10/10 PASS — 사고 패턴 (5d6cf72c pre-fix) 정확 차단 + 안전 패턴 (POST-가드) false positive 0
- 전체 codebase scan — 10 파일 사용 중 위반 0건 (cycle 2026-05-11 commit `5d6cf72c` / `a972acc4` 로 이미 정리됨)

### 미래 효과
- 새 vendor task 작성 시 동일 함정 재발 차단 (advisory 단계 시 stderr 경고로 학습)
- 1주 안정 후 BLOCKING 격상 검토 — false positive 0건 / true positive 1건 이상 발생 시 BLOCKING

### 영향 vendor
- 전 vendor (HPE / Dell / Lenovo / Cisco / Supermicro / Huawei / Inspur / Fujitsu / Quanta) — 새 task 작성 시 hook 적용
- 현재 모두 안전 패턴 (직전 commit 정리됨) — 회귀 없음

## 대안 비교 (Considered)

### 대안 A: 가드 토큰 단순 검사 (위치 무관) — 거절

- `| default('')` 가 regex_search 앞에 있어도 가드로 인정 → 5d6cf72c 사고 패턴 catch 못 함 (false negative)
- 본 ADR 선택안 (POST-위치 검사) 보다 정확도 낮음

### 대안 B: YAML 파서 기반 (ansible.parsing.utils.yaml) — 거절

- 의존성 추가 (rule 92 R1 — 사용자 확인 필요)
- false positive 줄지만 startup latency 증가 (pre-commit 매 commit 마다 실행)
- 본 ADR 선택안 (line-based heuristic + POST 위치 검사) 가 충분히 정확하면서도 의존성 0

### 대안 C: 즉시 BLOCKING 등록 — 거절

- false positive 발생 시 commit 차단 → 작업 정지 위험
- advisory 1주 안정 검증 후 격상이 안전 (다른 hook 의 advisory → BLOCKING 격상 패턴 따름 — `pre_commit_docs20_sync_check.py` / `pre_commit_status_logic_check.py` / `pre_commit_ticket_consistency.py` / `pre_commit_additive_only_check.py` / `pre_commit_jinja_namespace_check.py` 모두 advisory → BLOCKING 격상 경로 거침)

### 대안 D: settings.json PostToolUse 등록 — skip

- T-02 ticket 에 "settings.json 등록" 명시되어 있으나, settings.json 은 Claude Code hook (PostToolUse/Stop/SessionStart 등) 전용 — git pre-commit 은 `.git/hooks/pre-commit` (install-git-hooks.sh 로 등록) 이 올바른 layer
- PostToolUse Edit|Write 로 등록 가능하지만 매 Edit/Write 시 실행되어 latency 증가 + git pre-commit 과 중복 → skip

## 검증

- self-test 10/10 PASS (BAD 케이스 + GOOD 케이스 + edge 케이스 모두)
- 전체 codebase scan 0 violations
- 5d6cf72c pre-fix 사고 패턴 재현 → 정확 차단 확인
- 5d6cf72c post-fix (`is not none`) → false positive 0
- pytest 626/626 PASS (T-01 fix 영향 포함)

## 관련 문서

- rule 95: `.claude/rules/95-production-code-critical-review.md` R1 #12
- hook: `scripts/ai/hooks/pre_commit_regex_search_conditional_check.py`
- ticket: `docs/ai/tickets/2026-05-11-jenkins-test-followup/T-02-regex-when-lint-hook.md`
- evidence: `tests/evidence/2026-05-11-hpe-ilo6-gen11-adapter-fail.md` [RESOLVED #4]
- 회귀 commits (직전 cycle):
  - `5d6cf72c` — collect_oem.yml regex_search `is not none` 명시
  - `a972acc4` — normalize_oem.yml 동일 패턴 2곳
