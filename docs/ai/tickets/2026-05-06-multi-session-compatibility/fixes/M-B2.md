# M-B2 — F49/F50 5 vendor 매트릭스 정적 검증

> status: [PENDING] | depends: M-B1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "redfish 공통계정 생성 및 그것을 이용한 개더링부터 검증해봐."
> "지금 추가한 코드 및 현재돼있는 코드가 지금 프로젝트에 지원하는 모든 밴더 모든 세대 모든 장비에도 지원해야해."

→ F49 + F50 phase1~4 코드가 5 vendor + 신규 4 vendor 모두 지원하는지 정적 검증 (lab 부재).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (account_service_provision 영역, ~2157~2400 추정) |
| 영향 vendor | 5 + 4 = 9 vendor |
| 함께 바뀔 것 | (gap 발견 시) 코드 변경 → M-D3 와 연계 가능 |
| 리스크 top 3 | (1) lab 부재 → 정적 분석 한계 / (2) 신규 vendor 4 (Huawei~Quanta) lab 0 → web 검색 의존 / (3) 일부 BMC 펌웨어 (XCC v3 OpenBMC, iDRAC 10) 정적 분석으로 검증 한계 |
| 진행 확인 | M-B1 매트릭스 입력 |

## 검증 매트릭스 (M-B1 산출물 기반)

### 9 vendor × N generation × account_service 단계

| vendor | generation | endpoint 표준 | OEM 분기 | F50 verify-fallback | 정적 검증 결과 |
|---|---|---|---|---|---|
| Dell | iDRAC 7 | (M-B1 분석) | DelliDRACCard (F50 phase3) | (M-B1 확인) | ___ |
| Dell | iDRAC 8 | (M-B1 분석) | 동일 | 동일 | ___ |
| Dell | iDRAC 9 | (M-B1 분석) | 동일 | 동일 | ___ |
| Dell | iDRAC 10 | (M-B1 분석) | 동일 | 동일 | ___ |
| HPE | iLO 4 | 표준 | (있음) | 동일 | ___ |
| HPE | iLO 5 | 표준 | (있음) | 동일 | ___ |
| HPE | iLO 6 | 표준 | (있음) | 동일 | ___ |
| HPE | iLO 7 | 표준 | (있음) | 동일 | ___ |
| Lenovo | XCC | 표준 | OemAccountService | 동일 | ___ |
| Lenovo | XCC v2 | 표준 | 동일 | 동일 | ___ |
| Lenovo | XCC v3 (OpenBMC) | 표준 | 동일 (1.17.0 펌웨어 reverse regression — F50 phase4) | 동일 | ___ |
| Supermicro | X9~X14 | 표준 | (없음 / AMI MegaRAC) | 동일 | ___ |
| Cisco | CIMC M4~M8 | F50 phase1 (LoginRole/RemoteRole) | F50 phase 통일 | 동일 | ___ |
| Cisco | UCS X-Series | F50 phase 통일 | 동일 | 동일 | ___ |
| Huawei | iBMC | (M-D2 web 검색 — Huawei docs) | (M-D2 web) | (M-D2 web) | **lab 0** |
| Inspur | iSBMC | (M-D2 web) | (M-D2 web) | (M-D2 web) | **lab 0** |
| Fujitsu | iRMC | (M-D2 web) | (M-D2 web) | (M-D2 web) | **lab 0** |
| Quanta | QCT BMC | (M-D2 web) | (M-D2 web) | (M-D2 web) | **lab 0** |

### Gap 검출 4 카테고리

| Gap 종류 | 처리 |
|---|---|
| (1) endpoint 표준 미지원 BMC (예: Cisco M4 이전) | M-D3 fallback 추가 |
| (2) OEM 분기 누락 (예: Huawei iBMC ManagerAccount) | M-D2 web 검색 → M-D3 |
| (3) 권한 cache 동작 불일치 (Lenovo XCC v3 OpenBMC 같은) | F50 phase4 모범 따라 추가 fallback |
| (4) verify-fallback 누락 (vendor-specific 인증 캐시 깨짐) | M-D3 vendor 별 추가 |

## 회귀 / 검증

- pytest 회귀: `pytest tests/redfish-probe/ -v` (mock fixture)
- mock fixture 추가 (gap 발견 시): `tests/fixtures/redfish/<vendor>/account_service_*.json`
- 정적 검증:
  - `python -m ast redfish-gather/library/redfish_gather.py`
  - `python scripts/ai/verify_vendor_boundary.py` (rule 12)
  - `python scripts/ai/hooks/adapter_origin_check.py` (rule 96 R1)

## risk

- (HIGH) 신규 4 vendor (Huawei~Quanta) lab 0 → 정적 분석 한계. web 검색 origin 주석 의무 (rule 96 R1-A)
- (MED) Lenovo XCC v3 OpenBMC 1.17.0 reverse regression (cycle 2026-04-30) — 사이트 fixture 부재 시 회귀 못 막음
- (LOW) 5 vendor 기존 generation (iDRAC 8/9, iLO 5/6, XCC v2 등) 은 commit history + baseline 있어 검증 가능

## 완료 조건

- [ ] 매트릭스 17 row 모두 채움 (정적 분석 / web 검색 결과)
- [ ] Gap 4 카테고리 별 list (M-D3 입력)
- [ ] 정적 검증 PASS
- [ ] commit: `docs: [M-B2 DONE] account_service 9 vendor 매트릭스 + gap N건`

## 다음 세션 첫 지시 템플릿

```
M-B2 5 vendor 매트릭스 검증 진입. M-B1 분석 결과 입력.

작업:
1. M-B1.md 의 매트릭스 (B) 보고 빈칸 채움
2. 신규 4 vendor 는 M-D2 web 검색 결과 입력 시까지 lab 0 명시
3. Gap 4 카테고리 별 M-D3 ticket 후보 list

선행 ticket: M-B1 [DONE]
후속 ticket: M-B3 (회귀) + M-D3 (gap fallback)
```

## 관련

- rule 12 R1 (vendor 경계)
- rule 96 R1+R1-A (외부 계약 origin + lab 부재 web sources)
- skill: vendor-change-impact, score-adapter-match
