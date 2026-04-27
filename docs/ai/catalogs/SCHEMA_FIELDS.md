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
| network | (확인 필요 — sections.yml 후속 라인) | NIC / VLAN / 라우팅 |
| firmware | (확인 필요) | BIOS / BMC / 컴포넌트 |
| users | (확인 필요) | 시스템 계정 |
| power | (확인 필요) | PSU / 전력 |

## Field Dictionary (실측 카운트)

```bash
$ grep -cE "priority: must" schema/field_dictionary.yml
29

$ grep -cE "priority: nice" schema/field_dictionary.yml
8
```

| 분류 | 카운트 | 의미 |
|---|---|---|
| Must | **29** | 모든 vendor baseline에 존재 필수 |
| Nice | 8 | vendor-specific 허용 |
| Skip | (미등록 — 자명한 필드) |

**[INFO]** rule 13 / design doc / 일부 catalog에서 "28 Must"로 적힌 것은 stale 정보. **실측 29 Must**로 갱신 필요.

## 갱신 trigger (rule 28 #1)

- TTL 14일
- sections.yml 수정
- field_dictionary.yml 수정
- common/tasks/normalize/build_*.yml 수정

## 측정 명령

```bash
grep "^  [a-z]" schema/sections.yml | wc -l   # 섹션 수
grep -cE "priority: must" schema/field_dictionary.yml   # Must 카운트
grep -cE "priority: nice" schema/field_dictionary.yml   # Nice
python scripts/ai/hooks/output_schema_drift_check.py
```

## 갱신 이력

| 일자 | 변경 | commit |
|---|---|---|
| 2026-04-27 | Plan 3 초기 골격 | 145a0b1 |
| 2026-04-27 | 실측 갱신 (Must 28 → 29 정정) | (이번) |

## 정본 reference

- `schema/sections.yml`, `schema/field_dictionary.yml`, `schema/baseline_v1/`
- `docs/09_output-examples.md`, `docs/16_os-esxi-mapping.md`
- skill: `update-output-schema-evidence`, `plan-schema-change`

## 후속 작업 (사용자 결정)

- [ ] rule 13 본문의 "28 Must" → "29 Must" 갱신 결정 (Tier 2 변경)
- [ ] CLAUDE.md / 다른 catalog의 "28 Must" 표현 일관 갱신
- [ ] 본 catalog에 sections.yml의 network / firmware / users / power 섹션 상세 추가 실측
