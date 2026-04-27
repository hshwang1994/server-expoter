# server-exporter 현재 상태

## 일자: 2026-04-27

## 요약

server-exporter AI 하네스 **Plan 1 + 2 + 3 + cycle-002 + cycle-003 완료**. clovirone-base 풀스펙 하네스를 server-exporter 도메인으로 1:1 포팅 + 외부 시스템 reference 14개 + 3 cycle 자기개선 (DRIFT 3건 모두 resolved + rule 95 R1 의심 패턴 자동 검출 도구 + 13 adapter origin 주석 누락 검출). 약 260+ 파일 신규. 기존 server-exporter 도메인 코드 무수정.

## 완료된 Plan / Phase

| Plan | Phase | 산출물 | 파일 수 | commit |
|---|---|---|---|---|
| 1 | Phase 1 (Skeleton) | settings.json + 19 hooks + 8 supporting scripts | 28 | d87af96 |
| 1 | Phase 2 (Policy/Meta) | 10 policy + 6 role + 12 ai-context + 10 templates + 5 commands | 43 | 31526c3 |
| 1 | Phase 3 (Rules) | 29 rules | 29 | ee82f1b |
| 1 | Phase 4 (Verify+CLAUDE.md) | CLAUDE.md Tier 0 보강 + verify baseline | 5 | 031b32e |
| (refs) | 외부 시스템 reference | 7 docs (ansible / redfish / vmware / pyvmomi / pywinrm / vault) | 8 | 63eaceb |
| 2 | Phase A (Skills) | 43 skills | 43 | 183a79e |
| 2 | Phase B (Agents) | 51 agents | 51 | 2b3268f |

## 검증 결과

- `verify_harness_consistency.py`: **PASS** (참조 위반 0 + 잔재 어휘 0)
- `session_start.py`: **PASS** (브랜치 main 인지 + 측정 대상 출력)
- `commit_msg_check.py --self-test`: PASS
- 모든 Python 파일 ast.parse PASS

## 카탈로그 (실측, 2026-04-27)

| 카테고리 | 카운트 |
|---|---|
| rules | 29 |
| skills | 43 |
| agents | 51 |
| policies | 10 |
| roles | 6 |
| ai-context | 12 |
| templates | 8 (중복 제거: SKILL.template.md / DISCOVERY_STATE_TEMPLATE.json) |
| commands | 5 |
| hooks (Python) | 19 + supporting 8 |
| references (외부 docs) | 13 (Plan 3 후 보강: ansible 7 + redfish 3 + python 2 + winrm 1 + jenkins 1 = 14, 단 README 별도) |

## 채널별 / Vendor 상태 (기존 — 무수정)

| 채널 | 상태 | adapter |
|---|---|---|
| os-gather | ok | adapters/os/ 7 |
| esxi-gather | ok | adapters/esxi/ 4 |
| redfish-gather | ok | adapters/redfish/ 14 |

| Vendor | adapter | baseline |
|---|---|---|
| Dell | 3 (idrac8/9/generic) | 있음 |
| HPE | 4 (ilo5/6/synergy/generic) | 있음 |
| Lenovo | 2 (xcc/xcc_legacy) | 있음 |
| Supermicro | 3 (x12/x11/legacy) | 일부 |
| Cisco | 1 (cimc) | 일부 |

## 다음 작업 (Plan 3)

- [ ] `docs/ai/` 운영 메타 문서 골격 (catalogs / decisions / policy / workflows / harness / handoff / impact / incoming-review / roadmap / onboarding)
- [ ] 자기개선 루프 dry-run 검증 (harness-cycle 1회 실행)
- [ ] 첫 ADR 작성 (이번 하네스 도입 결정)
- [ ] CONVENTION_DRIFT.md / FAILURE_PATTERNS.md / EXTERNAL_CONTRACTS.md / VENDOR_ADAPTERS.md / SCHEMA_FIELDS.md / JENKINS_PIPELINES.md 초기 골격

## 정본 reference

- `CLAUDE.md` (Tier 0 정본, 보강됨)
- `GUIDE_FOR_AI.md`, `REQUIREMENTS.md`, `README.md`
- `docs/01_jenkins-setup` ~ `docs/19_decision-log`
- 설계서: `docs/superpowers/specs/2026-04-27-harness-refactor-design.md`
- 실행 계획: `docs/superpowers/plans/2026-04-27-harness-refactor-plan-1-foundation.md`
- 외부 시스템 reference: `docs/ai/references/`
