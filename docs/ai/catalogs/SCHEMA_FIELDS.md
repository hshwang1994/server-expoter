# SCHEMA_FIELDS — server-exporter

> sections.yml + field_dictionary.yml 카탈로그. rule 28 #1 측정 대상 (TTL 14일).

## 일자: 2026-04-27

## 10 섹션 (sections.yml)

| 섹션 | 용도 | 주 source |
|---|---|---|
| system | 호스트 식별 (hostname / os_family / fqdn) | OS gather + Redfish System |
| hardware | 모델 / 시리얼 / 메인보드 | Redfish Chassis + dmidecode |
| bmc | BMC IP / 펌웨어 / 사용자 (Redfish only) | Redfish Managers |
| cpu | 모델 / 코어 / 소켓 | OS setup + Redfish ProcessorSummary |
| memory | 용량 / DIMM list | dmidecode + Redfish MemorySummary |
| storage | 디스크 / 컨트롤러 / 볼륨 | OS lsblk + Redfish Storage/Volumes |
| network | NIC / VLAN / 라우팅 | ip / Redfish EthernetInterfaces |
| firmware | BIOS / BMC / 컴포넌트 | Redfish UpdateService/FirmwareInventory |
| users | 시스템 계정 (Linux/Windows) | getent / win_user |
| power | 전원 공급 장치 / 정책 | Redfish Chassis/Power |

## Field Dictionary (28 Must + Nice + Skip)

상세는 `schema/field_dictionary.yml` (정본). 본 catalog는 카운트 / 갱신 이력만.

### Must (28) — 모든 vendor baseline에 존재 필수

(상세 list는 schema/field_dictionary.yml 정본 참조)

### Nice — vendor-specific 허용

(상세 동일)

### Skip — 의도적 미수집

(상세 동일)

## 갱신 trigger (rule 28 #1)

- TTL 14일
- sections.yml 수정
- field_dictionary.yml 수정
- common/tasks/normalize/build_*.yml 수정

## 측정 명령

```bash
grep -E "^[a-z_]+:" schema/sections.yml | wc -l  # 섹션 수
python scripts/ai/hooks/output_schema_drift_check.py
```

## 갱신 이력

| 일자 | 변경 | commit |
|---|---|---|
| 2026-04-27 | Plan 3 초기 골격 | 145a0b1 |

(이후 갱신은 append)

## 정본 reference

- `schema/sections.yml`, `schema/field_dictionary.yml`, `schema/baseline_v1/`
- `docs/09_output-examples.md`, `docs/16_os-esxi-mapping.md`
- skill: `update-output-schema-evidence`, `plan-schema-change`
