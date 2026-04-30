# Coverage — system 영역

> ComputerSystem schema 기반. cold-start 가능하도록 자세히 기록. cycle 2026-05-01.

## 작업 원칙 (사용자 명시 2026-05-01)

> **"기존에있는것을 버리는게아니라 더 다양한환경을 호환하기위해서 하는것이다"**

→ Additive only. 기존 path/동작 유지 + 신 환경 호환만 추가.

## 채널

- **Redfish**: `/redfish/v1/Systems/{id}` + Chassis/{id} (manufacturer 보조)
- **OS Linux**: `/etc/os-release` + `hostnamectl` + `uname -a` + `dmidecode -t system`
- **OS Windows**: `Get-CimInstance Win32_ComputerSystem` + `Win32_BIOS` + `Win32_OperatingSystem`
- **ESXi**: `vmware_host_config_info` (pyvmomi) — vendor / model / serial / BIOS

## 표준 spec (R1 결과)

### Redfish ComputerSystem schema (DMTF v1_3_0 ~ v1_18_0+)

**필수 필드** (v1.0): `@odata.id`, `@odata.type`, `Id`, `Name`

**핵심 필드** (현재 코드 read):
- `Manufacturer`, `Model`, `SerialNumber`, `SKU`, `UUID`, `HostName`
- `PowerState` (enum: PoweringOn/PoweringOff/On/Off/Reset/null)
- `SystemType` (Physical/Virtual/OS/PhysicallyPartitioned/VirtuallyPartitioned/**DPU** 신규)
- `BiosVersion` (BiosReleaseDate 는 표준 미정의 — OEM 통해 추출)
- `Status.Health` / `Status.State`
- `IndicatorLED` (deprecated → `LocationIndicatorActive` 신규)
- `LastResetTime` (cycle-016 Phase N 추가 read)
- `BootProgress.LastState`
- `TrustedModules[]` (TPM 정보 — InterfaceType=TPM1_2/TPM2_0, FirmwareVersion, Status)
- `Boot.BootSourceOverrideTarget` (Pxe/Floppy/Cd/Usb/Hdd/BiosSetup/Utilities/Diags/UefiTarget)

**Summary 필드**:
- `ProcessorSummary` (Count, CoreCount, LogicalProcessorCount, Model, Status)
- `MemorySummary` (TotalSystemMemoryGiB, Status.Health/HealthRollup)

**OEM 필드** (vendor namespace):
- `Oem.Hpe` / `Oem.Hp` (iLO 4 fallback) → `Bios.Current.Date` 등
- `Oem.Dell.DellSystem` → `BIOSReleaseDate`
- `Oem.Lenovo` (chassis 일부에 있음 — `Oem.Lenovo.Chassis`)
- `Oem.Supermicro`
- `Oem.Cisco`

### OS Linux

- `/etc/os-release`: NAME / VERSION_ID / ID / PRETTY_NAME (freedesktop.org 표준)
- `/etc/redhat-release`: RHEL/CentOS/Rocky/Alma 추가 식별
- `/etc/debian_version`: Debian/Ubuntu 추가 식별
- `hostnamectl`: systemd 기반 distro의 표준 (Static hostname / Operating System / Kernel / Architecture)
- `uname -r`: kernel version
- `dmidecode -t system`: HW vendor / product / serial / UUID

### OS Windows

- `Win32_ComputerSystem`: Manufacturer / Model / Domain
- `Win32_BIOS`: SMBIOSBIOSVersion / Manufacturer / SerialNumber / ReleaseDate (WMI datetime format)
- `Win32_OperatingSystem`: Caption / Version / OSArchitecture / LastBootUpTime

### ESXi

- pyvmomi `HostSystem.summary.hardware` (vendor / model / uuid)
- pyvmomi `HostSystem.summary.config.product` (ESXi version / build)
- esxcli `system version get` / `hardware platform get`

## Vendor 펌웨어 호환성 (R2 결과)

| Vendor | 세대 | 호환성 | 비고 |
|---|---|---|---|
| Dell iDRAC 7 | 12G/11G | 매우 제한 | Manufacturer/Model OK / OEM 미지원 |
| Dell iDRAC 8 | 13G | 부분 | OEM (DellSystem.BIOSReleaseDate) 부분 |
| Dell iDRAC 9 (≤4) | 14G/15G | OK | OEM full |
| Dell iDRAC 9 (≥5) | 15G/16G | 신규 enum 가능 | SystemType=Virtual 가능 |
| Dell iDRAC 10 | **17G (2024-)** | 미검증 | 호환성 사전 검증 필요 (F14) |
| HPE iLO 4 | Gen9 | 제한 (Oem.Hp namespace) | |
| HPE iLO 5 | Gen10/Gen10+ | OK | BIOS Oem 위치 변경: Gen10 `/Bios/Service` vs Gen10+ `/Bios/Oem/Hpe/Service` (F9) |
| HPE iLO 6 | Gen11+ / **Compute Gen12** | OK | 사용자 사이트 검증 |
| Lenovo IMM2 | System x (구) | 매우 제한 | withdrawn |
| Lenovo XCC1 | ThinkSystem V1/V2 | OK | Oem.Lenovo.Chassis namespace |
| Lenovo XCC2 | V3 | OK | |
| Lenovo XCC3 | 최신 | OK | Redfish 1.17.0 |
| Supermicro X9 | 미지원 | 호환성 0 | adapter `supermicro_x9.yml` 정확성 (F15) |
| Supermicro X10/X11 | 부분 | Manufacturer 'Super Micro Computer, Inc.' alias 처리 필요 |
| Supermicro X12+ | OK | |
| Cisco CIMC | UCS C-series | OK | trailing whitespace PartNumber 정규화 (cycle 2026-04-30) |

## 알려진 사고 / 함정 (R3 결과)

### S1 — `HostName` 빈 문자열 (HPE 일부 펌웨어)
- **증상**: `Systems/{id}.HostName` = `""` 반환
- **fix 적용됨**: `redfish_gather.py:881-883` 빈 문자열 → None 정규화 ✓

### S2 — `IndicatorLED` deprecated (HPE Gen11)
- **증상**: HPE Gen11 부터 IndicatorLED 미제공, `LocationIndicatorActive` (boolean) 만
- **fix 적용됨**: `redfish_gather.py:886-890` LocationIndicatorActive → 'Blinking'/'Off' 매핑 ✓

### S3 — `MemorySummary.Status.Health` 미제공 (HPE)
- **증상**: HPE 가 Health 필드 미제공, HealthRollup 만
- **fix 적용됨**: `redfish_gather.py:893-895` HealthRollup fallback ✓

### S4 — Cisco PartNumber trailing whitespace
- **증상**: Cisco 가 `"PartNumber": "UCSX-... "` (공백 trailing)
- **fix 적용됨**: `redfish_gather.py:910-918` `_ne()` strip + None 정규화 ✓

### S5 — TrustedModules 빈 list / 비-list
- **증상**: 일부 펌웨어 TrustedModules 미응답 또는 비-list
- **fix 적용됨**: `redfish_gather.py:898-906` isinstance + 빈 list guard ✓

### S6 — F1: SystemType=DPU (NVIDIA SmartNIC, NVIDIA BlueField)
- **증상**: SystemType="DPU" 신규 enum (Redfish 2024.1+)
- **현재 코드 영향**: `_safe(data, 'SystemType')` 이 'DPU' 그대로 통과 — 호출자에 emit. 분기 없음 → **현재는 호환** (Physical/Virtual 처럼 단순 string)
- **권장 fix (Additive)**: 분기 코드 추가 안 함. envelope에 'DPU' 그대로 — 호출자가 분류
- **우선**: P3 (문제 없음, 등재만)

### S7 — F9: HPE Gen10 vs Gen10+ BIOS Oem 위치 변경
- **증상**: Gen10: `/Systems/1/Bios/Oem/Hpe/Service`, Gen10+/Gen11: `/Systems/1/Bios/Oem/Hpe/BaseConfigs`
- **현재 코드 영향**: 우리 코드는 BIOS endpoint 직접 호출 안 함. System.Oem.Hpe namespace 만 read → **영향 없음**
- **우선**: P3 (등재만)

## fix 후보 (system 영역, additive only)

### F1 — SystemType=DPU enum 통과 검증
- **현재**: `_safe(data, 'SystemType')` 그대로 통과 — Physical/Virtual/DPU 모두 string 반환
- **변경**: 없음 (현재 코드가 이미 호환)
- **회귀**: NVIDIA BlueField fixture 1대 수집 시 검증 — DPU 시스템 실 검증 필요
- **우선**: P3
- **Cold-start**: 사고 재현 시 `tests/fixtures/redfish/nvidia_dpu/` 추가

### F14 — Dell iDRAC 10 (17G PowerEdge, 2024-) 호환성
- **현재**: adapter `dell_idrac9.yml` priority 100, firmware_patterns `^[4-7]\\.` — iDRAC 10 firmware 8.x+ 매칭 안 됨
- **변경 (Additive)**: 새 adapter `dell_idrac10.yml` 작성 (priority 110). 기존 idrac9 수정 안 함
- **회귀**: lab Dell 14G/15G/16G 모두 idrac9 adapter 매칭 유지 + iDRAC 10 host에서 idrac10 매칭 검증
- **우선**: P3 (실 17G 도입 전까지 보류)
- **Cold-start**: `add-new-vendor` skill 따름. `common/vars/vendor_aliases.yml` 변경 없음 (Dell alias 그대로)

### F15 — Supermicro X9 adapter 정확성
- **현재**: `adapters/redfish/supermicro_x9.yml` priority 50? (확인 필요). Redfish 사실상 미지원 모델
- **변경 (Additive)**: adapter capabilities `sections_supported` 비우거나 generic으로 strict 분류. 기존 X10+ adapter 영향 없음
- **회귀**: X9 host (있으면) precheck 통과 → status='failed' 정상 분류
- **우선**: P3

## 추가 검색 항목 (R4 후보)

- iDRAC 10 정확한 Redfish endpoint 차이 (developer.dell.com 자세히)
- NVIDIA BlueField DPU SystemType 실 응답 형식
- HPE iLO 7 (Gen13 예상, 미발표) — 향후 검토

## 우리 코드 위치

- 라이브러리: `redfish-gather/library/redfish_gather.py:864` `gather_system`
- normalize: `redfish-gather/tasks/normalize_standard.yml:431` `hardware` fragment 매핑
- adapter capabilities: 16개 adapter `system` in sections_supported
- OS: `os-gather/tasks/{linux,windows}/gather_system.yml`
- ESXi: `esxi-gather/tasks/normalize_system.yml`

## Sources

- [Redfish ComputerSystem schema](https://redfish.dmtf.org/redfish/schema_index)
- [HPE iLO 5 ComputerSystem](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/ilo5/ilo5_307/ilo5_computersystem_resourcedefns307)
- [HPE iLO 6 ComputerSystem](https://redfish.redoc.ly/docs/redfishservices/ilos/ilo6/ilo6_168/ilo6_computersystem_resourcedefns168/)
- [Dell iDRAC9 BIOS](https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v4.x-series/idrac9_4.00.00.00_redfishapiguide_pub/bios)
- [Linux distro detection (cyberciti)](https://www.cyberciti.biz/faq/find-linux-distribution-name-version-number/)

## 갱신 history

- 2026-05-01: R1+R2+R3 통합 + S1~S7 알려진 사고 7건 + F1/F14/F15 fix 후보 자세히 기록
