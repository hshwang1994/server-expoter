# T-02 — `regex_search` + `when` 절 lint hook (rule 95 영구 차단)

## 우선순위
**LOW** — 현재 codebase 에 해당 위험 패턴 0건 (직전 세션 #5d6cf72c + #a972acc4 fix 후 전수 검색 — `regex_search` 9곳 모두 안전). 미래 코드 추가 시 재발 차단용 hook.

## 영역
- `scripts/ai/hooks/` (신규 hook 추가)
- `.claude/rules/95-production-code-critical-review.md` (검사 항목 추가)
- `.claude/policy/surface-counts.yaml` (hook 카운트 갱신)

## 함정 패턴

```yaml
# 위험 (NoneType conditional fail 가능)
- name: "..."
  when:
    - "var | regex_search('pattern')"
  ...

# 안전 1 — is not none 명시
- name: "..."
  when:
    - "(var | regex_search('pattern')) is not none"

# 안전 2 — length 변환
- name: "..."
  when:
    - "(var | regex_findall('pattern')) | length > 0"

# 안전 3 — Jinja2 set + if 가드 (when 절 외 사용)
- set_fact:
    foo: >-
      {%- set m = var | regex_search('pattern') -%}
      {%- if m -%}{{ m }}{%- else -%}{{ none }}{%- endif -%}
```

## 직전 세션 사고 사례

build #133 ~ #137 (4 빌드 fail) — HPE 10.50.11.231 (DL380 Gen11) 의 `vendors/hpe/collect_oem.yml` L82 + `normalize_oem.yml` L39, L45 의 위험 패턴.

`commit 5d6cf72c` + `a972acc4` 로 fix 완료. 직전 세션 evidence 잔여 후속 #4.

## 작업 계획

### Step 1: hook 스크립트 작성

`scripts/ai/hooks/pre_commit_regex_search_conditional_check.py` 신규:

```python
#!/usr/bin/env python3
"""
PreCommit hook — Ansible YAML 의 when 절에 `regex_search` / `regex_findall` /
`regex_replace` 가 사용되는데 명시 가드 (`is not none` / `is none` /
`| length` / `| bool`) 없는 경우 BLOCKING.

검사 대상: *.yml / *.yaml staged files
검사 패턴: when 절 (when:) 또는 conditional list (`    - "..."`) 의
           regex_* 사용 + 가드 없음.
"""
```

검사 알고리즘:
1. `git diff --cached --name-only` 로 staged YAML 파일 list
2. 각 파일을 라인 단위로 읽음
3. `when:` 라인 또는 `- "..."` 형식 conditional 라인 식별
4. 그 라인 (또는 multi-line) 에 `regex_search` / `regex_findall` / `regex_replace` 사용 + `is not none` / `is none` / `| length` / `| bool` 가드 없음 시 BLOCKING

### Step 2: self-test

```bash
python scripts/ai/hooks/pre_commit_regex_search_conditional_check.py --self-test
```

testcase:
- 위험 패턴 1건 staged → BLOCKING (exit 1)
- 안전 패턴 모두 staged → PASS (exit 0)
- 위험 + 안전 혼합 → BLOCKING (위험 1건 발견 시)

### Step 3: settings.json 등록

`.claude/settings.json` 의 PreCommit hooks 에 등록 — advisory 시작 → 1주 안정 확인 후 BLOCKING.

### Step 4: rule 95 본문 갱신

`.claude/rules/95-production-code-critical-review.md` R1 의심 패턴 11종 중 적절한 위치에 추가:
```
12. Ansible regex_search/findall/replace + when 절 단독 사용 — 미매치 시 None 반환 → strict conditional fail.
```

### Step 5: 카탈로그 갱신

- `.claude/policy/surface-counts.yaml` 의 `hooks` 카운트 +1
- `docs/ai/catalogs/PROJECT_MAP.md` 의 hooks 영역 갱신

## 산출물

- `scripts/ai/hooks/pre_commit_regex_search_conditional_check.py` 신규
- `.claude/rules/95-production-code-critical-review.md` 본문 갱신
- `.claude/policy/surface-counts.yaml` 카운트 +1
- `.claude/settings.json` PreCommit hook 등록
- commit + push

## 위험

- false positive 가능 (가드가 다른 형태 — `\| default(false)` 같은 boolean 변환)
- hook 너무 엄격 시 향후 코드 추가 비용 증가 → advisory 단계 충분히 후 BLOCKING
