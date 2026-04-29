# 2026-04-29 Bug Verification — Final Verdict (v2)

v2 correction: many original 'bugs' were false positives caused by wrong field names
in my Python analysis script (e.g. `username` instead of `name`, `capacity_gb` instead
of `total_mb`, `fstype` instead of `filesystem`, `free_mb` instead of `available_mb`).

Total tickets: 99

## Summary

| verdict | count | meaning |
|---|---|---|
| **verified** | 32 | confirmed bug — needs fix |
| **rejected** | 11 | not a bug (false positive due to wrong field name etc) |
| **needs_live** | 4 | need fresh raw capture (Dell auth fail blocks) |
| **policy** | 15 | decision required |
| **scope** | 18 | observation/environment, not actionable code change |
| **dup** | 19 | duplicate of another ticket |

## Per-ticket verdict

| ticket | verdict | summary |
|---|---|---|
| B01 | **verified** | r760-1 cpu.summary.groups=[{'model': 'Tesla T4', 'manufacturer': 'NVIDIA Corporation', 'max_speed_mhz': None, 'architect |
| B02 | **verified** | envelope hosts with unspecified IP in dns_servers: [('10.100.15.27', ['0.0.0.0', '::'], 'dell'), ('10.100.15.28', ['0.0. |
| B03 | **verified** | failed envelope (10.50.11.162): data None=['system', 'hardware', 'bmc', 'cpu', 'memory', 'power']; non-empty struct=['st |
| B04 | **verified** | Ubuntu hosts with 127.0.0.x in dns_servers: [('10.100.64.96', ['127.0.0.53']), ('10.100.64.167', ['127.0.0.53'])] |
| B05 | **verified** | raw_fallback hosts cpu.summary.groups counts: [('10.100.64.161', 0)] |
| B06 | **verified** | ESXi summary groups buggy: [{'ip': '10.100.64.1', 'adapter_count': 6, 'connected': 2, 'groups': [{'speed_mbps': None, 'l |
| B07 | **rejected** | Redfish system all-None+success entries: [] |
| B08 | **rejected** | BMC field None counts (out of 8 hosts): {'name': 0, 'model': 0, 'manager_type': 0, 'mac_address': 0, 'dns_name': 0}; sam |
| B09 | **rejected** | Redfish memory.slots samples: [{'ip': '10.100.15.27', 'id': 'DIMM.Socket.A1', 'name': 'DIMM A1', 'all_keys': ['id', 'nam |
| B10 | **rejected** | Redfish disks have total_mb populated: [{'ip': '10.100.15.27', 'first_disk': {'id': 'Disk.Direct.0-0:BOSS.SL.12-1', 'dev |
| B11 | **dup** | B01 |
| B12 | **policy** | vendor-specific firmware naming |
| B13 | **verified** | redfish iface link_status enum varies (linkup/linkdown vs none) |
| B14 | **policy** | iface name normalization decision |
| B15 | **policy** | AccountService 정책 결정 |
| B16 | **verified** | bios_date 형식 vendor마다 다름 (Dell MM/DD/YYYY vs ESXi ISO 8601 vs others null) |
| B17 | **rejected** | Linux users.name populated: [{'ip': '10.100.64.96', 'first_user': {'name': 'root', 'uid': '0', 'groups': ['root'], 'home |
| B18 | **rejected** | OS system has fqdn: [{'ip': '10.100.64.96', 'hostname': None, 'fqdn': 'r760-6', 'envelope_top_hostname': 'r760-6'}, {'ip |
| B19 | **verified** | r760-6 baremetal: data.hardware=None, sections.hardware=not_supported, system.hosting_type=baremetal, system.serial_numb |
| B20 | **scope** | VM CPU sockets observation |
| B21 | **dup** | B05 |
| B22 | **verified** | VM cpu.max_speed_mhz: [('10.100.64.161', None), ('10.100.64.163', None), ('10.100.64.165', None), ('10.100.64.169', None |
| B23 | **verified** | r760-6 memory.slots[0].manufacturer: 00AD063200AD |
| B24 | **policy** | memory speed 의미 정의 |
| B25 | **rejected** | Linux disks have total_mb populated: [{'ip': '10.100.64.96', 'first_disk': {'id': '/dev/sda', 'device': '/dev/sda', 'mod |
| B26 | **rejected** | Linux fs.filesystem populated: [{'ip': '10.100.64.96', 'first_fs': {'device': '/dev/mapper/ubuntu--vg-ubuntu--lv', 'moun |
| B27 | **scope** | tz environment |
| B28 | **dup** | B19 |
| B29 | **scope** | OS-level disk SSD/HDD limit |
| B30 | **scope** | esxi03 vmnic1 — env hardware |
| B31 | **verified** | ESXi runtime tz/ntp/firewall/swap all None — vSphere fact不 collected |
| B32 | **verified** | ESXi default_gateways=[] — routeConfig 미수집 |
| B33 | **dup** | B06 |
| B34 | **verified** | ESXi physical_disks=[] — esxcli storage core device 미사용 |
| B35 | **policy** | controllers vs hbas 정책 |
| B36 | **scope** | 환경별 HBA |
| B37 | **scope** | fallback_used 의미 |
| B38 | **scope** | ESXi memory installed_mb 한계 |
| B39 | **policy** | ESXi user 정책 |
| B40 | **verified** | Ansible reserved 'name' warning |
| B41 | **needs_live** | Dell PSU envelope counts: [('10.100.15.27', 1, False), ('10.100.15.28', 1, False), ('10.100.15.31', 1, False), ('10.100. |
| B42 | **dup** | B46 |
| B43 | **verified** | Lenovo firmware pending entry version=None |
| B44 | **dup** | B12 |
| B45 | **dup** | B41 |
| B46 | **rejected** | power_control IS dict in all envelopes: [('10.100.15.27', 'dict'), ('10.100.15.28', 'dict'), ('10.100.15.31', 'dict'), ( |
| B47 | **dup** | B30 |
| B48 | **verified** | Cisco logical_volume name='' |
| B49 | **needs_live** | Dell BOSS boot_volume — need raw |
| B50 | **verified** | duration_ms 1초 절삭 |
| B51 | **scope** | memory total/slot 합계 통과 |
| B52 | **policy** | raw vs usable storage capacity 정의 |
| B53 | **policy** | correlation.bmc_ip 정책 |
| B54 | **scope** | UUID prefix |
| B55 | **verified** | failed envelope diagnosis.details 누락 (B03 부분과 묶음) |
| B56 | **verified** | failed envelope auth_success=null (B03 부분) |
| B57 | **policy** | iface vs adapter mac 의미 정의 |
| B58 | **verified** | hosts with Critical PSU but no critical_count in summary: [{'ip': '10.50.11.231', 'vendor': 'hpe', 'critical_psus': 1, ' |
| B59 | **verified** | Lenovo None-cap PSU sum issue: [{'ip': '10.50.11.232', 'psu_caps': [None, 750], 'sm_total': 750}] |
| B60 | **dup** | B52 |
| B61 | **verified** | Lenovo Cisco OEM coverage 부족 |
| B62 | **verified** | ESXi diagnosis.details에 esxi_version 추가 필요 |
| B63 | **scope** | OS auth 통과 |
| B64 | **verified** | hosts with float used_mb (precision drift): [('10.100.64.96', [('/', 33965.5), ('/boot', 315.10000000000014), ('/ssd', 2 |
| B65 | **rejected** | Linux fs.available_mb populated: [{'ip': '10.100.64.96', 'first_fs': {'device': '/dev/mapper/ubuntu--vg-ubuntu--lv', 'mo |
| B66 | **rejected** | Linux fs schema keys: ['device', 'mount_point', 'filesystem', 'total_mb', 'used_mb', 'available_mb', 'usage_percent', 's |
| B67 | **dup** | B26 |
| B68 | **verified** | OS interfaces with v4 but no v6: [{'ip': '10.100.64.96', 'iface': 'bond0.64', 'v4_count': 1, 'v6_count': 0}, {'ip': '10. |
| B69 | **scope** | ESXi IPv6 환경 |
| B70 | **needs_live** | Dell adapter.name='Network Adapter View' — need raw |
| B71 | **dup** | B23 |
| B72 | **dup** | B24 |
| B73 | **dup** | B18 |
| B74 | **scope** | swap_used 관찰 |
| B75 | **policy** | visible_mb vs total_mb 필드명 |
| B76 | **verified** | Linux hosts with empty network.adapters: [('10.100.64.96', 0), ('10.100.64.161', 0), ('10.100.64.163', 0), ('10.100.64.1 |
| B77 | **dup** | B81 |
| B78 | **verified** | VM serial_number raw VMware 형식 |
| B79 | **policy** | OS BMC IP 정책 |
| B80 | **verified** | OS envelope.vendor=None 베어메탈도 |
| B81 | **policy** | target_type별 vendor 정책 |
| B82 | **scope** | RHEL hostname=localhost 환경 |
| B83 | **scope** | ESXi hostname short |
| B84 | **scope** | ESXi datastore 통과 |
| B85 | **dup** | B27 |
| B86 | **dup** | B82 |
| B87 | **dup** | B18 |
| B88 | **policy** | ESXi BMC IP 정책 |
| B89 | **scope** | DIMM 혼합 관찰 |
| B90 | **verified** | Cisco memory.mfg raw 0xCExx |
| B91 | **needs_live** | RHEL 8.10 raw fallback memory.mfg=None |
| B92 | **verified** | HPE iface.name 숫자만 |
| B93 | **verified** | HPE adapter.mac/link 모두 None |
| B94 | **scope** | HPE iface.addresses 0개 |
| B95 | **dup** | B58 |
| B96 | **scope** | ESXi collection_method 통과 |
| B97 | **policy** | OS collection_method 명확화 |
| B98 | **dup** | B16 |
| B99 | **policy** | listening_ports 구조화 |