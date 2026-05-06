# M-D2 — Web 검색 gap 영역 (DMTF / vendor docs)

> status: [PENDING] | depends: M-D1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-D1 매트릭스의 Gap (?, GAP) 영역에 대해 web 검색으로 호환성 정보 수집. lab 부재 영역 보완 (rule 96 R1-A).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | (산출물) `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` 갱신 + COMPATIBILITY-MATRIX.md 의 Gap cell 채움 |
| 영향 vendor | 9 vendor (Gap 영역만) |
| 함께 바뀔 것 | M-D3 fallback 추가 입력 |
| 리스크 | MED (web 검색 정보의 정확성 — origin 주석 의무) |
| 진행 확인 | M-D1 [DONE] Gap list 입력 |

## 검색 sources (rule 96 R1-A)

### 1. vendor 공식 docs

| vendor | docs URL |
|---|---|
| Dell | https://developer.dell.com/apis/2978/versions/12.x/ — iDRAC Redfish |
| HPE | https://hewlettpackard.github.io/ilo-rest-api-docs/ — iLO Redfish |
| Lenovo | https://pubs.lenovo.com/xcc-redfish/ |
| Supermicro | https://www.supermicro.com/manuals/other/RedfishRefGuide.pdf |
| Cisco | https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/redfish/ |
| Huawei | https://support.huawei.com/.../iBMC_Redfish_API.pdf |
| Inspur | https://www.inspur.com/.../BMC_Redfish_Reference.pdf |
| Fujitsu | https://manuals.ts.fujitsu.com/.../iRMC_S5_Redfish_Reference.pdf |
| Quanta | https://www.qct.io/.../QCT_BMC_Redfish.pdf |

### 2. DMTF Redfish 표준

- https://redfish.dmtf.org/schemas/v1/ — 모든 schema
- https://redfish.dmtf.org/profiles/ — vendor profile
- DSP-NNNN spec PDF (PowerSubsystem / NetworkAdapters / Storage / Volumes / 등)

### 3. GitHub issue / community

- https://github.com/DMTF/Redfish-Service-Validator/issues
- https://github.com/openbmc/openbmc/issues
- vendor 공식 GitHub (예: https://github.com/Lenovo/lenovo-redfish-tool)

### 4. 사용자 사이트 실측 (rule 25 R7-A-1)

- 본 cycle 은 lab 없음 → 4 sources 중 1~3 만 사용
- 향후 사이트 fixture 캡처 시 우선 (capture-site-fixture skill)

## 검색 spec

### 영역별 검색 query

M-D1 Gap list 의 각 (vendor, generation, section) 조합에 대해:

```
1. Standard endpoint 검증
   query: "<vendor> <bmc> Redfish <section> support"
   예: "HPE iLO 4 Redfish PowerSubsystem support"

2. OEM extension 식별
   query: "<vendor> <bmc> Oem <section>"
   예: "Dell iDRAC Oem DellPowerSupply"

3. 펌웨어 / 모델 특이사항
   query: "<vendor> <bmc> <firmware version> Redfish <issue>"
   예: "Lenovo XCC 1.17.0 Accept header reject"

4. DMTF deprecation / variation
   query: "DMTF Redfish <section> deprecated since 2020"
   예: "DMTF Redfish Power.PowerControl deprecated PowerSubsystem"
```

### 출력 형식 (각 Gap cell 채움)

```yaml
# COMPATIBILITY-MATRIX.md 의 cell 채울 형식

cell: huawei.ibmc.power
status: FB  # OK / OK★ / FB / GAP / BLOCK / N/A
sources:
  - "https://support.huawei.com/.../iBMC_Redfish_v1.30.pdf (확인 2026-05-06): /redfish/v1/Chassis/<id>/Power 표준"
  - "DMTF Power.v1_8_0 (2020.4): PowerSubsystem 신 schema — iBMC 1.30+ 지원"
fallback_needed: yes
fallback_target: "Chassis/{id}/PowerSubsystem → fallback Chassis/{id}/Power"
notes: "iBMC 1.20 이전 펌웨어는 PowerSubsystem 미지원 → fallback 필수"
```

### EXTERNAL_CONTRACTS.md 갱신

매 검색 결과 → `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` append:

```markdown
## <vendor> <bmc> <generation>

### <section> endpoint
- 표준: `/redfish/v1/...`
- 펌웨어 별 차이: ...
- DMTF schema 버전: ...
- source: ...
- 마지막 확인: 2026-05-06
```

## 회귀 / 검증

- (검색 결과 정확성)
- `python scripts/ai/hooks/adapter_origin_check.py` (rule 96 R1 — origin 주석 검증)

## risk

- (HIGH) web 검색 결과 ≠ 실 BMC 응답 (rule 25 R7-A-1) — 사용자 사이트 도입 시 fixture 갱신 의무
- (MED) DMTF spec 변경 / vendor docs deprecated link
- (LOW) sources 1~3 보유로 lab 부재 보완 가능

## 완료 조건

- [ ] M-D1 Gap list 모든 cell 검색 완료 (예상 ~50~80 cell)
- [ ] 각 cell sources 1+ 명시 (rule 96 R1-A)
- [ ] EXTERNAL_CONTRACTS.md 갱신
- [ ] COMPATIBILITY-MATRIX.md 의 ? / GAP → FB / OK★ 변환
- [ ] M-D3 fallback 후보 list 도출 (어느 endpoint 에 어떤 fallback)
- [ ] commit: `docs: [M-D2 DONE] web 검색 N건 + EXTERNAL_CONTRACTS 갱신`

## 다음 세션 첫 지시 템플릿

```
M-D2 web 검색 gap 진입.

읽기 우선순위:
1. fixes/M-D2.md
2. M-D1 산출물 (COMPATIBILITY-MATRIX.md Gap list)
3. docs/ai/catalogs/EXTERNAL_CONTRACTS.md (기존)
4. rule 96 R1-A web sources 4종

도구:
- WebSearch / WebFetch (deferred — ToolSearch 로 schema 로드 후 사용)
- agent: web-evidence-collector (delegate 가능, model: opus)
- skill: web-evidence-fetch

작업:
1. M-D1 Gap list 의 각 cell 검색
2. sources 1+ 명시
3. EXTERNAL_CONTRACTS.md / COMPATIBILITY-MATRIX.md 갱신
4. M-D3 fallback 후보 list

선행: M-D1 [DONE]
후속: M-D3 (fallback 추가)
```

## 관련

- rule 96 R1-A (lab 부재 → 4 sources 의무)
- agent: web-evidence-collector (model: opus)
- skill: web-evidence-fetch
- catalog: docs/ai/catalogs/EXTERNAL_CONTRACTS.md
