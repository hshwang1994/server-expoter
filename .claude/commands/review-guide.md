---
description: server-exporter 코드 리뷰 절차 가이드. 4축 리뷰 (구조/품질/보안/벤더경계).
argument-hint: "[file or PR]"
---

# /review-guide

server-exporter 코드 리뷰 4축 절차.

## 4축

1. **Structure** — Fragment 철학 (rule 22) / gather-output 경계 / adapter 점수 일관성 / 파일 500줄 / 함수 15줄
2. **Quality** — 의심 패턴 11종 (rule 95 R1)
3. **Security** — vault 누설 / BMC auth / log redaction / Vault 2단계
4. **Vendor Boundary** — common/ + 3-channel에 vendor 하드코딩 금지 (rule 12)

## 절차

1. `task-impact-preview` — 변경 영향 미리보기 (rule 91)
2. `review-existing-code` skill → 4축 리뷰 (또는 agent 위임)
3. 발견된 위반에 따라:
   - Critical → 즉시 수정 PR
   - High → 머지 전 수정
   - Med → 다음 PR (CONVENTION_DRIFT.md 기록)
   - Low → advisory
4. `prepare-regression-check` — 회귀 테스트 대상 선정
5. 회귀 통과 후 `pr-review-playbook` (PR 생성 전 체크리스트)

## 채널별 추가 점검

- **gather (os/esxi/redfish)**: `validate-fragment-philosophy` skill
- **adapter**: `score-adapter-match` + `verify-adapter-boundary`
- **schema**: `update-output-schema-evidence` + baseline 회귀
- **Jenkinsfile**: 4-Stage 정합 + cron 변경 시 사용자 승인

## 자가 검수 금지 (rule 25 R7)

본인이 작성한 코드를 본인이 리뷰/승인하지 말 것. 별도 reviewer agent 호출.

## 관련

- skill: `review-existing-code`, `verify-adapter-boundary`, `validate-fragment-philosophy`, `verify-json-output`
- agent: `code-reviewer`, `security-reviewer`, `adapter-boundary-reviewer`, `vendor-boundary-guardian`, `output-schema-reviewer`, `schema-mapping-reviewer`, `naming-consistency-reviewer`, `integration-impact-reviewer`
- policy: `.claude/policy/review-matrix.yaml`
