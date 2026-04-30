# Coverage — memory 영역 (Memory schema)

## 채널

- **Redfish**: `/redfish/v1/Systems/{id}/Memory/{dimm_id}`
- **OS Linux**: `dmidecode -t memory` + `free -m`
- **OS Windows**: `Win32_PhysicalMemory` + `Win32_OperatingSystem` (TotalVisibleMemorySize)
- **ESXi**: pyvmomi `HostSystem.summary.hardware.memorySize` + per-DIMM via vmware_host_config_info

## 표준 spec (R1)

### Memory schema 필드

- `CapacityMiB`, `DataWidthBits`, `BusWidthBits`, `ErrorCorrection`
- `MemoryType` (DRAM / NVDIMM_N / NVDIMM_F / NVDIMM_P / IntelOptane / **HBM** 신규 Gen11)
- `BaseModuleType` (DRAM / RDIMM / UDIMM / SO_DIMM / **HBM** Gen11)
- `Manufacturer`, `PartNumber`, `SerialNumber`
- `OperatingSpeedMhz`, `RankCount`, `LogicalSizeMiB`
- `Status.State` (Enabled/Disabled/Absent/StandbySpare/UnavailableOffline)

## Vendor 호환성 (R2)

| Vendor | DataWidth | ErrorCorrection | NVDIMM | HBM (Gen11) |
|---|---|---|---|---|
| Dell iDRAC 8/9 | OK | OK | 부분 (Optane) | — |
| HPE iLO 5/6 | OK | OK | 부분 | **Gen11+ HBM 신규** |
| Lenovo XCC | OK | OK | 부분 | — |
| Supermicro X11+ | OK | OK | 부분 | — |
| Cisco CIMC | raw JEDEC ID 정규화 필요 | OK | — | — |

## 알려진 사고 (R3)

### M1 — Cisco CIMC raw JEDEC ID Manufacturer
- **증상**: Cisco CIMC가 Manufacturer를 raw JEDEC ID '0xCExx' 형식 emit
- **fix 적용됨**: cycle 2026-04-29 fix B90 — `_normalize_jedec()` 로 Samsung / SK hynix / Micron 등 vendor 이름 정규화 ✓

### M2 — Total memory 합산 0/null (per-DIMM 미제공 펌웨어)
- **fix 적용됨**: BUG-14 — `System.MemorySummary.TotalSystemMemoryGiB * 1024` fallback ✓

### M3 — Absent 슬롯 처리
- **증상**: 빈 슬롯 다수일 때 `CapacityMiB=0` 또는 `Status.State=Absent`
- **fix 적용됨**: Absent skip ✓

### M4 — F10: HPE Gen11 HBM memory 신규
- **증상**: ProLiant Gen11 SuperDome / accelerator 시스템에 HBM (High Bandwidth Memory) module 추가됨
- **현재 코드 영향**: `MemoryType` / `BaseModuleType` raw 통과 — emit 자체는 OK. summary group 분류는 type 별로 그룹화 (cycle-016 Phase L) → 'HBM' enum 도 자동 분리 그룹 생성 ✓
- **검증 필요**: HBM fixture 추가 후 그룹 분리 정확성 확인
- **우선**: P2

### M5 — capacity_mb vs capacity_mib 키 일관성
- **증상**: cycle-016 Phase P 에서 `capacity_mb` 로 통일. 일부 fixture는 구 이름
- **fix 적용됨**: 두 이름 모두 read 가능 ✓

## fix 후보 (memory 영역)

### F10 — HPE Gen11 HBM memory enum 검증
- **현재 위치**: `redfish-gather/tasks/normalize_standard.yml:250-272` `_rf_summary_memory` 그룹 합산
- **변경 (Additive)**: 변경 없음 — 현재 코드가 이미 BaseModuleType 별로 그룹 자동 생성. HBM 이 'HBM' string 으로 응답되면 자동 그룹 분리
- **회귀**: HPE Gen11 Compute (HBM) fixture 신규 캡처 필요 (사이트 제공)
- **우선**: P2

## 우리 코드 위치

- 라이브러리: `redfish-gather/library/redfish_gather.py:1134` `gather_memory`
- normalize summary: `normalize_standard.yml:250-272` `_rf_summary_memory`
- OS: `os-gather/tasks/{linux,windows}/gather_memory.yml`

## Sources

- [Redfish Memory schema 2024.1](https://www.dmtf.org/content/redfish-release-20241-now-available)
- [Lenovo XCC Memory GET](https://pubs.lenovo.com/xcc-restapi/server_memory_properties_get)

## 갱신 history

- 2026-05-01: R1+R2+R3 / M1~M5 / F10 P2
