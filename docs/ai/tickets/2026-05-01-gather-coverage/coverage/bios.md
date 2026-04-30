# Coverage — bios 영역 (BIOS Attribute Registry) — 신규 검토

## 채널

- **Redfish only** — Systems 안 BIOS schema
- 우리 server-exporter 는 **현재 BiosVersion / BiosReleaseDate 만 수집** (system 섹션 안). Attribute Registry 미수집.

## 표준 spec (R1)

### 표준 path
- `/redfish/v1/Systems/{id}/Bios` (BIOS root)
- `/redfish/v1/Registries/` (Registry collection)
- `/redfish/v1/Registries/<vendor>BiosAttributeRegistry.<ver>`

### BIOS schema 필드
- `Attributes` (key-value: BIOS 설정값)
- `AttributeRegistry` (해당 attribute 의 정의 file 이름)
- POST `Bios/Settings` (변경 적용 — write action)

### Registry 필드
- `RegistryEntries.Attributes[]`: AttributeName / Type / DefaultValue / Immutable / ReadOnly / ResetRequired

## Vendor 호환성 (R2)

| Vendor | BIOS Attribute Registry | path 차이 |
|---|---|---|
| Dell iDRAC 9 | OK | 표준 |
| HPE iLO 5 | OK | OEM Service path 위치 (Gen10 vs Gen10+ 다름 — F9 영역) |
| Lenovo XCC | OK | 표준 |
| Supermicro X11+ | OK | 표준 |
| Cisco CIMC | 부분 | 표준 |

## 우리 코드 영향

### 현재 수집
- `data.hardware.bios_version`, `data.hardware.bios_date` (system 섹션 안)
- BIOS attribute 자체 미수집

### 미수집
- 현재 BIOS 설정값 (SecureBoot / VirtualizationTech / TurboMode 등)
- BIOS Attribute Registry 정의

## fix 후보

### F29 — BIOS Attribute Registry 수집 (P3 — 사용자 요구 시)
- **변경 (Additive)**: 신규 섹션 'bios_attributes' 또는 system 섹션 안 sub-key
- **회귀**: schema 변경 (rule 92 R5)
- **우선**: P3

## Sources

- [HPE BIOS data model](https://servermanagementportal.ext.hpe.com/docs/concepts/biosdatamodel)
- [Lenovo XCC BIOS Attribute Registries](https://pubs.lenovo.com/xcc-restapi/bios_attribute_registries_get)
- [Supermicro BIOS Configuration](https://www.supermicro.com/manuals/other/redfish-ref-guide-html/Content/general-content/bios-configuration.htm)
- [Dell iDRAC9 BIOS](https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v4.x-series/idrac9_4.00.00.00_redfishapiguide_pub/bios)

## 갱신 history

- 2026-05-01: 신규 영역 ticket / F29 P3
