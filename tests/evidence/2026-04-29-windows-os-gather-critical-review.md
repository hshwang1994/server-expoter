# Windows OS Gather — 비판적 검증 + 일괄 fix (2026-04-29)

## 개요

사용자 의심: "Windows OS에 실제 데이터가 수집안되는게 많거나 값이 이상한게 있다."
- 작업 범위: `os-gather/tasks/windows/*.yml` 8 파일 + adapter
- 검증 방법:
  - Jenkins agent (10.100.64.154) SSH 접속
  - 실 Windows VM (10.100.64.135 / horizon-cs.gooddi.lab / Windows Server 2022 / VMware VM) 대상
  - ansible-playbook 실행 → JSON output 캡처
  - 동일 VM에 직접 PowerShell raw 쿼리 실행 → 비교
  - rule 95 R1 11종 의심 패턴 스캔

## 검증 환경

| 항목 | 값 |
|---|---|
| Jenkins agent | 10.100.64.154 (Ubuntu 24.04, ansible-core 2.20.3) |
| Windows VM | 10.100.64.135 / horizon-cs.gooddi.lab |
| OS | Microsoft Windows Server 2022 Standard Evaluation, build 20348 21H2 |
| Hardware | VMware20,1, Intel(R) Xeon(R) Silver 4510, 8GB, 300GB SAS |
| Locale | en-US (Pacific Standard Time, en-US culture) |
| Domain | gooddi.lab (Domain-joined) |

## 발견된 데이터 누락 / 값 이상 (Before)

| # | 섹션 | 필드 | 출력값 (수정 전) | 진실 (raw PowerShell) | 원인 |
|---|---|---|---|---|---|
| 1 | memory | slots | `[]` (빈) | 1개 슬롯 8192MB | 코드 logic 문제 (이전 ver. `slots: []` 하드코딩) |
| 2 | memory | slot.speed_mhz | `null` | `4800` (ConfiguredClockSpeed) | Win32_PhysicalMemory.Speed가 VMware/일부 BIOS에서 null. ConfiguredClockSpeed fallback 누락 |
| 3 | memory | slot.type | `"3"` (raw int) | DDR/DDR4/DDR5 enum 또는 null | SMBIOSMemoryType switch가 24/26/34/0만 처리. 18/19/22/27/30/35 등 미매핑 |
| 4 | memory | slot.serial | `"00000001"` | (의미 없는 sentinel) | "VMware Virtual RAM"의 placeholder serial. 센티널 필터 미적용 |
| 5 | storage | physical_disks.media_type | `"Fixed hard disk media"` | "HDD" 또는 null | Get-PhysicalDisk fallback 후 Win32_DiskDrive raw 문자열을 잘못 매핑. fallback regex `(?i)fixed|external|removable` → 항상 HDD로 강제 매핑 (실제로 SSD 정보 없음에도) |
| 6 | storage | physical_disks.protocol | `null` | "SAS" | Get-PhysicalDisk.BusType이 PS7+에서 enum **string** ("SAS")로 반환. 코드는 `[int]$_.BusType`으로 cast → 0 → switch default → null |
| 7 | storage | physical_disks.health | `null` | "healthy" (HealthStatus="Healthy") | HealthStatus / OperationalStatus 매핑 누락 |
| 8 | cpu | model | `"INTEL(R) XEON(R) SILVER 4510"` | (정규화 표기 부재) | VMware/Hyper-V는 Win32_Processor.Name을 ALL CAPS로 노출. Linux와 표기 불일치 |
| 9 | hardware | uuid | `null` | `"39E43442-..."` (실제) | Win32_ComputerSystem.UUID = $null on VMware. ansible_product_uuid (Win32_ComputerSystemProduct) fallback 누락 |
| 10 | hardware | asset_tag | `"No Asset Tag"` | (의미 없는 OEM placeholder) | Sentinel 필터 누락 |
| 11 | hardware | chassis_type | `"1"` (raw int) | "Other" (enum) | Chassis enum 매핑 누락 |
| 12 | hardware | bios_date | `"01/23/2025 16:00:00"` | "2025-01-23" (ISO) | CIM datetime → ISO 변환 누락 |
| 13 | runtime | timezone | `"Pacific Standard Time"` (Windows ID) | "America/Los_Angeles" (IANA) | Linux/표준 표기와 일관성 누락 |
| 14 | runtime | ntp_synchronized | `false` (한국어 Windows에서) | true (실제 동기화 됨) | `w32tm /query /status` 출력은 OS locale 의존. "Last Successful Sync Time" 영문 패턴만 매칭 → ko-KR/ja-JP 서버에서 항상 false |
| 15 | runtime | ntp_last_sync | `"4/29/2026 1:36:06 AM"` (locale-aware) | "2026-04-29T08:36:06Z" (ISO/UTC) | Locale-aware 문자열 그대로 노출 |
| 16 | network | interfaces.subnet_mask | `null` | "255.255.255.0" | prefix_length=24만 노출. Linux는 mask까지 채움 — 일관성 누락 |

추가로 수집 안 되는 / 누락 항목 (사용자 지시: 새 키 추가 금지 → 보고만):
- 도메인-가입 서버에서 Administrators 그룹의 도메인 멤버 (`GOODDI\Domain Admins`) — `Get-LocalUser`만 사용하므로 누락. 별도 키 필요 → 보류.
- Disk SerialNumber — 기존 schema에 필드 없음. 보류.

## 적용된 fix

### B-MEM-1 / 2 / 3: gather_memory.yml

```powershell
# 변경 전
type = switch ($_.SMBIOSMemoryType) {
  24 {"DDR3"} 26 {"DDR4"} 34 {"DDR5"} 0 {$null}
  default { [string]$_.SMBIOSMemoryType }
}
speed_mhz = $_.Speed
serial    = $_.SerialNumber

# 변경 후
$smt = [int]$_.SMBIOSMemoryType
$type = switch ($smt) {
  18 {"DDR"} 19 {"DDR2"} 20 {"DDR2 FB-DIMM"} 22 {"DDR3"} 24 {"DDR3"}
  26 {"DDR4"} 27 {"LPDDR"} 28 {"LPDDR2"} 29 {"LPDDR3"} 30 {"LPDDR4"}
  34 {"DDR5"} 35 {"LPDDR5"}
  default { $null }
}
$speedRaw = if ($_.Speed -and [int]$_.Speed -gt 0) { [int]$_.Speed }
            elseif ($_.ConfiguredClockSpeed -and [int]$_.ConfiguredClockSpeed -gt 0) { [int]$_.ConfiguredClockSpeed }
            else { $null }
$is_virtual_mem = $mfrRaw -match '(?i)vmware|hyper-?v|microsoft|qemu|kvm|virtual|xen'
$serNorm = if (... or ($is_virtual_mem -and $serRaw -match '^0{6,}\d?$') ...) { $null } else { $serRaw }
```

### B-STO-1 / 2 / 4: gather_storage.yml

```powershell
# Get-PhysicalDisk: PS5.1 int / PS7+ enum string 양쪽 처리
$btRaw = $_.BusType
$bus = if ($btRaw -is [int]) { switch ([int]$btRaw) { 6{'SATA'} 10{'SAS'} 17{'NVMe'} ... } }
       else { switch ([string]$btRaw) { 'SATA'{'SATA'} 'SAS'{'SAS'} 'NVMe'{'NVMe'} ... } }

# HealthStatus → health 매핑
$hs = [string]$_.HealthStatus
$health = switch ($hs) { 'Healthy'{'healthy'} 'Warning'{'warning'} 'Unhealthy'{'unhealthy'} default{$null} }

# Win32_DiskDrive fallback: "Fixed hard disk media" → null (잘못된 HDD 추정 차단)
if ($rawMt -match '(?i)solid state|ssd') { $mt = 'SSD' }
else { $mt = $null }
```

### B-CPU-1: gather_cpu.yml

```powershell
function Normalize-CpuModel($n) {
  if (-not $n) { return $null }
  if ($n -cmatch '[a-z]') { return $n }  # already mixed-case
  $tokens = @{ 'INTEL'='Intel'; 'XEON'='Xeon'; 'SILVER'='Silver'; 'GOLD'='Gold'; ... }
  ...
}
```

### B-HW-1 / 2 / 3 / 4: gather_hardware.yml

```powershell
# UUID fallback: cs.UUID → cs_product.UUID (ansible_product_uuid 동일 source)
$uuid = if ($cs.UUID) { $cs.UUID }
        elseif ($csp -and $csp.UUID) { $csp.UUID }
        else { $null }
if ($uuid -in @('00000000-0000-0000-0000-000000000000', ...)) { $uuid = $null }

# Asset tag sentinel
$asset = if (-not $assetRaw -or $assetRaw -in @('No Asset Tag','Default string', ...)) { $null } else { $assetRaw }

# Chassis enum (SMBIOS 7.4.1)
$chassisMap = @{ 1='Other'; 2='Unknown'; 3='Desktop'; 17='Main Server Chassis'; 23='Rack Mount Chassis'; ... }

# BIOS date ISO
$biosDate = ([datetime]$bios.ReleaseDate).ToString('yyyy-MM-dd')
```

### B-RT-1 / 2: gather_runtime.yml

```powershell
# Timezone Windows ID → IANA 매핑
$tzMap = @{
  'Korea Standard Time' = 'Asia/Seoul'
  'Tokyo Standard Time' = 'Asia/Tokyo'
  'Pacific Standard Time' = 'America/Los_Angeles'
  ...
}

# Locale-free sync detection (w32tm /query /source)
$source = (w32tm /query /source).Trim()
$is_synced = ($source -and $source -ne 'Local CMOS Clock' -and $source -notmatch 'Free-running')

# ISO normalize last_sync timestamp
$sync_iso = ([datetime]::Parse($sync.Trim())).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
```

### B-NET-3: gather_network.yml

```jinja
{# windows-audit (2026-04-29): prefix_length → subnet_mask 자동 계산 (Linux 일관) #}
{%- set p = n.prefix | default(0) | int -%}
{%- set mask = none -%}
{%- if p > 0 and p <= 32 -%}
  {%- set bits = 4294967296 - 2 ** (32 - p) -%}
  {%- set mask = '%d.%d.%d.%d' % ((bits // 16777216) % 256, (bits // 65536) % 256, (bits // 256) % 256, bits % 256) -%}
{%- endif -%}
```

### Skip (revert): gather_users.yml

- `Get-LocalGroupMember -Name $key_groups` 인덱스 빌드 (N×M → N+M) 시도 → ansible-playbook task loader가 "unbalanced jinja2 block or quotes" 에러로 reject
- 원인 미상 (구조적으로 동등한 PowerShell이 원본에서는 작동). 격리 시간 비용 큼
- 결정: 데이터 정확성 fix가 아닌 **효율성 개선** → revert. 다른 fix는 모두 적용

## 실측 검증 결과 (Before vs After, 동일 VM 10.100.64.135)

| 필드 | Before | After |
|---|---|---|
| `memory.slots` | `[]` | `[{capacity_mb: 8192, speed_mhz: 4800, manufacturer: "VMware Virtual RAM", part_number: "VMW-8192MB", serial: null}]` |
| `memory.slots[0].speed_mhz` | (n/a) | `4800` |
| `storage.physical_disks[0].media_type` | `"Fixed hard disk media"` | `"HDD"` |
| `storage.physical_disks[0].protocol` | `null` | `"SAS"` |
| `storage.physical_disks[0].health` | `null` | `"healthy"` |
| `cpu.model` | `"INTEL(R) XEON(R) SILVER 4510"` | `"Intel(R) Xeon(R) Silver 4510"` |
| `hardware.uuid` | `null` | `"39E43442-73A7-5AEB-E472-C837FEE75510"` |
| `hardware.asset_tag` | `"No Asset Tag"` | `null` |
| `hardware.chassis_type` | `"1"` | `"Other"` |
| `hardware.bios_date` | `"01/23/2025 16:00:00"` | `"2025-01-23"` |
| `runtime.timezone` | `"Pacific Standard Time"` | `"America/Los_Angeles"` |
| `runtime.ntp_synchronized` | (locale-aware false on ko-KR) | `true` (locale-free) |
| `runtime.ntp_last_sync` | `"4/29/2026 1:36:06 AM"` | `"2026-04-29T08:36:06Z"` |
| `network...subnet_mask` | `null` | `"255.255.255.0"` |

상태 모두 `success`. JSON envelope 13 필드 무결.

## 수정 파일 목록

| 파일 | 변경 |
|---|---|
| `os-gather/tasks/windows/gather_memory.yml` | SMBIOS 매핑 + Speed fallback + serial sentinel |
| `os-gather/tasks/windows/gather_storage.yml` | BusType string 처리 + media fallback 정정 + health 매핑 |
| `os-gather/tasks/windows/gather_cpu.yml` | CPU model 정규화 (Normalize-CpuModel) |
| `os-gather/tasks/windows/gather_hardware.yml` | UUID/AssetTag/Chassis/bios_date 정규화 |
| `os-gather/tasks/windows/gather_runtime.yml` | Timezone IANA + locale-free sync + ISO last_sync |
| `os-gather/tasks/windows/gather_network.yml` | prefix → subnet_mask 자동 계산 |
| `os-gather/tasks/windows/gather_users.yml` | (변경 없음 — 효율성 개선 시도 후 revert) |

JSON envelope 13 필드 / sections 10 / field_dictionary 변경 없음 (사용자 지시 준수).

## 이전 Production 배포 코드와의 차이

Jenkins agent (`/home/cloviradmin/clovirone-portal`)의 코드는 Mar 30 시점:
- gather_hardware.yml / gather_runtime.yml 미존재 → hardware/runtime 섹션 자체 not_supported
- gather_memory: `slots: []` 하드코딩 → 슬롯 정보 영원히 빈 list
- gather_storage: media_type "Fixed hard disk media" raw 누출

Local main HEAD (Apr 29 cycle-016 + production-audit) 위에 본 fix를 추가했다.

## 검증 명령

```bash
# Jenkins agent 환경
cd /var/tmp/se_audit_test
export ANSIBLE_CONFIG=$PWD/ansible.cfg REPO_ROOT=$PWD INVENTORY_JSON='[{"ip":"10.100.64.135"}]'
/opt/ansible-env/bin/ansible-playbook -i os-gather/inventory.sh os-gather/site.yml \
  -e "ansible_user=Administrator" -e "ansible_password=***"
```

생성된 JSON envelope의 13 필드 무결, status=success, 모든 fix 항목이 raw PowerShell 결과와 일치.

## 미해결 (정보 누락 보고만, 별도 키 필요 → 보류)

- 도메인 admin 그룹 멤버 — Get-LocalUser는 로컬만. `Get-LocalGroupMember Administrators` 결과의 비-로컬 멤버는 schema에 추가 키 없으면 표현 불가.
- Disk SerialNumber — Win32_DiskDrive.SerialNumber 있으나 `physical_disks` schema에 serial 키 없음.
- Memory SMBIOSMemoryType=3 (Synchronous, "기타") 하드 매핑 안 함 → null. (사용자 입장 의미 있는 표현은 "VMware Virtual" 같은 것이지만 mfr 필드로 이미 표현됨.)
- Korean / Japanese Windows의 w32tm `last_sync` ISO 변환은 영문 + 독일어 패턴만 시도. (한글 출력은 PS console encoding과 충돌 위험으로 패턴 제외 — 다른 locale에서는 last_sync=null이지만 ntp_synchronized는 정확.)
