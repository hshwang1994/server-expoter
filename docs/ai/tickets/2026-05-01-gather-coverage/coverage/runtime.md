# Coverage — runtime 영역 (uptime / load / process)

## 채널

- **OS Linux**: `/proc/uptime`, `/proc/loadavg`, `who -b`
- **OS Windows**: `Get-CimInstance Win32_OperatingSystem` (LastBootUpTime), `Get-Process`
- **ESXi**: `esxcli system stats uptime get`
- Redfish: 미수집

## 표준 spec (R1)

### Linux
- `/proc/uptime`: 두 정수 (uptime_seconds, idle_seconds)
- `/proc/loadavg`: load1 / load5 / load15 / running_processes / total / last_pid
- `who -b`: boot time
- `pidstat` (sysstat): per-process load
- `swapon -s` / `/proc/swaps`: swap status

### Windows
- `Win32_OperatingSystem.LastBootUpTime` (CIM datetime: 'YYYYMMDDHHMMSS.ffffff+TZD')
- `Get-CimInstance Win32_PageFileUsage` — pagefile (swap 등가)
- `Get-Process` — 실행 프로세스
- `Get-CimInstance Win32_Service` — 서비스

### ESXi
- `esxcli system stats uptime get` (microsec 단위)
- `esxcli system process list`

## Vendor 호환성 (R2) — OS 별

| OS | uptime path | swap | last_boot |
|---|---|---|---|
| RHEL 7/8/9 | /proc/uptime | swapon | who -b |
| Ubuntu | /proc/uptime | swapon | who -b |
| Rocky / Alma | /proc/uptime | swapon | who -b |
| SLES | /proc/uptime | swapon | who -b |
| Alpine | /proc/uptime | 부분 | who 부재 가능 |
| Windows Server 2012/2016 | LastBootUpTime | PageFileUsage | OK |
| Windows Server 2019/2022 | LastBootUpTime | PageFileUsage | OK |
| Windows 11 / Win Server 2025 | OK | OK | OK |
| ESXi 6.5/6.7/7/8 | esxcli uptime | — | — |

## 알려진 사고 (R3)

### Rt1 — Windows runtime swap_total_mb 합산 버그
- **증상**: cycle-016 namespace fix가 memory/storage만 적용, runtime 누락 → 마지막 pagefile 크기만 emit
- **fix 적용됨**: production-audit 2026-04-29 — 9 파일 namespace pattern 수정 ✓

### Rt2 — Windows runtime InterfaceIndex grouping
- **fix 적용됨**: 같은 cycle ✓

### Rt3 — Linux LANG=C 정규화
- **증상**: locale에 따라 명령 출력 형식 다름 (예: who 출력 한글)
- **fix 적용됨**: cycle 2026-04-30 — `export LANG=C LC_ALL=C` ✓

### Rt4 — VLAN underscore 처리 (Linux network)
- **fix 적용됨**: production-audit ✓

### Rt5 — Filesystem allow-list (Linux)
- **fix 적용됨**: production-audit ✓

### Rt6 — df '-' parse 방어
- **증상**: df 출력에 '-' (mount point 없음 등)
- **fix 적용됨**: production-audit ✓

### Rt7 — Alpine / minimal container 'who' 부재
- **현재 코드 영향**: graceful (failed_when:false). 빈 결과
- **우선**: P3 (F23의 일부)

## fix 후보 (runtime 영역)

현재 fix 적용 완료. F23 OS 점진 전환에 통합 (모든 OS gather 미지원 분류).

## 우리 코드 위치

- Linux: `os-gather/tasks/linux/gather_runtime.yml`
- Windows: `os-gather/tasks/windows/gather_runtime.yml`
- ESXi: `esxi-gather/tasks/collect_runtime.yml`

## Sources

- [Linux uptime / loadavg](https://www.kernel.org/doc/Documentation/filesystems/proc.txt)
- [Win32_OperatingSystem CIM](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-operatingsystem)
- [VMware ESXi build numbers](https://knowledge.broadcom.com/external/article/316595/build-numbers-and-versions-of-vmware-esx.html)

## 갱신 history

- 2026-05-01: R1+R2+R3 / Rt1~Rt7 / fix 후보 통합 (F23)
