# Coverage — network_adapters 영역 (NetworkAdapter / NetworkPort / NetworkDeviceFunction)

## 채널

- **Redfish only** — Chassis 기반 NIC 카드 정보
- OS / ESXi 채널은 host-level NIC 만 (network 영역에서 처리)

## 표준 spec (R1)

### 표준 path
- `/redfish/v1/Chassis/{id}/NetworkAdapters/{adapter_id}` (DMTF 표준)
- `/NetworkPorts/{port_id}` — port-level 정보
- `/NetworkDeviceFunctions/{func_id}` — logical function (FCoE 등)

### OEM 구 path (HPE)
- `/redfish/v1/Systems/1/BaseNetworkAdapters` (HPE iLO 5 OEM, iLO 6 1.10+ deprecated → 표준 NA로 통합)

### NetworkPort schema 필드
- `PortType` enum: `Ethernet` / `FibreChannel` / `InfiniBand` / `iSCSI` / `FibreChannelOverEthernet`
- `LinkStatus`, `CurrentLinkSpeedMbps`, `MaxFrameSize`
- `AssociatedNetworkAddresses[]` (MAC / WWN 등)

### NetworkDeviceFunction schema
- `NetType` (Disabled / Ethernet / FibreChannel / iSCSI / FCoE / InfiniBand)

## Vendor 호환성 (R2)

| Vendor | Chassis/NA | Systems/BaseNA (구 OEM) | PortType detail |
|---|---|---|---|
| Dell iDRAC 8 | 부분 | — | Ethernet 위주 |
| Dell iDRAC 9 | OK | — | OK |
| HPE iLO 4 | — | OEM only | 매우 제한 |
| HPE iLO 5 (구 펌) | 부분 | OEM (구 펌) | iLO 5 1.10+ 표준 NA |
| HPE iLO 5/6 | OK | deprecated | OK |
| Lenovo XCC | OK | — | FC HBA / IB 분류 |
| Supermicro X11+ | 부분 | — | |
| Cisco CIMC | OK | — | UCSC-PCIE-... NetworkAdapter (cycle 2026-04-29 검증) |

## 알려진 사고 (R3)

### NA1 — Cisco CIMC PortType 빈 값
- **fix 적용됨**: cycle 2026-04-29 lenovo-critical-review — `link_type` 정규화 (Ethernet 기본값) ✓

### NA2 — Lenovo XCC SR650 V2 빈 placeholder NetworkAdapter
- **증상**: PCIe slot 자체를 NetworkAdapters 컬렉션에 빈 entry 노출
- **fix 적용됨**: ControllerCapabilities.NetworkPortCount=0 + manufacturer/model 빈 값 → skip ✓

### NA3 — HPE iLO Adapter root mac 누락
- **증상**: HPE NetworkAdapter root에 mac/link/speed 없음, NetworkPorts 안에만 있음
- **fix 적용됨**: cycle 2026-04-29 fix B93 — adapter level fold-in (첫 active port) ✓

### NA4 — F4: HPE iLO 5 BaseNetworkAdapters fallback 미구현
- **증상**: 구 iLO 5 펌웨어 (2.x 초기) 가 표준 NA 응답 안 함, OEM `Systems/BaseNetworkAdapters` 만
- **현재 코드 영향**: 이 BMC 들은 `network_adapters` 섹션 'not_supported' 분류 (cycle 2026-05-01 인프라 활용)
- **우선**: P2 (구 iLO 5 펌웨어 host 사고 재현 후)

### NA5 — 404 → 'not_supported' 분류
- **fix 적용됨**: cycle 2026-05-01 — Dell PowerEdge 일부 모델 등 ✓

## fix 후보

### F4 / F11 — HPE iLO 5 BaseNetworkAdapters fallback (Additive)
- **현재 위치**: `redfish_gather.py:1481` `gather_network_adapters_chassis`
- **변경 (Additive)**:
  ```python
  base = _p(chassis_uri) + '/NetworkAdapters'
  st, coll, err = _get(...)
  if st == 404:
      # HPE iLO 5 구 펌웨어 fallback
      st_oem, coll_oem, _ = _get(bmc_ip, 'Systems/1/BaseNetworkAdapters', ...)
      if st_oem == 200:
          # _parse_hpe_base_network_adapters 호출 (별도 parser)
          return _parse_hpe_base_na(coll_oem, ...), []
      return out, []   # 미지원 — noise 차단 (cycle 2026-05-01 패턴)
  ```
- **vendor 분기**: HPE 만 적용 (rule 12 R1 — Allowed: redfish_gather.py 의 vendor 시그니처 매핑)
- **회귀**: lab Dell / Cisco / Lenovo / Supermicro 표준 path 그대로 / HPE iLO 5 새 펌웨어 표준 path / HPE iLO 5 구 펌웨어 OEM fallback
- **신규 fixture**: HPE iLO 5 구 펌웨어 (2.x 초기) 응답 fixture 필요 — 사이트 확보
- **우선**: P2

## 우리 코드 위치

- 라이브러리: `redfish_gather.py:1481` `gather_network_adapters_chassis`
- normalize: `normalize_standard.yml:299-339` `_rf_summary_network` (port_type 정규화)
- HBA / IB 분리: `normalize_standard.yml:509-510` `data.storage.hbas` / `data.storage.infiniband`

## Sources

- [HPE iLO 6 Adapting from iLO 5](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/ilo6/ilo6_adaptation)
- [Lenovo XCC NetworkAdapter](https://pubs.lenovo.com/xcc-restapi/network_adapter_properties_get)
- [Cisco CIMC NetworkAdapter UCSC-PCIE-C25Q-04](https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/api/3_0/b_Cisco_IMC_REST_API_guide_301/m_redfish_api_examples.html)

## 갱신 history

- 2026-05-01: R1+R2+R3 / NA1~NA5 / F4 P2
