# Dynamic Routing Rules — server-exporter

> task-impact-preview 결과 → 다음 skill 자동 라우팅 규칙. rule 91 R4 정본.

## 라우팅 매트릭스

| Preview 리스크 | 변경 영역 | 다음 skill |
|---|---|---|
| LOW | 단일 vendor adapter | implement-safe-change (또는 직접 구현) |
| LOW | 문서만 (docs/ai/) | update-evidence-docs |
| LOW | fixture 추가 | implement-safe-change + run-baseline-smoke |
| MED | 다중 vendor | vendor-change-impact 먼저 |
| MED | Jenkinsfile cron | scheduler-change-playbook + 사용자 승인 |
| MED + 옵션 2+ | 후보안 다수 | compare-feature-options → recommend-product-direction |
| HIGH | schema 3종 동반 | plan-schema-change + write-impact-brief |
| HIGH | 새 vendor | add-new-vendor + 사용자 승인 |
| HIGH | 외부 시스템 계약 변경 | debug-external-integrated-feature → 사용자 질의 |
| Critical | 벤더 경계 | 즉시 중단 + verify-adapter-boundary + 사용자 승인 |
| Critical | vault 변경 | rotate-vault skill 절차 (cycle-011: security-reviewer 제거 — 운영자 직접) |
| Critical | 보호 경로 운영 권장 | 사용자 명시 승인 권장 (cycle-011: 보안 정책 해제, 운영 권장 수준) |
| Critical | settings 권한 변경 | (cycle-011: bypassPermissions 채택. 본 항목은 deprecated) |

## 회귀 영역 자동 식별 (rule 91 R7 / rule 92 R9)

다음 영역 변경 시 자동 회귀 포함:
- 공통 fragment 영역 (`common/tasks/normalize/`)
- 공통 라이브러리 (`common/library/`, `redfish-gather/library/`)
- adapter 추가/수정
- callback (`callback_plugins/json_only.py`)
- 출력 schema (sections.yml / field_dictionary.yml)
- Jenkinsfile* (모든 3종)
- vault 회전

## 사용자 명시 승인 대상 (Critical)

다음 변경은 사용자 명시 승인 없이 자동 진입 금지:
1. 보호 경로 (`vault/**`, `schema/baseline_v1/**`, `Jenkinsfile*`) 변경
2. `requirements.yml` / `requirements.txt` 추가/제거
3. `schema/sections.yml` + `field_dictionary.yml` 버전 결정
4. `Jenkinsfile*` cron 변경
5. 새 vendor 추가 (PO 결정 + 9단계 절차)
6. main 직접 push (PR 우회)

## 관련

- rule 91 R4 (preview 후속 라우팅)
- rule 92 R9 (자동 회귀 영역)
- (cycle-011: rule 60 해제 — 보안은 운영 권장 수준)
- skill: task-impact-preview, write-impact-brief, compare-feature-options
