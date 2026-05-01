---
name: web-evidence-fetch
description: lab 부재 vendor / 펌웨어 / 외부 계약 정보를 web 검색 (vendor docs / DMTF / GitHub) 으로 수집해 ticket / adapter origin 주석에 흡수. cycle 2026-05-01 학습 — lab 한계 보완. 사용자가 "Huawei iBMC docs 찾아줘", "DMTF PowerSubsystem 변천 확인", "vendor docs 자동 수집" 요청 시.
---

# web-evidence-fetch

## 목적

server-exporter lab 이 부재한 vendor / 펌웨어 / 외부 계약 영역에 대해 web 검색으로 sources 수집 → adapter origin 주석 / ticket coverage / EXTERNAL_CONTRACTS.md 갱신. cycle 2026-05-01 학습 — lab 한계가 본질적 제약이므로 web 검색이 fixture 대체.

## 호출 시점

- 신규 vendor 추가 검토 (Huawei / Inspur / NEC)
- 펌웨어 업그레이드 후 신 endpoint 응답 발견
- DMTF Redfish 표준 변천 추적 (예: Power → PowerSubsystem 2020.4)
- adapter origin 주석 부재 → 주석 보강

## 입력

- 검색 주제 (vendor / 펌웨어 / endpoint / DMTF spec)
- 우선 sources 영역:
  - vendor 공식: developer.dell.com / pubs.lenovo.com / support.hpe.com / cisco.com / supermicro.com / support.huawei.com
  - DMTF: redfish.dmtf.org / DSP-NNNN
  - GitHub: vendor 공식 repo / community issue

## 도구 우선순위

1. **WebSearch** — 일반 검색 (vendor + 펌웨어 + endpoint 키워드)
2. **WebFetch** — 특정 vendor docs URL 직접 (PDF / API guide)
3. **Context7 (mcp__context7)** — 표준 라이브러리 docs (선택)

## 출력 형식

```markdown
## web evidence — <주제>

### 검색 일시
YYYY-MM-DD

### sources
1. **<공식/DMTF/GitHub>** — `<URL>`
   - 핵심 인용: "<요약>"
   - 신뢰도: 공식 (vendor) / 표준 (DMTF) / community
2. ...

### server-exporter 적용
- adapter / library 위치
- origin 주석 후보 (rule 96 R1-A 포맷)
- evidence 첨부 위치 (tests/evidence/ 또는 EXTERNAL_CONTRACTS.md)
```

## 절차

### 1. 검색 키워드 구성

| 주제 | 검색 키워드 예 |
|---|---|
| vendor 펌웨어 | "Dell iDRAC9 6.10 Redfish API release notes" |
| endpoint 변천 | "DMTF Redfish PowerSubsystem 2020.4 schema" |
| 응답 차이 | "HPE iLO 5 vs iLO 6 Power endpoint difference" |
| 신 vendor | "Huawei iBMC Redfish API specification" |

### 2. WebSearch 1차 — 광범위 후보

- 결과 5~10개 중 공식 / DMTF 우선
- community / blog 는 보조 reference

### 3. WebFetch 2차 — 구체 docs

- 공식 URL 직접 fetch
- PDF / HTML 모두 가능
- 핵심 인용 추출 (rule 96 R1-A "마지막 동기화 확인" 일자 명시)

### 4. ticket / adapter 흡수

- ticket coverage/{section}.md 의 sources 절에 URL 추가
- 신규 adapter 추가 시 origin 주석 작성:
  ```yaml
  # source: https://developer.dell.com/.../iDRAC9_6.10_Redfish.pdf (확인 2026-05-01)
  # source: https://redfish.dmtf.org/schemas/v1/Power.v1_8_0.json
  # tested_against: ["iDRAC9 6.10.x"]
  # lab: 부재 — web sources 의존
  ```

### 5. EXTERNAL_CONTRACTS.md 갱신 (있으면)

- vendor / 펌웨어 / endpoint / 변경일 / sources 표 추가

### 6. ticket 추적

- web evidence 가 영향을 준 fix ID 등재 (F##)
- 후속 round 에서 사용자 사이트 실측 우선 (rule 25 R7-A-1) 으로 재검증

## 신뢰도 분류

| sources | 신뢰도 | 사용 |
|---|---|---|
| vendor 공식 docs (.com/.pdf) | 높음 | adapter 직접 적용 |
| DMTF Redfish spec | 높음 | endpoint path / schema |
| GitHub vendor 공식 repo | 중 | 보조 reference |
| community blog / Stack Overflow | 낮음 | 단서만 — 공식 docs 교차 |
| 사용자 사이트 실측 | 최우선 | spec 우선 (rule 25 R7-A-1) |

## 자율 vs 사용자 결정

- **AI 자율**: web 검색 → ticket 갱신 → adapter origin 주석 추가
- **사용자 결정**: 신 vendor 추가 commit / schema 변경 / lab 환경 추가 의뢰

## 학습 (cycle 2026-05-01)

- "lab 한계 → web 검색이 fixture 대체" — 사용자 인정
- web sources 0건 fix 는 다음 작업자 검증 불가 (rule 96 R1-A 의무)
- 공식 vs community sources 신뢰도 분리 명시

## 관련

- rule 96 R1-A (web sources 의무)
- rule 25 R7-A-1 (사용자 실측 > spec)
- agent: web-evidence-collector (자동 수집 위임)
- skill: capture-site-fixture (사이트 실측 우선)
- catalog: docs/ai/catalogs/EXTERNAL_CONTRACTS.md (있으면)
