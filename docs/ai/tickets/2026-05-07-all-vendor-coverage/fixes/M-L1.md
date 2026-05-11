# M-L1 — docs/ai/NEXT_ACTIONS.md 갱신 (lab 도입 후 별도 cycle 등재)

> status: [PENDING] | depends: M-K2 | priority: P1 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 도입 후 별도 cycle 등재 (rule 50 R2 단계 10 + rule 96 R1-C)." (cycle 진입)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/ai/NEXT_ACTIONS.md` (갱신 — "lab 도입 후 별도 cycle 권장" 절 대폭 보강) |
| 영향 vendor | 9 vendor 모두 — 사이트 검증 4 외 25+ generation × 4 후속 작업 |
| 함께 바뀔 것 | (없음 — 카탈로그) |
| 리스크 top 3 | (1) 후속 작업 우선순위 결정 (사용자 Q3 답변 — 장기) / (2) NEXT_ACTIONS 비대화 / (3) 후속 cycle 진입 시 본 절 reference |
| 진행 확인 | M-K2 후 진입 |

---

## 등재 항목 (rule 50 R2 단계 10 + rule 96 R1-C)

각 lab 부재 vendor × generation 마다 4 후속 작업:

1. **사이트 fixture 캡처** — `capture-site-fixture` skill 적용
2. **baseline 추가** — 실장비 검증 후 schema/baseline_v1/{vendor}_baseline.json
3. **lab 도입 후 cycle** — 별도 round (`{vendor} {generation} lab 검증`)
4. **vault 결정** — 사용자 명시 승인 시점 (현재는 임시 자격)

---

## 갱신 본문 (docs/ai/NEXT_ACTIONS.md)

### 신규 절 추가:

```markdown
## lab 도입 후 별도 cycle 권장 (cycle 2026-05-07 all-vendor-coverage 산출)

> 사용자 명시 (2026-05-07 Q3): lab 도입 timeline 장기 (미정).
> 본 절은 코드 path 가 깔린 영역 의 실 lab 검증 후속 작업 추적.

### 4 후속 작업 매트릭스 (vendor × generation 별)

#### Dell (iDRAC10 외)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| iDRAC7 (legacy) | [PENDING] | [PENDING] | [PENDING] — Round name: "Dell iDRAC7 lab 검증" | [PENDING] — vault primary 결정 |
| iDRAC8 | [PENDING] | [PENDING] | [PENDING] — "Dell iDRAC8 lab 검증" | [PENDING] |
| iDRAC9 | [PENDING] | [PENDING] | [PENDING] — "Dell iDRAC9 lab 검증" (3 variants — 3.x / 5.x / 7.x) | [PENDING] |
| iDRAC10 | [DONE] | [DONE] | [DONE] (사이트 검증 commit `0a485823`) | [DONE] (primary infraops + recovery root/calvin — M-A5) |

#### HPE (iLO7 외)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| iLO (legacy 1/2/3) | [SKIP] (Redfish 미지원) | [SKIP] | [SKIP] — IPMI fallback 별도 검토 | [SKIP] |
| iLO4 | [PENDING] | [PENDING] | [PENDING] — "HPE iLO4 lab 검증" | [PENDING] |
| iLO5 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| iLO6 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| iLO7 | [DONE] | [DONE] | [DONE] | [DONE] (primary infraops + recovery admin/admin) |
| Superdome Flex (Gen 1/2 + 280) | [PENDING] | [PENDING] | [PENDING] — "HPE Superdome Flex lab 검증" | [PENDING] |

#### Lenovo (XCC3 외)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| BMC (IBM 시기) | [SKIP] (Redfish 미지원) | [SKIP] | [SKIP] | [SKIP] |
| IMM (legacy) | [SKIP] (Redfish 미지원) | [SKIP] | [SKIP] | [SKIP] |
| IMM2 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| XCC | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| XCC2 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| XCC3 | [DONE] | [DONE] | [DONE] | [DONE] (primary infraops + recovery USERID/PASSW0RD) |

#### Cisco (UCS X-series 외)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| BMC (legacy) | [SKIP] | [SKIP] | [SKIP] | [SKIP] |
| CIMC C-series 1.x ~ 4.x | [PENDING] | [PENDING] | [PENDING] (4 variants) | [PENDING] |
| UCS S-series | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| UCS B-series | [SKIP] (UCS Manager 매개 — 별도 cycle) | [SKIP] | [PENDING] — "Cisco UCS Manager 통합 cycle" | [SKIP] |
| UCS X-series | [DONE] | [DONE] | [DONE] | [DONE] (primary infraops + recovery admin/password) |

#### Supermicro (사이트 BMC 0대 — Q2)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| BMC | [PENDING] | [PENDING] | [PENDING] — "Supermicro lab 도입 cycle" | [PENDING] |
| X9 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| X10 | [PENDING] (cycle 2026-05-07 M-B1 신설) | [PENDING] | [PENDING] | [PENDING] |
| X11 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| X12/X13/X14 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| H11~H14 (AMD) | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| ARS (ARM) | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

#### Huawei iBMC (lab 부재 — cycle 2026-05-01 명시)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| iBMC 1.x | [PENDING] (가능성 낮음 — Redfish 약함) | [PENDING] | [PENDING] | [PENDING] |
| iBMC 2.x | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| iBMC 3.x | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| iBMC 4.x | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| iBMC 5.x | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Atlas AI 서버 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

#### Inspur ISBMC (lab 부재 — cycle 2026-05-01)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| ISBMC | [PENDING] | [PENDING] | [PENDING] | [PENDING] (primary infraops + recovery admin/admin) |

#### Fujitsu iRMC (lab 부재 — cycle 2026-05-01)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| iRMC S2 | [SKIP] (Redfish 미지원 가능성) | [SKIP] | [SKIP] | [SKIP] |
| iRMC S4 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| iRMC S5 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| iRMC S6 | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

#### Quanta QCT (lab 부재 — cycle 2026-05-01)

| generation | 사이트 fixture | baseline | lab cycle | vault 결정 |
|---|---|---|---|---|
| QCT BMC | [PENDING] | [PENDING] | [PENDING] (S/D/T/J variants) | [PENDING] |

### 우선순위 (사용자 명시 Q3 — 장기 미정)

- 사이트 BMC 도입 가능 vendor 우선 (사용자 협의 후)
- Supermicro / Huawei / Inspur / Fujitsu / Quanta 는 사이트 도입 미정 — 코드 path 만 깔림 (본 cycle)
- 사이트 도입 시 우선순위는 별도 사용자 결정

### 후속 cycle 진입 절차

1. lab 도입 vendor / generation 결정 (사용자 협의)
2. `capture-site-fixture` skill 로 사이트 fixture 캡처
3. probe_redfish.py 또는 deep_probe_redfish.py 로 실장비 검증
4. baseline_v1/{vendor}_baseline.json 생성 (rule 13 R4)
5. tests/evidence/<날짜>-<vendor>-<generation>.md 작성
6. docs/13_redfish-live-validation.md Round 갱신
7. 본 NEXT_ACTIONS 표 [PENDING] → [DONE] 갱신
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `docs/ai/NEXT_ACTIONS.md` 새 절 추가
- [ ] 9 vendor × N generation 모두 등재
- [ ] 사이트 검증 4 vendor — [DONE] 표시
- [ ] 그 외 — [PENDING] 표시 (Redfish 미지원 generation 은 [SKIP])

### 의미 검증

- [ ] 4 후속 작업 (사이트 fixture / baseline / lab cycle / vault 결정) 모두 매트릭스
- [ ] 우선순위 명시 (사용자 Q3 — 장기)
- [ ] 후속 cycle 진입 절차 7단계 명시

---

## risk

- (LOW) NEXT_ACTIONS 비대화 — 9 vendor × N gen × 4 후속 = 100+ row. 다음 cycle 마다 갱신 의무

## 완료 조건

- [ ] docs/ai/NEXT_ACTIONS.md 새 절 추가 — lab 도입 후 별도 cycle 매트릭스
- [ ] 9 vendor 모두 등재
- [ ] commit: `docs: [M-L1 DONE] NEXT_ACTIONS lab 도입 후 별도 cycle 등재 (9 vendor × N gen × 4 후속)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-L2 (VENDOR_ADAPTERS 갱신).

## 관련

- M-K2 (EXTERNAL_CONTRACTS 매트릭스)
- rule 50 R2 단계 10 (vendor 추가 9단계 + lab 부재 등재)
- rule 96 R1-C (NEXT_ACTIONS 자동 등재 의무)
- 정본: 9 vendor × N gen × 4 후속 작업 매트릭스

## 분석 / 구현

(cycle 2026-05-11 Phase 7 추가 stub — 본 ticket 의 분석 / 구현 내용은 본문 다른 절 (## 컨텍스트 / ## 현재 동작 / ## 변경 / ## 구현 등) 참조. cycle DONE 시점에 cold-start 6 절 정본 도입 전 작성된 ticket.)
