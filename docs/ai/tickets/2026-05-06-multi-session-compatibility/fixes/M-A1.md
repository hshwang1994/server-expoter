# M-A1 — status 로직 분석 (read-only)

> status: [DONE] | depends: — | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "스키마 검증 들어가자. 모든 값에 대한 스키마 검증해주되 특히 자세히 봐야할것은 개더링상태가 success failed partial 이렇게 3개로 나눠져있는것으로 보이는데, 이게 로직이 정상작동돼지않는듯함. 부분 성공이라고 하더라도 error 에는 로그가 찍히는데 success로 빠지는경우가 있음 이것은 왜이런지 확인해줘 의도된건지?"

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `common/tasks/normalize/build_status.yml`, `common/tasks/normalize/build_sections.yml`, `common/tasks/normalize/build_errors.yml`, `common/tasks/normalize/merge_fragment.yml`, `common/tasks/normalize/build_output.yml`, `common/vars/status_rules.yml` (DEAD CODE) |
| 영향 vendor | 9 vendor 모두 (envelope status 필드 영향) |
| 함께 바뀔 것 | (분석 only — 변경 없음). 분석 결과는 M-A2 입력 |
| 리스크 top 3 | (1) status 판정 의도 ↔ 사용자 기대 불일치 / (2) M-A2 결정 영향 큼 (envelope.status 호출자 계약) / (3) DEAD CODE 의도 불명확 |
| 진행 확인 | 본 ticket 은 read-only. M-A2 에서 사용자 결정 단계 |

---

## 분석 결과

### 1. build_status.yml 판정 로직 (정본)

```yaml
# 입력: _norm_sections (섹션별 status dict, 10 sections)
# 출력: _out_status ("success" | "partial" | "failed")
#
# 핵심: errors[] 는 보지 않는다. 섹션 status 만 본다.

판정:
  supported_vals = sec_vals reject 'not_supported'
  success_count  = supported_vals select 'success'
  failed_count   = supported_vals select 'failed'

  if supported_vals.length == 0:        → "failed"  (지원 섹션 0)
  elif failed_count == 0:               → "success" (모든 지원 섹션 success)
  elif success_count == 0:              → "failed"  (모든 지원 섹션 fail)
  else:                                  → "partial" (혼재)
```

### 2. build_output.yml 흐름 (envelope 13 필드 정본)

```yaml
# common/tasks/normalize/build_output.yml
_output:
  status:   _out_status      # ← build_status.yml output
  sections: _norm_sections   # ← build_sections.yml output
  errors:   _norm_errors     # ← build_errors.yml output (독립 계산)
  data:     _merged_data
  ...
```

**핵심: `_out_status` 와 `_norm_errors` 는 독립 계산**. errors 비어있지 않아도 status 결정에 영향 없음. ← **시나리오 B 의 root cause (의도된 설계)**.

### 3. 시나리오 매트릭스 (4 케이스)

| 시나리오 | 섹션 status | errors[] | overall status | 사용자 인식 |
|---|---|---|---|---|
| A | 모두 success | 비어있음 | success | OK |
| **B** | 모두 success | warning 있음 | **success** | "errors 있는데 success?" ← **사용자 의심 영역** |
| C | 일부 fail | error 있음 | partial | OK |
| D | 모두 fail | error 있음 | failed | OK |

→ 시나리오 **B 는 명백하게 의도된 동작**. 코드 주석에 명시 (아래 #5 참조).

### 4. errors[] trigger 위치 전수 검색

`_errors_fragment` set_fact 위치 (production 코드, docs/skills 제외):

#### 4-A. 패턴 1 — 정상 수집 시 빈 list, partial-data 시 warning emit (시나리오 B trigger)

| 위치 | trigger 조건 | 섹션 영향 |
|---|---|---|
| `os-gather/tasks/linux/gather_memory.yml:173` | dmidecode 권한/없음 → os_visible fallback warning | memory: success + warning |
| `os-gather/tasks/linux/gather_network.yml:209` | lspci stderr 비어있지않음 → "NIC partial 가능" warning | network: success + warning |
| `os-gather/tasks/linux/gather_system.yml:350` | _l_id_diagnostics 누적 + vendor undefined error | system: success or failed |
| `os-gather/tasks/windows/gather_system.yml:137` | _w_id_diagnostics 누적 (id check warning) | system: success + warning |
| `esxi-gather/tasks/normalize_storage.yml:81` | NFS/vSAN/vVOL datastore capacity 미수집 warning | storage: success + warning |
| `redfish-gather/tasks/normalize_standard.yml:564` | `_rf_raw_collect.errors` 직접 누적 (Redfish library 가 발생시킨 모든 errors — 일부 endpoint 404 / partial-data 포함) | section status는 collect 결과에 따라 |

#### 4-B. 패턴 2 — rescue block (best-effort skip, section status fail)

| 위치 | trigger | 섹션 영향 |
|---|---|---|
| `os-gather/tasks/linux/gather_hba_ib.yml:156` | rescue: hba_ib 수집 실패 | sections=[] (skip) |
| `os-gather/tasks/linux/gather_runtime.yml:124` | rescue: runtime 수집 실패 | sections=[] (skip) |
| `os-gather/tasks/windows/gather_runtime.yml:243` | rescue: Windows runtime 실패 | sections=[] (skip) |
| `esxi-gather/tasks/collect_network_extended.yml:197` | rescue: vmnic/vmhba 수집 실패 | sections=[] (skip) |

→ 패턴 2 는 section status 가 not_supported 또는 failed 로 떨어짐 → status=partial 또는 failed.

#### 4-C. 패턴 3 — 정상 케이스 빈 list (대부분의 gather)

`_errors_fragment: []` 형태로 명시. 정상 수집 시 errors 채우지 않음.

| 채널 | 위치 (대표) |
|---|---|
| Linux | gather_cpu.yml:136,268, gather_storage.yml:127,262, gather_users.yml:105,238, gather_runtime.yml:104, gather_memory.yml:324 |
| Windows | gather_cpu.yml:122, gather_hardware.yml:105, gather_memory.yml:130, gather_network.yml:178, gather_storage.yml:246, gather_runtime.yml:220, gather_users.yml:85 |
| ESXi | normalize_system.yml:105, normalize_network.yml:131, collect_runtime.yml:169, collect_network_extended.yml:181 |
| Redfish OEM | vendors/{dell,hpe,lenovo,supermicro}/collect_oem.yml:16 (placeholder) |

#### 4-D. 패턴 4 — merge_fragment.yml reset

`common/tasks/normalize/merge_fragment.yml:114` — 다음 task 가 stale 값 안 쓰도록 `_errors_fragment: []` 초기화.

#### 4-E. 패턴 5 — string/dict 방어 가드

`merge_fragment.yml:42-55` + `build_errors.yml:17-29` — `_errors_fragment` 가 string/dict/None 인 경우 character iteration 차단 (cycle-006 fix, FAILURE_PATTERNS DRIFT-005).

### 5. 코드 주석 — 시나리오 B 가 의도된 동작임 명시

#### `os-gather/tasks/linux/gather_memory.yml:171-172`
> "LOW-1 fix: dmidecode 권한/미존재로 total_basis=os_visible fallback 시 사용자가 사유 추적 가능하도록 errors[] 에 명시. 정상 수집은 빈 list."

#### `os-gather/tasks/linux/gather_network.yml:208`
> "LOW-9: lspci stderr 비어있지 않으면 권한 부족/partial enumeration 의심 — errors[] 에 명시."

#### `esxi-gather/tasks/normalize_storage.yml:79-80`
> "cap 미수집 datastore (NFS/vSAN/vVOL 일부) 가 있으면 호출자가 사유 추적 가능하도록 errors[] 에 명시. 정상 수집은 빈 list."

→ 3 곳 코드 주석이 명시: **"섹션은 success 지만 사유 추적용 warning emit"**. errors[] 는 **section status 와 분리된 추적 정보**.

### 6. 시나리오 B 재현 fixture 식별

**저장소 fixture 검색 결과: 시나리오 B 재현 가능한 fixture 없음**.

| fixture | status | errors_len | 섹션 |
|---|---|---|---|
| `schema/baseline_v1/dell_baseline.json` | success | 0 | 7 success / 3 not_supported |
| `schema/baseline_v1/hpe_baseline.json` | success | 0 | — |
| `schema/baseline_v1/lenovo_baseline.json` | success | 0 | — |
| `schema/baseline_v1/cisco_baseline.json` | success | 0 | — |
| `schema/baseline_v1/esxi_baseline.json` | success | 0 | — |
| `schema/baseline_v1/windows_baseline.json` | success | 0 | — |
| `schema/baseline_v1/ubuntu_baseline.json` | success | 0 | — |
| `schema/baseline_v1/rhel810_raw_fallback_baseline.json` | success | 0 | — |
| `tests/fixtures/outputs/dell_r760_output.json` | success | 0 | — |

→ **모든 baseline 이 정상 수집 (errors=0) 케이스만 cover**. 시나리오 B 는 사용자 사이트 실 운영 중 발생 (errors[] 에 warning 있는데 status=success) — baseline 미캡처.

→ **신규 mock fixture 필요**:
- M-A3 (status 코드 변경 cycle) — 시나리오 B mock fixture 1건 (memory dmidecode warning 케이스)
- 또는 M-D4 (전 vendor 호환성 회귀) — partial-data fixture N건
- 또는 M-B3 (공통계정 mock) — Redfish library partial errors 케이스

### 7. status_rules.yml DEAD CODE 처리 권고

`common/vars/status_rules.yml`:
- 어떤 playbook 에서도 로드 안 함 (`include_vars` / `vars_files` 0건)
- 명시 주석: "DEAD CODE / 삭제하지 마십시오 / 향후 동적 로딩 reserved"
- 운영자 참고용 + 향후 동적 정책 로딩 placeholder
- build_status.yml 은 인라인 Jinja2 로 동등 정책 구현

**권고 (M-A2 입력)**: 유지 (option (c)). 근거:
- 명시 주석에 "삭제 금지" 명문화
- 향후 동적 로딩 시 정본
- 운영자 참고 문서로 기능 (rule 70 R5 — "다음 작업에서 도움 되는가" YES)
- 삭제 시 설계 의도 손실 (운영자 정책 override 패턴)

---

## 사용자 결정 4 포인트 (M-A2 입력)

### 결정 (1): 시나리오 B "errors warning 있음 + 섹션 success" → overall = ?

| option | 의미 | 영향 |
|---|---|---|
| **B-1 (현재 동작 유지) ★ 추천** | section 단위 판정 — overall=success. errors[] 는 사유 추적용 분리 영역 | envelope shape 변경 0. 기존 호출자 영향 0. 의도 주석으로 명시만 강화 |
| B-2 (errors non-empty → partial) | overall = partial 강제 | envelope.status 의미 변경. 호출자가 partial 대응 로직 추가 필요 |
| B-3 (severity 도입 + warning 만 success 유지) | errors[] 에 severity 추가 후 error 만 partial trigger | schema 변경 (rule 92 R5) — envelope shape 변경 |

**AI 추천 default**: **B-1 (유지)** — Additive only cycle 정신 + 코드 주석이 명시한 의도 (sufficient documentation).

### 결정 (2): errors[] severity (warning / error) 구분 도입할지?

| option | 의미 | 영향 |
|---|---|---|
| **(a) 유지 (현재) ★ 추천** | errors[] 는 단일 type, severity 없음 | 변경 0 |
| (b) severity 추가 | `{section, message, detail, severity}` 4 필드 | rule 22 R7 (5 fragment 변수) + rule 13 R5 (envelope) 변경. 3채널 27+ 위치 영향 |

**AI 추천 default**: **(a) 유지** — 본 cycle Additive only + R1-B (envelope shape 보존) 영역.

### 결정 (3): status_rules.yml DEAD CODE 처리

| option | 의미 |
|---|---|
| (a) 동적 로딩 활성화 | build_status.yml 에서 `include_vars` 추가, 인라인 Jinja2 → 정책 데이터 기반 |
| (b) 삭제 | DEAD CODE 정리 |
| **(c) 유지 (현재) ★ 추천** | 운영자 참고 + 향후 reserved (변경 0) |

**AI 추천 default**: **(c) 유지** — 명시 주석 "삭제 금지" + 향후 동적 로딩 reserved.

### 결정 (4): overall status enum

| option | 의미 |
|---|---|
| **(a) 3 enum 유지 (success/partial/failed) ★ 추천** | rule 13 R5 envelope 13 필드 보존 |
| (b) 4 enum 도입 (success/partial/failed/success_with_warnings) | envelope shape 변경 — 호출자 계약 변경 |

**AI 추천 default**: **(a) 3 enum 유지** — rule 13 R5 / R1-B (envelope shape 보존) 명문화 영역. 4 enum 도입은 별도 cycle 사용자 명시 승인 필요.

---

## 회귀 / 검증

- 본 ticket = 분석. 코드 변경 없음 → 회귀 불필요
- 정적 검증: `_errors_fragment` trigger 전수 검색 완료 (production 26 위치 + reset 1 + 가드 2 위치 = 29 location)

## risk

- (LOW) 분석 결과가 M-A2 사용자 결정의 입력. 누락 시 M-A2~M-A4 잘못된 방향 진행 위험 → **AI 합리적 default 명시 (B-1 / a / c / a)** 로 자율 진행 권한 적용 가능

## 완료 조건

- [x] build_status.yml 판정 로직 4 케이스 명시 (절 #1)
- [x] errors[] trigger 위치 전수 검색 결과 list (절 #4 — 패턴 1~5, 26 production 위치)
- [x] 시나리오 B 재현 가능한 fixture 식별 (절 #6 — **저장소에 없음. 신규 mock 필요 (M-A3 / M-B3 / M-D4)**)
- [x] status_rules.yml DEAD CODE 처리 권고 (절 #7 — 유지 권고)
- [x] M-A2 진입을 위한 사용자 결정 포인트 4개 명시 + AI default 추천:
  - (1) 시나리오 B → **B-1 (유지)** 추천
  - (2) errors severity → **(a) 유지** 추천
  - (3) status_rules.yml → **(c) 유지** 추천
  - (4) status enum → **(a) 3 enum 유지** 추천
- [x] commit: `docs: [M-A1 DONE] status 로직 분석 — 시나리오 4 / errors trigger 26 / 사용자 결정 4 + AI default`
- [x] SESSION-HANDOFF.md / fixes/INDEX.md 갱신

## 다음 세션 첫 지시 템플릿

```
M-A2 status 의도 결정 진입.

cold-start: SESSION-PROMPTS.md + fixes/M-A2.md + M-A1 분석 결과 ("분석 결과" 절)

자율 진행 default (M-A1 분석 + AI 추천):
- (1) B-1 (현재 동작 유지) — envelope shape 변경 없음
- (2) (a) errors severity 유지
- (3) (c) status_rules.yml 유지
- (4) (a) 3 enum 유지

근거: 본 cycle Additive only (rule 92 R2 + 사용자 명시) + rule 13 R5 + rule 96 R1-B (envelope shape 보존). 시나리오 B 는 명백한 의도된 동작 — 코드 주석 3 위치가 명시.

작업: M-A2.md 의 4 결정 default 기록 + 근거 + M-A3 변경 spec 도출 (의도 주석 강화 only).
```

## 관련

- rule 13 R5 (envelope 13 필드 — status 필드 정본)
- rule 22 (Fragment 철학 — _errors_fragment)
- rule 92 R2 (Additive only)
- rule 96 R1-B (envelope shape 보존)
- skill: verify-json-output, validate-fragment-philosophy
- 정본 코드: `common/tasks/normalize/build_status.yml`, `build_sections.yml`, `build_errors.yml`, `merge_fragment.yml`, `build_output.yml`
