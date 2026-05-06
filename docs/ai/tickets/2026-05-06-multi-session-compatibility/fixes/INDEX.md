# Fixes INDEX — 2026-05-06 Multi-Session Compatibility

> 24 ticket 분류 + 진행 상태 추적. worker 세션은 본 INDEX 보고 [PENDING] + 의존 통과 ticket 선택.

---

## 진행 상태

| ticket | 영역 | 우선 | 의존 | status | worker | commit |
|---|---|---|---|---|---|---|
| **M-A1** | status 로직 분석 (read-only) | P1 | — | [DONE] | Session-1 | `ba003b2f` |
| **M-A2** | status 의도 결정 (사용자) | P1 | M-A1 | [PENDING] | — | — |
| **M-A3** | status 코드 변경 + 회귀 | P1 | M-A2 | [PENDING] | — | — |
| **M-A4** | status ADR (rule 70 R8 trigger 시) | P2 | M-A3 | [PENDING] | — | — |
| **M-B1** | account_provision flow 분석 | P1 | — | [PENDING] | — | — |
| **M-B2** | F49/F50 5 vendor 매트릭스 검증 | P1 | M-B1 | [PENDING] | — | — |
| **M-B3** | 공통계정 회귀 mock fixture | P1 | M-B2 | [PENDING] | — | — |
| **M-C1** | vault 동적 로딩 분석 | P1 | — | [PENDING] | — | — |
| **M-C2** | cache invalidation 메커니즘 | P1 | M-C1 | [PENDING] | — | — |
| **M-C3** | vault 자동 반영 회귀 mock | P1 | M-C2 | [PENDING] | — | — |
| **M-D1** | 9 vendor × N gen × 9 sections 매트릭스 | P1 | — | [PENDING] | — | — |
| **M-D2** | web 검색 gap 영역 (DMTF / vendor docs) | P1 | M-D1 | [PENDING] | — | — |
| **M-D3** | fallback 코드 추가 (additive only) | P1 | M-D2 | [PENDING] | — | — |
| **M-D4** | 전 vendor 호환성 회귀 | P1 | M-D3 | [PENDING] | — | — |
| **M-E1** | Superdome web 검색 (Flex / Flex 280 / 2 / X / Integrity) | P1 | — | [PENDING] | — | — |
| **M-E2** | Superdome adapter (priority=80, lab 부재) | P1 | M-E1 | [PENDING] | — | — |
| **M-E3** | ai-context vendors/superdome.md | P2 | M-E1 | [PENDING] | — | — |
| **M-E4** | vendor-boundary-map.yaml 갱신 | P2 | M-E2 | [PENDING] | — | — |
| **M-E5** | README / docs 갱신 | P2 | M-E2 | [PENDING] | — | — |
| **M-E6** | Superdome pytest 회귀 mock | P1 | M-E5 | [PENDING] | — | — |
| **M-F1** | docs/20_json-schema-fields.md 신설 | P2 | — | [PENDING] | — | — |
| **M-F2** | 3채널 (Redfish/OS/ESXi) JSON 키 비교 | P2 | M-F1 | [PENDING] | — | — |
| **M-G1** | 본 cycle 학습 추출 | P3 | A~F all | [PENDING] | — | — |
| **M-G2** | rule/skill/agent 후보 정리 | P3 | M-G1 | [PENDING] | — | — |

총 **24 ticket**.

---

## 우선 분류

- **P1 (cycle 본 영역, 14건)**: M-A1~A3, M-B1~B3, M-C1~C3, M-D1~D4, M-E1~E2, M-E6
- **P2 (보강, 7건)**: M-A4, M-E3~E5, M-F1~F2
- **P3 (cycle 종료 학습, 2건)**: M-G1~G2

---

## 영역별 묶음

### A: status 로직 검증 (사용자 의심 영역)
사용자 명시: "errors 에는 로그가 찍히는데 success로 빠지는경우가 있음 이것은 왜이런지 확인해줘 의도된건지"
- M-A1 분석 → M-A2 사용자 결정 → M-A3 코드 변경 → M-A4 ADR

### B: Redfish 공통계정 (account_provision)
사용자 명시: "redfish 공통계정 생성 및 그것을 이용한 개더링부터 검증해봐"
- F49 (account_provision 호환성) + F50 phase1~4 (5 vendor 권한 cache 통일) 검증
- M-B1 분석 → M-B2 5 vendor 매트릭스 → M-B3 회귀

### C: Vault 자동 반영
사용자 명시: "redfish 공통계정의 패스워드가 vault 가 변경됐다면 자동으로 변경되는지 확인"
- M-C1 분석 → M-C2 cache invalidation → M-C3 회귀

### D: 모든 vendor 호환성
사용자 명시: "모든 밴더 모든 세대 모든 장비에도 지원해야해"
- M-D1 매트릭스 (9 vendor × N gen × 9 sections) → M-D2 gap 식별 → M-D3 fallback 추가 → M-D4 회귀

### E: HPE Superdome 추가
사용자 명시: "superdome 하드웨어도 벤더 추가해줘. 추가하고 web 검색 다해서"
- M-E1 web 검색 → M-E2 adapter → M-E3 ai-context → M-E4 boundary-map → M-E5 docs → M-E6 회귀

### F: JSON 스키마 의미 문서
사용자 명시: "redfish, os, esxi에 대해서 json스키마 키값이 무엇을 의미하는지 모르겠어"
- M-F1 docs/20 신설 → M-F2 3채널 비교

### G: 하네스 학습
사용자 명시: "지금까지 작업한내용중에 추가 하네스에 학습시켜야하는것들이있으면"
- M-G1 학습 추출 → M-G2 rule/skill/agent 후보

---

## status 의미

| status | 의미 |
|---|---|
| [PENDING] | 의존 통과 → worker 진입 가능 |
| [BLOCKED:dep] | 의존 ticket 미완료 |
| [IN-PROGRESS] | worker 진행 중 |
| [DONE] | 완료 + commit |
| [BLOCKED:user] | 사용자 결정 대기 |
| [BLOCKED:lab] | lab 검증 대기 (cycle 종료까지) |

---

## worker 진입 절차

1. 본 INDEX 읽고 [PENDING] + 의존 통과 ticket 선택
2. 해당 ticket M-X##.md 읽기
3. status 갱신: [PENDING] → [IN-PROGRESS], worker 컬럼 채움
4. 작업 진행
5. 완료 시: status 갱신 [IN-PROGRESS] → [DONE], commit sha 기록
6. SESSION-HANDOFF.md 갱신
7. commit + push (rule 93 R1+R4)

---

## 관련

- ../INDEX.md
- ../SESSION-HANDOFF.md
- ../DEPENDENCIES.md
