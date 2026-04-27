# server-exporter 다음 작업 (NEXT_ACTIONS)

## 일자: 2026-04-27

## P0 — 이번 세션 마무리

- [ ] Plan 3 docs/ai/ 골격 commit
- [ ] 자기개선 루프 dry-run 1회 (verify 통과 확인)
- [ ] 최종 README/onboarding 진입점 정리

## P1 — 다음 세션 (제품 루프)

- [ ] **(선택) 새 vendor 추가 시도** — `add-new-vendor` skill 검증 (예: Huawei iBMC 또는 NEC)
- [ ] **(선택) baseline 정합 검증** — 현재 vendor 5종 baseline과 schema/sections.yml 정합 확인
- [ ] **(선택) Round 11 검증** — 새 펌웨어 / 새 모델 시 probe-redfish-vendor 적용

## P1 — 다음 세션 (하네스 루프)

- [ ] **harness-cycle 정식 실행** — 일주일 동안 누적된 measurement drift 갱신
- [ ] **incoming-review hook 실 환경 테스트** — git merge 후 자동 보고서 생성 확인
- [ ] **외부 시스템 reference 보강** — Jenkins Pipeline syntax / jmespath / Ansible callback API 추가 fetch

## P2 — 백로그

- [ ] EXTERNAL_CONTRACTS.md 채우기 (현재 placeholder) — vendor별 Redfish endpoint 매핑 실측
- [ ] VENDOR_ADAPTERS.md 채우기 — adapter 매트릭스 표 (priority × specificity × tested_against)
- [ ] SCHEMA_FIELDS.md 채우기 — 28 Must 상세
- [ ] JENKINS_PIPELINES.md 채우기 — 3 Jenkinsfile 4-Stage 표
- [ ] tdd 작성 (rule 95 R1 의심 패턴 자동 검출 도구)
- [ ] verify_harness_consistency.py에 SKILL.md `name` ↔ 폴더 일치 검사 추가

## 의존성 체인

```
P0[모두] → P1[제품 루프 또는 하네스 루프 어느 쪽이든]
P1[하네스 cycle] → P2[catalog 채우기]
P1[새 vendor] → P2[VENDOR_ADAPTERS / EXTERNAL_CONTRACTS 갱신]
```

## 결정 필요

| 항목 | 결정자 | 마감 | 영향 |
|---|---|---|---|
| 다음 세션 P1 우선순위 | hshwang | 다음 세션 시작 시 | 작업 lane 결정 |
| harness-cycle 정기 주기 | hshwang | 정해지면 | 자동 trigger 도입 여부 |

## 정본 reference

- `docs/ai/CURRENT_STATE.md` — 현재 상태
- `docs/ai/decisions/` — ADR
- `REQUIREMENTS.md` — 벤더/펌웨어 검증 기준
- `docs/19_decision-log.md` — 운영 의사결정
