# server-exporter 현재 상태

## 일자: 2026-04-28 (cycle-005 후 갱신)

## 요약

server-exporter AI 하네스 **Plan 1+2+3 + cycle-001 ~ cycle-005 완료**. cycle-005는 사용자 명시 ("남아있는 AI 작업 모두 수행") 에 대응한 도구 정밀화 + DRIFT-007 catalog 정합:

- **DRIFT-007 catalog 정합**: validate_field_dictionary.py 기준 실측 분포 "Must 28 / Nice 7 / Skip 5 = 40 entries"로 5 위치 일괄 정정 (cycle-002 정정값 자체가 잘못된 grep 카운트였음 — 헤더 주석 noise)
- **scan #2 재설계**: set_fact 다음 indent 블록 lookahead로 누적 변수 직접 수정만 검출 → 107 → 0건
- **scan #4 specificity 분석**: 같은 priority여도 distribution_patterns / version_patterns / firmware_patterns로 분리되면 silence → 7 → 0건
- **verify_vendor_boundary docstring 인식**: Python triple-quote 페어링으로 docstring 라인 skip → 33 → 26건
- **verify_harness_consistency 동기화 게이트**: `_BUILTIN_VENDOR_MAP` ↔ vendor_aliases.yml drift advisory (DRIFT-005 옵션 (2) 사전 적용)
- **scan_suspicious_patterns.py: 11 패턴 모두 0건** (server-exporter 코드 rule 95 R1 100% 정합)

## 완료된 Plan / Cycle

| Plan / Cycle | 내용 | commit |
|---|---|---|
| Plan 1 (Foundation) | settings.json + 19 hooks + supporting scripts + policy + role + ai-context + templates + commands + 29 rules + CLAUDE.md Tier 0 | d87af96, 31526c3, ee82f1b, 031b32e |
| Plan 2 (Skills + Agents) | 43 skills + 51 agents | 183a79e, 2b3268f |
| Plan 3 (docs/ai 골격) | catalogs / decisions / policy / workflows / harness / handoff / impact / references | cc3067d, 50343f3 |
| cycle-001 (dry-run) | 자기개선 루프 dry-run | (cc3067d 일부) |
| cycle-002 (실측 + DRIFT 발견) | 실측 catalog 갱신 + 3 DRIFT 발견 + verify 강화 | 4b5ec30 |
| cycle-003 (DRIFT 정리 + 도구) | DRIFT-001/002/003 resolved + scan_suspicious_patterns.py 신규 + 13 adapter origin 발견 | 69abb8a |
| cycle-004 (전수조사) | 도구 3종 정밀화 + 13 adapter origin 일괄 + _safe_int + 변수 silence + DRIFT-004/005/006 등재 | fef5789..6142eea |
| **cycle-005 (AI 자체 가능 일괄)** | **DRIFT-007 catalog 정합 + scan #2/#4 재설계 + vendor_boundary docstring + alias 동기화 게이트 → scan 11 패턴 0건** | (이번 세션) |

## 검증 결과 (cycle-005 후)

```
[정적 — Windows]
verify_harness_consistency.py        : PASS (rules 29 / skills 43 / agents 51 / policies 10)
                                      + vendor alias 동기화 drift 0
validate_claude_structure.py         : OK
check_project_map_drift.py           : fingerprint 일치 (cycle-005 갱신 후)
scan_suspicious_patterns.py          : clean (11 패턴 0건) — cycle-004 114 → 0
verify_vendor_boundary.py --full     : 26건 (cycle-004 33 → 26, docstring 7 정리,
                                      잔여는 DRIFT-005/006 + W2 (b) 사용자 결정)
output_schema_drift_check.py         : 1건 (DRIFT-004 users 섹션 — 사용자 결정)

[ansible / pytest — WSL]
ansible-playbook --syntax-check 3-channel : ALL PASS
validate_field_dictionary.py         : PASS (10 checks, must=28 nice=7 skip=5 — DRIFT-007 정정값 일치)
pytest tests/                        : 95 passed in 2.13s (영향 vendor baseline 회귀 0건)
```

도메인 코드:
- cycle-005 도메인 코드 변경 0건 (도구 / 카탈로그만)
- pytest 95 PASS는 cycle-004 + cycle-005 누적 효과 검증

## 카탈로그 (실측, 2026-04-27 cycle-004 후)

| 카테고리 | 카운트 | 변화 |
|---|---|---|
| rules | 29 | 변화 없음 |
| skills | 43 | 변화 없음 |
| agents | 51 | 변화 없음 |
| policies | 10 | 변화 없음 |
| roles | 6 | 변화 없음 |
| ai-context | 12 | 변화 없음 |
| templates | 8 | 변화 없음 |
| commands | 5 | 변화 없음 |
| hooks (Python) | 19 + supporting 8 | 변화 없음 |
| references (외부 docs) | 14 | 변화 없음 |
| **adapters** | **25** (모두 origin 주석 보유 — cycle-004 이전 12개에서 +13) | 100% rule 96 R1 정합 |
| **DRIFT 등재** | **6** (resolved 3 + open 3) | DRIFT-004/005/006 신규 |

## 채널별 / Vendor 상태

| 채널 | 상태 | adapter | origin 주석 |
|---|---|---|---|
| os-gather | ok | 7 | 100% (cycle-004) |
| esxi-gather | ok | 4 | 100% (cycle-004) |
| redfish-gather | ok | 14 | 100% (cycle-003 12 + cycle-004 1 redfish_generic + 1 registry) |

| Vendor | adapter | baseline | origin |
|---|---|---|---|
| Dell | 3 (idrac8/9/generic) | 있음 | 기존 + 검증 |
| HPE | 4 (ilo4/5/6/generic) | 있음 | 기존 + 검증 |
| Lenovo | 2 (xcc/imm2) | 있음 | 기존 + 검증 |
| Supermicro | 3 (x11/x9/bmc) | 일부 | 기존 + 검증 |
| Cisco | 1 (cimc) | 일부 | 기존 + 검증 |

## DRIFT 현황

| ID | 분류 | 상태 |
|---|---|---|
| DRIFT-001 | catalog-stale (Field Dictionary 28→29 Must, cycle-003 정정 자체 stale) | resolved (cycle-003), DRIFT-007에서 재정정 |
| DRIFT-002 | catalog-stale (Stage 4 일반화) | resolved (cycle-003) |
| DRIFT-003 | catalog-stale (vendor-bmc-guides adapter 이름) | resolved (cycle-003) |
| DRIFT-004 | convention-violation (`users` 섹션 field_dictionary 미등록) | open — 사용자 결정 (schema 변경) |
| DRIFT-005 | convention-violation (`_BUILTIN_VENDOR_MAP` 중복) | open — 사용자 결정 (옵션 (2) 동기화 게이트는 cycle-005 사전 적용) |
| DRIFT-006 | convention-violation (redfish_gather.py vendor 분기 17건) | open — 사용자 결정 |
| **DRIFT-007** | **catalog-stale (Must 28/Nice 7/Skip 5 실측 — cycle-002 grep 헤더 noise 오인)** | **resolved (cycle-005)** |

## 다음 작업 (cycle-005 후보)

> `docs/ai/NEXT_ACTIONS.md` 참조.

### 사용자 결정 / 외부 의존
- DRIFT-004: `users` 섹션 field_dictionary 등록 (rule 92 R5 schema 변경 승인)
- DRIFT-005/006: vendor 경계 33건 옵션 결정 (`docs/ai/impact/2026-04-27-vendor-boundary-57.md`)
- 새 vendor 추가 (PO 결정)
- Round 11 검증 (실장비)

### AI 자체 가능 (cycle-005)
- scan_suspicious_patterns.py #2 재설계 (set_fact 다음 라인 분석)
- scan_suspicious_patterns.py #4 specificity 분석 (priority 동률 + match.distribution_patterns 결합)
- verify_vendor_boundary.py Python `"""` docstring 인식 추가
- verify_harness_consistency.py에 `_VENDOR_ALIASES` ↔ `vendor_aliases.yml` 동기화 게이트

## 정본 reference

- `CLAUDE.md` (Tier 0 정본, 보강됨)
- `GUIDE_FOR_AI.md`, `REQUIREMENTS.md`, `README.md`
- `docs/01_jenkins-setup` ~ `docs/19_decision-log`
- 직전 cycle: `docs/ai/harness/cycle-004.md`
- vendor 경계 분석: `docs/ai/impact/2026-04-27-vendor-boundary-57.md`
- DRIFT 카탈로그: `docs/ai/catalogs/CONVENTION_DRIFT.md`
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
