# Coverage — virtualmedia 영역 (VirtualMedia) — 운영 자동화 영역

## 채널

- **Redfish only** — Manager 또는 System 안
- 우리 server-exporter **미수집** (read-only gather scope 외 — InsertMedia / EjectMedia 는 write action)

## 표준 spec (R1)

### 표준 path (Manager 기반)
- `/redfish/v1/Managers/{id}/VirtualMedia/{device_id}`

### Action endpoint
- POST `/redfish/v1/Systems/{id}/VirtualMedia/{device_id}/Actions/VirtualMedia.InsertMedia`
- POST `.../Actions/VirtualMedia.EjectMedia`

### 필드
- `MediaTypes` (CD / DVD / Floppy / USBStick)
- `Image` (URL of mounted media)
- `Inserted`, `WriteProtected`
- `ConnectedVia` (NotConnected / URI / Applet / OEM)

## 운영 시나리오

- ISO mount 후 firmware update (HPE iLO Update Service / Dell Lifecycle Controller)
- Diagnostic ISO mount
- OS install over BMC

## 우리 코드 영향

**현재 scope 외**. server-exporter 는 read-only gather. firmware update / OS install 등은 별도 시스템 영역.

## fix 후보

### F28 — VirtualMedia 수집 (P3 — 사용자 요구 시)
- **변경 (Additive)**: 신규 섹션 'virtualmedia' — 현재 mount 상태 (read-only)
- **write action 영역**: 별도 cycle (운영 자동화 요구 시)
- **우선**: P3

## Sources

- [DMTF VirtualMedia](https://redfish.dmtf.org/redfish/schema_index)
- [Supermicro VirtualMedia](https://www.supermicro.com/manuals/other/redfish-ref-guide-html/Content/general-content/virtual-media-management.htm)
- [iDRAC 8 VirtualMedia (jimmdenton)](https://www.jimmdenton.com/mounting-virtual-media-drac8/)

## 갱신 history

- 2026-05-01: 신규 영역 ticket / F28 P3 (현재 scope 외)
