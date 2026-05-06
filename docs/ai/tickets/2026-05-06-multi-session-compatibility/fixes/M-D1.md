# M-D1 — 9 vendor × N gen × 9 sections 호환성 매트릭스 작성

> status: [PENDING] | depends: — | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "지금 추가한 코드 및 현재돼있는 코드가 지금 프로젝트에 지원하는 모든 밴더 모든 세대 모든 장비에도 지원해야해."

→ 9 vendor × N generation × 9 sections (system/hardware/bmc/cpu/memory/storage/network/firmware/users/power) 의 호환성 매트릭스 작성. lab 부재 → 정적 분석 + commit history + DMTF/vendor docs.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | (분석 산출물 → `docs/ai/tickets/2026-05-06-multi-session-compatibility/COMPATIBILITY-MATRIX.md` 신규) |
| 영향 vendor | 9 (Dell / HPE / Lenovo / Supermicro / Cisco / Huawei / Inspur / Fujitsu / Quanta) |
| 함께 바뀔 것 | (M-D2 web 검색 / M-D3 fallback 추가 입력) |
| 리스크 | LOW (read-only) |

## 참고 입력

- `adapters/redfish/*.yml` 27개 adapter (cycle 2026-05-01 +11)
- `redfish-gather/library/redfish_gather.py` (~2627 lines)
- `docs/ai/tickets/2026-05-01-gather-coverage/COMPATIBILITY-MATRIX.md` (이전 cycle 35건 적용)
- 신규 7 generation: dell_idrac10 / hpe_ilo7 / lenovo_xcc3 / supermicro_x12/x13/x14 / cisco_ucs_xseries
- 신규 4 vendor: huawei_ibmc / inspur_isbmc / fujitsu_irmc / quanta_qct_bmc (priority=80, lab 부재)

## 작업 spec — COMPATIBILITY-MATRIX.md (신설)

### Generation 매트릭스 (행: vendor × gen, 열: 9 sections)

| vendor | generation | system | hardware | bmc | cpu | memory | storage | network | firmware | users | power |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Dell | iDRAC 7 | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| Dell | iDRAC 8 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| Dell | iDRAC 9 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| Dell | iDRAC 10 | (cycle 2026-05-01 신규) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| HPE | iLO 4 | ? | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| HPE | iLO 5 | OK | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| HPE | iLO 6 | OK | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| HPE | iLO 7 | (cycle 2026-05-01 신규) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Lenovo | XCC | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Lenovo | XCC v2 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Lenovo | XCC v3 (OpenBMC) | (cycle 2026-05-01 신규 + 1.17.0 reverse regression hotfix) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Supermicro | X9 | (BLOCKED:lab-fixture F15) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Supermicro | X10/X11 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Supermicro | X12 | (cycle 2026-05-01 신규) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Supermicro | X13 | (cycle 2026-05-01 신규) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Supermicro | X14 | (cycle 2026-05-01 신규) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Cisco | CIMC M4 | ? | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Cisco | CIMC M5 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Cisco | CIMC M6/M7/M8 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Cisco | UCS X-Series | (cycle 2026-05-01 신규) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Huawei | iBMC | (lab 0 — web only) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Inspur | iSBMC | (lab 0) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Fujitsu | iRMC | (lab 0) | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Quanta | QCT BMC | (lab 0) | ... | ... | ... | ... | ... | ... | ... | ... | ... |

→ 24 row × 10 col = **240 cell** 호환성 판정.

### 판정 기호

| 기호 | 의미 |
|---|---|
| OK | adapter + 코드 + baseline 모두 확보 |
| OK★ | adapter 있음, baseline 부재 (mock 회귀만) |
| FB | fallback 적용 (cycle 2026-05-01 신규 generation 등) |
| ? | 미확인 — M-D2 web 검색 대상 |
| GAP | 명시적 미지원 — M-D3 fallback 추가 후보 |
| BLOCK | 외부 의존 (lab fixture / 사고 재현) |
| N/A | 해당 vendor/gen 에 해당 section 없음 (예: 일부 BMC 구 펌웨어 PowerSubsystem 없음) |

### Gap 우선 분류

매트릭스 작성 후 Gap (?, GAP) 영역 list → M-D2 web 검색 + M-D3 fallback 추가:

| 우선 | 영역 | M-D2/M-D3 진입 |
|---|---|---|
| P1 | 신규 4 vendor × 10 sections (40 cell) | M-D2 + M-D3 |
| P1 | 5 vendor 의 구 generation (iDRAC 7 / iLO 4 / XCC / Supermicro X9~X11 / CIMC M4) | M-D2 + M-D3 |
| P2 | 5 vendor 의 신 generation (iDRAC 10 / iLO 7 / XCC v3 / X12~X14 / UCS X-Series) | 이미 cycle 2026-05-01 fallback 적용 검증 |
| P3 | BLOCK 영역 (Supermicro X9 등) | lab 도입 시 |

## 회귀 / 검증

- (분석 only)
- 정적 검증: matrix YAML / Markdown 표 정합성

## risk

- (HIGH) 매트릭스 240 cell — 누락 시 M-D3 fallback 추가가 일부 cell 만 다룸. 누락 0 의무
- (MED) 신규 4 vendor 는 lab 0 → web 검색 결과만 입력 (M-D2 의존)
- (LOW) commit history + 기존 baseline 으로 5 vendor 검증 가능

## 완료 조건

- [ ] COMPATIBILITY-MATRIX.md 신설 (24 row × 10 col)
- [ ] 240 cell 모두 기호 (OK / OK★ / FB / ? / GAP / BLOCK / N/A)
- [ ] Gap (?, GAP) 영역 list (M-D2 입력)
- [ ] 우선 분류 (P1/P2/P3)
- [ ] commit: `docs: [M-D1 DONE] 9 vendor × N gen × 10 sections 매트릭스 240 cell`

## 다음 세션 첫 지시 템플릿

```
M-D1 호환성 매트릭스 진입.

읽기 우선순위:
1. fixes/M-D1.md (본 ticket)
2. adapters/redfish/*.yml (27 adapter)
3. docs/ai/tickets/2026-05-01-gather-coverage/COMPATIBILITY-MATRIX.md (이전 35건 입력)
4. schema/sections.yml (10 sections 정의)
5. schema/baseline_v1/ (8 baseline JSON)
6. redfish-gather/library/redfish_gather.py (vendor 분기 영역 — _FALLBACK_VENDOR_MAP)

산출물:
- docs/ai/tickets/2026-05-06-multi-session-compatibility/COMPATIBILITY-MATRIX.md
- 240 cell 판정
- Gap list
```

## 관련

- rule 12 R1 (vendor 경계)
- rule 96 R1+R1-A (외부 계약 + 사이트 fixture / web sources)
- skill: vendor-change-impact, score-adapter-match
- 이전 cycle: docs/ai/tickets/2026-05-01-gather-coverage/COMPATIBILITY-MATRIX.md
