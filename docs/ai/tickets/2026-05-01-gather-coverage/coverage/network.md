# Coverage — network 영역 (EthernetInterface schema)

## 채널

- **Redfish**: `/redfish/v1/Systems/{id}/EthernetInterfaces/{nic_id}` (host NIC)
- **OS Linux**: `ip -j addr show`, `ip -j route`, `bridge link`, `/sys/class/net/`, `cat /etc/resolv.conf`
- **OS Windows**: `Win32_NetworkAdapter` + `Win32_NetworkAdapterConfiguration` + `Get-NetIPAddress`
- **ESXi**: pyvmomi `HostSystem.config.network` (vSwitch + portgroups + vmnics)

## 표준 spec (R1)

### EthernetInterface schema 필드

- `MACAddress`, `SpeedMbps`, `MTUSize`
- `LinkStatus` enum: `LinkUp` / `LinkDown` / `NoLink` / `null`
- `IPv4Addresses[]`: Address / SubnetMask / Gateway / AddressOrigin (Static/DHCP/BOOTP/IPv4LinkLocal)
- `IPv6Addresses[]`: Address / PrefixLength / AddressOrigin (DHCPv6/SLAAC/Static)
- `IPv6DefaultGateway`, `StaticNameServers[]`, `NameServers[]`
- `InterfaceEnabled` boolean
- `HostName`, `FQDN`
- `Status.Health`

### IPv4 vs IPv6
- IPv6 호환은 vendor / 펌웨어별 다름 — 우리 코드 IPv4 전용

## Vendor 호환성 (R2)

| Vendor | LinkStatus | IPv4 | IPv6 | host NIC vs BMC NIC |
|---|---|---|---|---|
| Dell iDRAC 8/9 | linkup/linkdown | OK | 부분 | 둘 다 |
| HPE iLO 5/6 | LinkUp/NoLink | 부분 (host) / 0.0.0.0 가능 | OK | 둘 다 (Virtual NIC iLO) |
| Lenovo XCC | up/down | OK | OK | 둘 다 |
| Supermicro X11+ | OK | OK | 부분 | 둘 다 |
| Cisco CIMC | Connected/Disconnected | host NIC IPv4 종종 없음 → BMC NIC 활용 | OK | 둘 다 |

## 알려진 사고 (R3)

### N1 — link_status enum 정규화 (vendor 별 다름)
- **증상**: Dell linkup/linkdown / HPE NoLink / Cisco Connected/Disconnected 다양
- **fix 적용됨**: cycle 2026-04-29 fix B13 — `_normalize_link_status()` up/down/unknown ✓

### N2 — HPE iLO 6 host NIC IPv4 placeholder
- **증상**: IPv4 = 0.0.0.0 또는 빈 값
- **fix 적용됨**: 0.0.0.0 / "" 필터 ✓

### N3 — HPE iLO 6 StaticNameServers placeholder
- **증상**: ['0.0.0.0','0.0.0.0','0.0.0.0','::','::','::']
- **fix 적용됨**: cycle 2026-04-29 hpe-critical-review filter ✓

### N4 — Cisco BMC NIC Gateway / NameServers
- **증상**: Cisco 는 host NIC 에 IPv4 정보 없고 BMC NIC 에 있음
- **fix 적용됨**: BMC NIC NameServers / Gateway union (cycle 2026-04-29 cisco-critical-review) ✓

### N5 — is_primary 판정 (IPv4 부재 환경)
- **증상**: HPE 일부 host NIC 에 IPv4 없음
- **fix 적용됨**: cycle 2026-04-29 hpe-critical-review — 첫 LinkUp NIC fallback ✓

### N6 — F3: IPv6 미수집
- **현재 코드 영향**: IPv4 만. IPv6-only 망 미지원
- **우선**: P3 (현재 사이트 IPv4 운영, 사고 재현 없음)

## fix 후보

### F3 — IPv6 수집 (Additive)
- **현재 위치**: `redfish_gather.py:1463-1468` IPv4 만 build
- **변경 (Additive)**: `IPv6Addresses` read 추가, envelope `data.network.interfaces[].addresses` 에 family='ipv6' entry 추가. 기존 IPv4 동작 유지
- **회귀**: lab IPv4-only 호스트는 IPv6 필드 빈 list (영향 없음)
- **schema 영향**: `field_dictionary.yml` 에 `addresses[].family` 이미 정의됨 (ipv4/ipv6 enum) — 변경 없음
- **우선**: P3

## 우리 코드 위치

- 라이브러리: `redfish_gather.py:1446` `gather_network` (host NIC) + bmc 안 NIC 처리
- normalize: `normalize_standard.yml:56-103` `_rf_norm_interfaces`
- gateways: `normalize_standard.yml:105-145` `_rf_norm_gateways` + `_rf_norm_dns`
- OS: `os-gather/tasks/{linux,windows}/gather_network.yml`
- ESXi: `esxi-gather/tasks/normalize_network.yml`

## Sources

- [Redfish EthernetInterface](https://redfish.dmtf.org/redfish/schema_index)
- [HPE iLO 6 Network resource](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/ilo5/ilo5_306/ilo5_network_resourcedefns306)
- [HPE iLO host interface (vNIC)](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/supplementdocuments/vnic)

## 갱신 history

- 2026-05-01: R1+R2+R3 / N1~N6 / F3 P3
