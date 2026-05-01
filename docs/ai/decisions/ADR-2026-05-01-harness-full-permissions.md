# ADR-2026-05-01 — 하네스 모든 권한 부여 (보안 정책 완화)

## Status
Accepted (사용자 명시 2026-05-01)

## Context

사용자가 cycle 2026-05-01 진행 중 명시:
> "보안은 필요없다 하네스에 모든권한을 준다 모두 개선하고 모두 추가해라"

server-exporter 는 내부 프로젝트 + 감사 비대상. 이미 cycle-011 (2026-04-28) 에서 보안 정책 일부 해제됨 (rule 00 protected-paths 강제 해제 / pre_commit_policy.py 제거 / PreToolUse Edit guard 제거).

본 cycle 에서 추가 완화:
- agent 들에 모든 도구 / 모든 경로 / 모든 명령 허용
- pre-commit hooks 의 advisory 다수 유지 (학습 목적), blocking 최소화
- Claude Code CLI permissions — 작업자 환경에서 자유

## Decision

### 1. agent 권한 명시 정책 (`.claude/policy/agent-permissions.yaml`)

모든 agent 에 모든 권한 부여:
- 모든 파일 read/write/edit
- 모든 bash 명령
- 모든 web 검색 / fetch
- vendor / 보호 경로 자유 수정 (사용자 의도 시)

### 2. pre-commit hooks

| Hook | 강제 수준 | 변경 |
|---|---|---|
| `commit_msg_check.py` | advisory | 유지 (학습 목적) |
| `pre_commit_harness_drift.py` | advisory | 유지 |
| `pre_commit_jenkinsfile_guard.py` | advisory | 유지 |
| `verify_vendor_boundary.py` | blocking | **유지 (의도된 강제)** |
| `verify_harness_consistency.py` | blocking (CI) | **유지** |
| `pre_commit_policy.py` | (이미 제거됨) | — |
| `pre_commit_secrets_check.py` | (있다면) | advisory 로 완화 검토 |

### 3. 보호 경로 (`.claude/policy/protected-paths.yaml`)

- 강제 해제 유지 (cycle-011 결정)
- 권장 영역 분류로만 의미
- AI 자동화 우선 / 사용자 명시 시 모두 가능

### 4. 새 vendor / schema / Jenkinsfile 변경

- rule 50 R4 (사용자 명시 승인) — 유지 (의도된 게이트)
- rule 92 R5 (schema 버전) — 유지 (호환성 추적)
- 그 외 자동 진행 가능

## Consequences

### Positive
- AI 자동화 자유롭게 진행
- 작업자 friction 감소
- cycle 진행 속도 증가

### Negative
- 의도치 않은 변경 risk 증가 (rule 92 R2 정신 — 선제 변경 자제 / rule 25 R7 — 실측 검증 / rule 95 — 비판적 검증 으로 완화)
- 하지만 server-exporter 내부 프로젝트라 risk 허용

### Neutral
- git history / cycle log 가 감사 trace 역할
- 사고 발생 시 revert 로 회복

## 관련 rule

- rule 00 (protected-paths 정책 강제 해제 — 이미 적용됨)
- rule 92 R2 (선제 변경 자제 — 유지)
- rule 25 R7-A (실측 검증 — 유지)
- rule 50 R4 (vendor 명시 승인 — 유지)
- rule 92 R5 (schema 버전 명시 — 유지)
- rule 96 R1 (외부 계약 origin 주석 — 유지)

## Alternatives Considered

### 1. 일부만 완화
- agent 별 차등 권한 — overhead 증가, 사용자 의도와 다름

### 2. 그대로 유지 (cycle-011 상태)
- 사용자 명시 거부

### 3. 모든 hook 제거
- 학습 목적 advisory 까지 제거하면 일관성 검증 유실

→ **본 결정**: 모든 권한 부여 + 핵심 검증 hook 만 blocking 유지 (vendor boundary / harness consistency).

## 적용

본 ADR 작성 + commit 으로 명시 효력. 추가 코드 변경:
- `.claude/policy/agent-permissions.yaml` 신규
- 기타 hook 변경 — 별도 cycle (현재 advisory 유지)

## 갱신 history

- 2026-05-01: ADR 작성. 사용자 명시 받음.
