# Compatibility Matrix — 2026-05-07 cycle 진입 baseline

> 9 vendor × N generation × 10 sections 매트릭스. cycle 진입 시점의 코드 path 가용성 + 사이트 검증 / lab 부재 / web sources 의존 영역 표시.

---

## 사이트 검증 4 vendor × 1 generation (Round PASS — 2026-05-07 commit `0a485823`)

| vendor | generation | 사이트 BMC | adapter file | vault | OEM tasks | baseline |
|---|---|---|---|---|---|---|
| Dell | iDRAC10 | 5대 | `adapters/redfish/dell_idrac10.yml` (priority=110) | `vault/redfish/dell.yml` (encrypted) | `redfish-gather/tasks/vendors/dell/` | `schema/baseline_v1/dell_baseline.json` |
| HPE | iLO7 | 1대 | `adapters/redfish/hpe_ilo7.yml` (priority=110) | `vault/redfish/hpe.yml` (encrypted) | `redfish-gather/tasks/vendors/hpe/` | `schema/baseline_v1/hpe_baseline.json` |
| Lenovo | XCC3 | 1대 | `adapters/redfish/lenovo_xcc3.yml` (priority=110) | `vault/redfish/lenovo.yml` (encrypted) | `redfish-gather/tasks/vendors/lenovo/` | `schema/baseline_v1/lenovo_baseline.json` |
| Cisco | UCS X-series | 1대 | `adapters/redfish/cisco_ucs_xseries.yml` (priority=120) | `vault/redfish/cisco.yml` (encrypted) | (Cisco 영역 OEM tasks 부재 — M-J1) | `schema/baseline_v1/cisco_baseline.json` |

→ **Out of scope (rule 92 R2)**: 위 4 vendor × 1 generation 코드 path **변경 금지**.

---

## 9 vendor × N generation 매트릭스 (cycle 진입 시점)

| vendor | generation | adapter | vault | OEM tasks | mock fixture | 사이트 검증 | 본 cycle 작업 |
|---|---|---|---|---|---|---|---|
| **Dell** | iDRAC (legacy) | `dell_idrac.yml` (priority=10) | dell.yml | tasks/vendors/dell/ | 없음 | × | M-H1 (origin + mock) |
| Dell | iDRAC8 | `dell_idrac8.yml` (priority=80) | dell.yml | tasks/vendors/dell/ | 없음 | × | M-H1 |
| Dell | iDRAC9 | `dell_idrac9.yml` (priority=100) | dell.yml | tasks/vendors/dell/ | 일부 | × | M-H1 |
| Dell | **iDRAC10** | `dell_idrac10.yml` (priority=110) | dell.yml | tasks/vendors/dell/ | 일부 | **[PASS]** | (out of scope) |
| **HPE** | iLO (legacy) | `hpe_ilo.yml` (priority=10) | hpe.yml | tasks/vendors/hpe/ | 없음 | × | M-H2 |
| HPE | iLO4 | `hpe_ilo4.yml` (priority=80) | hpe.yml | tasks/vendors/hpe/ | 없음 | × | M-H2 |
| HPE | iLO5 | `hpe_ilo5.yml` (priority=90) | hpe.yml | tasks/vendors/hpe/ | 일부 | × | M-H2 |
| HPE | iLO6 | `hpe_ilo6.yml` (priority=100) | hpe.yml | tasks/vendors/hpe/ | 일부 | × | M-H2 |
| HPE | **iLO7** | `hpe_ilo7.yml` (priority=110) | hpe.yml | tasks/vendors/hpe/ | 일부 | **[PASS]** | (out of scope) |
| HPE | Superdome Flex | `hpe_superdome_flex.yml` (priority=95) | hpe.yml | tasks/vendors/hpe/ (분기 보강 필요) | 없음 | × (lab 부재) | M-G1, M-G2 |
| **Lenovo** | BMC (legacy) | `lenovo_bmc.yml` (priority=10) | lenovo.yml | tasks/vendors/lenovo/ | 없음 | × | M-H3 |
| Lenovo | IMM2 | `lenovo_imm2.yml` (priority=80) | lenovo.yml | tasks/vendors/lenovo/ | 없음 | × | M-H3 |
| Lenovo | XCC | `lenovo_xcc.yml` (priority=100) | lenovo.yml | tasks/vendors/lenovo/ | 일부 | × | M-H3 |
| Lenovo | **XCC3** | `lenovo_xcc3.yml` (priority=110) | lenovo.yml | tasks/vendors/lenovo/ | 일부 | **[PASS]** | (out of scope) |
| **Supermicro** | BMC | `supermicro_bmc.yml` (priority=10) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B2 |
| Supermicro | X9 | `supermicro_x9.yml` (priority=70) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B2 |
| Supermicro | X10 | **(누락 — M-B1 신설)** | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B1 (신설) |
| Supermicro | X11 | `supermicro_x11.yml` (priority=80) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B2 |
| Supermicro | X12 | `supermicro_x12.yml` (priority=90) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B2 |
| Supermicro | X13 | `supermicro_x13.yml` (priority=100) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B2 |
| Supermicro | X14 | `supermicro_x14.yml` (priority=110) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B2 |
| Supermicro | H11/H12/H13/H14 (AMD) | (model_patterns 확장 필요) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B3 |
| Supermicro | ARS (ARM) | (model_patterns 확장 필요) | supermicro.yml | tasks/vendors/supermicro/ | 없음 | × | M-B3 |
| **Cisco** | BMC (legacy) | `cisco_bmc.yml` (priority=10) | cisco.yml | (없음 — M-J1 Cisco vendor task 신설) | 없음 | × | M-H4 + M-J1 |
| Cisco | CIMC C-series 1.x ~ 4.x | `cisco_cimc.yml` (priority=80) | cisco.yml | (없음) | 없음 | × | M-H4 + M-J1 |
| Cisco | UCS B-series / S-series | (model_patterns 확장 필요) | cisco.yml | (없음) | 없음 | × | M-H4 |
| Cisco | **UCS X-series** | `cisco_ucs_xseries.yml` (priority=120) | cisco.yml | (없음 — M-J1 신설 시 포함) | 일부 | **[PASS]** | (out of scope) |
| **Huawei** | iBMC 1.x ~ 5.x | `huawei_ibmc.yml` (priority=70) | **(없음 — M-A1 신설)** | (없음 — M-C2 신설) | 없음 | × (lab 부재) | M-A1 + M-C1 + M-C2 + M-C3 |
| **Inspur** | ISBMC | `inspur_isbmc.yml` (priority=70) | **(없음 — M-A2 신설)** | (없음 — M-D1 신설) | 없음 | × (lab 부재) | M-A2 + M-D1 + M-D2 |
| **Fujitsu** | iRMC S2/S4/S5/S6 | `fujitsu_irmc.yml` (priority=70) | **(없음 — M-A3 신설)** | (없음 — M-E2 신설) | 없음 | × (lab 부재) | M-A3 + M-E1 + M-E2 + M-E3 |
| **Quanta** | QCT BMC | `quanta_qct_bmc.yml` (priority=70) | **(없음 — M-A4 신설)** | (없음 — M-F1 신설) | 없음 | × (lab 부재) | M-A4 + M-F1 + M-F2 |

---

## sections × vendor 변형 매트릭스 (10 sections)

본 cycle M-I 영역 작업 — vendor / generation 별 응답 형식 변형 + fallback.

### sections 목록 (10)

| section | 표준 path (DMTF Redfish) | 변형 영역 |
|---|---|---|
| system | `/redfish/v1/Systems/{id}` | 표준 가까움 (M-I5) |
| hardware | `/redfish/v1/Chassis/{id}` | 표준 가까움 (M-I5) |
| bmc | `/redfish/v1/Managers/{id}` | vendor OEM namespace 노출 (M-I3) |
| cpu | `/redfish/v1/Systems/{id}/Processors/{id}` | 표준 가까움 (M-I5) |
| memory | `/redfish/v1/Systems/{id}/Memory/{id}` | 표준 가까움 (M-I5) |
| storage | `/redfish/v1/Systems/{id}/Storage/{id}/Volumes` + `/Drives` | **PLDM RDE / SmartStorage / OEM** 분기 큼 (M-I1) |
| network | `/redfish/v1/Systems/{id}/EthernetInterfaces` 또는 `/Chassis/{id}/NetworkAdapters` | NIC OEM driver / SR-IOV / OCP (M-I4) |
| firmware | `/redfish/v1/UpdateService/FirmwareInventory` | vendor OEM namespace 노출 (M-I3) |
| users | `/redfish/v1/AccountService/Accounts` | 표준 가까움 (M-I5) |
| power | `/redfish/v1/Chassis/{id}/Power` 또는 `/PowerSubsystem` | **Power deprecated → PowerSubsystem 마이그레이션** (M-I2) |

### Storage 변형 매트릭스 (M-I1)

| vendor | generation | Storage path | Volume strategy | OEM Drive |
|---|---|---|---|---|
| Dell | iDRAC10 | `/Systems/{id}/Storage/{id}/Volumes` (PLDM RDE) | 표준 | `Oem.Dell.DellPhysicalDisk` |
| Dell | iDRAC8/9 | `/Systems/{id}/Storage/{id}` | 표준 + OEM | `Oem.Dell.DellPhysicalDisk` |
| HPE | iLO5/6/7 | `/Systems/{id}/Storage/{id}` (SmartStorage) | OEM | `Oem.Hpe.SmartStorage*` |
| HPE | iLO4 | `/Systems/{id}/SmartStorage/ArrayControllers` (legacy) | OEM only | `Oem.Hpe.SmartStorageArrayController` |
| Lenovo | XCC/XCC3 | `/Systems/{id}/Storage/{id}` | 표준 + OEM | `Oem.Lenovo.AnyBay` |
| Lenovo | IMM2 | `/Systems/{id}/SimpleStorage` (legacy) | SimpleStorage only | (없음) |
| Cisco | UCS X-series | `/Systems/{id}/Storage/{id}` | 표준 | `Oem.Cisco.UCS_DriveExtension` |
| Supermicro | X11~X14 | `/Systems/{id}/Storage/{id}` | 표준 | (Oem 약함) |
| Supermicro | X9/X10 | `/Systems/{id}/SimpleStorage` (legacy) | SimpleStorage only | (없음) |
| Huawei | iBMC | `/Systems/{id}/Storage/{id}` | 표준 + OEM | `Oem.Huawei` |
| Inspur | ISBMC | `/Systems/{id}/Storage/{id}` | 표준 | `Oem.Inspur` |
| Fujitsu | iRMC | `/Systems/{id}/Storage/{id}` | 표준 + OEM | `Oem.Fujitsu` |
| Quanta | QCT | `/Systems/{id}/Storage/{id}` | 표준 | `Oem.Quanta_Computer_Inc` |

### Power 변형 매트릭스 (M-I2)

| vendor | generation | Power path | PowerSubsystem 지원 |
|---|---|---|---|
| Dell | iDRAC10 | `/Chassis/{id}/PowerSubsystem` | YES (DSP0268 v1.13+) |
| Dell | iDRAC9 5.x+ | `/Chassis/{id}/Power` + `/PowerSubsystem` | dual |
| Dell | iDRAC9 4.x | `/Chassis/{id}/Power` (legacy) | NO |
| HPE | iLO7 | `/Chassis/{id}/PowerSubsystem` | YES |
| HPE | iLO5/6 | `/Chassis/{id}/Power` + `/PowerSubsystem` | dual |
| HPE | iLO4 | `/Chassis/{id}/Power` (legacy) | NO |
| Lenovo | XCC3 | `/Chassis/{id}/Power` + `/PowerSubsystem` | dual |
| Lenovo | XCC | `/Chassis/{id}/Power` | NO |
| Cisco | UCS X-series | `/Chassis/{id}/PowerSubsystem` | YES |
| Cisco | CIMC | `/Chassis/{id}/Power` | NO |
| Supermicro | X12~X14 | `/Chassis/{id}/PowerSubsystem` | YES |
| Supermicro | X9~X11 | `/Chassis/{id}/Power` (legacy) | NO |
| Huawei | iBMC | `/Chassis/{id}/Power` + `/PowerSubsystem` | mostly dual |
| Inspur | ISBMC | `/Chassis/{id}/Power` | NO (확인 필요) |
| Fujitsu | iRMC | `/Chassis/{id}/Power` | NO (확인 필요) |
| Quanta | QCT | `/Chassis/{id}/Power` | NO (확인 필요) |

→ M-I2 fallback: PowerSubsystem 우선 시도 → 404 시 Power legacy path fallback (Additive).

---

## OEM namespace 매핑 (M-J1)

| vendor | OEM namespace | redfish_gather.py 분기 |
|---|---|---|
| Dell | `Oem.Dell` | 기존 |
| HPE | `Oem.Hpe` (legacy `Oem.Hp` fallback) | 기존 |
| Lenovo | `Oem.Lenovo` | 기존 |
| Supermicro | `Oem.Supermicro` | 기존 |
| Cisco | `Oem.Cisco` (또는 `Oem.Cisco_RackUnit`) | 기존 |
| Huawei | `Oem.Huawei` | M-J1 신설 (또는 검증) |
| Inspur | `Oem.Inspur` (또는 `Oem.Inspur_System`) | M-J1 신설 |
| Fujitsu | `Oem.Fujitsu` | M-J1 신설 |
| Quanta | `Oem.Quanta_Computer_Inc` (또는 `Oem.QCT`) | M-J1 신설 |

---

## 본 cycle 산출 후 예상 매트릭스

| 항목 | cycle 진입 | cycle 종료 (예상) | 증감 |
|---|---|---|---|
| adapter | 28 | 29 | +1 (Supermicro X10 신설) |
| vault encrypted | 5 | 9 | +4 (Huawei/Inspur/Fujitsu/Quanta 신설) |
| vendor OEM tasks | 4 | 9 | +5 (Cisco/Huawei/Inspur/Fujitsu/Quanta 신설) |
| mock fixture (vendor 별) | 4 (사이트 검증 vendor) | 13+ | +9 |
| baseline_v1 | 8 | 8 | 0 (lab 부재 vendor SKIP — rule 13 R4) |
| EXTERNAL_CONTRACTS entry | 일부 | 9 vendor × N gen 모든 영역 | 대폭 증가 |
| catalog 갱신 | — | 5종 (NEXT_ACTIONS / VENDOR_ADAPTERS / COMPATIBILITY-MATRIX / EXTERNAL_CONTRACTS / docs/13) | — |

---

## 관련

- rule 13 R4 (baseline 실측 기반)
- rule 28 R1 #12 (COMPATIBILITY-MATRIX 측정 대상)
- rule 50 R2 (vendor 추가 9단계 + 단계 10 lab 부재)
- rule 96 R1+R1-A (외부 계약 origin / web sources)
- INDEX.md / DEPENDENCIES.md / fixes/INDEX.md
