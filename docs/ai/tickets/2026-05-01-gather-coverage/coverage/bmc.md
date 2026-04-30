# Coverage — bmc 영역 (Manager schema)

> Redfish Manager schema. 원칙: Additive only.

## 채널

- **Redfish only** — `/redfish/v1/Managers/{id}` (BMC 자체 메타)
- OS / ESXi 채널은 BMC 정보 미수집 (host OS만)

## 표준 spec (R1)

### Manager schema 필드

- 필수: `@odata.id`, `@odata.type`, `Id`, `Name`
- 권장: `FirmwareVersion` (interoperability profile에서 강제)
- 신규 (2024.1): `ServiceIdentification` — 사용자 식별 문자열
- `ManagerType` (enum: BMC / EnclosureManager / ManagementController / Service / AuxiliaryController)
- `Status.Health` / `State`
- `EthernetInterfaces` (BMC NIC link)
- `NetworkProtocol` (HTTPS/SSH/IPMI 활성 정보)
- `LogServices` (BMC log)
- `VirtualMedia`

### vendor display name (BMC 표시명)

- Dell: iDRAC
- HPE: iLO
- Lenovo: XCC (XClarity Controller) / IMM2
- Supermicro: AMI MegaRAC
- Cisco: CIMC

## Vendor 호환성 (R2)

| Vendor | BMC 세대 | FirmwareVersion | NetworkProtocol | LogServices |
|---|---|---|---|---|
| Dell iDRAC 7~10 | 모두 | OK | OK | OK (Lifecycle Log) |
| HPE iLO 4~6 | 모두 | OK | OK | OK (IEL) |
| Lenovo XCC1~3 / IMM2 | XCC OK / IMM2 제한 | OK / 제한 | OK | OK |
| Supermicro AMI X9~X14 | X9/X10 미지원 / X11+ OK | OK | OK | OK |
| Cisco CIMC | OK | OK | OK | OK |

## 알려진 사고 (R3)

### B1 — `_network_meta` 임시 키 (cycle 2026-04-29 cisco-critical-review)
- **증상**: BMC NIC NameServers / IPv4 Gateway 추출 위해 `result['_network_meta']` 임시 키 emit
- **fix 적용됨**: normalize_standard.yml `_rf_d_bmc_clean` 가 `_network_meta` 제거 후 envelope `data.bmc` 로 ✓

### B2 — Cisco BMC IPv4 Gateway 분리
- **증상**: Cisco 는 server NIC 에 IPv4 정보 없고 BMC NIC 에 있음
- **fix 적용됨**: `_rf_norm_gateways` 가 BMC NIC 도 union ✓

### B3 — HPE iLO 6 StaticNameServers placeholder
- **증상**: HPE iLO 6 가 `['0.0.0.0','0.0.0.0','0.0.0.0','::','::','::']` 형태 placeholder 응답
- **fix 적용됨**: `_rf_norm_dns` 가 placeholder 필터 (cycle 2026-04-29 hpe-critical-review) ✓

### B4 — F16 CVE-2024-54085 (AMI MegaRAC)
- **영향**: Supermicro / 일부 Lenovo / HPE 변종. 패치/미패치 응답 차이 가능
- **현재 코드 영향**: read-only gather라 직접 risk 작음
- **우선**: P3 (등재만)

### B5 — Lenovo IMM2 ManagerType 미응답
- **증상**: 일부 IMM2 펌웨어가 ManagerType 미응답
- **현재 코드 영향**: ManagerType 미사용 — 영향 없음

## fix 후보 (bmc 영역)

현재 모든 알려진 사고 fix 적용됨. 신규 fix 후보 없음.

향후 (R4 후보):
- ServiceIdentification (2024.1 신규) read 검토 — 사용자 식별 메타 — P3
- LogServices entry 수집 검토 (현재 미수집) — P3 (사용자 요구 시)

## 우리 코드 위치

- 라이브러리: `redfish-gather/library/redfish_gather.py:973` `gather_bmc`
- normalize: `redfish-gather/tasks/normalize_standard.yml:39-53` `_rf_d_bmc_network` + `_rf_d_bmc_clean`
- BMC 표시명 매핑: `redfish_gather.py` 내 `bmc_names` dict (`# nosec rule12-r1`)

## Sources

- [Redfish Manager schema](https://redfish.dmtf.org/redfish/schema_index)
- [DMTF 2024.1 (ServiceIdentification)](https://www.dmtf.org/content/redfish-release-20241-now-available)

## 갱신 history

- 2026-05-01: R1+R2+R3 통합 / B1~B5 알려진 사고 / 신규 fix 0건 (모두 적용됨)
