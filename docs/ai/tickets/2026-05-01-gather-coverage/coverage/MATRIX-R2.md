# Coverage Round 2 — Vendor 펌웨어 호환성 매트릭스

> 5 vendor 의 BMC 펌웨어 세대별 Redfish 호환성. cycle 2026-05-01.

## 개관 — Vendor × BMC 세대 × Redfish 표준 ver

| Vendor | BMC 세대 | 서버 세대 | Redfish ver | PowerSubsystem | 표준 NetworkAdapters | 비고 |
|---|---|---|---|---|---|---|
| Dell | iDRAC 7 | PowerEdge 12G/11G | <1.0 | ✗ | ✗ | 매우 제한, 우리 코드 graceful fail |
| Dell | iDRAC 8 | PowerEdge 13G | 1.x (제한) | ✗ Power만 | 부분 | 우리 lab 검증 |
| Dell | iDRAC 9 (≤4.x) | PowerEdge 14G/15G | 1.x~1.12 | ✗ Power만 | 지원 | |
| Dell | iDRAC 9 (≥5.x) | PowerEdge 15G/16G | 1.13+ | ✓ 둘 다 | 지원 | |
| Dell | iDRAC 10 | PowerEdge 17G (2024-) | 최신 (DMTF 2024.x) | ✓ | ✓ | 신규 |
| HPE | iLO 4 | ProLiant Gen9 | <1.0 (OEM 의존) | ✗ | OEM `Systems/BaseNetworkAdapters` | |
| HPE | iLO 5 (펌2.x) | ProLiant Gen10/Gen10+ | 1.20.1 | ✗ Power만 | 1.10+ 표준 NA | BIOS path Gen10+ 분리 |
| HPE | iLO 6 | ProLiant Gen11+ | 1.13+ (DMTF 2024.1) | ✓ | ✓ 표준 | HBM memory 신규 |
| HPE | iLO 6 | ProLiant Compute Gen12 | 1.20.0 | ✓ | ✓ | **사용자 lab 검증** |
| Lenovo | IMM2 | System x (구) | <1.2 | ✗ | ✗ | withdrawn |
| Lenovo | XCC1 | ThinkSystem V1/V2 (SR550/650/850) | 1.15.0 | 부분 | 지원 | |
| Lenovo | XCC2 | ThinkSystem V3 | 1.20.0 | ✓ | ✓ | 신 |
| Lenovo | XCC3 | ThinkSystem 최신 | 1.17.0 | ✓ | ✓ | **사용자 사이트 후보** |
| Supermicro | X9 / 이전 | (ARM11) | 미지원 / 매우 제한 | ✗ | ✗ | IPMI only |
| Supermicro | X10 (AST 2500) | | 1.x 제한 | ✗ | ✗ | Redfish 도입 시작 |
| Supermicro | X11 (AST 2500) | | 1.x | ✗ Power만 | 부분 | |
| Supermicro | X12 (AST 2600) | | 1.x ~ 1.13 | ✓ 도입 | 지원 | Whitley/Tatlow |
| Supermicro | X13 (AST 2600) | | 최신 | ✓ | ✓ | |
| Supermicro | X14 (AST 2600) | | 1.21+ | ✓ | ✓ | ClearCMOS/NodeManager 신규 |
| Cisco | CIMC 3.0 | UCS C-series | 1.0.1 | ✗ Power만 | 지원 | 초기 Redfish |
| Cisco | CIMC 4.x | UCS C-series | 1.x | ✗ Power만 (확인 필요) | 지원 | 우리 lab 검증 |

## 영역별 Vendor 호환성 (P0~P3 priority)

### Power
- Dell iDRAC 8 / 7: `/Power` 만, 일부 모델 미지원 → cycle 2026-05-01 fix로 'not_supported' 분류 ✓
- Dell iDRAC 9 ≥5.x / 10: PowerSubsystem 둘 다. fallback 동작 검증 필요 (P0)
- HPE iLO 6 / Gen12: PowerSubsystem 권장. 우리 fallback 효과 (P0 검증)
- Lenovo XCC2-3: PowerSubsystem 권장 (P0)
- Supermicro X12+: PowerSubsystem 도입. X11 이하 Power만
- Cisco CIMC: Power 표준, PowerSubsystem 미확인 (P2)

### NetworkAdapters
- HPE iLO 5 (펌 2.x 초기): OEM `Systems/BaseNetworkAdapters` only — 우리 코드 미수집 (F4 P2)
- HPE iLO 5 (펌 2.x 후기) / iLO 6: 표준 `Chassis/NA` 지원
- 다른 vendor: 표준 path 통상 지원

### Memory
- HPE Gen11 HBM memory 신규 — 현재 코드 영향 가능 (BaseModuleType=HBM 처리?) (P2)
- 기타 vendor 표준 호환

### BIOS extensions (System.Oem)
- HPE Gen10: `/Systems/1/Bios/Oem/Hpe/Service`
- HPE Gen10+/Gen11: `/Systems/1/Bios/Oem/Hpe/BaseConfigs`
- BIOS 정보 자체는 system schema 표준 필드 — 우리 코드는 raw API 풍부 필드 활용 OK
- 다만 OEM extractor (vendor namespace 기반)에 영향 가능 — Gen10 vs Gen10+ 차이 확인 필요 (P3)

### AccountService (users)
- Cisco CIMC 일부: AccountService 제한적 / `not_supported` 정책 (B15 ticket)
- Dell iDRAC: `/Accounts/{slot_uri}` PATCH (slot 기반)
- HPE/Lenovo/Supermicro: POST 방식 (Account 신규 생성)
- 우리 cycle 2026-04-28 P2 분기 코드 이미 처리

### ESXi (Round 2 보조)
- vSphere 7 → 8 upgrade path: 7.0 U3w → 8.0 U3g
- pyvmomi version 호환성 매핑 — 라이브러리 버전 ↔ vSphere 버전 정합 의무
- esxcli 명령은 7/8 양립 OK

## R2 발견 사항 추가 (R1 위에 추가)

| # | 영역 | 발견 | 우선 |
|---|---|---|---|
| F9 | system | HPE Gen10/Gen10+/Gen11 BIOS path Oem 위치 변경 — OEM extractor 영향 가능 | P3 |
| F10 | memory | HPE Gen11 HBM memory 모듈 신규 — BaseModuleType=HBM enum 추가 검토 | P2 |
| F11 | network_adapters | HPE iLO 5 초기 펌웨어 BaseNetworkAdapters fallback 미구현 (F4와 동일) | P2 |
| F12 | power | Cisco CIMC PowerSubsystem 지원 여부 미확인 — 검증 필요 | P2 |
| F13 | users | Cisco CIMC AccountService 제한 — 'not_supported' 분류 적용 (cycle 2026-05-01 인프라 활용) | P1 |
| F14 | system | Dell iDRAC 10 (17G PowerEdge, 2024-) 신규 — 호환성 사전 검증 필요 | P3 |
| F15 | system | Supermicro X9 / X10: 우리 adapter `supermicro_x9.yml` 정확성 — Redfish 사실상 미지원 | P3 |

## R3 진입 시 검색 주제

- GitHub `dell/iDRAC-Redfish-Scripting` open issues
- HPE `ilo-rest-api-docs` repo issues
- DMTF `Redfish-Service-Validator` issue tracker
- Redfish Forum 사용자 보고 사례
- Lenovo XCC firmware release notes의 known issue

## Sources

- [Dell iDRAC9 Redfish API](https://www.dell.com/support/kbdoc/en-us/000178045/redfish-api-with-dell-integrated-remote-access-controller)
- [iDRAC10 17G PowerEdge](https://www.dell.com/support/kbdoc/en-us/000178045/)
- [HPE iLO 6 Adapting from iLO 5](https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/ilo6/ilo6_adaptation)
- [HPE Gen10 vs Gen11 ProLiant](https://www.globalonetechnology.com/blog/hpe-gen10-vs-gen11-proliant-servers-key-differences/)
- [Lenovo XCC support on ThinkSystem](https://lenovopress.lenovo.com/lp0880-xcc-support-on-thinksystem-servers)
- [Lenovo IMM2 (withdrawn)](https://lenovopress.lenovo.com/tips0849-imm2-support-on-lenovo-servers)
- [Supermicro Redfish (X14 ASPEED 2600)](https://www.supermicro.com/manuals/other/RedfishUserGuide.pdf)
- [Cisco CIMC Redfish 4.3](https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/api/4_3/b-cisco-ucs-c-series-servers-rest-api-programmer-s-guide-release-4-3/m-cisco-imc-rest-api-overview.html)
- [Cisco CIMC Redfish examples 4.2](https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/api/3_0/b_Cisco_IMC_REST_API_guide_301/m_redfish_api_examples.html)

## 갱신 history

- 2026-05-01: R2 5 vendor 검색 완료 (7건 fix 후보 추가 — F9~F15)
