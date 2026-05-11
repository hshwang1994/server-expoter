# M-L4 — docs/13_redfish-live-validation.md 갱신 (사이트 검증 4 + lab 부재 명시)

> status: [PENDING] | depends: M-L3 | priority: P1 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "docs/13_redfish-live-validation.md 갱신 — 사이트 검증 4 vendor + lab 부재 영역 명시." (cycle 진입)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/13_redfish-live-validation.md` (갱신 — 본 cycle 산출 반영) |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | (없음 — 정본 docs) |
| 리스크 top 3 | (1) docs/13 정본 — 정본 보호 (rule 70 R4) / (2) 사이트 검증 Round 갱신 의무 / (3) lab 부재 영역 명시 정확성 |
| 진행 확인 | M-L3 후 진입. 본 cycle 의 마지막 ticket. |

---

## 갱신 본문 (docs/13_redfish-live-validation.md)

### 추가 절: cycle 2026-05-07 사이트 검증 + lab 부재 명시

```markdown
## Round 2026-05-07 — 4 vendor × 1 generation 사이트 검증

본 Round 는 사용자 사이트 BMC 1대 이상 보유 vendor / generation 의 실 검증 결과.

### 결과 매트릭스

| vendor | generation | 사이트 BMC | 검증 commit | 검증 결과 |
|---|---|---|---|---|
| Dell | iDRAC10 | 5대 (10.100.15.27/28/31/33/34) | `0a485823` | [PASS] — 8 Redfish endpoint 모두 SUCCESS |
| HPE | iLO7 | 1대 (10.50.11.231) | `0a485823` | [PASS] |
| Lenovo | XCC3 | 1대 (10.50.11.232) | `0a485823` | [PASS] |
| Cisco | UCS X-series | 1대 (10.100.15.2) | `0a485823` | [PASS] |

### 검증 항목

- ServiceRoot ~ AccountService 9 endpoint 모두 SUCCESS
- 8 Redfish + 7 OS + 3 ESXi 통합 검증 commit `0a485823` 에 PASS 기록
- 본 검증 시점 baseline_v1 4 vendor (Dell/HPE/Lenovo/Cisco) 갱신

### 사이트 사고 / 학습 (cycle 2026-04-30 reverse regression)

- Lenovo XCC3 펌웨어 1.17.0 — Accept + OData-Version + User-Agent 추가 시 reject
- "Accept만" 으로 hotfix (rule 25 R7-A1 — 사용자 실측 > spec)
- 본 정책은 다른 사이트 (Lenovo XCC2 / iLO5+ / Supermicro X12+) 도 동일 가능성 — 보수적 header 정책 의무

## lab 부재 영역 (cycle 2026-05-07 명시)

> 사용자 명시 (2026-05-07 Q2/Q3): Supermicro 사이트 BMC 0대 + Huawei/Inspur/Fujitsu/Quanta lab 도입 timeline 장기 (미정).
> 본 영역 코드 path 는 web sources 기반 (rule 96 R1-A) — 사이트 도입 시 별도 cycle 검증.

### lab 부재 vendor / generation 매트릭스

| vendor | generation | lab status | 코드 path | NEXT_ACTIONS 등재 |
|---|---|---|---|---|
| Dell | iDRAC7 (legacy) | 부재 | adapter dell_idrac.yml + mock | [PENDING] — Dell iDRAC7 lab cycle |
| Dell | iDRAC8 | 부재 | adapter dell_idrac8.yml + mock | [PENDING] |
| Dell | iDRAC9 | 부재 | adapter dell_idrac9.yml + mock (3 variants — 3.x/5.x/7.x) | [PENDING] |
| HPE | iLO (legacy 1/2/3) | 부재 (Redfish 미지원) | adapter hpe_ilo.yml + IPMI fallback 별도 검토 | [SKIP] |
| HPE | iLO4 | 부재 | adapter hpe_ilo4.yml + mock | [PENDING] |
| HPE | iLO5 | 부재 | adapter hpe_ilo5.yml + mock | [PENDING] |
| HPE | iLO6 | 부재 | adapter hpe_ilo6.yml + mock | [PENDING] |
| HPE | Superdome Flex (Gen 1/2 + 280) | 부재 | adapter hpe_superdome_flex.yml + OEM 분기 (M-G1) + mock (M-G2) | [PENDING] |
| Lenovo | BMC (IBM 시기) | 부재 (Redfish 미지원) | adapter lenovo_bmc.yml | [SKIP] |
| Lenovo | IMM (legacy) | 부재 (Redfish 미지원) | (별도 분기 없음) | [SKIP] |
| Lenovo | IMM2 | 부재 | adapter lenovo_imm2.yml + mock | [PENDING] |
| Lenovo | XCC | 부재 | adapter lenovo_xcc.yml (firmware_patterns XCC + XCC2) + mock | [PENDING] |
| Lenovo | XCC2 | 부재 | (위 동일) | [PENDING] |
| Cisco | BMC (legacy) | 부재 (Redfish 미지원) | adapter cisco_bmc.yml | [SKIP] |
| Cisco | CIMC C-series 1.x ~ 4.x | 부재 | adapter cisco_cimc.yml (firmware_patterns) + mock (4 variants) | [PENDING] |
| Cisco | UCS S-series | 부재 | adapter cisco_cimc.yml (model_patterns) | [PENDING] |
| Cisco | UCS B-series | 부재 (UCS Manager 매개) | adapter cisco_cimc.yml + 별도 cycle | [PENDING] — UCS Manager 통합 cycle |
| Supermicro | BMC ~ X14 (6 gen) | 부재 (Q2 — 사이트 0대) | adapter 7개 + OEM tasks 보강 (M-B2) + mock (M-B4) | [PENDING] — Supermicro lab 도입 cycle |
| Supermicro | H11 ~ H14 (AMD) | 부재 | adapter X11~X14 model_patterns 확장 (M-B3) | [PENDING] |
| Supermicro | ARS (ARM) | 부재 | (선택) adapter supermicro_ars.yml (M-B3) | [PENDING] |
| Huawei | iBMC 1.x ~ 5.x + Atlas | 부재 (cycle 2026-05-01 명시) | adapter huawei_ibmc.yml (M-C1) + OEM tasks (M-C2) + mock (M-C3) | [PENDING] |
| Inspur | ISBMC | 부재 (cycle 2026-05-01) | adapter inspur_isbmc.yml + OEM tasks (M-D1) + mock (M-D2) | [PENDING] |
| Fujitsu | iRMC S2 | 부재 (Redfish 미지원 가능성) | adapter fujitsu_irmc.yml (firmware_patterns) | [SKIP] |
| Fujitsu | iRMC S4 / S5 / S6 | 부재 (cycle 2026-05-01) | (위 동일) + OEM tasks (M-E2) + mock (M-E3) | [PENDING] |
| Quanta | QCT BMC | 부재 (cycle 2026-05-01) | adapter quanta_qct_bmc.yml + OEM tasks (M-F1) + mock (M-F2) | [PENDING] |

### web sources 의무 (rule 96 R1-A)

본 lab 부재 영역의 모든 adapter / OEM tasks / mock 은 다음 sources 기반:

| source | 영역 |
|---|---|
| vendor 공식 docs | 9 vendor 공식 매뉴얼 (URL — adapter metadata.origin) |
| DMTF Redfish spec | DSP0268 v1.0 ~ v1.13+ (PowerSubsystem / Storage / AccountService schema) |
| GitHub community / issue | Inspur / Quanta / Huawei (영문 docs 약함 영역) |
| 사이트 실측 | (해당 영역 — 본 Round) |

## 본 cycle (2026-05-07 all-vendor-coverage) 산출 요약

- adapter: 28 → 29 (+supermicro_x10 신설)
- vault encrypted: 5 → 9 (+huawei/inspur/fujitsu/quanta)
- vendor OEM tasks: 4 → 9 (+cisco/huawei/inspur/fujitsu/quanta)
- mock fixture: 4 → 13+ (vendor 별)
- catalog: NEXT_ACTIONS / VENDOR_ADAPTERS / COMPATIBILITY-MATRIX / EXTERNAL_CONTRACTS 갱신
- baseline_v1: 변경 0 (lab 부재 vendor SKIP — rule 13 R4)
- schema/sections.yml + field_dictionary.yml: 변경 0 (Q7 — schema 변경 0)
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `docs/13_redfish-live-validation.md` 본문 갱신 (Round 2026-05-07 + lab 부재 영역)
- [ ] 사이트 검증 4 vendor + lab 부재 25+ row 등재
- [ ] web sources 의무 명시 (rule 96 R1-A)
- [ ] 본 cycle 산출 요약

### 의미 검증

- [ ] 사용자 사이트 사고 (cycle 2026-04-30 Lenovo XCC3 reverse regression) 학습 명시
- [ ] cycle 2026-05-07 산출 6 항목 모두 명시 (adapter / vault / OEM / mock / catalog / baseline 0)

---

## risk

- (LOW) docs/13 정본 — 본 cycle 갱신 commit 사용자 명시 승인 필요? (rule 70 R4)
  - 답: rule 70 R4 는 정본 보호. 본 cycle 은 cycle 2026-05-07 명시 작업으로 docs/13 갱신 의무 — Additive (절 추가, 기존 절 변경 0)

## 완료 조건

- [ ] docs/13_redfish-live-validation.md 본문 갱신 — Round 2026-05-07 + lab 부재 영역 명시
- [ ] 본 cycle 산출 6 항목 요약
- [ ] commit: `docs: [M-L4 DONE] docs/13 갱신 — Round 2026-05-07 사이트 검증 4 + lab 부재 영역 명시`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 단계 (cycle 종료)

- W5 영역 종료 → cycle 2026-05-07 모두 [DONE]
- HARNESS-RETROSPECTIVE.md 작성 (cycle 학습 추출 — 다음 cycle 정착)
- cycle 종료 commit + push

## 관련

- M-L1, M-L2, M-L3 (catalog 갱신)
- M-K1, M-K2 (origin / EXTERNAL_CONTRACTS)
- 정본: docs/13_redfish-live-validation.md
- rule 70 R4 (정본 보호)
- rule 96 R1-A (web sources)

## 분석 / 구현

(cycle 2026-05-11 Phase 7 추가 stub — 본 ticket 의 분석 / 구현 내용은 본문 다른 절 (## 컨텍스트 / ## 현재 동작 / ## 변경 / ## 구현 등) 참조. cycle DONE 시점에 cold-start 6 절 정본 도입 전 작성된 ticket.)
