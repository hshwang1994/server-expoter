# M-E1 — HPE Superdome web 검색 (Flex / Flex 280 / 2 / X / Integrity)

> status: [PENDING] | depends: — | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "superdome 하드웨어도 벤더 추가해줘. 추가하고 web 검색 다해서 여기 개더링프로젝트에 추가해줘."

→ HPE Superdome 시리즈 web 검색으로 BMC 정보 + Redfish 지원 + 모델 별 차이 식별. lab 부재 → web sources 만 (rule 96 R1-A).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | (산출물) `docs/ai/tickets/2026-05-06-multi-session-compatibility/fixes/M-E1.md` 의 검색 결과 절 + EXTERNAL_CONTRACTS.md 갱신 |
| 영향 vendor | HPE (기존 vendor — Superdome 은 HPE 의 high-end 라인) — vendor 별도 분류 결정 (M-E2 입력) |
| 함께 바뀔 것 | M-E2 adapter 작성 입력 |
| 리스크 top 3 | (1) Superdome 시리즈가 일반 ProLiant 와 management infrastructure 다름 / (2) 일부 (Integrity Itanium) 은 Redfish 미지원 가능 / (3) Flex 의 RMC (Rack Management Controller) 가 별도 — iLO 와 차이 |
| 진행 확인 | 사용자 명시 (2026-05-06) "벤더 추가해줘" 승인 받음 |

## HPE Superdome 시리즈 정리 (사전 지식)

| 모델 | 출시 | 아키텍처 | management |
|---|---|---|---|
| **HPE Superdome Flex 280** | 2020+ | x86 (Intel Xeon SP) | iLO 5 + Rack Management Controller (RMC) |
| **HPE Superdome Flex** | 2017+ | x86 (Intel Xeon SP) | RMC + iLO 5 (각 컴퓨트 모듈) |
| HPE Superdome 2 | 2010~2017 | Itanium / IA-64 | Onboard Administrator (OA) — Redfish 미지원 가능 |
| HPE Superdome X | 2014~ | x86 (Xeon E7) | iLO 4 + OA |
| HPE Integrity Superdome | ~2010 | Itanium | OA only (legacy) |

→ **본 cycle 대상**: Superdome Flex 280 + Superdome Flex (현행 운영 가능 모델). Superdome 2 / X / Integrity 는 legacy → fallback 또는 N/A 분류.

## 검색 sources (rule 96 R1-A)

### 1. HPE 공식 docs

| URL | 내용 |
|---|---|
| https://support.hpe.com/.../HPE_Superdome_Flex_Family/ | Superdome Flex / Flex 280 manuals |
| https://support.hpe.com/.../iLO_5/ | iLO 5 Redfish API (Superdome Flex 280 의 BMC 표준) |
| https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/ | iLO 5 Redfish reference |
| https://support.hpe.com/.../Superdome_Flex_RMC/ | Rack Management Controller (RMC) docs |
| https://support.hpe.com/.../Onboard_Administrator/ | OA (legacy Superdome 2 / X) |

### 2. DMTF Redfish 표준

- https://redfish.dmtf.org/ — Superdome RMC 가 Redfish 표준 따라가는지
- https://redfish.dmtf.org/profiles/ — HPE profile

### 3. GitHub / Community

- https://github.com/HewlettPackard/python-redfish-utility — HPE Redfish CLI
- https://github.com/HewlettPackard/python-ilorest-library

### 4. 사용자 사이트 실측

- 본 cycle 은 lab 0 → web sources 만

## 검색 spec (산출물)

### (A) Manufacturer string

```
검색: "HPE Superdome Redfish ServiceRoot Manufacturer"
결과: ["HPE", "Hewlett Packard Enterprise"] (일반 ProLiant 와 동일?)
또는: ["HPE Superdome Flex"] (별도 string?)
→ M-E2 vendor_aliases.yml 매핑 결정 입력
```

### (B) Model 식별

| model_pattern | 매칭 BMC |
|---|---|
| `Superdome Flex 280*` | iLO 5 + RMC |
| `Superdome Flex*` | iLO 5 + RMC |
| `Superdome 2*` | OA (Redfish 미지원 가능) |
| `Superdome X*` | iLO 4 + OA |

→ M-E2 adapter `match.model_patterns` 입력

### (C) Redfish endpoint 차이 (vs 일반 ProLiant iLO 5)

- ServiceRoot: 동일 `/redfish/v1/`?
- Systems: `/redfish/v1/Systems/<id>` — Flex 의 multi-partition 시 ID 수?
- Chassis: `/redfish/v1/Chassis/<id>` — RMC 가 chassis aggregation?
- Managers: iLO 5 + RMC 두 manager?
- nPAR (np Partition) 정보 — Superdome Flex 의 partitioning

→ M-E2 adapter `capabilities.endpoints` 입력

### (D) OEM extension

```
검색: "HPE Superdome Flex Oem.Hpe extension Redfish"
결과: 일반 iLO 5 OEM (Hpe.Privileges, Hpe.Power, ...) 외 Superdome 전용?
```

→ M-E2 adapter `normalize.oem_path` 입력

### (E) 펌웨어 호환성

| 펌웨어 | Redfish 지원 |
|---|---|
| iLO 5 2.x ~ 3.x | 표준 Redfish |
| RMC 2.x | (검색 결과로 판정) |
| OA 4.x (Superdome 2/X) | Redfish 부분 지원 / 없음 |

### (F) 신 vendor (별도 분류) vs HPE 의 sub-line 결정

**결정 포인트** (M-E2 입력):

| option | 변경 |
|---|---|
| **(a)** Superdome = HPE sub-line | `adapters/redfish/hpe_superdome*.yml` 신규 (priority=80~90) — vendor=hpe, model_patterns 으로 분기 |
| **(b)** Superdome = 별도 vendor | `vendor_aliases.yml` 신규 entry + `adapters/redfish/superdome*.yml` |

→ **추천**: (a). HPE 의 sub-line 이 자연스럽고 Manufacturer string 도 "HPE" 동일 가능성 높음.

## 회귀 / 검증

- (분석 only)

## risk

- (HIGH) Superdome Flex 의 multi-partition 시 nPAR 정보 — 일반 ProLiant gather 패턴 적용 가능 여부 검증 필요
- (HIGH) RMC 가 별도 BMC — Manager 가 iLO 5 + RMC 두개? 어떻게 정규화할지 (M-E2 adapter spec)
- (MED) Superdome 2 / X / Integrity 는 legacy → fallback 적용 또는 N/A 분류 (사용자 결정)
- (LOW) Manufacturer string 표준 따라가면 (a) 결정 자동

## 완료 조건

- [ ] (A) Manufacturer string 검색 결과
- [ ] (B) 모델 매트릭스 (Flex 280 / Flex / 2 / X / Integrity) + BMC 매핑
- [ ] (C) Redfish endpoint 차이 (vs 일반 iLO 5)
- [ ] (D) OEM extension 식별
- [ ] (E) 펌웨어 호환성
- [ ] (F) 결정 (a) HPE sub-line / (b) 별도 vendor — 사용자 답변 또는 AI 추천 + 사용자 승인
- [ ] sources URL list (rule 96 R1-A)
- [ ] EXTERNAL_CONTRACTS.md 갱신 (HPE Superdome entry)
- [ ] M-E2 adapter spec 도출 (match / capabilities / collect / normalize 4 필드)
- [ ] commit: `docs: [M-E1 DONE] HPE Superdome web 검색 + adapter spec 도출`

## 다음 세션 첫 지시 템플릿

```
M-E1 HPE Superdome web 검색 진입.

읽기 우선순위:
1. fixes/M-E1.md (본 ticket)
2. adapters/redfish/hpe_*.yml (5 generation 기존 패턴)
3. rule 50 R2 (vendor 추가 9단계)
4. rule 96 R1-A (web sources 4종)

도구:
- WebSearch / WebFetch
- agent: web-evidence-collector (model: opus)
- skill: web-evidence-fetch

산출물:
- (A) Manufacturer / (B) 모델 매트릭스 / (C) endpoint / (D) OEM / (E) 펌웨어
- (F) 결정 (a/b)
- sources URL list
- M-E2 adapter spec
```

## 관련

- rule 50 R2 (vendor 추가 9단계)
- rule 96 R1-A (web sources)
- agent: web-evidence-collector
- skill: web-evidence-fetch, add-new-vendor
