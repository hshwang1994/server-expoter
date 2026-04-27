# Harness Governance — server-exporter

> 하네스 변경 거버넌스 — Tier 분류 / 승인 권한 / 자가 검수 금지.

## 거버넌스 원칙

1. **자유방임 자기수정 금지**: 모든 변경은 6단계 파이프라인 (HARNESS_EVOLUTION_MODEL.md) 거침
2. **자가 검수 금지** (rule 25 R7): architect → reviewer / updater → verifier 별도 agent
3. **Tier 3 절대 금지**: 권한 완화 / 보호 경로 제거 / control plane 우회는 사람만
4. **두 루프 분리**: 제품 / 하네스 침범 금지

## 승인 권한 (`.claude/policy/approval-authority.yaml`)

| 영역 | 권한자 |
|---|---|
| `common/library/`, `redfish-gather/library/` | hshwang (common_library_approver) |
| `adapters/{redfish,os,esxi}/` | hshwang (vendor_adapter_approver) |
| `.claude/policy/protected-paths.yaml` 자체 | hshwang (protected_paths_approver) |
| `.claude/rules/`, `.claude/policy/` | hshwang (harness_rule_approver) |
| `schema/sections.yml`, `field_dictionary.yml`, `baseline_v1/` | hshwang (schema_approver) |
| `Jenkinsfile*` | hshwang (jenkinsfile_approver) |
| `vault/**` | hshwang (vault_approver) |

## Tier 2 승인 요청 포맷 (rule 23 R1)

```
무엇: <변경 요약, 한 줄, 결과 중심>
왜: <observer drift 결과 / 사고 대응 / 사용자 요구>
영향: <파일 N개 / rules M건 / vendor / channel>
결정 필요: 진행 / 조정 / 취소

결정 주체: **{권한자}**의 결정이 필요합니다 (rule 23 R3).
```

## Tier 3 절대 금지 항목

- `.claude/settings.json`의 `permissions.deny` → `allow` 이동
- `disableBypassPermissionsMode` 활성화 해제
- 보호 경로 (`vault/**`, `schema/baseline_v1/**`, `Jenkinsfile*`) 제거
- 자가 검수 허용 (rule 25 R7 우회)
- bypassPermissions 활성화

이런 변경은 사용자가 직접 PR 생성 + 명시 승인 + 별도 ADR 필수.

## 거버넌스 위반 시

1. cycle 즉시 abort
2. 위반 내용을 `docs/ai/harness/cycle-NNN.md`에 기록
3. `docs/ai/catalogs/FAILURE_PATTERNS.md`에 `governance-violation` append
4. 사용자에게 보고

## 관련

- rule 25 R7 (자가 검수 금지)
- rule 70 (docs-and-evidence-policy)
- agent: harness-governor (메인), harness-evolution-coordinator
- policy: HARNESS_CHANGE_POLICY.md, approval-authority.yaml
