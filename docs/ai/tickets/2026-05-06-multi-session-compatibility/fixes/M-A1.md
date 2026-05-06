# M-A1 — status 로직 분석 (read-only)

> status: [PENDING] | depends: — | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "스키마 검증 들어가자. 모든 값에 대한 스키마 검증해주되 특히 자세히 봐야할것은 개더링상태가 success failed partial 이렇게 3개로 나눠져있는것으로 보이는데, 이게 로직이 정상작동돼지않는듯함. 부분 성공이라고 하더라도 error 에는 로그가 찍히는데 success로 빠지는경우가 있음 이것은 왜이런지 확인해줘 의도된건지?"

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `common/tasks/normalize/build_status.yml`, `common/tasks/normalize/build_sections.yml`, `common/tasks/normalize/build_errors.yml`, `common/vars/status_rules.yml` (DEAD CODE) |
| 영향 vendor | 9 vendor 모두 (envelope status 필드 영향) |
| 함께 바뀔 것 | (분석 only — 변경 없음). 분석 결과는 M-A2 입력 |
| 리스크 top 3 | (1) status 판정 의도 ↔ 사용자 기대 불일치 / (2) M-A2 결정 영향 큼 (envelope.status 호출자 계약) / (3) DEAD CODE 의도 불명확 |
| 진행 확인 | 본 ticket 은 read-only. M-A2 에서 사용자 결정 단계 |

## 현재 상태 (Session-0 분석 결과)

### build_status.yml 판정 로직 (정본)

```yaml
# 입력: _norm_sections (섹션별 status dict)
# 출력: _out_status ("success" | "partial" | "failed")

판정:
  supported_vals = sec_vals reject 'not_supported'
  success_count  = supported_vals select 'success'
  failed_count   = supported_vals select 'failed'

  if supported_vals.length == 0:        → "failed"  (지원 섹션 0)
  elif failed_count == 0:               → "success" (모든 지원 섹션 success)
  elif success_count == 0:              → "failed"  (모든 지원 섹션 fail)
  else:                                  → "partial" (혼재)
```

### 사용자 의심 케이스 (가능 시나리오)

build_status.yml 은 **섹션 단위 status** 만 본다. errors[] 자체는 안 본다.

| 시나리오 | 섹션 status | errors[] | overall status | 사용자 인식 |
|---|---|---|---|---|
| A | 모두 success | 비어있음 | success | OK |
| B | 모두 success | warning 있음 | **success** | "errors 있는데 success?" ← **사용자 의심 영역** |
| C | 일부 fail | error 있음 | partial | OK |
| D | 모두 fail | error 있음 | failed | OK |

→ 시나리오 **B** 가 사용자가 의심하는 케이스. 의도된 동작 (섹션 단위 판정) vs 버그 (errors 비어있어야 success 라야 함) 결정 필요.

### errors[] 가 채워지는 trigger (Session-0 분석)

`common/tasks/normalize/build_errors.yml` 흐름:
- 각 gather 의 `_errors_fragment` (rule 22 R1) 누적
- raw 수집은 성공했지만 일부 endpoint/필드 누락 시 warning 추가 가능
- partial-data 케이스 (예: Redfish Storage success 지만 Volumes endpoint 404) → 섹션 status=success + errors[]에 warning 가능

### status_rules.yml 의 위치 (DEAD CODE)

- `common/vars/status_rules.yml` — 어떤 playbook 에서도 로드 안 함
- 운영자 참고용 + 향후 동적 로딩 reserved
- build_status.yml 은 인라인 Jinja2 로 동등 정책 구현
- 명시 주석: "DEAD CODE / 삭제하지 마십시오 / 향후 동적 로딩"

→ M-A2 에서 결정: status_rules.yml 살릴지 / 인라인 유지할지

## 변경 spec

본 ticket = **분석 only**. 변경 없음. 산출물:

1. **분석 보고서** — 본 ticket M-A1.md 의 "현재 상태" 절 (위) 갱신/확정
2. **시나리오 매트릭스** — A/B/C/D 케이스 명시
3. **errors[] trigger 전수 검색** — `_errors_fragment` 가 채워지는 모든 코드 위치 list (3 채널 × N gather)
4. **회귀 fixture 식별** — 시나리오 B 재현 가능한 mock fixture 후보 (없으면 M-B3/M-D4 에서 생성)

## 회귀 / 검증

- 본 ticket = 분석. 코드 변경 없음 → 회귀 불필요
- 정적 검증: 분석 결과 정확성 확인 (`grep -n "_errors_fragment" -r .` 으로 trigger 위치 누락 없음 확인)

## risk

- (LOW) 분석 결과가 M-A2 사용자 결정의 입력. 누락 시 M-A2~M-A4 잘못된 방향 진행 위험

## 완료 조건

- [ ] build_status.yml 판정 로직 4 케이스 명시
- [ ] errors[] trigger 위치 전수 검색 결과 list (`_errors_fragment` 가 set_fact 되는 모든 위치)
- [ ] 시나리오 B 재현 가능한 fixture 식별 (있으면 list, 없으면 "신규 생성 필요" 명시)
- [ ] status_rules.yml DEAD CODE 처리 권고 (살림 / 삭제 / 유지) M-A2 입력
- [ ] M-A2 진입을 위한 사용자 결정 포인트 4개 명시:
  - (1) 시나리오 B: "errors warning 있음 + 섹션 success" → overall = success vs partial?
  - (2) errors[] 의 severity (warning / error) 구분 도입할지?
  - (3) status_rules.yml 살릴지 (동적 로딩) / 삭제 (DEAD CODE 정리)?
  - (4) overall status 4 enum 도입 (success/partial/failed/success_with_warnings) vs 3 enum 유지?
- [ ] commit: `docs: [M-A1 DONE] status 로직 분석 — 시나리오 4 / errors trigger / 사용자 결정 4`
- [ ] SESSION-HANDOFF.md / fixes/INDEX.md 갱신

## 다음 세션 첫 지시 템플릿

```
M-A1 status 로직 분석 진입.

읽기 우선순위:
1. docs/ai/tickets/2026-05-06-multi-session-compatibility/INDEX.md
2. fixes/M-A1.md (본 ticket)
3. common/tasks/normalize/build_status.yml
4. common/tasks/normalize/build_sections.yml
5. common/tasks/normalize/build_errors.yml
6. common/vars/status_rules.yml (DEAD CODE 확인)

작업:
- "errors warning 있음 + 섹션 success" 시나리오 B 재현 가능한 fixture 식별
- _errors_fragment trigger 전수 검색
- M-A2 사용자 결정 포인트 4개 정리
```

## 관련

- rule 13 R5 (envelope 13 필드 — status 필드 정본)
- rule 22 (Fragment 철학 — _errors_fragment)
- skill: verify-json-output, validate-fragment-philosophy
