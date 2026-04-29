# 2026-04-29 Bug Ticket Verification (Comprehensive)

- raw redfish hosts captured: 3
- raw linux hosts captured: 6
- redfish envelopes: 9, os envelopes: 6


---
## B01: **VERIFIED**

r760-1 envelope shows GPU in cpu.summary.groups: [{'ip': '10.100.15.27', 'model': 'Tesla T4', 'mfg': 'NVIDIA Corporation'}]


**fix hint**: fix: redfish_gather.py Processors loop must filter ProcessorType=='CPU'


---
## B02: **VERIFIED**

7 envelope(s) carry 0.0.0.0/:: in dns_servers; HPE raw NameServers={'1__eth_1.json': ['0.0.0.0', '0.0.0.0', '0.0.0.0', '::', '::', '::'], '1__eth_2.json': ['0.0.0.0', '0.0.0.0', '0.0.0.0', '::', '::', '::'], '1__eth_3.json': [], '1__eth_collection.json': None}


**fix hint**: fix: redfish_gather.py DNS extraction must filter unspecified addresses


---
## B03: **VERIFIED**

failed envelope drift: [{'ip': '10.50.11.162', 'data_None_keys': ['system', 'hardware', 'bmc', 'cpu', 'memory', 'power'], 'data_empty_dict_or_list_keys': ['users', 'firmware'], 'sections_failed': ['system', 'hardware', 'bmc', 'cpu', 'memory', 'storage', 'network', 'firmware', 'power'], 'sections_not_supported': ['users'], 'auth_success': None, 'failure_stage': None, 'duration_ms': None}]


**fix hint**: fix: site.yml always block + build_output.yml — emit consistent shapes for all sections


---
## B04: **VERIFIED**

Ubuntu envelopes have 127.0.0.x; raw confirms /etc/resolv.conf has 127.0.0.53 stub: {'ubuntu-2404': {'resolv_conf_has_127': True, 'resolvectl_dns_servers_present': True, 'runtime_resolv_first_ns': ['nameserver 10.100.64.251', 'nameserver 10.100.64.251']}, 'ubuntu-r760-6-baremetal': {'resolv_conf_has_127': True, 'resolvectl_dns_servers_present': True, 'runtime_resolv_first_ns': ['nameserver 10.100.64.251']}}


**fix hint**: fix: collect_dns.yml — read resolvectl/run/systemd/resolve/resolv.conf when systemd-resolved active


---
## B05: **VERIFIED**

raw_fallback host has empty cpu.summary.groups: [{'ip': '10.100.64.161', 'gather_mode': 'python_incompatible', 'groups_count': 0}]


**fix hint**: fix: normalize_cpu.yml raw branch must populate summary.groups


---
## B06: **VERIFIED**

esxi summary groups undercount: [{'ip': '10.100.64.1', 'adapter_count': 6, 'actual_link_up': 2, 'summary_groups': [{'speed_mbps': None, 'link_type': None, 'quantity': 1, 'link_up_count': 0}], 'summary_quantity_sum': 1}, {'ip': '10.100.64.2', 'adapter_count': 6, 'actual_link_up': 3, 'summary_groups': [{'speed_mbps': None, 'link_type': None, 'quantity': 1, 'link_up_count': 0}], 'summary_quantity_sum': 1}, {'ip': '10.100.64.3', 'adapter_count': 5, 'actual_link_up': 2, 'summary_groups': [{'speed_mbps': None, 'link_type': None, 'quantity': 1, 'link_up_count': 0}], 'summary_quantity_sum': 1}]


**fix hint**: fix: esxi-gather/tasks/normalize_network.yml — group adapters by link_status+speed; null-safe key


---
## B07: **REJECTED**

Redfish envelope system.* not all None


---
## B08: **VERIFIED**

BMC product/mac/hostname None across vendors: [{'ip': '10.100.15.27', 'product': None, 'firmware_version': '7.10.70.00', 'mac': None, 'hostname': None}, {'ip': '10.100.15.28', 'product': None, 'firmware_version': '7.10.70.00', 'mac': None, 'hostname': None}, {'ip': '10.100.15.31', 'product': None, 'firmware_version': '7.10.70.00', 'mac': None, 'hostname': None}, {'ip': '10.100.15.33', 'product': None, 'firmware_version': '7.10.70.00', 'mac': None, 'hostname': None}, {'ip': '10.50.11.231', 'product': None, 'firmware_version': 'iLO 6 v1.73', 'mac': None, 'hostname': None}, {'ip': '10.100.15.34', 'product': None, 'firmware_version': '7.10.70.00', 'mac': None, 'hostname': None}, {'ip': '10.50.11.232', 'product': None, 'firmware_version': 'AFBT58B 5.70 2025-08-11', 'mac': None, 'hostname': None}, {'ip': '10.100.15.2', 'product': None, 'firmware_version': '4.1(2g)', 'mac': None, 'hostname': None}]


**fix hint**: fix: redfish_gather.py bmc extraction — populate product (iDRAC9/iLO6/XCC/CIMC mapping) + EthernetInterface mac/hostname


---
## B09: **VERIFIED**

all redfish envelopes have None locator on every slot; raw HPE Memory has DeviceLocator: {'proc1dimm1.json': {'DeviceLocator': 'PROC 1 DIMM 1', 'MemoryLocation': {'Channel': 8, 'MemoryController': 4, 'Slot': 1, 'Socket': 1}}, 'proc1dimm2.json': {'DeviceLocator': 'PROC 1 DIMM 2', 'MemoryLocation': {'Channel': 8, 'MemoryController': 4, 'Slot': 2, 'Socket': 1}}}


**fix hint**: fix: redfish_gather.py memory.slots — extract DeviceLocator (or MemoryLocation.Slot)


---
## B10: **VERIFIED**

all envelope disks have None capacity; raw has CapacityBytes: {'DE00C000__drive_0.json': {'CapacityBytes': 1920383410176, 'Model': 'SAMSUNGMZ7L31T9HBLT-00A07'}, 'DE00C000__drive_1.json': {'CapacityBytes': 1920383410176, 'Model': 'SAMSUNGMZ7L31T9HBLT-00A07'}}


**fix hint**: fix: redfish_gather.py physical_disks — capacity_gb = CapacityBytes // (1024**3)


---
## B17: **VERIFIED**

all envelope users.username=None across 6 hosts; raw getent has username: {'sample': ['# cmd: getent passwd | head -50', '# rc: 0', 'root:x:0:0:root:/root:/bin/bash']}


**fix hint**: fix: gather_users / normalize_users — extract field 0 of getent output as username


---
## B25: **VERIFIED**

all OS envelopes have None disk capacity; raw lsblk has SIZE: {'rhel-810-raw-fallback': ['sda           sda   53687091200 disk Virtual d VMware     1        ', 'sdb           sdb   53687091200 disk Virtual d VMware     1        ']}


**fix hint**: fix: normalize_storage.yml — capacity_gb = SIZE_BYTES // (1024**3) from lsblk -b or /sys/block size


---
## B41: **NEEDS_LIVE**

all dell envelopes show PSU=1 (envelope: {'10.100.15.27': {'psu_count_envelope': 1}, '10.100.15.28': {'psu_count_envelope': 1}, '10.100.15.31': {'psu_count_envelope': 1}, '10.100.15.33': {'psu_count_envelope': 1}, '10.100.15.34': {'psu_count_envelope': 1}}); raw not captured (auth fail), need live verify


**fix hint**: next: capture Dell raw, compare PSU count


---
## B46: **REJECTED**

power_control IS a dict in all envelopes: [('10.100.15.27', 'dict'), ('10.100.15.28', 'dict'), ('10.100.15.31', 'dict')] — earlier 'list of strings' was an iteration artifact (printing dict iterates keys).


---
## B58: **VERIFIED**

2 envelopes have Critical PSU but summary lacks critical_count: [{'ip': '10.50.11.231', 'critical_psus': 1, 'summary_keys': ['psu_count', 'psu_active', 'redundant', 'total_capacity_w', 'consumed_watts', 'consumed_capacity_pct']}, {'ip': '10.50.11.232', 'critical_psus': 1, 'summary_keys': ['psu_count', 'psu_active', 'redundant', 'total_capacity_w', 'consumed_watts', 'consumed_capacity_pct']}]


**fix hint**: fix: redfish-gather/tasks/normalize_standard.yml power summary — add critical_count, unhealthy_count, health_rollup


---
## B59: **VERIFIED**

Lenovo envelopes have None+sum: [{'ip': '10.50.11.232', 'psu_caps': [None, 750], 'summary_total': 750, 'non_none_sum': 750}]


**fix hint**: fix: normalize_standard power_summary — handle None capacity entries (separate capacity_unknown_count)


---
## B11: **dup** -> B01


---
## B15: **policy** -> AccountService 정책 결정 필요


---
## B20: **scope** -> lscpu vs setup module 차이 — 호환성 정책


---
## B21: **dup** -> B05


---
## B27: **scope** -> 환경 timezone 관찰


---
## B28: **dup** -> B19


---
## B29: **scope** -> OS-level 한계 — smartctl 필요


---
## B33: **dup** -> B06


---
## B35: **policy** -> ESXi controller 수집 정책


---
## B36: **scope** -> 환경별 HBA 차이


---
## B37: **scope** -> fallback_used 의미 명확화


---
## B38: **scope** -> ESXi API 한계


---
## B39: **policy** -> ESXi user 수집 정책


---
## B42: **dup** -> B46


---
## B43: **scope** -> pending firmware 표시


---
## B44: **dup** -> B12


---
## B45: **dup** -> B41


---
## B47: **dup** -> B30


---
## B51: **scope** -> 검증 통과 항목


---
## B53: **policy** -> correlation.bmc_ip 정책


---
## B54: **scope** -> 관찰


---
## B60: **dup** -> B52


---
## B63: **scope** -> 검증 통과


---
## B67: **dup** -> B26


---
## B69: **scope** -> ESXi IPv6 환경 의존


---
## B71: **dup** -> B23


---
## B72: **dup** -> B24


---
## B73: **dup** -> B18


---
## B74: **scope** -> 관찰


---
## B75: **policy** -> 필드명 변경 결정


---
## B77: **dup** -> B81


---
## B79: **policy** -> OS-side BMC IP 수집 정책


---
## B82: **scope** -> 환경 misconfig


---
## B83: **scope** -> 환경


---
## B84: **scope** -> 검증 통과


---
## B85: **dup** -> B27


---
## B86: **dup** -> B82


---
## B87: **dup** -> B18


---
## B88: **policy** -> ESXi BMC IP 정책


---
## B89: **scope** -> 운영 alert 후보


---
## B94: **scope** -> 환경


---
## B95: **dup** -> B58


---
## B96: **scope** -> 검증 통과


---
## B98: **dup** -> B16


---
## Summary counts

```
{
  "VERIFIED": 13,
  "REJECTED": 2,
  "NEEDS_LIVE": 1,
  "policy": 7,
  "scope": 18,
  "dup": 19
}
```