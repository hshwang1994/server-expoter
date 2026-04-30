# Coverage — cpu 영역 (Processor schema)

## 채널

- **Redfish**: `/redfish/v1/Systems/{id}/Processors/{cpu_id}`
- **OS Linux**: `/proc/cpuinfo` + `lscpu`
- **OS Windows**: `Win32_Processor` (WMI)
- **ESXi**: pyvmomi `HostSystem.summary.hardware.cpuModel/numCpuCores/numCpuThreads`

## 표준 spec (R1)

### Processor schema 필드 (DMTF v1.x)

- `ProcessorType` enum: **CPU** / GPU / FPGA / DSP / Accelerator / **Core** (신규)
- `Manufacturer`, `Model`, `Socket`, `MaxSpeedMHz`
- `TotalCores`, `TotalThreads`, **`TotalEnabledCores`** (신규)
- `ProcessorArchitecture` (x86/ARM/IA-64 등), `InstructionSet` (x86-64 등)
- `Status.State` (Enabled/Disabled/Absent)
- `SerialNumber`, `PartNumber`
- `ProcessorId.IdentificationRegisters` (CPUID 등)

## Vendor 호환성 (R2)

| Vendor | TotalCores/Threads | Architecture | OEM 분리 |
|---|---|---|---|
| Dell iDRAC 8/9 | OK | OK | DellSystem.Oem |
| HPE iLO 5/6 | OK | OK | Hpe.Bios |
| Lenovo XCC | OK | OK | Lenovo OEM 일부 |
| Supermicro X11+ | OK | OK | |
| Cisco CIMC | OK | OK | trailing whitespace 정규화 |

## 알려진 사고 (R3)

### C1 — GPU/Accelerator 가 Processor 컬렉션에 함께 (Dell R760 Tesla T4)
- **증상**: GPU 가 `/Systems/.../Processors/` 컬렉션에 함께 노출 → cpu.summary.groups 잘못 합산
- **fix 적용됨**: cycle 2026-04-29 fix B01 — `ProcessorType=='CPU'` filter (또는 빈 값 → CPU 가정 legacy 호환) ✓

### C2 — F2: ProcessorType 신규 enum 'Accelerator' / 'Core'
- **증상**: 현재 코드 `ptype == 'CPU' or ptype == ''` 만 통과. 'Core' (개별 logical core) 가 응답되면 누락
- **현재 코드 영향**: 일반 PC/서버는 'CPU' 만 응답. 'Core' 는 deep CPU detail (드물게)
- **우선**: P2 (lab fixture 확보 후 검증)
- **fix 후보 (Additive)**: filter에 `ptype in ('CPU', '', 'Core')` 추가. legacy 동작 유지

### C3 — TotalThreads 누락 (일부 펌웨어)
- **증상**: per-processor TotalThreads = 0 / null
- **fix 적용됨**: BUG-13 — `System.ProcessorSummary.LogicalProcessorCount` fallback ✓

### C4 — `ProcessorSummary.Status.Health` HPE 미제공
- **fix 적용됨**: HealthRollup fallback ✓

## fix 후보 (cpu 영역, additive only)

### F2 — ProcessorType 'Accelerator' / 'Core' 통과
- **현재 위치**: `redfish-gather/tasks/normalize_standard.yml:25-32` filter
- **변경 (Additive)**: `if ptype in ('CPU', '', 'CORE')` (대문자 정규화 유지). 'GPU' / 'FPGA' / 'DSP' 는 여전히 제외
- **회귀**: lab Dell R760 Tesla T4 fixture (이미 존재) — GPU 제외 유지 검증
- **신규 fixture 필요**: ARM 서버 또는 'Core' 응답 fixture (아직 없음)
- **우선**: P2

## 우리 코드 위치

- 라이브러리: `redfish-gather/library/redfish_gather.py:1085` `gather_processors`
- normalize filter: `redfish-gather/tasks/normalize_standard.yml:22-32` ProcessorType filter
- summary 합산: `redfish-gather/tasks/normalize_standard.yml:228-247` `_rf_summary_cpu`
- OS: `os-gather/tasks/{linux,windows}/gather_cpu.yml`

## Sources

- [Redfish Processor schema](https://redfish.dmtf.org/redfish/schema_index)
- [Lenovo XCC CPU GET](https://pubs.lenovo.com/xcc-restapi/cpu_properties_get)

## 갱신 history

- 2026-05-01: R1+R2+R3 / C1~C4 사고 / F2 fix 후보 (P2)
