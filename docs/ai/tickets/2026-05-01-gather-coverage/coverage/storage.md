# Coverage — storage 영역 (Storage / SimpleStorage)

## 채널

- **Redfish**: `/redfish/v1/Systems/{id}/Storage/{controller_id}` + Drives + Volumes (fallback `/SimpleStorage`)
- **OS Linux**: `lsblk -J`, `df`, `mount`, `dmidecode`, `multipath -l`
- **OS Windows**: `Win32_DiskDrive` + `Win32_LogicalDisk` + `Get-PhysicalDisk`
- **ESXi**: pyvmomi `HostSystem.config.storageDevice` (datastores) + esxcli `storage core adapter list`

## 표준 spec (R1)

### Storage schema 필드

- Storage controller: `StorageControllers[*]` (legacy) → **Controllers** sub-resource (신규)
- `SupportedControllerProtocols` (PCIe / FC / SAS)
- `SupportedDeviceProtocols` (NVMe / SAS / SATA)

### Drive schema 필드

- `MediaType` (HDD / SSD / SMR / **NVMe** 일부 표시)
- `Protocol` (SAS / SATA / NVMe / PCIe / FC)
- `CapacityBytes`, `BlockSizeBytes`
- `FailurePredicted`, `PredictedMediaLifeLeftPercent`
- `RotationSpeedRPM` (HDD only)
- `SerialNumber`, `Model`, `Manufacturer`, `Revision`
- 신규 (2024.2): `BlockSecurityIDEnabled`, `TargetConfigurationLockLevel`, `SetControllerPassword`

### Volume schema 필드

- `RAIDType` (RAID0/1/5/6/10/...)
- `CapacityBytes`, `Encrypted`
- `Identifiers` (WWN 등)
- `BootVolume` (boolean)

### SimpleStorage (fallback for 구 BMC)

- `Devices[*]` (vendor / Model / Capacity)

## Vendor 호환성 (R2)

| Vendor | Storage | SimpleStorage fallback | NVMe | RAID |
|---|---|---|---|---|
| Dell iDRAC 8/9 | OK | 거의 미사용 | OK | RAID0~10 |
| HPE iLO 5/6 | OK | 부분 | OK | SmartArray |
| Lenovo XCC | OK | 부분 | OK | |
| Supermicro X11+ | OK | 부분 | OK | |
| Cisco CIMC | 일부 펌웨어 SimpleStorage only | OK | 부분 | |

## 알려진 사고 (R3)

### St1 — Storage 미지원 BMC (구 IMM2)
- **fix 적용됨**: SimpleStorage fallback (`redfish_gather.py:1417-1434`) ✓

### St2 — Inline storage controllers (HPE iLO 6 일부)
- **증상**: Storage 응답 안에 controller 정보 직접 포함, 별도 controller URI 없음
- **fix 적용됨**: cycle 2026-04-29 — `tests/unit/test_redfish_storage_controller.py` 검증 ✓

### St3 — Volume member_drive_ids 누락
- **증상**: 일부 펌웨어 Volume 응답에 `Links.Drives` 부재
- **현재 코드**: `vol.member_drive_ids|default([])` 로 graceful

### St4 — SmartArray HPE OEM
- **현재 코드 영향**: 표준 path 응답 OK — OEM 추출 미사용

### St5 — VMFS datastores (ESXi only)
- **fix 적용됨**: cycle 2026-04-29 esxi storage normalize ✓

## fix 후보 — 현재 없음

모든 알려진 사고 fix 적용. 신규 권장 사항 R4에:
- 2024.2 신규 필드 (`BlockSecurityIDEnabled` 등) — 보안 메타 추출 검토 (P3)

## 우리 코드 위치

- 라이브러리: `redfish_gather.py:1417` `gather_storage` + `_gather_simple_storage` / `_gather_standard_storage`
- normalize: `normalize_standard.yml:148-218` (controllers + physical_disks + logical_volumes)
- summary: `normalize_standard.yml:274-294` `_rf_summary_storage`
- OS: `os-gather/tasks/{linux,windows}/gather_storage.yml`
- ESXi: `esxi-gather/tasks/normalize_storage.yml`

## Sources

- [DMTF Redfish 2024.2 (NVMe)](https://www.dmtf.org/content/redfish-release-20242-now-available)
- [HPE iLO 5 Storage](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/supplementdocuments/storage)

## 갱신 history

- 2026-05-01: R1+R2+R3 / St1~St5 사고 / fix 후보 0건 (다 적용됨)
