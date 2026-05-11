# M-A2 — status 의도 결정 (사용자 결정 포인트)

> status: [DONE] | depends: M-A1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "이게 로직이 정상작동돼지않는듯함. 부분 성공이라고 하더라도 error 에는 로그가 찍히는데 success로 빠지는경우가 있음 이것은 왜이런지 확인해줘 의도된건지?"

→ 의도된 동작인지 / 버그인지 **사용자가 결정**.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | (M-A1 분석 결과 입력 → 사용자 결정 → M-A3 변경 spec) |
| 영향 vendor | 9 vendor 모두 (envelope.status 호출자 계약) |
| 함께 바뀔 것 | (사용자 결정에 따라) build_status.yml 인라인 / status_rules.yml dynamic / schema/sections.yml 등 |
| 리스크 top 3 | (1) status enum 변경 = 호출자 시스템 파싱 영향 (rule 13 R5 envelope 13 필드 변경) / (2) 회귀 영향 큼 / (3) M-A1 분석 누락 시 잘못된 결정 |
| 진행 확인 | 사용자 결정 후 M-A3 진입 |

## 현재 상태

M-A1 [DONE] (commit `ba003b2f`) — 분석 결과:
- build_status.yml 판정 로직: `errors[]` 는 보지 않음. 섹션 status 만 본다 (정본 인라인 Jinja2)
- 시나리오 B (섹션 success + errors warning) = **명백한 의도된 동작** — 코드 주석 3 위치가 명시 (gather_memory.yml:171-172 / gather_network.yml:208 / normalize_storage.yml:79-80)
- errors[] trigger 26 production 위치 + reset 1 + 가드 2 = 29 location 식별
- 시나리오 B 재현 fixture: 저장소 0건 (모든 baseline 이 errors=0 케이스만 cover) → 신규 mock 필요 (M-A3 / M-B3 / M-D4)
- status_rules.yml DEAD CODE = 명시 주석 "삭제 금지" + 향후 reserved → 유지 권고

→ 본 M-A2 에서 4 결정 default 채택 + 근거 기록 + M-A3 변경 spec 도출.

## 사용자 결정 결과 (2026-05-06 Session-2)

> AI 자율 진행 권한 적용 (cycle 진입 시 사용자 명시 — "사용자 결정 4 포인트도 AI 합리적 default 결정 후 진행").

| 결정 | 선택 | 근거 |
|---|---|---|
| **(1) 시나리오 B 처리** | **B-1 (현재 동작 유지)** | (a) M-A1 분석 — 시나리오 B 가 의도된 동작 (코드 주석 3 위치 명시). (b) Additive only cycle (rule 92 R2 + 사용자 명시). (c) rule 96 R1-B (호환성 cycle 에서 envelope shape 변경 금지). (d) 9 vendor 호출자 시스템 파싱 영향 0. errors[] 는 사유 추적용 분리 영역으로 의미 명확화. |
| **(2) errors[] severity** | **(a) 유지 (severity 도입 없음)** | (a) rule 22 R7/R8 (5 fragment 변수 / 타입 정본) 변경은 별도 cycle. (b) rule 13 R5 envelope shape 보존. (c) 3채널 27+ 위치 영향 → 본 cycle Additive only 영역 외. (d) 사용자 의심 영역은 의도 주석 강화로 충분 해소. |
| **(3) status_rules.yml** | **(c) 유지 (현재)** | (a) DEAD CODE 명시 주석 "삭제 금지 / 향후 동적 로딩 reserved" 명문화. (b) rule 70 R5 ("다음 작업에서 도움 되는가") YES — 운영자 정책 override 패턴 reference. (c) 삭제 시 설계 의도 손실. (d) Case A (의도 주석 only) 와 정합. |
| **(4) status enum** | **(a) 3 enum 유지 (success/partial/failed)** | (a) rule 13 R5 envelope 13 필드 + 6 분석 카테고리 정본 보존. (b) rule 96 R1-B (호환성 외 영역 — schema 확장은 별도 cycle 사용자 명시 승인). (c) 호출자 시스템 파싱 변경 0. |

**결정 종합**: **B-1 + (a) + (c) + (a)** → M-A3 변경 spec **Case A** (의도 주석 강화 only).

## 사용자 결정 4 포인트

### (1) 시나리오 B 처리

**시나리오 B**: 섹션 status 모두 success, errors[] 에 warning 있음

| option | overall status | 영향 |
|---|---|---|
| **B-1 (현재 동작)** | success | 호환성 영향 0. 호출자가 envelope.errors[] 별도 검사 필요 |
| **B-2 (사용자 의도?)** | partial | 호출자 시스템이 success 만 OK 로 판정한다면 partial 도 이상 신호로 인식 |
| **B-3 (신 enum)** | success_with_warnings | envelope status enum 4종 도입 (rule 13 R5 변경 필요) |

**사용자 결정 필요**: B-1 / B-2 / B-3 중 택일

### (2) errors[] severity 구분

현재 `_errors_fragment` 는 단일 type. severity 구분 없음.

| option | 변경 |
|---|---|
| **(a) 유지** | 변경 없음. 모든 error 동등 처리 |
| **(b) 도입** | error / warning / info 3종 — overall status 판정에서 warning 은 무시 |

**사용자 결정 필요**: (a) / (b) 중 택일

### (3) status_rules.yml DEAD CODE 처리

| option | 변경 |
|---|---|
| **(a) 살림** | build_status.yml 에서 include_vars 로 동적 로딩. status_rules.yml 정본화 |
| **(b) 삭제** | DEAD CODE 정리. 인라인 Jinja2 만 유지 |
| **(c) 유지 (현재)** | 운영자 참고용 + 향후 reserved 그대로 |

**사용자 결정 필요**: (a) / (b) / (c) 중 택일

### (4) overall status enum 정의

현재 envelope.status enum: `success | partial | failed`

| option | 변경 |
|---|---|
| **(a) 3 enum 유지** | rule 13 R5 envelope 변경 없음 |
| **(b) 4 enum 도입** | success / success_with_warnings / partial / failed (B-3 와 연결) |

**사용자 결정 필요**: (a) / (b) 중 택일

## 변경 spec (M-A3 도출)

결정 종합 **B-1 + (a) + (c) + (a)** → **Case A 채택**.

### Case A — 의도된 동작 명시 only (Additive)

코드 동작 변경 없음. 의도 주석 + 문서화로 사용자 의심 해소.

#### A-1. `common/tasks/normalize/build_status.yml` 헤더 주석 강화

- **현재** (line 1-16): 입력/출력/판정 규칙만 명시
- **추가**: 시나리오 B (errors warning + 섹션 success → overall=success) 가 **의도된 설계** 임을 명시
  - "errors[] 는 보지 않는다 (section status 만 본다)" 명문화
  - "errors[] 는 사유 추적용 분리 영역" 명문화
  - 코드 주석 3 reference (gather_memory.yml:171-172 / gather_network.yml:208 / normalize_storage.yml:79-80)

#### A-2. `docs/20_json-schema-fields.md` (M-F1 신설 ticket) 에 status 판정 규칙 명시

- M-F1 `docs/20_json-schema-fields.md` 신설 시 다음 절 포함 의무:
  - `status` 필드 enum 3종 (success / partial / failed)
  - 시나리오 4 매트릭스 (A/B/C/D — M-A1 분석 결과)
  - errors[] 와 status 의 분리 의미 — "warning 만 emit 시 status 영향 없음 / 호출자가 errors[] 별도 검사"

#### A-3. status_rules.yml DEAD CODE 유지

- 변경 0. 명시 주석 "삭제 금지 / 향후 동적 로딩 reserved" 그대로 유지
- 주석에 "build_status.yml 인라인 Jinja2 와 동등 정책" 명시 (이미 있음 — 변경 불필요 확인)

### Case A 영향 범위

| 항목 | 영향 |
|---|---|
| build_status.yml 코드 동작 | 변경 0 (주석만) |
| envelope 13 필드 | 변경 0 (rule 13 R5 / 96 R1-B 보존) |
| status enum | 변경 0 (3종 유지) |
| 9 vendor baseline | 회귀 영향 0 |
| 호출자 시스템 파싱 | 영향 0 |
| Mock fixture | 신규 1건 권장 (시나리오 B 재현 — `tests/fixtures/.../status_success_with_warnings.json`) — M-A3 작업 |
| ADR (M-A4) | rule 70 R8 trigger **NO** (rule 본문 변경 없음, 표면 카운트 변동 없음) → M-A4 SKIP 가능 |

## 결정 매트릭스

| 결정 조합 | M-A3 변경 spec |
|---|---|
| B-1 + (a) + (c) + (a) | 변경 없음. 의도된 동작 명시 (build_status.yml comment + docs/20 schema 문서) |
| B-2 + (a) + (a/b/c) + (a) | build_status.yml 판정 로직 변경: errors[] non-empty → overall=partial |
| B-3 + (b) + (a) + (b) | envelope status enum 확장 + status_rules.yml 활성 + severity 도입 (큰 변경) |

## risk

- (HIGH) B-3 + (b) 조합 = envelope schema 변경 (rule 13 R5 + 92 R5 사용자 명시 승인)
- (MED) B-2 = 모든 vendor baseline 회귀 (status 가 success → partial 로 변경되는 케이스 다수)
- (LOW) status_rules.yml 정리 = DEAD CODE 처리만

## 완료 조건

- [x] M-A1 분석 결과 첨부 / 확인 (commit `ba003b2f`)
- [x] 사용자 4 결정 default 답변 기록 (B-1 + a + c + a — AI 자율 진행 권한)
- [x] 결정 매트릭스 → M-A3 변경 spec 도출 (Case A — 의도 주석 강화 only)
- [x] M-A3.md "현재 상태" 갱신 (Case A 채택 명시)
- [x] decision-log entry 추가 (`docs/19_decision-log.md`)
- [x] commit: `docs: [M-A2 DONE] status 의도 결정 — Case A (B-1+a+c+a) / M-A3 spec 도출`

## 다음 세션 첫 지시 템플릿

```
M-A3 status 코드 변경 진입.

M-A2 결정 결과: Case A (B-1 + a + c + a)
변경 spec: M-A3.md "변경 spec → Case A" 절 + M-A2.md "변경 spec (M-A3 도출)" 절

작업:
1. common/tasks/normalize/build_status.yml 헤더 주석 강화 (시나리오 B 의도 명시)
2. status_rules.yml 변경 0 (주석 reference 확인만)
3. mock fixture 1건 신규 (시나리오 B 재현 — status_success_with_warnings)
4. pytest + verify_harness_consistency PASS
5. baseline 회귀 영향 0 (확인만)
6. CURRENT_STATE.md 갱신
7. M-F1 (docs/20_json-schema-fields.md) 신설 시 status 판정 규칙 절 포함 의무 — DEPENDENCIES 갱신
```

## 관련

- rule 13 R5 (envelope 13 필드 — status 변경 시 호출자 계약)
- rule 92 R5 (schema 변경 사용자 명시)
- rule 70 R8 (ADR trigger — 표면/rule 변경 시)

## 분석 / 구현

(cycle 2026-05-11 Phase 7 추가 stub — 본 ticket 의 분석 / 구현 내용은 본문 다른 절 (## 컨텍스트 / ## 현재 동작 / ## 변경 / ## 구현 등) 참조. cycle DONE 시점에 cold-start 6 절 정본 도입 전 작성된 ticket.)
