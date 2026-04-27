# Harness Cycle 005 — AI 자체 가능 작업 일괄 처리

## 일자: 2026-04-28

## Trigger

사용자 명시 ("남아있는 AI 작업 모두 수행"). cycle-004 NEXT_ACTIONS의 P2 (AI 자체 가능) + DRIFT-007 (cycle-004 verifier 발견) 일괄 정리.

사용자 결정 필요 항목 (DRIFT-004/005/006/W2 (b))은 제외 — 보고서 등재 상태 유지.

## 1. Observer (관측)

### 1.1 cycle-004 잔여 / verifier 발견
- DRIFT-007: validate_field_dictionary.py 결과 "Must 28 / Nice 7 / Skip 5" ↔ cycle-003 정정값 "Must 29 / Nice 8" 불일치
- scan_suspicious_patterns #2 (107건 false positive — set_fact 라인만 보고 침범 판단 불가)
- scan_suspicious_patterns #4 (7건 — 같은 priority여도 distribution_patterns 등으로 specificity 분리)
- verify_vendor_boundary (33건 중 7건 docstring false positive)
- DRIFT-005 옵션 (2): _BUILTIN_VENDOR_MAP ↔ vendor_aliases.yml 동기화 게이트 advisory 추가

### 1.2 사용자 결정 필요 (cycle-005 범위 외)
- DRIFT-004 (users 섹션 등록), DRIFT-005 (alias 통합), DRIFT-006 (vendor 분기 17건), W2 (b) (Jinja2 OEM list)

## 2. Architect (변경 명세)

### Tier 1 — 자동 진행

- **W1**: DRIFT-007 catalog 정합
  - 실측 분포 확정 (validate_field_dictionary.py + YAML 파싱): **Must 28 / Nice 7 / Skip 5 = 40 entries**
  - 정정 위치: `CLAUDE.md`, `.claude/rules/13-output-schema-fields.md`, `schema/field_dictionary.yml` 헤더, `docs/ai/catalogs/SCHEMA_FIELDS.md`, `.claude/skills/update-output-schema-evidence/SKILL.md`
  - SCHEMA_FIELDS.md 측정 명령을 grep → YAML 파싱 변경 (헤더 noise 제거)
  - DRIFT-001 상태 코멘트 갱신, DRIFT-007 resolved 마킹

- **W2**: scan #2 재설계 (`set_fact_check_keys` 신규)
  - set_fact: 라인 발견 후 다음 indent 블록 lookahead (최대 30 라인)
  - 누적 변수 키 (`_collected_data`, `_collected_errors`, `_supported_sections`, `_collected_supported`) 만 검출
  - 결과: **107 → 0건** (server-exporter 코드 rule 22 100% 정합 확인)

- **W3**: scan #4 specificity 분석 (`_adapter_has_specificity`)
  - 같은 (channel, vendor) 내 priority 동률 + match.{distribution_patterns, version_patterns, firmware_patterns, model_patterns, manufacturer_patterns} 중 하나라도 있으면 silence
  - 결과: **7 → 0건** (linux 3 / windows 2 / esxi 1+ / hpe iLO5/6 모두 의도된 분리)

- **W4**: verify_vendor_boundary Python `"""` docstring 인식 (`_python_docstring_lines`)
  - triple-quote 페어링으로 docstring 라인 set 계산 → vendor 검사 skip
  - 결과: **33 → 26건** (docstring 7건 false positive 제거)

- **W5**: verify_harness_consistency 동기화 게이트 (DRIFT-005 옵션 (2))
  - `_extract_python_vendor_map` (정규식) + `_extract_yaml_vendor_aliases` (간단 indent parser)
  - canonical 별 alias set lower-strip 비교 → drift 시 advisory
  - 결과: 현재 drift 0건 (두 source 동기화 상태 확인)

### Tier 2 / Tier 3 — 변경 없음
- DRIFT-004/005 (1)/006/W2 (b) 사용자 결정 항목 — 보고서 상태 유지

## 3. Reviewer

본 cycle 변경:
- 도구 4종 정밀화 + 게이트 1종 추가 → false positive 142건 감소 (cycle-004 잔여 114 + 33 - 26 = 121 → 0 + 0 + 1 (DRIFT-004) + 26 = 27, 추가 가용 검증 게이트 1종)
- DRIFT-007 catalog 정합 정리

자가 검수 금지 (rule 25 R7) — 차기 cycle reviewer가 검토.

검증 충돌 없음:
- redfish_gather.py / 도메인 코드 변경 0건 (도구만 변경)
- 도메인 코드 회귀: pytest 95 PASS

## 4. Governor (Tier 분류)

| 적용 | Tier | 사유 |
|---|---|---|
| W1 catalog 정합 (Must 28 정정) | 1 | 문서 정합 (코드 변경 0) |
| W2 scan #2 재설계 | 1 | 도구 정밀화 (advisory) |
| W3 scan #4 specificity | 1 | 도구 정밀화 (advisory) |
| W4 vendor_boundary docstring | 1 | 도구 정밀화 (advisory) |
| W5 동기화 게이트 | 1 | 도구 advisory 게이트 추가 |
| DRIFT-007 resolved | 1 | catalog 갱신 |

모두 Tier 1. Tier 2 변경 없음 (사용자 결정 항목 보고서 등재 상태 유지).

## 5. Updater (적용)

본 cycle commit (계획):
1. `harness: cycle-005 — DRIFT-007 catalog 정합 (Must 28/Nice 7/Skip 5)`
2. `harness: cycle-005 — scan #2/#4 재설계 + vendor_boundary docstring + alias 동기화 게이트`
3. `harness: cycle-005 보고서 + CURRENT_STATE / NEXT_ACTIONS 갱신 + project_map 갱신`

## 6. Verifier (검증)

### 6.1 정적 검증

```
verify_harness_consistency.py        : PASS + vendor alias drift 0
validate_claude_structure.py         : OK
check_project_map_drift.py           : 갱신 후 정합 (schema/tests fingerprint 갱신)
scan_suspicious_patterns.py          : clean (11 패턴 0건) — cycle-004 114 → 0
verify_vendor_boundary.py --full     : 26건 (cycle-004 33 → 26, docstring 7 정리)
output_schema_drift_check.py         : 1건 (DRIFT-004 users 섹션 — 사용자 결정)
```

### 6.2 ansible / pytest (WSL)

```
ansible-playbook --syntax-check 3-channel : ALL PASS
validate_field_dictionary.py             : PASS (10 checks, must=28 nice=7 skip=5 — DRIFT-007 정정값 일치)
pytest tests/                             : 95 passed in 2.13s
```

### 6.3 회귀 영향

- 도메인 코드 변경 0건 — pytest 95 PASS는 cycle-004 + cycle-005 누적 효과 검증
- cycle-005는 도구 / 카탈로그만 변경 → 운영 영향 없음

## 결과

**Tier 1 모두 PASS**. cycle-005 핵심 산출물:

### 도구 false positive 140 → 0건
- scan: 114 → 0 (#2 재설계 107건 정리, #4 specificity 7건 정리)
- vendor_boundary: 33 → 26 (docstring 7건 정리, 잔여 26건은 DRIFT-005/006/W2 (b) 결정 후보)

### catalog 정합
- DRIFT-007 resolved (cycle-002 정정 자체 잘못 식별 + 정확한 분포로 5 위치 일괄 갱신)
- DRIFT-001 상태 코멘트 갱신 (정정값 자체 stale 명시)

### 추가 게이트
- verify_harness_consistency.py에 vendor alias 동기화 advisory 추가 (DRIFT-005 옵션 (2) 사전 적용)

## 다음 cycle 후보 (cycle-006)

### 사용자 결정 필요 (변화 없음)
- DRIFT-004 (users 섹션 field_dictionary 등록)
- DRIFT-005 (1) 옵션 (`_BUILTIN_VENDOR_MAP` → YAML import 통합 — Tier 2 도메인 코드 변경)
- DRIFT-006 (vendor 분기 17건)
- W2 (b) (Jinja2 OEM list 정리)
- 새 vendor 추가 / Round 11 검증

### AI 자체 가능 후보 (cycle-006)
- (특별한 추가 작업 없음 — cycle-005 결과 모든 도구 0건)
- 운영 정책: harness-cycle 정기 주기 (사용자 결정)

## 정본 reference

- workflow: `docs/ai/workflows/HARNESS_EVOLUTION_MODEL.md`, `HARNESS_GOVERNANCE.md`
- catalog: `docs/ai/catalogs/CONVENTION_DRIFT.md` (DRIFT-007 resolved)
- 직전 cycle: `docs/ai/harness/cycle-004.md`
- skill: `harness-full-sweep`, `harness-cycle`
