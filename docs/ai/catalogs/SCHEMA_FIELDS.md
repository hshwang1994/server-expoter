# SCHEMA_FIELDS — server-exporter

> sections.yml + field_dictionary.yml 카탈로그. rule 28 #1 측정 대상 (TTL 14일).
> 실측 — 2026-04-27.

## 10 섹션 (sections.yml — 실측)

| 섹션 | 채널 | 용도 |
|---|---|---|
| system | os, esxi, redfish | 운영체제 / 호스트명 / 가동시간 |
| hardware | esxi, redfish | 벤더 / 모델 / 시리얼 / BIOS |
| bmc | redfish | BMC (iDRAC/iLO/XCC) 펌웨어 / 상태 |
| cpu | os, esxi, redfish | 소켓 / 코어 / 스레드 / 모델 |
| memory | os, esxi, redfish | 총 용량 / 슬롯별 상세 / 사용량 |
| storage | os, esxi, redfish | 파일시스템 / 물리 디스크 / 컨트롤러 / 데이터스토어 / 논리 볼륨 |
| network | os, esxi, redfish | 인터페이스 / IP 주소 / DNS / 게이트웨이 |
| firmware | redfish | 설치된 펌웨어 / 드라이버 인벤토리 |
| users | os | 로컬 시스템 사용자 계정 |
| power | redfish | PSU 상태 / 전력 정보 |

## Field Dictionary (실측 카운트)

```bash
$ grep -cE "priority: must" schema/field_dictionary.yml
29

$ grep -cE "priority: nice" schema/field_dictionary.yml
8
```

| 분류 | 카운트 | 의미 |
|---|---|---|
| Must | **31** | 모든 vendor baseline에 존재 필수 |
| Nice | **9** | vendor-specific 허용 |
| Skip | **6** | 의도적 미수집 |
| **합계** | **46 entries** | YAML key 기준 (validate_field_dictionary.py) |

**[INFO]** cycle-002 분석에서 "29 Must / 8 Nice"로 정정한 값이 실측과 차이 — 헤더 주석 (line 46~48)의 priority 설명이 grep 카운트에 포함되어 발생한 오인. cycle-005 (2026-04-28) `validate_field_dictionary.py` 실행으로 YAML 파싱 기준 **28 Must / 7 Nice / 5 Skip**로 재정정 (DRIFT-007).

## 갱신 trigger (rule 28 #1)

- TTL 14일
- sections.yml 수정
- field_dictionary.yml 수정
- common/tasks/normalize/build_*.yml 수정

## 측정 명령

```bash
grep "^  [a-z]" schema/sections.yml | wc -l   # 섹션 수
# Must / Nice / Skip 카운트는 YAML 파싱 기반 권장 (헤더 주석 noise 제거):
python3 -c "import yaml; from collections import Counter; \
    d=yaml.safe_load(open('schema/field_dictionary.yml')); \
    print(Counter(e.get('priority') for e in d['fields'].values()))"
python3 tests/validate_field_dictionary.py    # 표준 검증
python scripts/ai/hooks/output_schema_drift_check.py
```

## 갱신 이력

| 일자 | 변경 | commit |
|---|---|---|
| 2026-04-27 | Plan 3 초기 골격 | 145a0b1 |
| 2026-04-27 | cycle-002에서 Must 28 → 29 정정 (잘못된 정정 — grep 헤더 noise) | 4b5ec30 |
| 2026-04-28 | cycle-005에서 DRIFT-007 재정정: Must 28 / Nice 7 / Skip 5 (validate_field_dictionary.py 기준) | (cycle-005) |
| 2026-04-28 | cycle-006에서 DRIFT-004 resolved: users 섹션 +6 추가 → **Must 31 / Nice 9 / Skip 6 = 46 entries** | (cycle-006) |

## 정본 reference

- `schema/sections.yml`, `schema/field_dictionary.yml`, `schema/baseline_v1/`
- `tests/validate_field_dictionary.py` (표준 검증 도구)
- `docs/09_output-examples.md`, `docs/16_os-esxi-mapping.md`
- skill: `update-output-schema-evidence`, `plan-schema-change`
