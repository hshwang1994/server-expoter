---
name: cross-review-workflow
description: 단일 agent 작업 신뢰 안 함 — 다중 agent cross-review 강제 워크플로우. cycle 2026-05-01 사용자 명시 ("한 에이전트가 작업한 것을 다른 에이전트가 검수"). 호환성 fix / 큰 변경 / 하네스 자기개선 시 진입. 사용자가 "cross-review", "다중 검수" 요청 시.
---

# Cross-Review Workflow Skill

> 단일 agent 작업 신뢰 안 함. 사용자 명시 (2026-05-01) cross-review 강제.

## 호출 명령
`/cross-review-workflow`

## 사용 시점
- 호환성 fix 진행 (cycle 2026-05-01 표준)
- 큰 변경 (신규 vendor / schema)
- 하네스 자기개선

## Workflow 1: 호환성 fix (자세히)

### Step 1 — Specialist 분석 (도메인)
선택:
- **redfish-specialist** — Redfish API / DMTF / OEM
- **network-specialist** — TLS / SSH / WinRM / IB
- **system-engineer** — OS / Ansible / pyvmomi
- **compatibility-detective** — 자동 호환성 영역 탐지

출력: 사고 분석 + 호환성 영역 분류 + fix 후보 제안

### Step 2 — Implementation
- **implementation-engineer** — 구체 코드 작성 (Additive only)

### Step 3 — Cross-review (3중)
1. **code-reviewer** — 4축 (구조/품질/보안/벤더경계)
2. **원래 specialist** — 도메인 정확성 재검수
3. **qa-tester** — 회귀 테스트 정확성

### Step 4 — Verification
- pytest / py_compile / yaml syntax
- verify_harness_consistency / verify_vendor_boundary

### Step 5 — Commit + Push
- rule 24 R9 6 체크리스트
- ticket 갱신 (COMPATIBILITY-MATRIX / NEXT_ACTIONS / FAILURE_PATTERNS)

## Workflow 2: 하네스 자기개선

→ self-improvement-loop-coordinator agent 위임

## Workflow 3: 신규 vendor / schema (큰 변경)

→ rule 50 R2 9단계 / rule 92 R5 사용자 명시 승인 필수

## 주의

- 단일 agent 만으로 commit 금지 (cross-review 의무)
- specialist 없는 implementer 호출 금지
- reviewer 자가 검수 금지 (별도 agent)

## 관련
- cross-review-orchestrator agent
- ADR-2026-05-01-harness-full-permissions
