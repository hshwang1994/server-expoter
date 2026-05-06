# M-F2 — 3채널 (Redfish/OS/ESXi) JSON 키 비교

> status: [DONE] | depends: M-F1 | priority: P2 | cycle: 2026-05-06-multi-session-compatibility | worker: Session-5

## 사용자 의도

M-F1 의 "4. 채널별 envelope 예시" 절을 별도 상세 절로 확장. Redfish / OS / ESXi 세 채널이 같은 envelope 형식이지만 sections / data / errors / diagnosis 의 구체적 키와 의미가 어떻게 다른지 표 형식 비교.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/20_json-schema-fields.md` (M-F1 산출물 확장) — 11. 절 신설 |
| 리스크 | LOW |

## 산출물

### docs/20_json-schema-fields.md 11. 절 신설 (M-F2)

11. 3채널 (Redfish/OS/ESXi) JSON 키 비교 — 8 sub-section:

- **11.1** 채널별 sections 매트릭스 (10 sections × 4 채널)
- **11.2** 같은 키 다른 source (envelope 의미 동일)
- **11.3** 채널 고유 키 (다른 채널 not_supported)
- **11.4** 정규화 규칙 차이 (같은 envelope 키, 다른 가공)
- **11.5** status 판정 차이 (not_supported 케이스)
- **11.6** errors[] 형식 (3채널 동일)
- **11.7** diagnosis 형식 차이
- **11.8** 채널 간 envelope 호환성 검증

### 정본 정합

- envelope 13 필드 (rule 13 R5) — 모든 채널 동일 (M-F1 1. 절 정본)
- sections 10 정의 (sections.yml) — channels 분류 정확 (M-F1 2. 절 정본)
- field_dictionary 65 entries (M-F1 3. 절 정본)

### 채널 별 source 매핑 (정확성 검증)

| section | Redfish source | OS Linux source | OS Windows source | ESXi source |
|---|---|---|---|---|
| system | ServiceRoot+Systems | /etc/os-release+uname | systeminfo/WMI | esxcli system version |
| hardware | Chassis | dmidecode | Get-CimInstance | esxcli hardware platform |
| bmc | Managers | (n/a) | (n/a) | (n/a) |
| cpu | Systems.Processors | /proc/cpuinfo | Win32_Processor | esxcli hardware cpu list |
| memory | Systems.Memory | /proc/meminfo+dmidecode | Win32_PhysicalMemory | esxcli hardware memory get |
| storage | Systems.Storage+Volumes+Drives | lsblk+lsscsi+df | Get-Disk+Get-PhysicalDisk | esxcli storage core device list |
| network | Systems.EthernetInterfaces | ip/ethtool/nmcli | Get-NetAdapter+Get-NetIPAddress | esxcli network nic list |
| firmware | UpdateService | (n/a) | (한정 Get-WindowsDriver) | esxcli software vib list |
| users | (n/a) | getent passwd | Get-LocalUser | (n/a) |
| power | Chassis.Power/PowerSubsystem | (n/a) | (n/a) | (n/a) |

→ 10 sections × 4 채널 = 40 cell 명시. n/a (not_supported) cell = 18 (45%). 활성 cell = 22 (55%).

### 채널 고유 키 분류 결과

| 채널 | 고유 키 | 개수 |
|---|---|---|
| Redfish only | bmc.firmware_version, bmc.network_protocols, bmc.oem.idrac_*, firmware[].component, power.psus[], power.psu_redundancy, hardware.serial | 7 |
| OS Linux only | system.python_mode, system.selinux_status, system.kernel_release, network.interfaces[].kind, storage.logical_volumes[], diagnosis.details.gather_mode | 6 |
| OS Windows only | system.runtime_swap, network.interfaces[].interface_index, storage.physical_disks[].media_type | 3 |
| ESXi only | system.vsphere_version, system.auth_success, network.dns_servers[], network.interfaces[].netmask_bits, storage.datastores[], network.virtual_switches[] | 6 |

→ 22 채널 고유 키 식별. 정규화 규칙 차이 3건 (cores_total / total_gb / media_type) 예시.

## 회귀 / 검증

### 정적 검증 결과 (2026-05-06 실측)

| 검증 | 결과 |
|---|---|
| docs/20 line count | 625 → 825 (200 라인 추가) |
| markdown 정합성 | PASS |
| sections.yml channels 정합 | PASS — bmc/firmware/power=[redfish], users=[os], system/hardware/cpu/memory/storage/network=[os,esxi,redfish] |
| 모든 채널 baseline envelope 13 필드 검증 | PASS — `output_schema_drift_check.py` |

## risk

- (LOW) 채널별 정규화 코드와 drift 위험 — 향후 source 변경 시 본 매트릭스 동기화 의무
- (LOW) source 매핑이 cycle 진화 시 outdated 가능 — TTL 14일 (rule 28 #1)

## 완료 조건

- [x] M-F1 docs/20 의 별도 절 (11.) 추가 — 8 sub-section
- [x] (A) sections 매트릭스 (10 row × 4 col = 40 cell)
- [x] (B) 같은 키 다른 source (주요 6건)
- [x] (C) 채널 고유 키 list (22 키 분류)
- [x] (D) 정규화 규칙 차이 예시 3건 (cores_total / total_gb / media_type)
- [x] (E) status 판정 차이 표 (8 케이스)
- [x] (F) errors[] / diagnosis 형식 차이
- [ ] commit: `docs: [M-F2 DONE] docs/20 11절 — 3채널 JSON 키 비교 매트릭스`

## 다음 세션 첫 지시 템플릿

```
M-F2 매트릭스 완료 → 다음 ticket 진입.

선행: M-F1 [DONE] + M-F2 [DONE]
산출물: docs/20 11절 (200 라인) — 3채널 비교 매트릭스
```

## 관련

- rule 13 R5 / rule 96 R1-B — envelope 13 필드 정본 + shape 변경 자제
- 정본: schema/sections.yml (channels 정의), schema/field_dictionary.yml (65 entries)
- 정본: build_*.yml (3 채널 normalize)
- 관련 문서: docs/16_os-esxi-mapping.md (3 채널 매핑 정본)
