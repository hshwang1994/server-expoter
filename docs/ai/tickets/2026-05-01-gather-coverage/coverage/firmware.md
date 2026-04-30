# Coverage — firmware 영역 (UpdateService / FirmwareInventory)

## 채널

- **Redfish**: `/redfish/v1/UpdateService/FirmwareInventory/{fw_id}` (+ SoftwareInventory)
- **OS Linux**: `dmidecode -t bios` + 부분 (NIC firmware는 ethtool / nvidia-smi 등)
- **OS Windows**: `Win32_BIOS` + driver/firmware 일부
- **ESXi**: esxcli `software vib list` 일부

## 표준 spec (R1)

### UpdateService entry
- `/redfish/v1/UpdateService` (root)
- `/UpdateService/FirmwareInventory/{id}` — 하드웨어 펌웨어
- `/UpdateService/SoftwareInventory/{id}` — 드라이버 / provider

### SoftwareInventory schema 필드
- `Id`, `Name`, `Version`, `Updateable`
- `SoftwareId` (벤더 component ID)
- `ReleaseDate`, `LowestSupportedVersion`
- `Manufacturer`, `RelatedItem[]` (영향 컴포넌트)

## Vendor 호환성 (R2)

| Vendor | FirmwareInventory | 변종 처리 |
|---|---|---|
| Dell iDRAC 9 | OK | `Previous-` prefix (비활성 이전 버전) skip |
| HPE iLO 5/6 | OK | |
| Lenovo XCC | OK | `Pending` (적용 대기) — pending=true 메타 추가 |
| Supermicro X11+ | OK | |
| Cisco CIMC | OK | `N/A` / `NA` / `""` Version (빈 슬롯) skip |

## 알려진 사고 (R3)

### Fw1 — Dell `Previous-` prefix
- **fix 적용됨**: Q-14 — `Previous-` prefix skip ✓

### Fw2 — Cisco `N/A` Version (빈 PCIe 슬롯)
- **fix 적용됨**: cycle 2026-04-29 cisco-critical-review — `N/A` / `NA` / `""` skip ✓

### Fw3 — Lenovo Pending firmware
- **증상**: BMC-Primary-Pending, UEFI-Pending — version=null + ID에 'Pending' 포함
- **fix 적용됨**: cycle 2026-04-29 fix B43 — `pending` 메타 필드 추가 ✓

### Fw4 — SoftwareId 문자열 'null'
- **fix 적용됨**: Q-13 — Python None 변환 ✓

### Fw5 — Members 에 Name/Version 없으면 개별 URI 조회
- **fix 적용됨**: 개별 URI 조회 fallback ✓

### Fw6 — category 자동 분류 (cycle-016 Phase M)
- **현재**: bios / bmc / nic / storage_controller / drive / psu / cpld / tpm / lifecycle / driver_pack / diagnostic / backplane / service_module / other
- 매칭은 firmware id substring (vendor 분기 아님 — `# nosec rule12-r1`)

## fix 후보 — 현재 없음

모든 알려진 사고 fix 적용. 추가 후보:
- SoftwareInventory 도 수집 검토 (현재 FirmwareInventory만) — P3

## 우리 코드 위치

- 라이브러리: `redfish_gather.py:1620` `gather_firmware`
- normalize category 분류: `normalize_standard.yml:341-365` `_rf_firmware_categorized`

## Sources

- [HPE UpdateService](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/supplementdocuments/updateservice)
- [Supermicro Firmware Inventory](https://www.supermicro.com/manuals/other/redfish-ref-guide-html/Content/general-content/firmware-inventory-update-service.htm)
- [Lenovo XCC Firmware](https://pubs.lenovo.com/xcc-restapi/firmware_inventory_prop_get)

## 갱신 history

- 2026-05-01: R1+R2+R3 / Fw1~Fw6 / fix 후보 0건
