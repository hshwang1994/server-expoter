# M-B3 — 공통계정 회귀 mock fixture 추가

> status: [PENDING] | depends: M-B2 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-B2 매트릭스 검증 결과로 식별된 gap 영역 + 5 vendor 통일 후 동작에 대한 mock fixture 회귀 추가. lab 부재 → mock 만.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/<vendor>/account_service_*.json` (신규), `tests/redfish-probe/` (회귀 추가) |
| 영향 vendor | 5 + 4 = 9 vendor |
| 함께 바뀔 것 | pytest 결과 (108 → 108+N) |
| 리스크 | LOW (회귀만 추가, 코드 변경 없음. M-D3 / M-A3 코드 변경 후 회귀 검증 입력) |
| 진행 확인 | M-B2 [DONE] 후 진입 |

## 작업 spec

### Mock fixture 카테고리

| fixture | vendor | 시나리오 |
|---|---|---|
| account_service_standard.json | 5 vendor 각 (Dell/HPE/Lenovo/Supermicro/Cisco) | 표준 endpoint (`/redfish/v1/AccountService/Accounts`) 응답 |
| account_service_oem_dell.json | Dell | DelliDRACCard OEM 응답 |
| account_service_oem_hpe.json | HPE | Hpe.Privileges OEM 응답 |
| account_service_oem_lenovo.json | Lenovo | OemAccountService OEM 응답 |
| account_service_xcc_v3_openbmc.json | Lenovo XCC v3 | OpenBMC 1.17.0 reverse regression 케이스 (cycle 2026-04-30) |
| account_service_cisco_unified.json | Cisco | F50 phase 통일 후 LoginRole / RemoteRole 응답 |
| account_service_cache_corruption.json | Lenovo | F50 phase4 권한 cache 손상 fix 검증 |
| account_service_verify_fallback.json | 5 vendor 각 | verify-fallback 분기 진입 시나리오 |

### 신규 vendor 4 (lab 부재, web 검색 기반)

| fixture | vendor | 출처 |
|---|---|---|
| account_service_huawei_ibmc.json | Huawei | M-D2 web 검색 → support.huawei.com docs |
| account_service_inspur_isbmc.json | Inspur | M-D2 web 검색 |
| account_service_fujitsu_irmc.json | Fujitsu | M-D2 web 검색 |
| account_service_quanta_qct.json | Quanta | M-D2 web 검색 |

→ 각 fixture 헤더 주석에 `# source: <web URL>` (rule 96 R1-A)

### pytest 회귀 케이스

```python
# tests/redfish-probe/test_account_service.py (신규 또는 기존 확장)

@pytest.mark.parametrize("vendor,fixture", [
    ("dell", "account_service_oem_dell.json"),
    ("hpe", "account_service_oem_hpe.json"),
    ("lenovo", "account_service_oem_lenovo.json"),
    ("lenovo", "account_service_xcc_v3_openbmc.json"),
    ("supermicro", "account_service_standard.json"),
    ("cisco", "account_service_cisco_unified.json"),
    ("huawei", "account_service_huawei_ibmc.json"),
    ("inspur", "account_service_inspur_isbmc.json"),
    ("fujitsu", "account_service_fujitsu_irmc.json"),
    ("quanta", "account_service_quanta_qct.json"),
])
def test_account_service_provision_compat(vendor, fixture):
    ...
```

## 회귀 / 검증

- pytest 108 + N건 PASS
- `python scripts/ai/hooks/adapter_origin_check.py` (rule 96 R1 — fixture 헤더 origin 주석 검증)
- `python scripts/ai/verify_vendor_boundary.py` (rule 12 — fixture 자체에는 vendor 하드코딩 OK, vendor 디렉터리 분리)

## risk

- (MED) 신규 4 vendor mock fixture 가 web 검색 결과만 → 실 BMC 응답과 차이 가능 (차이는 lab 도입 시 갱신)
- (LOW) 5 vendor mock 은 commit history + 기존 baseline 패턴 따라 작성 가능

## 완료 조건

- [ ] mock fixture 16개 생성 (8 + 4 vendor) — 헤더 origin 주석
- [ ] pytest 회귀 N건 추가 (parametrize 활용)
- [ ] pytest 전체 PASS
- [ ] adapter_origin_check / verify_vendor_boundary PASS
- [ ] commit: `test: [M-B3 DONE] account_service mock fixture 16건 + pytest N건`

## 다음 세션 첫 지시 템플릿

```
M-B3 공통계정 mock fixture 진입. M-B2 매트릭스 + gap 결과 입력.

작업:
1. tests/fixtures/redfish/<vendor>/account_service_*.json 16건 생성
2. tests/redfish-probe/test_account_service.py 회귀 추가 (parametrize)
3. pytest PASS + verify_* PASS
4. 신규 4 vendor fixture 는 M-D2 web 검색 결과 origin 주석

선행: M-B2 [DONE], M-D2 (신규 4 vendor 부분만)
후속: 없음 (M-B 영역 종료)
```

## 관련

- rule 21 R2 (Fixture 출처 기록)
- rule 40 R4 (새 펌웨어 deep_probe — lab 도입 시 갱신)
- rule 96 R1-A (lab 부재 → web sources)
- skill: probe-redfish-vendor (lab 도입 시)
