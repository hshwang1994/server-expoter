# 20. JSON 출력 스키마 키 의미

> **이 문서는** server-exporter 가 호출자에게 돌려주는 표준 JSON 의 **모든 키 하나하나가 무슨 뜻인지** 정의하는 사전이다.
>
> envelope 의 최상위 13 필드, 그 안의 sections (10개), 그리고 65개 세부 필드 (필수 39 + 권장 20 + 자명 6) 의 의미를 한 페이지에서 찾을 수 있다.
> 호출자 시스템 개발자가 "이 필드 null 은 뭐고, 빈 배열은 뭐고, 숫자 0 은 뭔지" 헷갈릴 때 가장 먼저 보는 곳이다.

## 정본 정합

본 문서의 모든 정의는 다음 정본과 한 글자 drift 없음을 보장:
- envelope 13 필드: `common/tasks/normalize/build_output.yml`
- sections 10 정의: `schema/sections.yml`
- field_dictionary 65 entries: `schema/field_dictionary.yml`
- status 판정 규칙: `common/tasks/normalize/build_status.yml` (M-A3 의도 주석 정본)
- baseline 예시: `schema/baseline_v1/<vendor>_baseline.json`

---

## 1. Envelope 13 필드

> 정본: `common/tasks/normalize/build_output.yml`

모든 채널 (Redfish / OS / ESXi) 의 JSON 출력은 정확히 아래 13 필드를 갖는다. 작성 순서:

| # | 필드 | 타입 | enum | 의미 | 정규화 규칙 |
|---|------|------|------|------|-------------|
| 1 | `target_type` | string | os / esxi / redfish | 수집 채널. 호출자 라우팅용 | 호출자 입력 그대로 |
| 2 | `collection_method` | string | agent / vsphere_api / redfish_api | 수집 방식 | target_type 따라 자동 (agent=Ansible SSH/WinRM, vsphere_api=community.vmware, redfish_api=stdlib HTTP+Basic Auth) |
| 3 | `ip` | string | — | 대상 장비 IP. OS=서비스 IP, ESXi=management IP, Redfish=BMC IP | 호출자 inventory_json 값과 동일 |
| 4 | `hostname` | string | — | 해석된 hostname. 해석 실패 시 ip 값으로 fallback | data.system.hostname → fqdn → ip 순 fallback |
| 5 | `vendor` | string\|null | dell / hpe / lenovo / supermicro / cisco / null | 정규화된 벤더 (소문자) | `common/vars/vendor_aliases.yml` 매핑 |
| 6 | `status` | string | success / partial / failed | 전체 수집 결과 상태 | 5절 판정 규칙 참조 |
| 7 | `sections` | object | — | 섹션별 수집 상태 dict | 값: success / failed / not_supported |
| 8 | `diagnosis` | object\|null | — | 진단 정보 (precheck 4단계 + gather 모드 + details) | 7절 참조 |
| 9 | `meta` | object\|null | — | 메타 정보 (loc / duration_ms / adapter_id 등) | 9절 참조 |
| 10 | `correlation` | object\|null | — | 상관관계 식별자 (serial / system_uuid / bmc_ip / host_ip) | 8절 참조 |
| 11 | `errors` | array | — | 수집 중 발생한 오류 목록. 성공 시 빈 배열 | 6절 참조 |
| 12 | `data` | object | — | 실제 수집 데이터. 섹션별 필드 그룹 | 3절 Field Dictionary 참조 |
| 13 | `schema_version` | string | "1" | envelope schema 버전 | 현재 "1" 고정. 변경 시 rule 92 R5 사용자 승인 필요 |

**[INFO]** rule 13 R5 / rule 96 R1-B — envelope 13 필드 추가 / 삭제 / 리네임 금지. 분석 카테고리 6 (status / sections / data / errors / meta / diagnosis) + 라우팅·식별 5 (target_type / collection_method / ip / hostname / vendor) + 추적 2 (correlation / schema_version).

---

## 2. Sections 10 정의

> 정본: `schema/sections.yml`

| section | 의미 | 지원 채널 | 빈 값 |
|---------|------|-----------|------|
| `system` | 운영체제 / 호스트명 / 가동시간 등 기본 시스템 정보 | os / esxi / redfish | null |
| `hardware` | 벤더 / 모델 / 시리얼 / BIOS 등 물리 장비 정보 | esxi / redfish | null |
| `bmc` | BMC (iDRAC / iLO / XCC) 펌웨어 / 상태 정보 | redfish 전용 | null |
| `cpu` | 프로세서 소켓 / 코어 / 스레드 / 모델 정보 | os / esxi / redfish | null |
| `memory` | 총 용량 / 슬롯 / 사용량 정보 | os / esxi / redfish | null |
| `storage` | 파일시스템 / 물리 디스크 / 컨트롤러 / 데이터스토어 / 논리 볼륨 / HBA / InfiniBand | os / esxi / redfish | dict (filesystems[] / physical_disks[] / datastores[] / controllers[] / logical_volumes[] / hbas[] / infiniband[] / summary) |
| `network` | 인터페이스 / IP / DNS / 게이트웨이 / NIC 카드 / port-level / vSwitch | os / esxi / redfish | dict (dns_servers[] / default_gateways[] / interfaces[] / adapters[] / ports[] / virtual_switches[] / portgroups[] / driver_map[] / summary) |
| `firmware` | 설치된 펌웨어 / 드라이버 인벤토리 | redfish 전용 | [] |
| `users` | 로컬 시스템 사용자 계정 정보 | os 전용 | [] |
| `power` | PSU 상태 및 전력 정보 | redfish 전용 | null |

**총 10 sections.** OS 채널은 hardware/bmc/firmware/power = `not_supported`. ESXi 채널은 bmc/firmware/users/power = `not_supported`. Redfish 채널은 system/users = `not_supported` (하드웨어 채널 특성).

---

## 3. Field Dictionary 65 entries

> 정본: `schema/field_dictionary.yml`
>
> Path 표기: `hardware.health` = data.hardware.health, `physical_disks[].id` = 배열 item 의 id, `sections.*` = sections 객체의 모든 값.

### 3.1 Must (39 entries) — 모든 vendor 보장

호출자가 모든 응답에서 존재 보장 받는 계약 필드.

#### envelope top-level Must (8 entries)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `schema_version` | string | "1" | redfish/os/esxi | envelope schema 버전. "1" 고정 (2026-04-29 기준) |
| `target_type` | string | os/esxi/redfish | redfish/os/esxi | 수집 채널 |
| `collection_method` | string | agent/vsphere_api/redfish_api | redfish/os/esxi | 수집 방식 |
| `ip` | string | — | redfish/os/esxi | 대상 장비 IP |
| `hostname` | string | — | redfish/os/esxi | 해석된 hostname (실패 시 ip fallback) |
| `vendor` | string\|null | dell/hpe/lenovo/supermicro/cisco/null | redfish/os/esxi | 정규화된 벤더 |
| `meta` | object | — | redfish/os/esxi | 수집 메타데이터 |
| `correlation` | object | — | redfish/os/esxi | 상관관계 식별자 |

#### status / sections Must (2 entries)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `status` | string | success/partial/failed | redfish/os/esxi | 전체 수집 결과 상태. "수집 성공"이지 "장비 정상"이 아님 |
| `sections.*` | string | success/failed/not_supported | redfish/os/esxi | 개별 섹션 수집 상태. not_supported=이 채널이 해당 섹션 미지원 |

#### bmc Must (1 entry)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `bmc.ip` | string\|null | redfish | BMC 관리 인터페이스 IPv4 (서버 OS IP 아님) |

#### hardware Must (3 entries)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `hardware.health` | string\|null | OK/Warning/Critical | redfish | 서버 하드웨어 전체 상태 (BMC rollup health). "수집 성공 여부"가 아닌 "장비 자체 건강 상태" |
| `hardware.sku` | string\|null | — | redfish | 서버 제품 식별 번호. 벤더마다 의미 다름 (Lenovo=CTO 주문, HPE=파트, Dell=서비스 태그, Cisco=null) |
| `hardware.oem` | object | — | redfish | 벤더 전용 확장 데이터. 키 구조가 벤더마다 완전히 다름 |

#### memory Must (3 entries)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `memory.total_basis` | string | physical_installed/os_visible/hypervisor_visible | redfish/os/esxi | total_mb 산출 기준. 같은 서버라도 채널마다 값 다를 수 있음 |
| `memory.installed_mb` | integer\|null | — | redfish/os/esxi | 물리 장착 메모리 (MB). Redfish 주로 제공 |
| `memory.visible_mb` | integer\|null | — | redfish/os/esxi | OS/하이퍼바이저 인식 메모리 (MB). OS/ESXi 주로 제공 |

#### cpu Must (1 entry)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `cpu.cores_physical` | integer\|null | redfish/os/esxi | 서버 전체 물리 코어 합계. "소켓당 코어"가 아닌 "전체 코어 수" |

#### storage Must (10 entries)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `storage.physical_disks[]` | array of object | — | redfish/os/esxi | 시스템 전체 물리 디스크 목록 (중복 제거). CapacityBytes=0 (Empty Bay) 제외 |
| `storage.physical_disks[].id` | string\|null | — | redfish/os | 물리 디스크 식별자. logical_volumes[].member_drive_ids 에서 참조 |
| `storage.physical_disks[].predicted_life_percent` | integer\|null | — | redfish | SSD 남은 미디어 수명 (%). HDD=null |
| `storage.controllers[].drives[]` | array of object | — | redfish | 컨트롤러별 드라이브 목록. RAID 구성 확인용 |
| `storage.logical_volumes[]` | array of object | — | redfish | RAID 논리 볼륨 목록. HBA 모드 / OS / ESXi = [] |
| `storage.logical_volumes[].id` | string\|null | — | redfish | 논리 볼륨 식별자. 벤더마다 형식 다름 |
| `storage.logical_volumes[].raid_level` | string\|null | RAID0/RAID1/RAID5/RAID6/RAID10/RAID50/JBOD | redfish | RAID 레벨. 표준 RAIDType 우선, Dell 레거시는 VolumeType fallback |
| `storage.logical_volumes[].member_drive_ids` | array of string | — | redfish | 구성 물리 드라이브 Id 목록. physical_disks[].id 와 매칭 |
| `storage.logical_volumes[].controller_id` | string\|null | — | redfish | 소속 컨트롤러 Id. controllers[].id 와 매칭 |
| `storage.logical_volumes[].total_mb` | integer\|null | — | redfish | 볼륨 용량 (MB). RAID 레벨에 따라 물리 디스크 합산과 다를 수 있음 |
| `storage.logical_volumes[].health` | string\|null | OK/Warning/Critical | redfish | 볼륨 건강 상태 |
| `storage.logical_volumes[].state` | string\|null | Enabled/Degraded/Offline | redfish | 볼륨 동작 상태 |

#### network Must (1 entry)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `network.interfaces[].link_status` | string\|null | linkup/linkdown/none/null | redfish/os/esxi | NIC 링크 상태. none=BMC 가 상태 미제공 (HPE/Cisco System NIC) |

#### firmware Must (1 entry)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `firmware[].component` | string\|null | redfish | 펌웨어 SoftwareId. 벤더마다 형식 다름 (Lenovo=BMC-AFBT-10, Dell=숫자, HPE=숫자/UUID, Cisco=슬롯명) |

#### users Must (3 entries)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `users[]` | array of object | os | OS 사용자 계정 목록 (Linux: getent passwd, Windows: Get-LocalUser). Redfish/ESXi=[] |
| `users[].name` | string | os | 계정 이름 (Linux: passwd 첫 필드, Windows: SamAccountName) |
| `users[].uid` | string\|integer | os | 사용자 ID (Linux: 정수 UID, Windows: SID 문자열) |

#### power Must (1 entry)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `power.power_supplies[].state` | string\|null | redfish | PSU 동작 상태 (Enabled/UnavailableOffline). health 와 별개 필드 |

#### system Must (1 entry)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `system.hosting_type` | string | virtual/baremetal/unknown | os | 호스팅 유형. virtual=VM guest, baremetal=물리, unknown=판별 불가 |

#### correlation / diagnosis Must (2 entries)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `correlation.host_ip` | string | redfish/os/esxi | 수집 대상 IP. Redfish 채널: BMC IP 와 동일 (정상) |
| `diagnosis.auth_success` | boolean\|null | redfish/os/esxi | 인증 성공 여부. null=인증 단계 미실행 또는 확인 불가 ("실패"가 아닌 "미확인") |

→ Must 합계: 8 + 2 + 1 + 3 + 3 + 1 + 12 + 1 + 1 + 3 + 1 + 1 + 2 = **39 entries**

---

### 3.2 Nice (20 entries) — vendor-specific / 채널-specific

수집 가능한 경우 제공되나 모든 vendor / 채널에서 보장되지 않음.

#### hardware Nice (1 entry)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `hardware.power_state` | string\|null | On/Off/PoweringOn/PoweringOff | redfish | 서버 전원 상태 |

#### storage Nice (5 entries)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `storage.logical_volumes[].name` | string\|null | redfish | 볼륨 이름 (예: "Virtual Disk 0") |
| `storage.logical_volumes[].boot_volume` | boolean\|null | redfish | 부트 볼륨 여부. Dell OEM(DellVolume.BootVolumeSource) 만 판별 가능 |
| `storage.physical_disks[].failure_predicted` | boolean\|null | redfish | SMART 기반 디스크 고장 예측 |
| `storage.summary` | object | redfish/os/esxi | 디스크 그룹 summary. 같은 단위 용량/미디어 디스크 수량 + 총량 |
| `storage.hbas[]` | object[] | redfish/os/esxi | FC HBA 목록 (wwpn / link_status / link_speed_gbps / port_type) |
| `storage.infiniband[]` | object[] | redfish/os/esxi | InfiniBand 어댑터 목록 (node_guid / link_status / rate) |

#### users Nice (2 entries)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `users[].groups` | array of string | os | 소속 그룹 목록 |
| `users[].home` | string\|null | os | 홈 디렉터리 경로 (Linux: passwd 6번째, Windows: 프로파일 경로) |

#### network Nice (5 entries)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `network.interfaces[].kind` | string | server_nic/os_nic/vmkernel | redfish/os/esxi | NIC 유형 |
| `network.summary` | object | — | redfish/os/esxi | NIC 그룹 summary. 같은 대역폭 NIC 수량 + link up 개수 |
| `network.adapters[]` | object[] | — | redfish/esxi | NIC 카드 정보 (manufacturer / model / part_number / serial / firmware) |
| `network.ports[]` | object[] | — | redfish | NIC port-level (adapter_id / port_id / link_status / speed / port_type) |
| `network.virtual_switches[]` | object[] | — | esxi | ESXi vSwitch 목록 (name / num_ports / mtu / pnics / portgroups) |
| `network.driver_map[]` | object[] | — | os | Linux interface → driver / VLAN ID / bond master 매핑 |

#### meta / diagnosis Nice (2 entries)

| path | type | enum | 채널 | 의미 |
|------|------|------|------|------|
| `meta.duration_ms` | integer\|null | — | redfish/os/esxi | 수집 소요 시간 (ms). 호스트 1대 기준 |
| `diagnosis.failure_stage` | string\|null | port/protocol/auth | redfish/os/esxi | 실패 시 단계 식별. null=실패 안 함 또는 단계 확인 불가 |

#### cpu / memory Nice (2 entries)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `cpu.summary` | object | redfish/os/esxi | CPU 그룹 summary. 같은 model 의 socket 합쳐 보여줌 |
| `memory.summary` | object | redfish/os/esxi | 메모리 그룹 summary. 같은 단위 용량 DIMM 의 수량 + 총량 + 전체 합 |

#### system Nice (1 entry)

| path | type | 채널 | 의미 |
|------|------|------|------|
| `system.runtime` | object | os | OS 운영 런타임 정보 (timezone / ntp / firewall / listening_ports / swap or pagefiles) |

→ Nice 합계: 1 + 6 + 2 + 6 + 2 + 2 + 1 = **20 entries**

---

### 3.3 Skip (6 entries) — 의도적 미수집 / 자명

수집 기술적으로 가능하나 의미가 자명하거나 보편적 미수집인 필드. `field_dictionary.yml` 에 `priority: skip` 으로 등록.

| path | type | enum | 채널 | skip 이유 |
|------|------|------|------|-----------|
| `users[].last_access_time` | string\|null | — | os | 수집 환경에 따라 보편적 null. 현재 baseline 미수집 |
| `storage.physical_disks[].media_type` | string\|null | SSD/HDD | redfish/os | 의미 자명 (SSD/HDD) |
| `storage.physical_disks[].protocol` | string\|null | SATA/SAS/NVMe | redfish | 의미 자명 (디스크 연결 프로토콜) |
| `cpu.architecture` | string\|null | — | os/esxi | 의미 자명 (예: x86_64) |
| `system.uptime_seconds` | integer\|null | — | os/esxi | 의미 자명 (가동 시간 초) |
| `firmware[].updateable` | boolean | — | redfish | 의미 자명 (펌웨어 업데이트 가능 여부) |

→ Skip 합계: **6 entries**

**총합: Must 39 + Nice 20 + Skip 6 = 65 entries.**

---

## 4. 채널별 envelope 예시

### 4.1 Redfish 채널 (Dell PowerEdge iDRAC9 기준)

> 출처: `schema/baseline_v1/dell_baseline.json`

```json
{
  "target_type": "redfish",
  "collection_method": "redfish_api",
  "ip": "10.1.2.3",
  "hostname": "10.1.2.3",
  "vendor": "dell",
  "status": "success",
  "sections": {
    "system": "not_supported",
    "hardware": "success",
    "bmc": "success",
    "cpu": "success",
    "memory": "success",
    "storage": "success",
    "network": "success",
    "firmware": "success",
    "users": "not_supported",
    "power": "success"
  },
  "diagnosis": {
    "auth_success": true,
    "failure_stage": null
  },
  "meta": { "duration_ms": 4200, "adapter_id": "dell_idrac9" },
  "correlation": { "host_ip": "10.1.2.3", "bmc_ip": "10.1.2.3" },
  "errors": [],
  "data": {
    "hardware": { "health": "OK", "sku": "...", "oem": { "chassis_service_tag": "..." } },
    "bmc": { "ip": "10.1.2.3" },
    "cpu": { "cores_physical": 32 },
    "memory": { "total_basis": "physical_installed", "installed_mb": 262144, "visible_mb": null },
    "storage": { "physical_disks": [...], "logical_volumes": [...], "controllers": [...] },
    "network": { "interfaces": [...] },
    "firmware": [{ "component": "BIOS", ... }],
    "power": { "power_supplies": [{ "state": "Enabled", ... }] }
  },
  "schema_version": "1"
}
```

**Redfish 채널 특징**:
- `system` / `users` = `not_supported` (하드웨어 채널은 OS 정보 / 로컬 계정 미수집)
- `bmc.ip` 와 `correlation.host_ip` 가 같은 값 (Redfish 는 BMC 통해 수집 — 정상)
- `memory.total_basis` = `physical_installed` (DIMM 장착 기준)
- `firmware[]` / `storage.logical_volumes[]` 가 풍부

### 4.2 OS 채널 (RHEL 8.10 raw fallback 기준)

> 출처: `schema/baseline_v1/rhel810_raw_fallback_baseline.json`

```json
{
  "target_type": "os",
  "collection_method": "agent",
  "ip": "10.2.3.4",
  "hostname": "rhel-app-01",
  "vendor": "dell",
  "status": "success",
  "sections": {
    "system": "success",
    "hardware": "not_supported",
    "bmc": "not_supported",
    "cpu": "success",
    "memory": "success",
    "storage": "success",
    "network": "success",
    "firmware": "not_supported",
    "users": "success",
    "power": "not_supported"
  },
  "diagnosis": {
    "auth_success": true,
    "failure_stage": null,
    "gather_mode": "raw_only",
    "python_version": "3.6.8"
  },
  "meta": { "duration_ms": 8100, "adapter_id": "linux_rhel" },
  "correlation": { "host_ip": "10.2.3.4" },
  "errors": [],
  "data": {
    "system": { "hostname": "rhel-app-01", "hosting_type": "baremetal", "runtime": {...} },
    "cpu": { "cores_physical": 24 },
    "memory": { "total_basis": "physical_installed", "installed_mb": 131072, "visible_mb": 130000 },
    "storage": { "physical_disks": [...], "logical_volumes": [], "filesystems": [...] },
    "network": { "interfaces": [...], "driver_map": [...] },
    "users": [{ "name": "root", "uid": 0, "home": "/root", "groups": [...] }]
  },
  "schema_version": "1"
}
```

**OS 채널 특징**:
- `hardware` / `bmc` / `firmware` / `power` = `not_supported`
- `diagnosis.gather_mode` 추가 — Linux 2-tier (`python_ok` / `raw_only` / `raw_forced`)
- `diagnosis.python_version` 추가 — 수집 대상 Python 버전
- `system.hosting_type` = `virtual` / `baremetal` / `unknown`
- `users[]` 풍부 (getent passwd 결과)
- `storage.logical_volumes` = [] (RAID 정보 없음 — Redfish 영역)

### 4.3 ESXi 채널 (VMware ESXi 7.x 기준)

> 출처: `schema/baseline_v1/esxi_baseline.json`

```json
{
  "target_type": "esxi",
  "collection_method": "vsphere_api",
  "ip": "10.3.4.5",
  "hostname": "esxi-host-01",
  "vendor": "dell",
  "status": "success",
  "sections": {
    "system": "success",
    "hardware": "success",
    "bmc": "not_supported",
    "cpu": "success",
    "memory": "success",
    "storage": "success",
    "network": "success",
    "firmware": "not_supported",
    "users": "not_supported",
    "power": "not_supported"
  },
  "diagnosis": { "auth_success": true, "failure_stage": null },
  "meta": { "duration_ms": 5300, "adapter_id": "esxi_7x" },
  "correlation": { "host_ip": "10.3.4.5" },
  "errors": [],
  "data": {
    "system": { "hostname": "esxi-host-01" },
    "hardware": { "vendor": "Dell Inc.", "model": "PowerEdge R740" },
    "cpu": { "cores_physical": 20 },
    "memory": { "total_basis": "hypervisor_visible", "installed_mb": null, "visible_mb": 196608 },
    "storage": { "physical_disks": [...], "datastores": [...] },
    "network": { "interfaces": [...], "virtual_switches": [...], "adapters": [...] }
  },
  "schema_version": "1"
}
```

**ESXi 채널 특징**:
- `bmc` / `firmware` / `users` / `power` = `not_supported`
- `memory.total_basis` = `hypervisor_visible` (ESXi 가 본 메모리)
- `network.virtual_switches[]` 포함 (vSwitch 정보)
- `storage.datastores[]` 포함 (vSphere datastore)

---

## 5. status 판정 규칙

> 정본 코드: `common/tasks/normalize/build_status.yml` (M-A3 의도 주석 강화 — 2026-05-06)

### 시나리오 4 매트릭스 (정본)

| # | 섹션 status | errors[] | overall.status | 의미 |
|---|-------------|----------|----------------|------|
| **A** | 모두 success | empty | `success` | 정상 수집 완료 |
| **B** | 모두 success | warnings 포함 | `success` | warning emit 시 status 영향 없음 (의도된 설계) |
| **C** | success + failed 혼재 | any | `partial` | 일부 섹션 수집 성공 / 일부 실패 |
| **D** | 모두 failed | any | `failed` | 전체 실패 또는 supported 0 |

**[INFO] 시나리오 B 의도 (M-A2 결정)**:
- 섹션 자체는 정상 수집 — 호출자가 데이터를 신뢰 가능
- `errors[]` 는 **사유 추적용 분리 영역** — overall status 판정에 영향 없음
- 호출자 시스템이 warning 분리 인식하려면 `envelope.errors[]` 별도 검사
- severity (error/warning/info) 도입 안 함 — rule 22 R7/R8 (5 fragment 변수 / 타입 정본) 영역

### 시나리오 B 발생 위치 (3 reference — 의도된 fallback / partial enumeration)

- `os-gather/tasks/linux/gather_memory.yml:171-175` — dmidecode 권한/미존재 → `total_basis=os_visible` fallback
- `os-gather/tasks/linux/gather_network.yml:208-209` — lspci stderr 비어있지 않음 → NIC partial enumeration
- `esxi-gather/tasks/normalize_storage.yml:79-83` — NFS/vSAN/vVOL datastore capacity 미수집

### 판정 코드 (build_status.yml)

```jinja
{%- set sec_vals = _norm_sections.values() | list -%}
{%- set supported_vals = sec_vals | reject('equalto','not_supported') | list -%}
{%- set success_count  = supported_vals | select('equalto','success') | list | length -%}
{%- set failed_count   = supported_vals | select('equalto','failed')  | list | length -%}
{%- if supported_vals | length == 0 -%}failed
{%- elif failed_count == 0 -%}success
{%- elif success_count == 0 -%}failed
{%- else -%}partial
{%- endif -%}
```

### sections 값 enum

| 값 | 의미 |
|----|------|
| `success` | 해당 섹션 수집 성공 |
| `failed` | 수집 시도했으나 실패 (`errors[]` 에 상세 기록) |
| `not_supported` | 이 채널/adapter 가 해당 섹션 미지원 (수집 시도 안 함) |

**주의**: `status: success` 는 "수집 성공"이지 "장비 정상"이 아님. `hardware.health` 가 `Critical` 이어도 status 는 success 일 수 있음 (수집 자체는 정상).

---

## 6. errors[] 형식

```json
{
  "errors": [
    {
      "section": "storage",
      "code": "REDFISH_ENDPOINT_404",
      "message": "Volumes endpoint not found at /redfish/v1/Systems/1/Storage/.../Volumes",
      "severity": "warning",
      "vendor": "dell",
      "timestamp": "2026-05-06T10:00:00Z"
    }
  ]
}
```

| 키 | 타입 | 의미 |
|----|------|------|
| `section` | string | 오류 발생 섹션. 섹션 외 = `precheck` / `gather` |
| `code` | string | 분류 코드 (예: `REDFISH_ENDPOINT_404`) |
| `message` | string | 사람 읽기 요약 (1줄) |
| `severity` | string | warning / error / info (선택적) |
| `vendor` | string | 벤더 (해당 시) |
| `timestamp` | ISO8601 | 발생 시각 |

[INFO] errors[] 항목이 있어도 status 가 `success` 일 수 있음 (시나리오 B — 5절 참조).

---

## 7. diagnosis 형식

> precheck 4단계 (ping → port → protocol → auth) + gather 모드 + 진단 details.

```json
{
  "diagnosis": {
    "precheck": {
      "ping": "ok",
      "port": "ok",
      "protocol": "ok",
      "auth": "ok"
    },
    "auth_success": true,
    "failure_stage": null,
    "gather_mode": "python_ok",
    "python_version": "3.11.9",
    "details": [
      { "stage": "vendor_detect", "result": "dell" }
    ]
  }
}
```

| 키 | 타입 | 채널 | 의미 |
|----|------|------|------|
| `precheck.ping` | string | redfish/os/esxi | ICMP/TCP SYN. ok / failed |
| `precheck.port` | string | redfish/os/esxi | 포트 응답 (SSH=22, WinRM=5986, vSphere=443, Redfish=443). ok / failed |
| `precheck.protocol` | string | redfish/os/esxi | HTTPS handshake / SSH banner / Redfish JSON 응답. ok / failed |
| `precheck.auth` | string | redfish/os/esxi | 자격증명 인증 결과. ok / failed |
| `auth_success` | bool\|null | redfish/os/esxi | 인증 성공 여부. null=미확인 |
| `failure_stage` | string\|null | redfish/os/esxi | 실패 단계 식별 (port / protocol / auth). null=실패 안 함 |
| `gather_mode` | string | os 전용 | Linux 2-tier 모드 (python_ok / raw_only / raw_forced) |
| `python_version` | string | os 전용 | 수집 대상 Python 버전 |
| `details` | array | redfish/os/esxi | 진단 이력. dict 형태 entry |

---

## 8. correlation 형식

```json
{
  "correlation": {
    "host_ip": "10.1.2.3",
    "bmc_ip": "10.1.2.3",
    "serial_number": "ABC1234",
    "system_uuid": "..."
  }
}
```

| 키 | 타입 | 의미 |
|----|------|------|
| `host_ip` | string | 수집 대상 IP. Redfish 채널: BMC IP 와 동일 (정상) |
| `bmc_ip` | string\|null | BMC 관리 IP. Redfish 채널만 |
| `serial_number` | string\|null | 서버 시리얼. 여러 채널에서 같은 장비 식별용 |
| `system_uuid` | string\|null | 시스템 UUID |

---

## 9. meta 형식

```json
{
  "meta": {
    "loc": "ich",
    "duration_ms": 4200,
    "started_at": "2026-05-06T10:00:00Z",
    "finished_at": "2026-05-06T10:00:04Z",
    "adapter_id": "dell_idrac9",
    "adapter_version": "1.0",
    "ansible_version": "2.20.3"
  }
}
```

| 키 | 타입 | 의미 |
|----|------|------|
| `loc` | string | 운영 사이트 (ich / chj / yi) |
| `duration_ms` | integer\|null | 수집 소요 시간 (ms). 호스트 1대 |
| `started_at` | ISO8601 | 시작 시각 |
| `finished_at` | ISO8601 | 종료 시각 |
| `adapter_id` | string | 선택된 adapter 식별자 |
| `adapter_version` | string | adapter 버전 |
| `ansible_version` | string | Ansible 버전 |

---

## 10. 호환성 정책 (rule 96 R1-B)

호출자 시스템은 envelope shape 가정으로 파싱한다. 필드 변경은 호출자 파싱 오류를 유발한다.

### 금지

- envelope 13 필드 추가 / 삭제 / 리네임 (rule 96 R1-B)
- `data.<section>.<field>` 신규 추가 / 삭제 / 리네임 (호환성 cycle 외)
- `sections` 값 종류 변경 (success / failed / not_supported 외 추가 금지)
- `status` enum 변경 (success / partial / failed 외 추가 금지)

### 허용 (Additive only — 호환성 cycle)

- 기존 path 유지 + 새 환경 fallback path 추가
- 호환성 fix: 기존 필드에 값이 없던 vendor 에서 값 채우기

### 신규 데이터 / 필드 추가 절차 (별도 cycle)

새 데이터 / 새 섹션 / 새 vendor 추가는 **별도 cycle** (호환성 cycle 외):

1. `schema/sections.yml` + `schema/field_dictionary.yml` + baseline 3종 동반 갱신 (rule 13 R1)
2. 영향 vendor baseline 전수 갱신 (`schema/baseline_v1/`)
3. `schema_version` 변경 시 사용자 명시 승인 (rule 92 R5)
4. ADR 작성 의무 (rule 70 R8 trigger — schema 변경)

---

## 11. 3채널 (Redfish/OS/ESXi) JSON 키 비교 (M-F2 — 2026-05-06)

> envelope 13 필드는 모든 채널 동일. **sections / data / errors / diagnosis 의 구체 키와 의미가 채널 별 차이**. 본 절은 그 차이를 매트릭스로 정리.

### 11.1 채널별 sections 매트릭스 (10 sections × 4 채널)

| section | Redfish | OS Linux | OS Windows | ESXi |
|---|---|---|---|---|
| `system` | ServiceRoot + Systems | `/etc/os-release` + `uname` (raw or facts) | `systeminfo` / WMI `Win32_OperatingSystem` | `esxcli system version` |
| `hardware` | Chassis | dmidecode (raw or facts) | `Get-CimInstance Win32_ComputerSystemProduct` | `esxcli hardware platform` |
| `bmc` | Managers | n/a (`not_supported`) | n/a (`not_supported`) | n/a (`not_supported`) |
| `cpu` | Systems.Processors | `/proc/cpuinfo` | `Win32_Processor` | `esxcli hardware cpu list` |
| `memory` | Systems.Memory | `/proc/meminfo` + dmidecode | `Win32_PhysicalMemory` | `esxcli hardware memory get` |
| `storage` | Systems.Storage + Volumes + Drives | `lsblk` + `lsscsi` + `df` | `Get-Disk` + `Get-PhysicalDisk` | `esxcli storage core device list` |
| `network` | Systems.EthernetInterfaces | `ip` / `ethtool` / `nmcli` | `Get-NetAdapter` + `Get-NetIPAddress` | `esxcli network nic list` |
| `firmware` | UpdateService | n/a (`not_supported`) | (한정) `Get-WindowsDriver` | `esxcli software vib list` |
| `users` | n/a (`not_supported`) | `getent passwd` (raw or facts) | `Get-LocalUser` | n/a (`not_supported`) |
| `power` | Chassis.Power / PowerSubsystem | n/a (`not_supported`) | n/a (`not_supported`) | n/a (`not_supported`) |

> 채널 별 source 차이 — 같은 envelope 키 의미는 동일 (Field Dictionary 정합).

### 11.2 같은 키 다른 source (주의 — 정규화 후 의미 동일)

| envelope 키 | Redfish source | OS Linux source | OS Windows source | ESXi source |
|---|---|---|---|---|
| `data.cpu.model` | `Systems.Processors[0].Model` | `/proc/cpuinfo` "model name" | `Win32_Processor.Name` | `esxcli hardware cpu list` Brand |
| `data.cpu.cores_total` | sum(Processors[].TotalCores) | `/proc/cpuinfo` "cpu cores" × sockets | `Win32_Processor.NumberOfCores` × sockets | esxcli cpu count |
| `data.memory.total_gb` | sum(Memory.CapacityMiB) / 1024 | dmidecode `physical_installed` (raw mode) | sum(`Win32_PhysicalMemory.Capacity`) | `esxcli hardware memory get` |
| `data.storage.physical_disks[].media_type` | `Drives[].MediaType` (HDD/SSD/NVMe enum) | `lsblk` + `smartctl` 추정 | `Get-PhysicalDisk.MediaType` (HDD/SSD/Unspecified — Windows 정규화 cycle 2026-04-29) | `esxcli storage core device list` IsSSD |
| `data.network.interfaces[].mac` | `EthernetInterfaces[].MACAddress` | `ip link` MAC | `NetAdapter.MacAddress` | `esxcli network nic list` MAC |
| `data.system.hostname` | `Systems.HostName` | `hostname` 명령 | `Win32_OperatingSystem.CSName` | `esxcli system hostname get` |

### 11.3 채널 고유 키 (다른 채널은 `not_supported`)

#### Redfish only

| 키 | 의미 |
|---|---|
| `data.bmc.firmware_version` | BMC (iDRAC/iLO/XCC/CIMC) 펌웨어 버전 |
| `data.bmc.network_protocols` | SSH / WinRM / Redfish enabled 상태 dict |
| `data.bmc.oem.idrac_*` | Dell DelliDRACCard 4 필드 (F50 phase 3) |
| `data.firmware[].component` | UpdateService 의 firmware list 각 entry |
| `data.power.psus[]` | Chassis.Power.PowerSupplies (legacy) 또는 PowerSubsystem.PowerSupplies |
| `data.power.psu_redundancy` | Chassis.Power.Redundancy |
| `data.hardware.serial` | Chassis 또는 Systems.SerialNumber |

#### OS Linux only

| 키 | 의미 |
|---|---|
| `data.system.python_mode` | `python_ok` / `python_missing` / `python_incompatible` / `raw_forced` (preflight.yml 산출) |
| `data.system.selinux_status` | `enabled` / `disabled` (raw 정규화 — Round 2 fix) |
| `data.system.kernel_release` | `uname -r` |
| `data.network.interfaces[].kind` | `ethernet` / `bond` / `bridge` / `vlan` / `container` / `lo` (raw 정규화) |
| `data.storage.logical_volumes[]` | LVM2 lv list (raw) |
| `diagnosis.details.gather_mode` | `python_ok` / `raw_forced` 등 |

#### OS Windows only

| 키 | 의미 |
|---|---|
| `data.system.runtime_swap` | namespace pattern (cycle 2026-04-29 Jinja2 loop scoping fix) |
| `data.network.interfaces[].interface_index` | `Win32_NetworkAdapter.InterfaceIndex` 기반 grouping |
| `data.storage.physical_disks[].media_type` | `HDD`/`SSD`/`Unspecified` enum (cycle 2026-04-29 정규화) |

#### ESXi only

| 키 | 의미 |
|---|---|
| `data.system.vsphere_version` | ESXi build / version |
| `data.system.auth_success` | 인증 성공 boolean (cycle 2026-04-29 정규화 — vendor_aliases 적용 후) |
| `data.network.dns_servers[]` | DNS dict-level drill-in (cycle 2026-04-29 fix) |
| `data.network.interfaces[].netmask_bits` | /22, /26, /28 netmask bit 카운팅 (cycle 2026-04-29) |
| `data.storage.datastores[]` | ESXi datastore list (vSphere API) |
| `data.network.virtual_switches[]` | vSwitch / portgroup |

### 11.4 정규화 규칙 차이 (같은 envelope 키, 다른 가공)

```
envelope: data.cpu.cores_total

Redfish:  sum(Systems.Processors[].TotalCores)
          → 표준 Redfish enum int

Linux:    /proc/cpuinfo "cpu cores" × sockets
          → set_fact + multiply (raw mode 시 dmidecode 보강)

Windows:  Win32_Processor.NumberOfCores × sockets
          → WMI count

ESXi:     esxcli hardware cpu list | wc -l (정규화)
          → vSphere API count
```

```
envelope: data.memory.total_gb

Redfish:  sum(Systems.Memory[].CapacityMiB) / 1024
          → MiB → GB 변환

Linux:    dmidecode physical_installed (raw mode 정밀)
          또는 /proc/meminfo MemTotal (Python mode)

Windows:  sum(Win32_PhysicalMemory.Capacity) / 1024^3
          → byte → GB 변환

ESXi:     esxcli hardware memory get
          → MB → GB 변환
```

```
envelope: data.storage.physical_disks[].media_type

Redfish:  Drives[].MediaType
          → 'HDD' / 'SSD' / 'NVMe' (DMTF enum)

Linux:    lsblk + smartctl 추정
          → 'HDD' / 'SSD' (Round 4 정규화)

Windows:  Get-PhysicalDisk.MediaType
          → 'HDD' / 'SSD' / 'Unspecified' (cycle 2026-04-29 정규화 — SSD/HDD enum)

ESXi:     esxcli storage core device list IsSSD bool
          → True → 'SSD', False → 'HDD'
```

### 11.5 status 판정 차이 (not_supported 케이스)

| 채널 | not_supported 케이스 | 사례 |
|---|---|---|
| Redfish | endpoint 404 → not_supported (DMTF 표준 변천 fallback 후) | iDRAC 7 의 PowerSubsystem 부재 → Power fallback → 둘 다 부재 시 not_supported |
| Redfish | 채널 자체 미지원 | system / users 섹션은 항상 not_supported |
| OS Linux | 명령 출력 없음 / Python 미설치 / WSL 환경 | Python 3.6 환경 → raw_forced fallback. raw 도 실패 시 not_supported |
| OS Linux | 채널 자체 미지원 | hardware / bmc / firmware / power = not_supported |
| OS Windows | WMI 조회 실패 / WinRM 미연결 | network adapter 부재 시 not_supported |
| OS Windows | 채널 자체 미지원 | hardware / bmc / firmware / power = not_supported |
| ESXi | esxcli 명령 실패 / vSphere 응답 없음 | datastore 부재 환경 → not_supported |
| ESXi | 채널 자체 미지원 | bmc / firmware / users / power = not_supported |

### 11.6 errors[] 형식 (3채널 동일)

```json
{
  "category": "<섹션명>",      // 예: "cpu", "storage", "account_service"
  "message": "<요약 메시지>",   // 사용자 친화 (한국어 / 영어 혼용)
  "detail": "<원인 detail>"    // 선택 — HTTP code / errno / vendor 메시지
}
```

→ rule 13 R5 / rule 96 R1-B — `errors[]` 의 dict shape 는 3채널 모두 동일.

### 11.7 diagnosis 형식 차이

```
Redfish: {
  precheck: {ping, port, protocol, auth},
  vendor_detected: <vendor>,
  details: {adapter_id, account_service_*, ...}
}

OS Linux: {
  precheck: {ping, port, protocol},
  details: {gather_mode, python_version, selinux_*}
}

OS Windows: {
  precheck: {ping, port, protocol, auth},
  details: {winrm_transport, namespace_pattern}
}

ESXi: {
  precheck: {ping, port, protocol, auth},
  details: {vsphere_version, datastore_count, ...}
}
```

→ details dict shape 는 채널 별로 다른 키 (channel-specific). top-level 4 키 (precheck / vendor_detected / details / [기타]) 는 동일.

### 11.8 채널 간 envelope 호환성 검증

```bash
# 모든 채널 baseline 의 envelope 13 필드 동일성 검증
python scripts/ai/hooks/output_schema_drift_check.py
```

→ Jenkins Stage 3 (Validate Schema) 정합. 본 매트릭스 변경 시 동기화 의무 (rule 13 R1).

---

## 관련

- rule 13 R5 — envelope 13 필드 정본
- rule 96 R1-B — envelope shape 변경 자제
- rule 92 R5 — schema 변경 사용자 명시 승인
- rule 22 R7/R8 — fragment 변수 / 타입 정본
- skill: `verify-json-output`
- 정본 코드: `common/tasks/normalize/build_output.yml`, `common/tasks/normalize/build_status.yml`
- 정본 schema: `schema/sections.yml`, `schema/field_dictionary.yml`
- baseline: `schema/baseline_v1/<vendor>_baseline.json`
- 관련 문서: `docs/09_output-examples.md`, `docs/07_normalize-flow.md`, `docs/10_adapter-system.md`, `docs/12_diagnosis-output.md`, `docs/16_os-esxi-mapping.md`

---

## 본 문서를 빠르게 읽는 법

| 알고 싶은 것 | 어느 절을 보면 되나 |
|--------------|---------------------|
| envelope 최상위에 어떤 필드가 있는가 | "1. Envelope 13 필드" |
| sections 가 success / failed / not_supported 어떤 의미인가 | "sections 값의 의미" |
| 특정 필드가 null 인 이유 | 해당 필드의 "정규화 규칙" 절 |
| status 가 success 인데 errors[] 에 뭐가 있는 이유 | "status 판정 규칙" 의 시나리오 B |
| 새 필드를 추가하면 어디를 갱신해야 하나 | rule 13 R7 (envelope 변경 시 docs/20 동기화 의무) |

## 다음 단계

| 다음 작업 | 문서 |
|---|---|
| 채널별 응답 실제 예시 | [09_output-examples.md](09_output-examples.md) |
| OS / ESXi 필드 매핑 표 | [16_os-esxi-mapping.md](16_os-esxi-mapping.md) |
| 호환성 매트릭스 (어느 벤더에서 어느 섹션이 되는지) | [22_compatibility-matrix.md](22_compatibility-matrix.md) |
| 호출자 입력 형식 | [05_inventory-json-spec.md](05_inventory-json-spec.md) |
