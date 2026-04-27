# Session Routing Policy — server-exporter

> 세션 시작 시 작업 유형 → 역할 / ai-context 자동 라우팅. CLAUDE.md Step 2 정본.

## 역할 추론 (키워드 → role)

| 키워드 | 추론 role |
|---|---|
| Ansible / playbook / gather / 채널 / Fragment / precheck | gather |
| schema / sections / field_dictionary / baseline / callback / output | output-schema |
| Jenkins / cron / agent (노드) / vault / Redis / 인프라 | infra |
| pytest / probe / fixture / 회귀 / Round | qa |
| 요구사항 / 기획 / 명세 | po |
| 일정 / 릴리즈 / 진행률 | tpm |

## 컨텍스트 자동 로드

| 작업 영역 | 로드 ai-context |
|---|---|
| os-gather/, esxi-gather/, redfish-gather/, common/library/ | ai-context/gather/convention.md |
| schema/, common/tasks/normalize/, callback_plugins/ | ai-context/output-schema/convention.md |
| Jenkinsfile*, ansible.cfg, scripts/ | ai-context/infra/convention.md |
| tests/ | role/qa/README.md |
| adapters/{vendor}_*.yml, redfish-gather/tasks/vendors/{v}/ | ai-context/vendors/{vendor}.md |
| 외부 시스템 (Redfish/IPMI/SSH/WinRM/vSphere) | ai-context/external/integration.md |
| .claude/, docs/ai/ | role/tpm/README.md |

## task-impact-preview 자동 호출 (rule 91 R1)

다음 키워드 감지 시 다른 skill 호출 전 task-impact-preview 먼저:
- "추가해줘", "구현해줘", "만들어줘", "개발해줘", "리팩토링", "변경", "고쳐줘", "수정해줘"
- "벤더 추가", "schema 변경", "필드 추가", "섹션 추가", "마이그레이션", "Jenkinsfile cron"

## skip 조건

- 사용자 명시 ("그냥 진행" / "프리뷰 skip")
- 오타 1줄 / 주석만 / 변수명 1개
- 이미 plan-* 단계 끝남

## 관련

- rule 23 (communication-style)
- rule 91 (task-impact-gate)
- skill: task-impact-preview, analyze-new-requirement, discuss-feature-direction
- 정본: CLAUDE.md "AI 하네스 운영" 절
