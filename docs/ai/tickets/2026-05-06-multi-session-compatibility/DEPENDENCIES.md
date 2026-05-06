# Dependencies — 2026-05-06 Multi-Session Compatibility

> ticket 간 의존성 + worker 세션 진입 가능 여부 판정.

---

## 의존성 그래프

```
M-A1 (status 분석)              ── M-A2 (의도 결정) ── M-A3 (코드 변경) ── M-A4 (ADR)
                                          ↓
                                   사용자 결정 필요

M-B1 (공통계정 분석)            ── M-B2 (F49/F50 검증) ── M-B3 (회귀)

M-C1 (vault 로딩 분석)          ── M-C2 (cache invalidation) ── M-C3 (회귀)

M-D1 (호환성 매트릭스)         ── M-D2 (web 검색 gap) ── M-D3 (fallback 추가) ── M-D4 (회귀)

M-E1 (Superdome web 검색)       ── M-E2 (adapter 추가) ── M-E3 (ai-context)
                                          ↓                          ↓
                                  M-E4 (boundary-map)        M-E5 (docs)
                                          ↓                          ↓
                                          └─── M-E6 (pytest 회귀) ─┘

M-F1 (JSON schema 문서)        ── M-F2 (3채널 비교)
   (독립 — M-A1/M-B1 분석 결과 반영하면 더 풍부)
   ※ M-A3 [DONE] (Session-3) — M-F1 신설 시 다음 절 포함 의무:
      · `status` 필드 enum 3종 (success / partial / failed)
      · 시나리오 4 매트릭스 (A/B/C/D — build_status.yml 헤더 주석 정본)
      · errors[] 와 status 분리 의미 (warning emit 시 status 영향 없음)

M-G1 (학습 추출) ── M-G2 (rule/skill/agent 후보)
   (모든 다른 ticket [DONE] 후 진입)
```

---

## 진행 가능 ticket (의존 없음)

worker 세션 즉시 착수 가능:

| ticket | 작업 영역 (충돌 방지) | 추정 소요 |
|---|---|---|
| **M-A1** | `common/tasks/normalize/build_status.yml`, `status_rules.yml` (read-only) | 1 세션 |
| **M-B1** | `redfish-gather/library/redfish_gather.py` `account_service_provision` / `infraops_account_provision` (read-only) | 1 세션 |
| **M-C1** | `redfish-gather/site.yml`, vault 동적 로딩 task (read-only) | 1 세션 |
| **M-D1** | `docs/ai/tickets/2026-05-06-multi-session-compatibility/COMPATIBILITY-MATRIX.md` (신규 작성) | 1~2 세션 |
| **M-E1** | `docs/ai/tickets/2026-05-06-multi-session-compatibility/fixes/M-E1.md` (web 검색 결과 append) | 1 세션 |
| **M-F1** | `docs/20_json-schema-fields.md` (신규) | 1 세션 |

위 6 ticket 동시 진행 가능 (서로 다른 파일 영역, 충돌 없음).

---

## 차단된 ticket (의존 미해소)

| ticket | 차단 사유 | 해소 조건 |
|---|---|---|
| M-A2 | M-A1 분석 결과 + 사용자 결정 필요 | M-A1 [DONE] + 사용자 답변 |
| M-A3 | M-A2 결정 결과 (코드 변경 / 안 함) | M-A2 [DONE] |
| M-A4 | M-A3 결과 (ADR 의무 — rule 70 R8 trigger 시) | M-A3 [DONE] |
| M-B2 | M-B1 분석 결과 (5 vendor 매트릭스) | M-B1 [DONE] |
| M-B3 | M-B2 검증 결과 (mock fixture 회귀 추가) | M-B2 [DONE] |
| M-C2 | M-C1 분석 결과 (cache invalidation 메커니즘) | M-C1 [DONE] |
| M-C3 | M-C2 결과 (회귀 추가) | M-C2 [DONE] |
| M-D2 | M-D1 매트릭스 (gap 영역 식별) | M-D1 [DONE] |
| M-D3 | M-D2 web 검색 gap 결과 | M-D2 [DONE] |
| M-D4 | M-D3 fallback 추가 후 회귀 | M-D3 [DONE] |
| M-E2 | M-E1 web 검색 결과 (Superdome 세대별 BMC 정보) | M-E1 [DONE] |
| M-E3 | M-E1 + M-E2 (vendor 식별 후 ai-context) | M-E1 [DONE] |
| M-E4 | M-E2 (adapter 추가 후 boundary-map 갱신) | M-E2 [DONE] |
| M-E5 | M-E2 + M-E3 (docs README 등 갱신) | M-E2 [DONE] |
| M-E6 | M-E2~M-E5 모두 (회귀 통합) | M-E5 [DONE] |
| M-F2 | M-F1 (3채널 비교 추가) | M-F1 [DONE] |
| M-G1 | 다른 모든 ticket [DONE] 후 진입 | A~F 모두 [DONE] |
| M-G2 | M-G1 결과 (학습 → rule/skill/agent 후보) | M-G1 [DONE] |

---

## 추천 진행 순서 (1 worker 가 순차 진행 시)

```
Phase 1 (분석 — read-only, 병렬 가능):
  M-A1 + M-B1 + M-C1 + M-D1 + M-E1 + M-F1
       ↓
Phase 2 (사용자 결정):
  M-A2 (status 로직 의도 결정)
       ↓
Phase 3 (구현 — 병렬 가능):
  M-A3 + M-B2 + M-C2 + M-D2 + M-E2 + M-F2
       ↓
Phase 4 (회귀 / 통합):
  M-A4 + M-B3 + M-C3 + M-D3 + M-D4 + M-E3 + M-E4 + M-E5 + M-E6
       ↓
Phase 5 (cycle 종료):
  M-G1 + M-G2 + HARNESS-RETROSPECTIVE
```

---

## 충돌 방지 (rule 26 R3+R4)

### 동시 편집 가능 (서로 다른 파일 영역)

| 그룹 A | 그룹 B | 그룹 C |
|---|---|---|
| `common/tasks/normalize/` | `redfish-gather/library/` | `adapters/redfish/` |
| (M-A) | (M-B) | (M-E) |

### 동시 편집 금지 (공용 파일 — 한 세션이 먼저 편집, 다른 세션은 pull 후 append)

- `schema/sections.yml`
- `schema/field_dictionary.yml`
- `common/vars/vendor_aliases.yml`
- `Jenkinsfile*`
- `vault/redfish/*.yml`
- `docs/ai/tickets/2026-05-06-multi-session-compatibility/SESSION-HANDOFF.md` (마지막 저장 우선)

### 회귀 충돌 방지

- M-D3 (fallback 추가) 와 M-E2 (Superdome adapter) 병행 시:
  - M-D3 이 redfish_gather.py 수정 영역 = `_endpoint_with_fallback` 헬퍼 / vendor map
  - M-E2 가 redfish_gather.py 수정 영역 = `_FALLBACK_VENDOR_MAP` / `_BMC_PRODUCT_HINTS`
  - 같은 파일 — 한쪽 [DONE] 후 다른 쪽 진입 (또는 명확한 라인 영역 분리)

---

## 환경별 worker 추천

| worker 환경 | 추천 ticket |
|---|---|
| 사용자 환경 (Windows) | M-A1, M-B1, M-C1, M-F1 (read-only / docs 작성) |
| Linux 환경 (ansible) | M-D3, M-E2, M-E6 (pytest 회귀 검증 가능) |
| 동등 (Windows + pytest) | 모두 가능 |

---

## 관련

- INDEX.md
- SESSION-HANDOFF.md
- fixes/INDEX.md
