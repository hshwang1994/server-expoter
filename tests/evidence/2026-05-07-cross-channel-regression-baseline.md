# Cross-channel envelope 회귀 baseline (Phase A) — 2026-05-07

## 사고 요약

- 환경: 7 우려사항 검토 cycle Phase A
- 발견 사고: `cisco_baseline.json` hostname=null (envelope fallback chain 의도와 불일치)
- root cause 후보 (실측 검증 전):
  1. baseline이 `build_output.yml` fallback chain 도입 이전에 캡처됨 (stale)
  2. cisco UCS BMC가 system.hostname / system.fqdn 모두 null + Ansible run에서 `_out_ip` 도 null이었음
- hotfix commit: 없음 (Phase A 회귀 테스트로 검출만, baseline 수정은 후속 cycle)

## fixture / 회귀 출처

- 캡처 일시: 2026-05-07
- 영향 파일:
  - `tests/regression/__init__.py` (신규)
  - `tests/regression/conftest.py` (신규 — 8 baseline registry)
  - `tests/regression/test_cross_channel_consistency.py` (신규 — T1~T10)
- pytest 결과: **441 passed + 1 xfailed** (cisco hostname known drift)

## 회귀 보호 범위 (107 신규 검증)

T1 envelope 13 필드 (rule 13 R5) × 8 baseline = 16 (1 정+1 부)
T2 target_type 검증 × 8 = 8
T2 collection_method 매칭 × 8 = 8
T3 hostname not null × 8 = 7 + 1 xfail
T3 ip 존재 × 8 = 8
T4 vendor canonical (rule 50 R1) × 8 = 8
T5 status enum (rule 13 R8) × 8 = 8
T6 sections values enum × 8 = 8
T7 diagnosis dict × 8 = 8
T7 diagnosis 4-stage keys (rule 27) × 8 = 8
T8 errors[] is list (rule 22 R8) × 8 = 8
T9 schema_version "1" (rule 13 R3) × 8 = 8
T10 채널 baseline coverage (redfish≥4 / os≥3 / esxi≥1) = 3

총: 107 검증, 106 PASS + 1 xfail.

## 후속 (rule 13 R4 — 실측 기반 baseline 갱신)

- **cisco_redfish hostname=null baseline 재실측**: lab Cisco UCS 또는 사이트 fixture 캡처 필요
- 재실측 후 `cisco_baseline.json:8` 갱신 + `_HOSTNAME_FALLBACK_KNOWN_DRIFT` set에서 cisco_redfish 제거 + xfail → 정 PASS 격상
- 추적 위치: `docs/ai/NEXT_ACTIONS.md` 2026-05-07 entry

## 학습 (rule 95 R1 #6 — 빈 callback message 검출 패턴 확장)

cross-channel envelope 회귀가 아니었다면 cisco baseline drift는 단일 vendor 회귀 테스트만으로는 발견 못함. 본 회귀 테스트가 **모든 baseline 동시 검증**으로 drift 가시화. 향후 새 baseline 추가 시 자동으로 13 필드 + fallback chain + canonical vendor 검증 적용됨.

## 관련

- rule 13 R4 (실측 기반 baseline 갱신)
- rule 13 R5 (envelope 13 필드)
- rule 13 R8 (status 4 시나리오)
- rule 21 R2 (fixture 출처 기록)
- rule 22 R8 (fragment 변수 타입)
- rule 27 (precheck 4-stage)
- rule 50 R1 (vendor 정규화 정본)
- rule 70 R3 (절대 날짜)
- rule 95 R1 (production code critical review)
