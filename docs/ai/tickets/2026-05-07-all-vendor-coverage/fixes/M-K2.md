# M-K2 — docs/ai/catalogs/EXTERNAL_CONTRACTS.md 갱신 (9 vendor × N gen × N section × source)

> status: [PENDING] | depends: M-K1 | priority: P1 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "9 vendor × N generation × N section 매트릭스 × source URL — EXTERNAL_CONTRACTS.md 갱신 (rule 96 R4)." (cycle 진입)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` (대폭 갱신 또는 신설) |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | M-L1 NEXT_ACTIONS 입력 (lab 부재 영역) |
| 리스크 top 3 | (1) 카탈로그 비대화 (9 vendor × N generation × 10 sections 매트릭스 큼) / (2) source URL stale / (3) cycle 종료 후 정기 갱신 의무 |
| 진행 확인 | M-K1 후 진입 |

---

## 매트릭스 구조

`docs/ai/catalogs/EXTERNAL_CONTRACTS.md` 신규 또는 기존 갱신:

```markdown
# EXTERNAL_CONTRACTS — 외부 시스템 계약 매트릭스

> rule 96 R1+R1-A 정본 카탈로그 — 9 vendor × N generation × N section × source URL.
> cycle 2026-05-07 all-vendor-coverage 갱신 (M-K2).

## 사이트 검증 4 vendor × 1 generation (cycle 2026-05-07 PASS)

| vendor | generation | 사이트 BMC | 검증 commit | source URL |
|---|---|---|---|---|
| Dell | iDRAC10 | 5대 | `0a485823` | https://developer.dell.com/apis/2978/versions/4/docs/ |
| HPE | iLO7 | 1대 | `0a485823` | https://hewlettpackard.github.io/ilo-rest-api-docs/ilo7/ |
| Lenovo | XCC3 | 1대 | `0a485823` | https://lenovopress.lenovo.com/.../xcc3-redfish |
| Cisco | UCS X-series | 1대 | `0a485823` | https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/x/ |

## 9 vendor × N generation 매트릭스

### Dell iDRAC

| generation | 펌웨어 매트릭스 | source URL | DSP0268 | lab |
|---|---|---|---|---|
| iDRAC7 (legacy) | 1.30+ ~ 2.x | https://developer.dell.com/apis/2978/versions/1/docs/ | v1.0 | 부재 |
| iDRAC8 | 2.30+ ~ 4.x | https://developer.dell.com/apis/2978/versions/2/docs/ | v1.4+ | 부재 |
| iDRAC9 | 3.x ~ 7.x | https://developer.dell.com/apis/2978/versions/3/docs/ | v1.6+ ~ v1.13+ | 부재 |
| iDRAC10 | 6.x+ | https://developer.dell.com/apis/2978/versions/4/docs/ | v1.13+ | **PASS** |

### HPE iLO

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| iLO (legacy 1/2/3) | — | HPE archive | 미지원 | 부재 |
| iLO4 | 2.50+ | https://hewlettpackard.github.io/ilo-rest-api-docs/ilo4/ | v1.0+ | 부재 |
| iLO5 | 1.40+ | https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/ | v1.4+ | 부재 |
| iLO6 | 1.20+ | https://hewlettpackard.github.io/ilo-rest-api-docs/ilo6/ | v1.10+ | 부재 |
| iLO7 | 1.00+ | (사이트 검증 commit `0a485823`) | v1.13+ | **PASS** |
| Superdome Flex | Gen 1/2 + 280 | https://support.hpe.com/hpesc/public/docDisplay?docId=... | v1.6+ | 부재 |

### Lenovo BMC/IMM/XCC

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| BMC (IBM 시기) | — | IBM xSeries archive | 미지원 | 부재 |
| IMM (legacy) | — | IBM IMM archive | 미지원 또는 v1.0 부분 | 부재 |
| IMM2 | 2.50+ | https://lenovopress.lenovo.com/.../imm2-redfish | v1.0+ | 부재 |
| XCC | 1.x ~ 2.x | https://lenovopress.lenovo.com/.../xcc-redfish | v1.4+ | 부재 |
| XCC2 | 1.x ~ 2.x | https://lenovopress.lenovo.com/.../xcc2-redfish | v1.10+ | 부재 |
| XCC3 | 1.17+ | (사이트 검증 commit `0a485823`) | v1.13+ | **PASS** |

### Cisco UCS / CIMC

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| BMC (legacy) | — | UCS C-series archive | 미지원 | 부재 |
| CIMC C-series | 1.x ~ 4.x | https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/ | v1.0+ ~ v1.10+ | 부재 |
| UCS S-series | CIMC 와 유사 | (Cisco docs) | v1.0+ | 부재 |
| UCS B-series | UCS Manager 매개 | (Cisco docs) | (별도 cycle) | 부재 |
| UCS X-series | (사이트 검증) | https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/x/ | v1.13+ | **PASS** |

### Supermicro BMC

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| BMC (legacy) | — | https://www.supermicro.com/manuals/superserver/IPMI/ | v1.0+ | 부재 |
| X9 | 1.x ~ 3.x | https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X9.pdf | v1.0 | 부재 |
| X10 | 1.x ~ 3.x | https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X10.pdf | v1.0+ | 부재 |
| X11 | 1.x ~ 3.x | https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X11.pdf | v1.4+ | 부재 |
| X12 | 1.x+ | https://www.supermicro.com/manuals/superserver/IPMI/X12_BMC_RedfishRefGuide.pdf | v1.6+ | 부재 |
| X13 | 1.x+ | https://www.supermicro.com/manuals/superserver/X13/X13_BMC_RedfishRefGuide.pdf | v1.8+ | 부재 |
| X14 | 1.x+ | https://www.supermicro.com/manuals/superserver/X14/ (확인 필요) | v1.10+ | 부재 |
| H11~H14 (AMD) | (X 동세대 동일) | (위 동일) | (위 동일) | 부재 |
| ARS (ARM) | — | https://www.supermicro.com/manuals/superserver/ARS/ | v1.10+ | 부재 |

### Huawei iBMC

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| iBMC | 1.x ~ 5.x | https://support.huawei.com/.../iBMC_Redfish_API_v*.pdf | v1.0+ ~ v1.13+ | 부재 |

### Inspur ISBMC

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| ISBMC | (NF/NP/SA series) | Inspur 공식 + GitHub community | v1.0+ | 부재 |

### Fujitsu iRMC

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| iRMC S2 | — | https://support.ts.fujitsu.com/IndexDownload.asp | 미지원 또는 v1.0 부분 | 부재 |
| iRMC S4 | 9.x+ | (위 동일) | v1.0+ | 부재 |
| iRMC S5 | 1.x+ | (위 동일) | v1.6+ | 부재 |
| iRMC S6 | 1.x+ | (위 동일) | v1.10+ | 부재 |

### Quanta QCT

| generation | 펌웨어 | source | DSP0268 | lab |
|---|---|---|---|---|
| QCT BMC | (S/D/T/J series) | Quanta QCT 공식 + GitHub | v1.0+ | 부재 |

## DMTF Redfish 표준 reference

| 영역 | spec |
|---|---|
| Data Model | DSP0268 (v1.0 ~ v1.13+) |
| Resource & Schema Guide | DSP2046 |
| Schema Bundle | DSP8010 |
| AccountService | https://redfish.dmtf.org/schemas/v1/AccountService.json |
| PowerSubsystem | https://redfish.dmtf.org/schemas/v1/PowerSubsystem.json (v1.13+) |
| Storage | https://redfish.dmtf.org/schemas/v1/Storage.json |

## 갱신 정책 (rule 96 R5)

- 펌웨어 업그레이드 / 신규 vendor 도입 시 본 매트릭스 갱신 의무 (cycle 단위)
- 6개월 주기 origin URL dead link 검증
- DRIFT 발견 시 (origin 주석 ↔ 실 응답 차이) FAILURE_PATTERNS.md + CONVENTION_DRIFT.md 동반 기록
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` 본문 위 매트릭스 모두 작성
- [ ] 9 vendor × N generation 모두 등재 (총 약 30+ row)
- [ ] DMTF spec reference 6 영역 명시
- [ ] 갱신 정책 절 명시

### 의미 검증

- [ ] 사이트 검증 4 vendor — "**PASS**" 표시
- [ ] lab 부재 25+ row — "부재" 표시
- [ ] 모든 row 에 source URL 또는 archive 명시 (rule 96 R1-A)
- [ ] cycle 2026-05-01 / 2026-05-06 / 2026-05-07 변경 기록

---

## risk

- (LOW) 매트릭스 비대화 — 9 vendor × N generation = 30+ row. 대용량 카탈로그가 catalog stale 가속 가능. 6개월 주기 갱신 정책 명시
- (LOW) source URL dead link — 검증 시 발견 시 후속 cycle

## 완료 조건

- [ ] docs/ai/catalogs/EXTERNAL_CONTRACTS.md 본문 갱신 (위 매트릭스 + DMTF + 갱신 정책)
- [ ] 9 vendor 모두 등재
- [ ] 사이트 검증 4 vendor "PASS" 표시
- [ ] commit: `docs: [M-K2 DONE] EXTERNAL_CONTRACTS.md 갱신 — 9 vendor × N gen × source URL 매트릭스`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-L1 (NEXT_ACTIONS 갱신).

## 관련

- M-K1 (origin 주석 일관성)
- rule 96 R1+R1-A+R1-C+R4+R5 (외부 계약 매트릭스 정본)
- 정본: 9 vendor × N gen 매트릭스 — 본 cycle 산출 baseline

## 분석 / 구현

(cycle 2026-05-11 Phase 7 추가 stub — 본 ticket 의 분석 / 구현 내용은 본문 다른 절 (## 컨텍스트 / ## 현재 동작 / ## 변경 / ## 구현 등) 참조. cycle DONE 시점에 cold-start 6 절 정본 도입 전 작성된 ticket.)
