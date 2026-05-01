---
name: write-cold-start-ticket
description: 새 cycle ticket 디렉터리를 cold-start (다음 세션이 컨텍스트 없이 진입 가능) 형식으로 생성. SESSION-HANDOFF + INDEX + coverage/{section}.md + COMPATIBILITY-MATRIX + LAB-INVENTORY 자동 구성. cycle 2026-05-01 학습 — 첫 ticket cold-start 부족으로 두 번째 cycle에서 재구성. 사용자가 "새 cycle ticket 만들어줘", "cold-start 가이드 작성", "ticket 디렉터리 새로" 등 요청 시.
---

# write-cold-start-ticket

## 목적

다음 세션 (사용자 / AI 모두) 이 **컨텍스트 0 상태로 진입**해서 작업 이어갈 수 있는 ticket 디렉터리 생성. cycle 2026-05-01 학습 — 처음 만든 ticket 일부가 매트릭스만 있고 cold-start 가이드 부족 → 두 번째 cycle 에서 SESSION-HANDOFF + coverage/{section}.md 분리.

## 호출 시점

- 새 cycle 진입 (호환성 / schema 변경 / 큰 리팩토링)
- gather coverage 전수조사 같은 멀티-round 작업
- 사용자가 "이 cycle ticket 잘 정리해서 다음 세션 시작 가능하게"

## 입력

- cycle 주제 (예: "gather-coverage", "vendor-onboard-huawei", "schema-v2-migration")
- 시작일 (YYYY-MM-DD)
- 추정 round 수 (1 / 다수)

## 출력 디렉터리 구조

```
docs/ai/tickets/<YYYY-MM-DD>-<주제>/
├── INDEX.md                    # cycle 진입점 — 다음 세션이 처음 읽는 문서
├── SESSION-HANDOFF.md          # 직전 세션 종료 시점 상태 + 다음 세션 첫 지시
├── COMPATIBILITY-MATRIX.md     # (호환성 cycle) 적용 매트릭스 추적
├── LAB-INVENTORY.md            # (선택) lab 보유 / 부재 영역 sanitized
├── HARNESS-RETROSPECTIVE.md    # (선택) cycle 종료 회고
├── coverage/                   # (전수조사 cycle) 영역별 분리
│   ├── MATRIX-R1.md ~ MATRIX-RN.md
│   ├── {section}.md            # power / users / cpu / memory / ...
└── fixes/                      # 개별 fix ticket (P0/P1/P2/P3)
    ├── F01.md ~ F##.md
```

## INDEX.md 필수 섹션

1. **목적** (1~2 문장)
2. **현재 상태** (시작일 / 진행 round / 완료 / 잔여)
3. **cold-start 가이드** — 다음 세션 처음 읽을 순서 (3~5 문서 list)
4. **티켓 구조 요약** — 위 디렉터리 구조 표
5. **결정 의존** (사용자 / 외부 의존 분리)
6. **갱신 history**

## SESSION-HANDOFF.md 필수 섹션

1. **마지막 commit / 시점** (sha + 메시지 + 일시)
2. **이번 cycle 종료 상태** (round / fix 수)
3. **다음 세션 첫 지시 템플릿** (사용자가 복붙 가능한 한 줄)
4. **차단 사유** (외부 의존 / 사용자 결정)
5. **검증 통과 여부** (pytest / verify_harness_consistency / etc.)

## coverage/{section}.md 형식 (호환성 cycle 시)

```markdown
# coverage — <section>

## 영역 정의
<DMTF / vendor docs reference>

## 우리 코드 현재 동작
- 위치: <file:line>
- path: <외부 endpoint>
- fallback 적용: <yes/no — 적용된 cycle 명시>

## fix 후보
| ID | 우선 | 작업 | 검증 |
|---|---|---|---|
| F## | P# | ... | ... |

## sources (rule 96 R1)
- vendor docs: ...
- DMTF: ...
- evidence: tests/evidence/...
```

## 절차

### 1. 디렉터리 생성
```bash
mkdir -p docs/ai/tickets/<YYYY-MM-DD>-<주제>/{coverage,fixes}
```

### 2. INDEX.md 초안
- 위 6 섹션 모두 포함
- "현재 상태" 는 시작 시 `(round 0, fix 0)`

### 3. SESSION-HANDOFF.md 초안
- 시작 시점은 placeholder ("cycle 시작 — 첫 round 진입 직전")
- 매 round 종료 시 갱신

### 4. coverage/ 또는 fixes/ 채움
- 호환성 cycle: coverage/{section}.md 13 영역 또는 그 이상
- fix cycle: fixes/F##.md 개별 ticket

### 5. NEXT_ACTIONS.md 진입점 추가
- 상단에 본 cycle entry + INDEX.md 링크

### 6. cycle 종료 시
- HARNESS-RETROSPECTIVE.md (선택) — 2주 회고 / 부족점 / 학습
- INDEX.md 의 "현재 상태" 갱신
- SESSION-HANDOFF.md 마지막 commit / 다음 지시 템플릿 채움

## 학습 (cycle 2026-05-01)

- 매트릭스만 있는 ticket → 다음 세션 진입 시 어디서 시작할지 모름
- coverage/{section}.md 분리 → 영역별 독립 작업 가능
- SESSION-HANDOFF "다음 세션 첫 지시 템플릿" → 사용자 인지 부담 0
- HARNESS-RETROSPECTIVE → 2주 단위 부족점 검출

## 관련

- rule 26 R6 (CONTINUATION.md 5 섹션)
- rule 70 R1 (변경 종류 → 갱신 대상 매핑)
- agent: docs-sync-worker (ticket 갱신 위임)
- skill: capture-site-fixture (fixture 절차)
