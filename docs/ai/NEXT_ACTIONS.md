# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-27 (cycle-002 후 갱신)

## 완료 항목 (이번 세션)

- [x] Plan 1 (Foundation) — settings + hooks + rules + policy + role + ai-context + templates + commands
- [x] Plan 2 (Skills + Agents) — 43 skills + 51 agents
- [x] Plan 3 (docs/ai/) — catalogs + decisions + policy + workflows + harness + handoff + onboarding + roadmap
- [x] References 14개 (외부 시스템 / 라이브러리 / 표준)
- [x] cycle-001 dry-run + cycle-002 실측 cycle (3 DRIFT 발견)
- [x] verify_harness_consistency.py에 SKILL.md name 검사 추가
- [x] output_schema_drift_check.py nested parse fix
- [x] git hooks 실 환경 설치 (`scripts/ai/hooks/install-git-hooks.sh`)
- [x] clovirone-base/ 폴더 제거
- [x] 중복 templates 제거 (SKILL.template.md / DISCOVERY_STATE_TEMPLATE.json)

## P1 — 차기 cycle (Tier 2 — 사용자 승인 필요)

- [ ] **DRIFT-001 정리**: rule 13 본문 "Field Dictionary 28 Must" → "29 Must" 갱신
- [ ] **DRIFT-002 정리**: rule 80 본문 "4-Stage = E2E Regression" 일반화 표기 정정 (Stage 4가 Jenkinsfile별 차이 — E2E Regression / Ingest / Callback)
- [ ] **DRIFT-003 정리**: `docs/ai/references/redfish/vendor-bmc-guides.md` adapter 이름 정정 (실측 14개 매칭)
- [ ] **CLAUDE.md / Plan 1 design**의 동일 stale 표현 일괄 갱신

## P1 — 제품 루프 (사용자 / PO / 실장비 의존)

- [ ] **새 vendor 추가 시도** — `add-new-vendor` skill 검증 (Huawei iBMC / NEC / Inspur 등) — PO 결정
- [ ] **Round 11 실장비 검증** — 새 펌웨어 / 새 모델 (probe-redfish-vendor) — 실장비 + Round 일정 결정
- [ ] **baseline 정합 정밀 검증** — output_schema_drift_check.py 매칭 로직 정밀화 (field_dictionary 안 path와 sections 매칭)

## P1 — 하네스 루프

- [ ] **incoming-review hook 실 환경 테스트** — 다음 git merge 시 `docs/ai/incoming-review/<날짜>-<sha>.md` 자동 생성 확인 (이번 GitHub push 후 다음 머지 trigger)
- [ ] **harness-cycle 정기 주기 결정** — 매주 / 격주 / 수동만 (사용자 결정)
- [ ] **외부 reference 보강** — IPMI / Ansible Shared Library / Sushy 활용 검토 (필요 시)

## P2 — 백로그

- [ ] rule 95 R1 의심 패턴 11종 자동 검출 도구 (현재 일부만 자동화)
- [ ] EXTERNAL_CONTRACTS.md vendor별 Redfish endpoint 실측 매핑
- [ ] sections.yml의 network / firmware / users / power 섹션 상세 SCHEMA_FIELDS catalog 추가
- [ ] Jenkins console에서 cron 표현식 실측 → JENKINS_PIPELINES.md 보강
- [ ] vendor-bmc-guides.md vendor 공식 docs 직접 fetch 재시도 (Dell developer portal 등)

## 결정 필요 (사용자)

| 항목 | 비고 |
|---|---|
| DRIFT-001/002/003 정리 PR 우선순위 | 차기 cycle Tier 2 일괄 vs 개별 |
| 새 vendor 추가 일정 | PO 결정 + 실장비 확보 |
| harness-cycle 정기 주기 | 자동 trigger 도입 여부 |
| Round 11 검증 일정 | 운영 정책 |

## 정본 reference

- `docs/ai/CURRENT_STATE.md`
- `docs/ai/decisions/ADR-2026-04-27-harness-import.md`
- `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT 3건)
- `docs/ai/harness/cycle-002.md` (이번 cycle 결과)
