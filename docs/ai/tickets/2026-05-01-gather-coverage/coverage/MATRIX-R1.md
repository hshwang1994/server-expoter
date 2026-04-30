# Coverage Round 1 — DMTF 표준 spec + 신·구 schema 변천

> 13 영역에 대한 표준 spec / schema 위치 / 변천 history. cycle 2026-05-01.

## 영역별 R1 결과

### 1. system (ComputerSystem schema)
- **표준 path**: `/redfish/v1/Systems/{id}`
- **필수 필드**: `@odata.id`, `@odata.type`, `Id`, `Name`. 그 외 (PowerState, SystemType, BiosVersion 등)는 권장
- **enum SystemType**: Physical / Virtual / OS / PhysicallyPartitioned / VirtuallyPartitioned / **DPU** (신규, NVIDIA SmartNIC)
- **enum PowerState**: PoweringOn / PoweringOff / On / Off / Reset / null
- **OEM**: vendor namespace 명시 (`Oem.Hpe`, `Oem.Dell`, `Oem.Lenovo` 등)
- **현재 코드 호환성**: OK — `_safe(data, 'PowerState')` 등 안전 추출. 다만 SystemType=DPU 는 향후 신경 (Virtual/OS 와 구분 필요)
- **변천**: 2024.x 에서 새 필드 (LastResetTime, BootProgress) 추가 — 이미 코드 반영됨 (cycle-016 Phase N)
- Sources: [Redfish Schema Index](https://redfish.dmtf.org/redfish/schema_index)

### 2. bmc (Manager schema)
- **표준 path**: `/redfish/v1/Managers/{id}`
- **필수 필드**: `@odata.id`, `@odata.type`, `Id`, `Name`
- **권장 필드**: FirmwareVersion (interoperability profile에서 강제), ServiceIdentification (신규)
- **OEM**: BMC 제품명 (iDRAC / iLO / XCC / CIMC / AMI MegaRAC)
- **변천**: ServiceIdentification 2024.1 추가 — 사용자 기억하기 위한 식별 문자열
- **현재 코드 호환성**: OK — manager_uri 무인증/인증 fallback 잘 동작
- Sources: [Redfish Manager schema](https://redfish.dmtf.org/redfish/schema_index)

### 3. cpu (Processor schema)
- **표준 path**: `/redfish/v1/Systems/{id}/Processors/{cpu_id}`
- **필수 필드**: ProcessorType (CPU/GPU/FPGA/DSP/Accelerator/Core)
- **표준 enum**: TotalCores, TotalThreads, MaxSpeedMHz, ProcessorArchitecture, InstructionSet
- **신규**: TotalEnabledCores (TotalCores 와 별개)
- **현재 코드 호환성**: 잘 됨 — cycle-016 Phase N 에서 ProcessorType 필터 적용 (GPU/FPGA 분리). 다만 신규 enum 'Accelerator' 등은 ProcessorType=='CPU' 조건만으로 통과 가능 — confirm 필요
- **변천**: GPU/Accelerator 분리는 2018+ 표준
- Sources: [Lenovo XCC CPU GET](https://pubs.lenovo.com/xcc-restapi/cpu_properties_get)

### 4. memory (Memory schema)
- **표준 path**: `/redfish/v1/Systems/{id}/Memory/{dimm_id}`
- **필드**: CapacityMiB, DataWidthBits, ErrorCorrection, MemoryType (DRAM/NVDIMM/...), Manufacturer, PartNumber, OperatingSpeedMhz
- **enum Status.State**: Enabled / Disabled / Absent / StandbySpare / UnavailableOffline
- **현재 코드 호환성**: OK — Absent 슬롯 skip 처리. 다만 NVDIMM / PMem 분류는 미반영 가능 (cycle-016 Phase N 에서 BaseModuleType 추가)
- Sources: [DMTF Redfish 2024.1](https://www.dmtf.org/content/redfish-release-20241-now-available)

### 5. storage (Storage schema)
- **표준 path**: `/redfish/v1/Systems/{id}/Storage/{controller_id}`
- **fallback**: SimpleStorage (구 BMC 호환) — 우리 코드 이미 활용 [redfish_gather.py:1417]
- **신규 (2024.2)**: TargetConfigurationLockLevel, NVMe BlockSecurityIDEnabled, SetControllerPassword
- **Drive 필드**: MediaType (HDD/SSD/SMR), Protocol (SAS/SATA/NVMe/PCIe/FC), CapacityBytes, FailurePredicted, PredictedMediaLifeLeftPercent
- **Volume**: VirtualDisk, RAID type, BootVolume
- **현재 코드 호환성**: 잘 됨 — Storage→SimpleStorage fallback 모범 패턴
- Sources: [DMTF 2024.2](https://www.dmtf.org/content/redfish-release-20242-now-available), [HPE iLO 5 Storage](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/supplementdocuments/storage)

### 6. network (EthernetInterface schema)
- **표준 path**: `/redfish/v1/Systems/{id}/EthernetInterfaces/{nic_id}` (host NIC)
- **다른 path**: `/redfish/v1/Managers/{id}/EthernetInterfaces` (BMC NIC) — 우리는 host 만 수집
- **enum LinkStatus**: LinkUp / LinkDown / NoLink / null
- **IPv4Addresses**: Address, AddressOrigin (Static/DHCP/BOOTP), SubnetMask, Gateway
- **IPv6**: IPv6Addresses, IPv6DefaultGateway 등 — 우리 코드 미수집
- **OEM**: HPE virtual NIC (iLO Host Interface), Dell BMC management 등
- **현재 코드 호환성**: 잘 됨 — link_status 정규화, IPv4 0.0.0.0 필터
- Sources: [HPE iLO 6 changelog](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/ilo6/ilo6_changelog)

### 7. network_adapters (NetworkAdapter / NetworkPort / NetworkDeviceFunction)
- **표준 path**: `/redfish/v1/Chassis/{id}/NetworkAdapters/{adapter_id}` (DMTF 표준)
- **OEM 구 path**: `/redfish/v1/Systems/{id}/BaseNetworkAdapters` (HPE iLO5 OEM, iLO 6 1.10+ deprecated → 표준 NA로 통합)
- **PortType enum**: Ethernet / FibreChannel / InfiniBand / iSCSI / FibreChannelOverEthernet
- **NetworkDeviceFunction**: 단일 port에 여러 logical function (FCoE 등)
- **현재 코드 호환성**: 우리 코드는 표준 path 만. cycle 2026-05-01에서 404 → unsupported 분류 적용. **HPE iLO 5 구 펌웨어 BaseNetworkAdapters fallback 미구현** (Round 2/3 follow-up)
- Sources: [HPE iLO 6 Adapting from iLO 5](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/ilo6/ilo6_adaptation), [Lenovo XCC NetworkAdapter](https://pubs.lenovo.com/xcc-restapi/network_adapter_properties_get)

### 8. firmware (UpdateService / FirmwareInventory + SoftwareInventory)
- **표준 path**: `/redfish/v1/UpdateService/FirmwareInventory/{fw_id}`
- **별도 path**: `/redfish/v1/UpdateService/SoftwareInventory/{sw_id}` (드라이버 / provider)
- **공통 schema**: SoftwareInventory (FirmwareInventory 도 같은 schema)
- **필드**: Id, Name, Version, Updateable, SoftwareId, ReleaseDate, LowestSupportedVersion
- **vendor 변종**: Dell `Previous-` prefix (비활성 이전 버전), Lenovo `Pending` (적용 대기), Cisco `N/A` (빈 슬롯) — 우리 코드 모두 필터링 처리
- **현재 코드 호환성**: 잘 됨 — Q-13 / Q-14 / B43 fix 다수 반영
- Sources: [HPE UpdateService](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/supplementdocuments/updateservice)

### 9. users (AccountService / Accounts / ManagerAccount)
- **표준 path**: `/redfish/v1/AccountService/Accounts/{slot_id}`
- **필드**: UserName, Password (write-only), RoleId, Enabled, Locked, PasswordChangeRequired
- **표준 RoleId**: Administrator / Operator / ReadOnly
- **OEM**: Dell DMC role mapping, HPE iLO 5 OEM privileges
- **현재 코드 호환성**: cycle 2026-04-28 P2 account_service.yml 도입 완료. `not_supported` 케이스 (Cisco CIMC 일부 — Round 2에서 확인 필요)
- Sources: [HPE iLO 5 AccountService](https://github.com/HewlettPackard/ilo-rest-api-docs/blob/master/source/includes/_ilo5_accountservice.md)

### 10. power (Power → PowerSubsystem)
- **구 path**: `/redfish/v1/Chassis/{id}/Power` (deprecated DMTF 2020.4)
- **신 path**: `/redfish/v1/Chassis/{id}/PowerSubsystem` + `/PowerSupplies/{id}` + `/PowerSupplyMetrics`
- **EnvironmentMetrics**: PowerControl 같은 system metric 분리 → `/redfish/v1/Chassis/{id}/EnvironmentMetrics`
- **현재 코드 호환성**: cycle 2026-05-01 fallback 추가. 단 EnvironmentMetrics 미수집 — PowerControl 정보 누락 가능 (Round 2 follow-up)
- Sources: [Redfish PowerControl in PowerSubsystem](https://redfishforum.com/thread/710/powercontrol-attribute-equivalent-powersubsystem)

### 11. thermal (Thermal → ThermalSubsystem) — **신규 검토 영역**
- **구 path**: `/redfish/v1/Chassis/{id}/Thermal` (deprecated DMTF 2020.4)
- **신 path**: `/redfish/v1/Chassis/{id}/ThermalSubsystem` + `/Fans/{id}` + `/EnvironmentMetrics`
- **Sensor**: `/redfish/v1/Chassis/{id}/Sensors/{sensor_id}` (별도 schema)
- **schema/sections.yml에 thermal 섹션 부재** — 현재 server-exporter 미수집
- **검토 결정**: thermal 섹션 신규 추가? (NEXT_ACTIONS P2 등재됨)
- Sources: [DMTF DSP2064 (Thermal Equipment)](https://www.dmtf.org/sites/default/files/standards/documents/DSP2064_1.0.0.pdf), [NVIDIA ThermalSubsystem](https://github.com/NVIDIA/nvbmc-docs/blob/develop/Redfish%20APIs%20Design%20for%20ThermalSubsystem%20Management.md)

### 12. hba_ib (Linux only — lspci / dmidecode 기반)
- **표준 도구**: `lspci -nn | egrep -i "fibre|hba"` (FC HBA 식별), `mlxconfig` (Mellanox InfiniBand)
- **persistent 이름**: `/etc/udev/rules.d/70-persistent-ipoib.rules` (RHEL)
- **분류**: WWN / WWPN (FC) / GUID (IB)
- **현재 코드**: `os-gather/tasks/linux/gather_hba_ib.yml` 존재. lspci 부재 시 graceful (raw fallback)
- **호환성**: lspci 부재 환경 (minimal container, 일부 임베디드) — 미지원 케이스 분류 follow-up (Round 2)
- Sources: [Configuring InfiniBand RHEL 8](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/configuring_infiniband_and_rdma_networks/index)

### 13. runtime (OS only — uptime / load / process)
- **Linux**: `/proc/uptime`, `/proc/loadavg`, `who -b`
- **Windows**: `Get-CimInstance Win32_OperatingSystem` (LastBootUpTime), `Get-Process`
- **ESXi**: `esxcli system stats uptime get`
- **현재 코드**: 정상 동작
- **호환성**: uptime path 부재 시 (very minimal container) — graceful 필요

### 14. esxi (compatibility 보조)
- **esxcli 명령**: `esxcli storage core adapter list`, `esxcli network nic list`, `esxcli system version get`
- **pyvmomi**: vSphere API SDK, vSphere 7/8 호환성 명시
- **vSphere 8 upgrade**: 7.0 U3w → 8.0 U3g 권장 path
- **호환성 주의**: pyvmomi 버전 ↔ vSphere 버전 매핑
- Sources: [Broadcom ESXi Network Storage Firmware](https://knowledge.broadcom.com/external/article/323110/), [pyvmomi](https://pypi.org/project/pyvmomi/)

## R1 발견 사항 (다음 cycle fix 후보)

| # | 영역 | 발견 | 우선 |
|---|---|---|---|
| F1 | system | SystemType=DPU 신규 — Virtual/OS와 구분 필요 (NVIDIA SmartNIC 도입 시) | P3 |
| F2 | cpu | ProcessorType 'Accelerator'/'Core' 등 신규 enum — 현재 'CPU' / '' / None 만 통과 | P2 |
| F3 | network | IPv6 미수집 — 향후 IPv6-only 망 호환 | P3 |
| F4 | network_adapters | HPE iLO 5 구 펌웨어 BaseNetworkAdapters fallback 미구현 | P2 |
| F5 | power | EnvironmentMetrics path 미수집 — PowerSubsystem fallback 시 PowerControl null | P1 |
| F6 | thermal | 섹션 자체 미수집 — ThermalSubsystem 신규 도입 검토 | P2 |
| F7 | hba_ib | lspci 부재 환경 미지원 graceful 검증 | P3 |
| F8 | users | Cisco CIMC 일부 펌웨어 AccountService 제한 — Round 2 확인 | P2 |

## R2 진입 시 검색 주제

- Dell iDRAC 7/8/9 펌웨어별 endpoint 차이 (각 13 영역)
- HPE iLO 4/5/6 펌웨어별 차이
- Lenovo XCC 1/2/3 + IMM2
- Supermicro X9~X14 (X14에서 PowerSubsystem 도입)
- Cisco CIMC UCS C-series 호환성

## R3 진입 시 검색 주제

- GitHub issue (DMTF/Redfish-Service-Validator, dell/iDRAC-Redfish-Scripting, HewlettPackard/ilo-rest-api-docs)
- Redfish Forum 사고 사례
- 펌웨어 release notes의 known issue

## 갱신 history

- 2026-05-01: R1 12 영역 검색 + 종합 (system/bmc/cpu/memory/storage/network/network_adapters/firmware/users/thermal/hba_ib/runtime+esxi)
- power R1은 cycle 2026-05-01 본문에서 충분히 다룸
