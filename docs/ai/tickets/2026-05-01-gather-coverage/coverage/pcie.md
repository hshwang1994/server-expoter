# Coverage — pcie 영역 (PCIeDevice / PCIeFunction / PCIeSlot) — 신규 검토

## 채널

- **Redfish only** — Chassis 기반
- 우리 server-exporter **미수집** (storage controllers / network adapters 안 일부 PCIe 정보만)

## 표준 spec (R1)

### 표준 path
- `/redfish/v1/Chassis/{id}/PCIeDevices/{device_id}` (PCIeDevice)
- `/redfish/v1/Chassis/{id}/PCIeDevices/{device_id}/PCIeFunctions/{func_id}` (PCIeFunction)
- `/redfish/v1/Chassis/{id}/PCIeSlots` (PCIeSlots)

### Schema 버전 (현재 latest)
- PCIeDevice 1.6.0
- PCIeFunction 1.2.3
- PCIeSlots 1.4.1

### 필드
- PCIeDevice: Manufacturer / Model / SKU / SerialNumber / PartNumber / FirmwareVersion / DeviceType
- PCIeFunction: ClassCode / DeviceClass / DeviceId / VendorId / SubsystemId / FunctionType
- PCIeSlot: SlotType / Lanes / PCIeType / Status / Location

## 영향 — 우리 코드 deep-dive

### 현재 우리 수집
- **storage controllers** — SAS/RAID 카드 (Storage 안 sub)
- **network_adapters** — NIC 카드 (Chassis NetworkAdapters)
- **firmware** — 모든 펌웨어 inventory (PCIe 카드 firmware 일부 포함)

### 미수집
- PCIe 카드 자체 inventory (storage/network 외 — accelerator card / GPU / FPGA 등)
- PCIe slot 매핑 (어느 slot에 어떤 카드)
- PCIe 카드 deep info (Lanes / PCIeType / DeviceId / VendorId)

## fix 후보

### F26 — PCIeDevice 섹션 수집 검토 (P3)
- **현재 영향**: storage / network 외 PCIe 카드 (GPU / FPGA / accelerator) 미수집
- **변경 (Additive)**: 신규 섹션 'pcie' 또는 hardware 섹션 안 sub-key 'pcie_devices'
- **회귀**: schema 변경 — 사용자 승인 필수 (rule 92 R5)
- **우선**: P3 — 운영 요구 시 (GPU 서버 deep inventory)

## Sources

- [DMTF PCIeDevice schema](https://redfish.dmtf.org/redfish/schema_index)
- [HPE iLO 5 PCIeFunction](https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/)
- [Dell iDRAC9 PCIeFunction](https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v4.x-series/idrac9_4.00.00.00_redfishapiguide_pub/pciefunction)

## 갱신 history

- 2026-05-01: 신규 영역 ticket / F26 P3
