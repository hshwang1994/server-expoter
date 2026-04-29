# 2026-04-29 Bug Ticket Verification Report

raw_redfish_root: `tests\evidence\2026-04-29-deep-verify\redfish` (exists: True)
raw_linux_root: `tests\evidence\2026-04-29-deep-verify\linux` (exists: True)


---
## B01: NOT_REPRODUCED

**Claim**: GPU(Tesla T4)가 redfish CPU 섹션에 합쳐짐 (ProcessorType 필터 부재)


```json
{
  "cisco-c220": [
    {
      "id": "CPU1",
      "ProcessorType": "CPU",
      "Manufacturer": "Intel(R) Corporation",
      "Model": "Intel(R) Xeon(R) CPU E5-2699 v4 @ 2.20GHz"
    },
    {
      "id": "CPU2",
      "ProcessorType": "CPU",
      "Manufacturer": "Intel(R) Corporation",
      "Model": "Intel(R) Xeon(R) CPU E5-2699 v4 @ 2.20GHz"
    }
  ],
  "hpe-dl380": [
    {
      "id": "1",
      "ProcessorType": "CPU",
      "Manufacturer": "Intel(R) Corporation",
      "Model": "Intel(R) Xeon(R) Gold 6430"
    },
    {
      "id": "2",
      "ProcessorType": "CPU",
      "Manufacturer": "Intel(R) Corporation",
      "Model": "Intel(R) Xeon(R) Gold 6430"
    }
  ],
  "lenovo-sr650": [
    {
      "id": "1",
      "ProcessorType": "CPU",
      "Manufacturer": "Intel(R) Corporation",
      "Model": "Intel(R) Xeon(R) Gold 6338 CPU @ 2.00GHz"
    },
    {
      "id": "2",
      "ProcessorType": "CPU",
      "Manufacturer": "Intel(R) Corporation",
      "Model": "Intel(R) Xeon(R) Gold 6338 CPU @ 2.00GHz"
    }
  ]
}
```


---
## B02: VERIFIED

**Claim**: Redfish DNS unspecified IP(0.0.0.0/::) 그대로 노출


```json
{
  "cisco-c220": [
    {
      "file": "CIMC__eth_NICs.json",
      "NameServers": [
        "10.100.13.9"
      ]
    },
    {
      "file": "CIMC__network_protocol.json",
      "NameServers": null
    }
  ],
  "hpe-dl380": [
    {
      "file": "1__eth_1.json",
      "NameServers": [
        "0.0.0.0",
        "0.0.0.0",
        "0.0.0.0",
        "::",
        "::",
        "::"
      ]
    },
    {
      "file": "1__eth_2.json",
      "NameServers": [
        "0.0.0.0",
        "0.0.0.0",
        "0.0.0.0",
        "::",
        "::",
        "::"
      ]
    },
    {
      "file": "1__network_protocol.json",
      "NameServers": null
    }
  ],
  "lenovo-sr650": [
    {
      "file": "1__eth_NIC.json",
      "NameServers": [
        "",
        "",
        "",
        "::",
        "::",
        "::"
      ]
    },
    {
      "file": "1__eth_ToHost.json",
      "NameServers": [
        "0.0.0.0",
        "0.0.0.0",
        "0.0.0.0",
        "::",
        "::",
        "::"
      ]
    },
    {
      "file": "1__network_protocol.json",
      "NameServers": null
    }
  ]
}
```


---
## B09: VERIFIED

**Claim**: Redfish memory.slots[*].locator 모두 None — DeviceLocator/MemoryLocation 추출 누락


```json
{
  "cisco-c220": [
    {
      "id": "DIMM_A1",
      "DeviceLocator": "DIMM_A1",
      "MemoryLocation": {
        "Channel": 0,
        "Slot": 0,
        "Socket": 0
      },
      "Manufacturer": "0xCE00",
      "OperatingSpeedMhz": 2400,
      "AllowedSpeedsMHz": null,
      "PartNumber": "M386A8K40BM1-CRC    "
    },
    {
      "id": "DIMM_A2",
      "DeviceLocator": "DIMM_A2",
      "MemoryLocation": {
        "Channel": 0,
        "Slot": 1,
        "Socket": 0
      },
      "Manufacturer": "0xCE00",
      "OperatingSpeedMhz": 2400,
      "AllowedSpeedsMHz": null,
      "PartNumber": "M386A8K40BM1-CRC    "
    },
    {
      "id": "DIMM_B1",
      "DeviceLocator": "DIMM_B1",
      "MemoryLocation": {
        "Channel": 1,
        "Slot": 0,
        "Socket": 0
      },
      "Manufacturer": "0xCE00",
      "OperatingSpeedMhz": 2400,
      "AllowedSpeedsMHz": null,
      "PartNumber": "M386A8K40BM1-CRC    "
    },
    {
      "id": "DIMM_B2",
      "DeviceLocator": "DIMM_B2",
      "MemoryLocation": {
        "Channel": 1,
        "Slot": 1,
        "Socket": 0
      },
      "Manufacturer": "0xCE00",
      "OperatingSpeedMhz": 2400,
      "AllowedSpeedsMHz": null,
      "PartNumber": "M386A8K40BM1-CRC    "
    },
    {
      "id": "DIMM_C1",
      "DeviceLocator": "DIMM_C1",
      "MemoryLocation": {
        "Channel": 2,
        "Slot": 0,
        "Socket": 0
      },
      "Manufacturer": "0xCE00",
      "OperatingSpeedMhz": 2400,
      "AllowedSpeedsMHz": null,
      "PartNumber": "M386A8K40BM1-CRC    "
    },
    {
      "id": "DIMM_C2",
      "DeviceLocator": "DIMM_C2",
      "MemoryLocation": {
        "Channel": 2,
        "Slot": 1,
        "Socket": 0
      },
      "Manufacturer": "0xCE00",
      "OperatingSpeedMhz": 2400,
      "AllowedSpeedsMHz": null,
      "PartNumber": "M386A8K40BM1-CRC    "
    }
  ],
  "hpe-dl380": [
    {
      "id": "proc1dimm1",
      "DeviceLocator": "PROC 1 DIMM 1",
      "MemoryLocation": {
        "Channel": 8,
        "MemoryController": 4,
        "Slot": 1,
        "Socket": 1
      },
      "Manufacturer": "Samsung",
      "OperatingSpeedMhz": 4400,
      "AllowedSpeedsMHz": [
        4400
      ],
      "PartNumber": "M321R4GA3EB0-CWMXJ"
    },
    {
      "id": "proc1dimm2",
      "DeviceLocator": "PROC 1 DIMM 2",
      "MemoryLocation": {
        "Channel": 8,
        "MemoryController": 4,
        "Slot": 2,
        "Socket": 1
      },
      "Manufacturer": null,
      "OperatingSpeedMhz": null,
      "AllowedSpeedsMHz": [],
      "PartNumber": null
    },
    {
      "id": "proc1dimm3",
      "DeviceLocator": "PROC 1 DIMM 3",
      "MemoryLocation": {
        "Channel": 7,
        "MemoryController": 4,
        "Slot": 3,
        "Socket": 1
      },
      "Manufacturer": "Samsung",
      "OperatingSpeedMhz": 4400,
      "AllowedSpeedsMHz": [
        4400
      ],
      "PartNumber": "M321R4GA3EB0-CWMXJ"
    },
    {
      "id": "proc1dimm4",
      "DeviceLocator": "PROC 1 DIMM 4",
      "MemoryLocation": {
        "Channel": 7,
        "MemoryController": 4,
        "Slot": 4,
        "Socket": 1
      },
      "Manufacturer": null,
      "OperatingSpeedMhz": null,
      "AllowedSpeedsMHz": [],
      "PartNumber": null
    },
    {
      "id": "proc1dimm5",
      "DeviceLocator": "PROC 1 DIMM 5",
      "MemoryLocation": {
        "Channel": 6,
        "MemoryController": 3,
        "Slot": 5,
        "Socket": 1
      },
      "Manufacturer": "Samsung",
      "OperatingSpeed
```


---
## B10: VERIFIED

**Claim**: Redfish Drive.CapacityBytes 추출 누락 (capacity_gb=None)


```json
{
  "cisco-c220": [
    {
      "id": "FlexFlash-0__drive_SLOT-1",
      "CapacityBytes": 0,
      "Model": "NA",
      "MediaType": null
    },
    {
      "id": "FlexFlash-0__drive_SLOT-2",
      "CapacityBytes": 0,
      "Model": "NA",
      "MediaType": null
    },
    {
      "id": "SLOT-HBA__drive_PD-1",
      "CapacityBytes": 1600320962560,
      "Model": "INTEL SSDSC2BB016T6K",
      "MediaType": "SSD"
    },
    {
      "id": "SLOT-HBA__drive_PD-2",
      "CapacityBytes": 1600320962560,
      "Model": "INTEL SSDSC2BB016T6K",
      "MediaType": "SSD"
    },
    {
      "id": "SLOT-HBA__drive_PD-3",
      "CapacityBytes": 1600320962560,
      "Model": "INTEL SSDSC2BB016T6K",
      "MediaType": "SSD"
    },
    {
      "id": "SLOT-HBA__drive_PD-4",
      "CapacityBytes": 1600320962560,
      "Model": "INTEL SSDSC2BB016T6K",
      "MediaType": "SSD"
    }
  ],
  "hpe-dl380": [
    {
      "id": "DE00C000__drive_0",
      "CapacityBytes": 1920383410176,
      "Model": "SAMSUNGMZ7L31T9HBLT-00A07",
      "MediaType": "SSD"
    },
    {
      "id": "DE00C000__drive_1",
      "CapacityBytes": 1920383410176,
      "Model": "SAMSUNGMZ7L31T9HBLT-00A07",
      "MediaType": "SSD"
    },
    {
      "id": "DE00C000__drive_2",
      "CapacityBytes": 1920383410176,
      "Model": "SAMSUNGMZ7L31T9HBLT-00A07",
      "MediaType": "SSD"
    },
    {
      "id": "DE00C000__drive_3",
      "CapacityBytes": 1920383410176,
      "Model": "SAMSUNGMZ7L31T9HBLT-00A07",
      "MediaType": "SSD"
    },
    {
      "id": "DE00C000__drive_64517",
      "CapacityBytes": null,
      "Model": null,
      "MediaType": null
    },
    {
      "id": "DE00C000__drive_64518",
      "CapacityBytes": null,
      "Model": null,
      "MediaType": null
    }
  ],
  "lenovo-sr650": [
    {
      "id": "RAID_Slot3__drive_Disk.0",
      "CapacityBytes": 1920383410176,
      "Model": "MZ7L31T9HBLT-00A07",
      "MediaType": "SSD"
    },
    {
      "id": "RAID_Slot3__drive_Disk.1",
      "CapacityBytes": 1920383410176,
      "Model": "MZ7L31T9HBLT-00A07",
      "MediaType": "SSD"
    },
    {
      "id": "RAID_Slot3__drive_Disk.2",
      "CapacityBytes": 1920383410176,
      "Model": "MZ7L31T9HBLT-00A07",
      "MediaType": "SSD"
    },
    {
      "id": "RAID_Slot3__drive_Disk.3",
      "CapacityBytes": 1920383410176,
      "Model": "MZ7L31T9HBLT-00B7C",
      "MediaType": "SSD"
    }
  ]
}
```


---
## B41/B45: INSPECT_RAW

**Claim**: Dell PSU 1개 노출 — PS2 누락 의심


```json
{
  "cisco-c220": {
    "psu_count": 2,
    "psu_names": [
      "PSU1",
      "PSU2"
    ],
    "psu_health": [
      null,
      null
    ],
    "psu_capacity_w": [
      null,
      null
    ],
    "power_control_count": 1,
    "power_control_keys": [
      [
        "PhysicalContext",
        "PowerMetrics",
        "MemberId",
        "PowerLimit",
        "PowerConsumedWatts",
        "@odata.id"
      ]
    ]
  },
  "hpe-dl380": {
    "psu_count": 2,
    "psu_names": [
      "HpeServerPowerSupply",
      "HpeServerPowerSupply"
    ],
    "psu_health": [
      "Critical",
      "OK"
    ],
    "psu_capacity_w": [
      800,
      800
    ],
    "power_control_count": 1,
    "power_control_keys": [
      [
        "@odata.id",
        "MemberId",
        "PowerCapacityWatts",
        "PowerConsumedWatts",
        "PowerMetrics"
      ]
    ]
  },
  "lenovo-sr650": {
    "psu_count": 2,
    "psu_names": [
      "PSU1",
      "PSU2"
    ],
    "psu_health": [
      "Critical",
      "OK"
    ],
    "psu_capacity_w": [
      null,
      750
    ],
    "power_control_count": 3,
    "power_control_keys": [
      [
        "Name",
        "PhysicalContext",
        "RelatedItem@odata.count",
        "PowerAvailableWatts",
        "PowerCapacityWatts",
        "PowerLimit",
        "Oem",
        "PowerAllocatedWatts",
        "PowerConsumedWatts",
        "PowerRequestedWatts",
        "PowerMetrics",
        "Status",
        "@odata.id",
        "MemberId",
        "RelatedItem"
      ],
      [
        "Name",
        "PhysicalContext",
        "Status",
        "PowerConsumedWatts",
        "PowerMetrics",
        "RelatedItem@odata.count",
        "RelatedItem",
        "MemberId",
        "@odata.id"
      ]
    ]
  }
}
```


---
## B46: RAW_IS_DICT

**Claim**: envelope의 power.power_control이 list of strings 형태 — Redfish raw는 list of dicts


```json
{
  "cisco-c220": {
    "power_control_count": 1,
    "first_item_type": "dict",
    "first_item_keys": [
      "PhysicalContext",
      "PowerMetrics",
      "MemberId",
      "PowerLimit",
      "PowerConsumedWatts",
      "@odata.id"
    ],
    "sample_values": [
      {
        "PhysicalContext": "PowerSupply",
        "PowerMetrics": {
          "MinConsumedWatts": 192,
          "AverageConsumedWatts": 438,
          "MaxConsumedWatts": 565
        },
        "MemberId": "1",
        "PowerLimit": {
          "LimitException": "NoAction"
        },
        "PowerConsumedWatts": 424,
        "@odata.id": "/redfish/v1/Chassis/1/Power#/PowerControl/1"
      }
    ]
  },
  "hpe-dl380": {
    "power_control_count": 1,
    "first_item_type": "dict",
    "first_item_keys": [
      "@odata.id",
      "MemberId",
      "PowerCapacityWatts",
      "PowerConsumedWatts",
      "PowerMetrics"
    ],
    "sample_values": [
      {
        "@odata.id": "/redfish/v1/Chassis/1/Power#PowerControl/0",
        "MemberId": "0",
        "PowerCapacityWatts": 800,
        "PowerConsumedWatts": 481,
        "PowerMetrics": {
          "AverageConsumedWatts": 480,
          "IntervalInMin": 20,
          "MaxConsumedWatts": 495,
          "MinConsumedWatts": 478
        }
      }
    ]
  },
  "lenovo-sr650": {
    "power_control_count": 3,
    "first_item_type": "dict",
    "first_item_keys": [
      "Name",
      "PhysicalContext",
      "RelatedItem@odata.count",
      "PowerAvailableWatts",
      "PowerCapacityWatts",
      "PowerLimit",
      "Oem",
      "PowerAllocatedWatts",
      "PowerConsumedWatts",
      "PowerRequestedWatts",
      "PowerMetrics",
      "Status",
      "@odata.id",
      "MemberId",
      "RelatedItem"
    ],
    "sample_values": [
      {
        "Name": "Server Power Control",
        "PhysicalContext": "Chassis",
        "RelatedItem@odata.count": 1,
        "PowerAvailableWatts": 0,
        "PowerCapacityWatts": 750,
        "PowerLimit": {
          "LimitException": "NoAction",
          "LimitInWatts": null
        },
        "Oem": {
          "Lenovo": {
            "@odata.type": "#LenovoPower.v1_0_0.PowerControl",
            "PowerUtilization": {
              "GuaranteedInWatts": 675,
              "LimitMode": "AC",
              "MaxLimitInWatts": 750,
              "MinLimitInWatts": 0,
              "EnablePowerCapping@Redfish.Deprecated": "The property is deprecated. Please use LimitInWatts instead.",
              "CapacityMaxAC": 782,
              "CapacityMaxDC": 758,
              "CapacityMinAC": 675,
              "CapacityMinDC": 645,
              "EnablePowerCapping": false
            },
            "HistoryPowerMetric": {
              "@odata.id": "/redfish/v1/Chassis/1/Power/PowerControl/0/Oem/Lenovo/HistoryPowerMetric"
            }
          }
        },
        "PowerAllocatedWatts": 750,
        "PowerConsumedWatts": 245,
        "PowerRequestedWatts": 782,
        "PowerMetrics": {
          "AverageConsumedWatts": 221,
          "IntervalInMin": 1,
          "MaxConsumedWatts": 271,
          "MinConsumedWatts": 212
        },
        "Status": {
          "State": "Enabled",
          "HealthRollup": "Critical",
          "Health": "OK"
        },
        "@odata.id": "/redfish/v1/Chassis/1/Power#/PowerControl/0",
        "MemberId": "0",
        "RelatedItem": [
          {
            "@odata.id": "/redfish/v1/Chassis/1"
          }
        ]
      }
    ]
  }
}
```


---
## B58: VERIFIED

**Claim**: PSU.Status.Health=Critical인데 summary에 critical_count 노출 없음


```json
{
  "hpe-dl380": [
    {
      "Name": "HpeServerPowerSupply",
      "Health": "Critical",
      "State": "UnavailableOffline",
      "Manufacturer": "LTEON"
    }
  ],
  "lenovo-sr650": [
    {
      "Name": "PSU1",
      "Health": "Critical",
      "State": "Enabled",
      "Manufacturer": "DETA"
    }
  ]
}
```


---
## B04: INSPECT_RAW

**Claim**: Ubuntu DNS=127.0.0.53 (systemd-resolved stub) — /etc/resolv.conf만 보면 stub만 잡힘


```json
{
  "rhel-810-raw-fallback": {
    "resolv_conf_first3": [
      "search gooddi.lab",
      "nameserver 10.100.64.251",
      "--- stderr ---"
    ],
    "resolvectl_dns_lines": [],
    "runtime_resolv_first3": [
      "cat: /run/systemd/resolve/resolv.conf: No such file or directory",
      "ABSENT",
      "--- stderr ---"
    ]
  },
  "rhel-92": {
    "resolv_conf_first3": [
      "search gooddi.lab",
      "nameserver 10.100.64.251",
      "--- stderr ---"
    ],
    "resolvectl_dns_lines": [],
    "runtime_resolv_first3": [
      "cat: /run/systemd/resolve/resolv.conf: No such file or directory",
      "ABSENT",
      "--- stderr ---"
    ]
  },
  "rhel-96": {
    "resolv_conf_first3": [
      "search gooddi.lab",
      "nameserver 10.100.64.251",
      "--- stderr ---"
    ],
    "resolvectl_dns_lines": [],
    "runtime_resolv_first3": [
      "cat: /run/systemd/resolve/resolv.conf: No such file or directory",
      "ABSENT",
      "--- stderr ---"
    ]
  },
  "rocky-96": {
    "resolv_conf_first3": [
      "search gooddi.lab",
      "nameserver 10.100.64.251",
      "--- stderr ---"
    ],
    "resolvectl_dns_lines": [],
    "runtime_resolv_first3": [
      "cat: /run/systemd/resolve/resolv.conf: No such file or directory",
      "ABSENT",
      "--- stderr ---"
    ]
  },
  "ubuntu-2404": {
    "resolv_conf_first3": [
      "nameserver 127.0.0.53",
      "options edns0 trust-ad",
      "search gooddi.lab"
    ],
    "resolvectl_dns_lines": [
      "Current DNS Server: 10.100.64.251",
      "DNS Servers: 10.100.64.251",
      "Current DNS Server: 10.100.64.251"
    ],
    "runtime_resolv_first3": [
      "nameserver 10.100.64.251",
      "nameserver 10.100.64.251",
      "search gooddi.lab"
    ]
  },
  "ubuntu-r760-6-baremetal": {
    "resolv_conf_first3": [
      "nameserver 127.0.0.53",
      "options edns0 trust-ad",
      "search gooddi.lab"
    ],
    "resolvectl_dns_lines": [
      "Current DNS Server: 10.100.64.251",
      "DNS Servers: 10.100.64.251"
    ],
    "runtime_resolv_first3": [
      "nameserver 10.100.64.251",
      "search gooddi.lab",
      "--- stderr ---"
    ]
  }
}
```


---
## B17: INSPECT_RAW

**Claim**: getent passwd 첫 컬럼이 username — 빌더 매핑 누락 의심


```json
{
  "rhel-810-raw-fallback": [
    "root:x:0:0:root:/root:/bin/bash",
    "bin:x:1:1:bin:/bin:/sbin/nologin",
    "daemon:x:2:2:daemon:/sbin:/sbin/nologin",
    "adm:x:3:4:adm:/var/adm:/sbin/nologin",
    "lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin"
  ],
  "rhel-92": [
    "root:x:0:0:root:/root:/bin/bash",
    "bin:x:1:1:bin:/bin:/sbin/nologin",
    "daemon:x:2:2:daemon:/sbin:/sbin/nologin",
    "adm:x:3:4:adm:/var/adm:/sbin/nologin",
    "lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin"
  ],
  "rhel-96": [
    "root:x:0:0:root:/root:/bin/bash",
    "bin:x:1:1:bin:/bin:/sbin/nologin",
    "daemon:x:2:2:daemon:/sbin:/sbin/nologin",
    "adm:x:3:4:adm:/var/adm:/sbin/nologin",
    "lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin"
  ],
  "rocky-96": [
    "root:x:0:0:root:/root:/bin/bash",
    "bin:x:1:1:bin:/bin:/sbin/nologin",
    "daemon:x:2:2:daemon:/sbin:/sbin/nologin",
    "adm:x:3:4:adm:/var/adm:/sbin/nologin",
    "lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin"
  ],
  "ubuntu-2404": [
    "root:x:0:0:root:/root:/bin/bash",
    "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
    "bin:x:2:2:bin:/bin:/usr/sbin/nologin",
    "sys:x:3:3:sys:/dev:/usr/sbin/nologin",
    "sync:x:4:65534:sync:/bin:/bin/sync"
  ],
  "ubuntu-r760-6-baremetal": [
    "root:x:0:0:root:/root:/bin/bash",
    "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
    "bin:x:2:2:bin:/bin:/usr/sbin/nologin",
    "sys:x:3:3:sys:/dev:/usr/sbin/nologin",
    "sync:x:4:65534:sync:/bin:/bin/sync"
  ]
}
```


---
## B19/B80: INSPECT_RAW

**Claim**: Baremetal Linux의 dmidecode hardware 정보 미수집 (sections.hardware=not_supported)


```json
{
  "rhel-810-raw-fallback": {
    "manuf": "Shared connection to 10.100.64.161 closed.",
    "product": "Shared connection to 10.100.64.161 closed.",
    "serial": "Shared connection to 10.100.64.161 closed.",
    "chassis_present": true,
    "system_present": true
  },
  "rhel-92": {
    "manuf": "Shared connection to 10.100.64.163 closed.",
    "product": "Shared connection to 10.100.64.163 closed.",
    "serial": "Shared connection to 10.100.64.163 closed.",
    "chassis_present": true,
    "system_present": true
  },
  "rhel-96": {
    "manuf": "Shared connection to 10.100.64.165 closed.",
    "product": "Shared connection to 10.100.64.165 closed.",
    "serial": "Shared connection to 10.100.64.165 closed.",
    "chassis_present": true,
    "system_present": true
  },
  "rocky-96": {
    "manuf": "Shared connection to 10.100.64.169 closed.",
    "product": "Shared connection to 10.100.64.169 closed.",
    "serial": "Shared connection to 10.100.64.169 closed.",
    "chassis_present": true,
    "system_present": true
  },
  "ubuntu-2404": {
    "manuf": "Shared connection to 10.100.64.167 closed.",
    "product": "Shared connection to 10.100.64.167 closed.",
    "serial": "Shared connection to 10.100.64.167 closed.",
    "chassis_present": true,
    "system_present": true
  },
  "ubuntu-r760-6-baremetal": {
    "manuf": "Shared connection to 10.100.64.96 closed.",
    "product": "Shared connection to 10.100.64.96 closed.",
    "serial": "Shared connection to 10.100.64.96 closed.",
    "chassis_present": true,
    "system_present": true
  }
}
```


---
## B25: INSPECT_RAW

**Claim**: Linux storage.physical_disks.capacity_gb=None — lsblk/sys block size 미사용


```json
{
  "rhel-810-raw-fallback": {
    "lsblk_disk_lines": [
      "sda           sda   53687091200 disk Virtual d VMware     1        ",
      "sdb           sdb   53687091200 disk Virtual d VMware     1        "
    ],
    "sys_block_first3": [
      "dm-0 size_blocks=91037696 rotational=1",
      "dm-1 size_blocks=10485760 rotational=1",
      "dm-2 size_blocks=62914560 rotational=1",
      "sda size_blocks=104857600 rotational=1",
      "sdb size_blocks=104857600 rotational=1"
    ]
  },
  "rhel-92": {
    "lsblk_disk_lines": [
      "sda           sda   53687091200 disk Virtual disk    VMware     1        ",
      "sdb           sdb   53687091200 disk Virtual disk    VMware     1        "
    ],
    "sys_block_first3": [
      "dm-0 size_blocks=91037696 rotational=1",
      "dm-1 size_blocks=10485760 rotational=1",
      "dm-2 size_blocks=62914560 rotational=1",
      "sda size_blocks=104857600 rotational=1",
      "sdb size_blocks=104857600 rotational=1"
    ]
  },
  "rhel-96": {
    "lsblk_disk_lines": [
      "sda           sda   53687091200 disk Virtual disk    VMware     1        ",
      "sdb           sdb   53687091200 disk Virtual disk    VMware     1        "
    ],
    "sys_block_first3": [
      "dm-0 size_blocks=91037696 rotational=1",
      "dm-1 size_blocks=10485760 rotational=1",
      "dm-2 size_blocks=62914560 rotational=1",
      "sda size_blocks=104857600 rotational=1",
      "sdb size_blocks=104857600 rotational=1"
    ]
  },
  "rocky-96": {
    "lsblk_disk_lines": [
      "sda         sda   53687091200 disk Virtual disk      VMware     1        ",
      "sdb         sdb   53687091200 disk Virtual disk      VMware     1        "
    ],
    "sys_block_first3": [
      "dm-0 size_blocks=91037696 rotational=1",
      "dm-1 size_blocks=10485760 rotational=1",
      "dm-2 size_blocks=62914560 rotational=1",
      "sda size_blocks=104857600 rotational=1",
      "sdb size_blocks=104857600 rotational=1"
    ]
  },
  "ubuntu-2404": {
    "lsblk_disk_lines": [
      "sda             sda   53687091200 disk Virtual disk  VMware    1        ",
      "sdb             sdb   53687091200 disk Virtual disk  VMware    1        "
    ],
    "sys_block_first3": [
      "dm-0 size_blocks=49225728 rotational=1",
      "dm-1 size_blocks=62914560 rotational=1",
      "loop0 size_blocks=0 rotational=1",
      "loop1 size_blocks=0 rotational=1",
      "loop2 size_blocks=0 rotational=1"
    ]
  },
  "ubuntu-r760-6-baremetal": {
    "lsblk_disk_lines": [
      "sda          sda       11518296981504 disk RAID  DELL      0        00e0faed649a",
      "sdb          sdb        1798651772928 disk RAID  DELL      1        0021b319c1d8",
      "nvme0n1      nvme0n1     480036519936 disk Dell            0 nvme   CN0WW56VFCP0"
    ],
    "sys_block_first3": [
      "dm-0 size_blocks=931168256 rotational=0",
      "loop0 size_blocks=0 rotational=0",
      "loop1 size_blocks=0 rotational=1",
      "loop2 size_blocks=0 rotational=1",
      "loop3 size_blocks=0 rotational=1"
    ]
  }
}
```


---
## B26/B65/B66: INSPECT_RAW

**Claim**: Linux fs.fstype/free_mb/read_only=None — df -T / findmnt / /proc/mounts 미사용


```json
{
  "rhel-810-raw-fallback": {
    "df_T_sample": [
      "devtmpfs                   devtmpfs  4004102144          0  4004102144   0% /dev",
      "tmpfs                      tmpfs     4035252224      86016  4035166208   1% /dev/shm",
      "tmpfs                      tmpfs     4035252224   18202624  4017049600   1% /run",
      "tmpfs                      tmpfs     4035252224          0  4035252224   0% /sys/fs/cgroup"
    ],
    "findmnt_sample": [
      "/            /dev/mapper/rhel-root      xfs    rw,rela  43.4G   5.5G    38G  13%",
      "├─/boot      /dev/sda2                  xfs    rw,rela  1014M 266.6M 747.5M  26%",
      "│ └─/boot/efi",
      "│            /dev/sda1                  vfat   rw,rela 598.8M   5.8M   593M   1%"
    ],
    "proc_mounts_sample": [
      "sysfs /sys sysfs rw,seclabel,nosuid,nodev,noexec,relatime 0 0",
      "proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0",
      "devtmpfs /dev devtmpfs rw,seclabel,nosuid,size=3910256k,nr_inodes=977564,mode=755 0 0",
      "securityfs /sys/kernel/security securityfs rw,nosuid,nodev,noexec,relatime 0 0"
    ]
  },
  "rhel-92": {
    "df_T_sample": [
      "devtmpfs                   devtmpfs     4194304          0     4194304   0% /dev",
      "tmpfs                      tmpfs     4030304256      86016  4030218240   1% /dev/shm",
      "tmpfs                      tmpfs     1612124160    9682944  1602441216   1% /run",
      "/dev/mapper/rhel-root      xfs      46588542976 4492800000 42095742976  10% /"
    ],
    "findmnt_sample": [
      "/            /dev/mapper/rhel-root      xfs    rw,rela  43.4G   4.2G  39.2G  10%",
      "├─/boot      /dev/sda2                  xfs    rw,rela  1014M 283.3M 730.7M  28%",
      "│ └─/boot/efi",
      "│            /dev/sda1                  vfat   rw,rela 598.8M     7M 591.8M   1%"
    ],
    "proc_mounts_sample": [
      "proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0",
      "sysfs /sys sysfs rw,seclabel,nosuid,nodev,noexec,relatime 0 0",
      "devtmpfs /dev devtmpfs rw,seclabel,nosuid,size=4096k,nr_inodes=975976,mode=755,inode64 0 0",
      "securityfs /sys/kernel/security securityfs rw,nosuid,nodev,noexec,relatime 0 0"
    ]
  },
  "rhel-96": {
    "df_T_sample": [
      "devtmpfs                   devtmpfs     4194304          0     4194304   0% /dev",
      "tmpfs                      tmpfs     4026851328      86016  4026765312   1% /dev/shm",
      "tmpfs                      tmpfs     1610743808    9687040  1601056768   1% /run",
      "efivarfs                   efivarfs      262128      30350      226658  12% /sys/firmware/efi/efivars"
    ],
    "findmnt_sample": [
      "/            /dev/mapper/rhel-root      xfs    rw,rela  43.3G   4.6G  38.8G  11%",
      "├─/boot      /dev/sda2                  xfs    rw,rela   960M 355.9M 604.1M  37%",
      "│ └─/boot/efi",
      "│            /dev/sda1                  vfat   rw,rela 598.8M   7.1M 591.8M   1%"
    ],
    "proc_mounts_sample": [
      "proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0",
      "sysfs /sys sysfs rw,seclabel,nosuid,nodev,noexec,relatime 0 0",
      "devtmpfs /dev devtmpfs rw,seclabel,nosuid,size=4096k,nr_inodes=974764,mode=755,inode64 0 0",
      "securityfs /sys/kernel/security securityfs rw,nosuid,nodev,noexec,relatime 0 0"
    ]
  },
  "rocky-96": {
    "df_T_sample": [
      "devtmpfs                   devtmpfs     4194304          0     4194304   0% /dev",
      "tmpfs                      tmpfs     4026847232          0  402684
```


---
## B68: INSPECT_RAW

**Claim**: Linux interfaces.addresses에 IPv6 0개 — ip -6 addr 미사용


```json
{
  "rhel-810-raw-fallback": {
    "link_local": 2,
    "global": 0
  },
  "rhel-92": {
    "link_local": 2,
    "global": 0
  },
  "rhel-96": {
    "link_local": 2,
    "global": 0
  },
  "rocky-96": {
    "link_local": 2,
    "global": 0
  },
  "ubuntu-2404": {
    "link_local": 2,
    "global": 0
  },
  "ubuntu-r760-6-baremetal": {
    "link_local": 5,
    "global": 0
  }
}
```


---
## B78/B80: INSPECT_RAW

**Claim**: Linux VM serial 길고(정규화 필요), 베어메탈 envelope.vendor=None (dmidecode 미사용)


```json
{
  "rhel-810-raw-fallback": {
    "serial": "Shared connection to 10.100.64.161 closed.",
    "manuf": "Shared connection to 10.100.64.161 closed."
  },
  "rhel-92": {
    "serial": "Shared connection to 10.100.64.163 closed.",
    "manuf": "Shared connection to 10.100.64.163 closed."
  },
  "rhel-96": {
    "serial": "Shared connection to 10.100.64.165 closed.",
    "manuf": "Shared connection to 10.100.64.165 closed."
  },
  "rocky-96": {
    "serial": "Shared connection to 10.100.64.169 closed.",
    "manuf": "Shared connection to 10.100.64.169 closed."
  },
  "ubuntu-2404": {
    "serial": "Shared connection to 10.100.64.167 closed.",
    "manuf": "Shared connection to 10.100.64.167 closed."
  },
  "ubuntu-r760-6-baremetal": {
    "serial": "Shared connection to 10.100.64.96 closed.",
    "manuf": "Shared connection to 10.100.64.96 closed."
  }
}
```
