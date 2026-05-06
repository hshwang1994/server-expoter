# M-F2 — 3채널 (Redfish/OS/ESXi) JSON 키 비교

> status: [PENDING] | depends: M-F1 | priority: P2 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-F1 의 "4. 채널별 차이" 절을 별도 상세 절로 확장. Redfish / OS / ESXi 세 채널이 같은 envelope 형식이지만 sections / data / errors 의 구체적 키와 의미가 어떻게 다른지 표 형식 비교.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/20_json-schema-fields.md` (M-F1 산출물 확장) — 별도 절 또는 부록 |
| 리스크 | LOW |

## 작업 spec

### (A) 채널별 sections 매트릭스

| section | Redfish | OS Linux | OS Windows | ESXi |
|---|---|---|---|---|
| system | ServiceRoot + Systems | /etc/os-release + uname | systeminfo / WMI | esxcli system |
| hardware | Chassis | dmidecode | Get-CimInstance Win32_ComputerSystemProduct | esxcli hardware |
| bmc | Managers | n/a | n/a | n/a |
| cpu | Systems.Processors | /proc/cpuinfo | Win32_Processor | esxcli hardware cpu |
| memory | Systems.Memory | /proc/meminfo + dmidecode | Win32_PhysicalMemory | esxcli hardware memory |
| storage | Systems.Storage + Volumes | lsblk + lsscsi | Get-Disk + Get-PhysicalDisk | esxcli storage |
| network | Systems.EthernetInterfaces | ip / ethtool | Get-NetAdapter | esxcli network |
| firmware | UpdateService | (n/a — OS 단에서 미수집) | Get-WindowsDriver (한정) | esxcli software |
| users | AccountService.Accounts | n/a | n/a | n/a |
| power | Chassis.Power / PowerSubsystem | n/a | n/a | n/a |

### (B) 같은 키 다른 의미 (주의)

| 키 | Redfish | OS Linux | OS Windows | ESXi |
|---|---|---|---|---|
| `data.cpu.model` | Systems.Processors[0].Model | /proc/cpuinfo "model name" | Win32_Processor.Name | esxcli hardware cpu list |
| `data.memory.total_gb` | sum(Memory.CapacityMiB) / 1024 | dmidecode physical_installed | sum(Win32_PhysicalMemory.Capacity) | esxcli hardware memory get |
| `data.storage.disks[].media_type` | DriveType (HDD/SSD/SSD/NVMe) | lsblk + smartctl 추정 | MediaType (HDD/SSD/Unspecified) — Windows 정규화 (cycle 2026-04-29) | (esxcli) |
| `data.network.interfaces[].mac` | MAC | ip link | NetAdapter.MacAddress | (esxcli) |

### (C) 채널 고유 키

#### Redfish only

| 키 | 의미 |
|---|---|
| `data.bmc.firmware_version` | BMC 펌웨어 |
| `data.bmc.network_protocols` | SSH / WinRM / Redfish enabled |
| `data.firmware.list[]` | UpdateService 의 firmware list |
| `data.users.accounts[]` | AccountService.Accounts |
| `data.power.psu_redundancy` | Chassis.Power.Redundancy |

#### OS Linux only

| 키 | 의미 |
|---|---|
| `data.system.python_mode` | python_ok / raw_only / raw_forced |
| `data.system.selinux_status` | enabled / disabled (raw 정규화 — cycle Round 2 fix) |
| `data.network.bridges[]` | bridge / VLAN / container NIC topology |

#### OS Windows only

| 키 | 의미 |
|---|---|
| `data.system.runtime_swap` | namespace pattern (cycle 2026-04-29 fix) |
| `data.network.interface_index_grouping` | InterfaceIndex 기반 grouping |

#### ESXi only

| 키 | 의미 |
|---|---|
| `data.system.vsphere_version` | ESXi 버전 |
| `data.network.dns` | DNS dict-level drill-in (cycle 2026-04-29 fix) |
| `data.network.netmask_bits` | /22, /26, /28 netmask bit 카운팅 |
| `data.system.auth_success` | vendor_aliases.yml 정규화 + true (cycle 2026-04-29) |

### (D) 정규화 규칙 차이

각 채널이 같은 의미의 데이터를 어떻게 다른 source 에서 가져와 정규화하는지:

```
data.cpu.cores
  Redfish:  Systems.Processors[].TotalCores → sum
  Linux:    /proc/cpuinfo "cpu cores" * 소켓 수 (정규화)
  Windows:  Win32_Processor.NumberOfCores * 소켓 수
  ESXi:     esxcli hardware cpu list | wc -l (정규화)
```

### (E) status 판정 차이

| 채널 | not_supported 케이스 |
|---|---|
| Redfish | endpoint 404 → not_supported (DMTF 표준 변천 fallback 후) |
| OS Linux | 명령 출력 없음 / Python 미설치 → raw fallback |
| OS Windows | WMI 조회 실패 / WinRM 미연결 → not_supported |
| ESXi | esxcli 명령 실패 / vSphere 응답 없음 → not_supported |

## 회귀 / 검증

- 마크다운 정합성
- 각 채널 baseline JSON 과 본 문서 매트릭스 일치 검증

## risk

- (LOW) 채널별 정규화 코드와 drift 위험

## 완료 조건

- [ ] M-F1 docs/20 의 "4. 채널별 차이" 절 확장 또는 별도 부록
- [ ] (A) sections 매트릭스 (10 row × 4 col)
- [ ] (B) 같은 키 다른 의미 (주요 4건)
- [ ] (C) 채널 고유 키 list
- [ ] (D) 정규화 규칙 차이 예시 3건
- [ ] (E) status 판정 차이 표
- [ ] commit: `docs: [M-F2 DONE] 3채널 JSON 키 비교 매트릭스`

## 다음 세션 첫 지시 템플릿

```
M-F2 3채널 비교 진입.

선행: M-F1 [DONE]

읽기 우선순위:
1. fixes/M-F2.md
2. M-F1 산출물 (docs/20)
3. schema/baseline_v1/dell_baseline.json (Redfish)
4. schema/baseline_v1/rhel810_raw_fallback.json (OS Linux)
5. (Windows / ESXi baseline 있으면)
6. os-gather/, esxi-gather/ tasks (정규화 코드)

작업:
1. (A) sections 매트릭스
2. (B) 같은 키 다른 의미
3. (C) 채널 고유 키
4. (D) 정규화 차이
5. (E) status 차이
```

## 관련

- rule 13 R5 / rule 96 R1-B
- 정본: schema/sections.yml, schema/field_dictionary.yml
- 정본: build_*.yml (3 채널 normalize)
