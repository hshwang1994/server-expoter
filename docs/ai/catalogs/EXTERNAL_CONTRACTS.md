# EXTERNAL_CONTRACTS — server-exporter

> 외부 시스템 (Redfish / IPMI / SSH / WinRM / vSphere) 계약 카탈로그. rule 28 #11 측정 대상 (TTL 90일). rule 96 origin 주석 정본.

## 일자: 2026-04-28 (cycle-006 + full-sweep 갱신 — redfish_gather.py 변경 trigger 반영)

## Redfish API

### ServiceRoot 진입

| Endpoint | 용도 | 인증 |
|---|---|---|
| GET /redfish/v1/ | ServiceRoot (Manufacturer 추출) | 무인증 |

### 핵심 Resource

| Path 패턴 | 섹션 매핑 | 비고 |
|---|---|---|
| /redfish/v1/Chassis | hardware (vendor / model / serial) | OEM 별로 path 차이 |
| /redfish/v1/Systems | system / cpu / memory | summary fields |
| /redfish/v1/Systems/<id>/Storage | storage (controllers) | iDRAC9 5.x+ 표준 |
| /redfish/v1/Systems/<id>/Storage/<sid>/Drives | storage (drives) | NAA id |
| /redfish/v1/Systems/<id>/Storage/<sid>/Volumes | storage (volumes) | iDRAC9 5.x+ 표준, 구 펌웨어는 OEM only |
| /redfish/v1/Managers | bmc | iDRAC / iLO / XCC / CIMC |
| /redfish/v1/UpdateService/FirmwareInventory | firmware | 멤버 list |
| /redfish/v1/AccountService/Accounts | users (BMC accounts) | |
| /redfish/v1/Chassis/<id>/Power | power (PSU) | |

### Vendor별 OEM path

| Vendor | OEM 경로 |
|---|---|
| Dell | /redfish/v1/Dell/... (DellSystem 등) |
| HPE | Oem.Hp.Links.SmartStorage |
| Lenovo | 표준에 가까움 |
| Supermicro | AMI MegaRAC 기반, 표준에 가까움 |
| Cisco | UCS RAID controller OEM |

### 갱신 trigger (rule 28 #11)

- TTL 90일
- 펌웨어 업그레이드 (BMC 운영자 통보)
- BMC API path 변경 발견 (probe 결과)

## SSH (Linux gather)

- 라이브러리: paramiko (Ansible 내부)
- 인증: SSH key 또는 password (vault/linux.yml)
- privilege: become_method=sudo
- Linux 2-tier: Python 3.9+ → setup/shell, 그 외 → raw

## WinRM (Windows gather)

- 라이브러리: pywinrm 0.5.0
- 인증: NTLM (도메인) / Basic (로컬, HTTPS)
- Port: 5985 (HTTP) / 5986 (HTTPS)
- Vault: vault/windows.yml

## vSphere API (ESXi gather)

- 라이브러리: pyvmomi 9.0.0 + community.vmware 6.2.0
- 인증: vault/esxi.yml (root or SSO)
- 버전 지원: 6.x / 7.x / 8.x (adapters/esxi/*.yml 분기)
- pyvmomi 호환 매트릭스: 4 버전 backward (8.0.0 → 5.x ~ 8.x)

## IPMI

- 현재 server-exporter 미사용
- 향후 Redfish 미지원 BMC fallback 검토

## callback URL

- Method: POST
- 무결성 (rule 31): 공백 / 후행 슬래시 방어 (commit 4ccc1d7)
- payload: callback_plugins/json_only.py JSON envelope (6 필드)
- 재시도: Jenkins post stage 일부

## drift 발견 시 (rule 96 R4)

3 곳 기록:
1. 본 문서 (EXTERNAL_CONTRACTS.md)
2. `FAILURE_PATTERNS.md` — `external-contract-drift` / `external-contract-unverified`
3. `CONVENTION_DRIFT.md` — DRIFT-NNN
4. 해당 adapter / 상수 origin 주석

## redfish_gather.py 실측 endpoint / field (2026-04-27 cycle-003)

`redfish-gather/library/redfish_gather.py` 실 사용 path / field:

### Endpoint 진입 순서

1. `/redfish/v1/` (ServiceRoot) — 무인증, Manufacturer 추출
2. ServiceRoot에서 `Systems`.`@odata.id` link 따라가기
3. ServiceRoot에서 `Managers`.`@odata.id`
4. ServiceRoot에서 `Chassis`.`@odata.id`
5. Systems members[0] `@odata.id` → System 본체
6. System.`EthernetInterfaces`.`@odata.id` → 각 NIC member
7. System.`Storage`.`@odata.id` → controllers / Drives / Volumes
8. Manager.`Oem.Dell.DellManager` 등 vendor OEM (분기)

### 핵심 field (모든 vendor 공통 / dot path)

| Field | 위치 | server-exporter section |
|---|---|---|
| `Manufacturer` | ServiceRoot / System / Drive / Controller / Memory / NIC | meta.vendor (정규화) + 각 섹션 vendor |
| `Model` | System / Drive / Memory / NIC | hardware / storage / memory / network |
| `SerialNumber` | System / Chassis | hardware |
| `BiosVersion` | System | hardware / firmware |
| `BIOSReleaseDate` | System | firmware |
| `ProcessorSummary.{Count, Model, ...}` | System | cpu |
| `MemorySummary.TotalSystemMemoryGiB` | System | memory |
| `EthernetInterfaces` | System | network |
| `Storage` | System | storage |
| `Drives` | Storage/{id}/Drives | storage.physical_disks |
| `Volumes` | Storage/{id}/Volumes | storage.logical_volumes |
| `CapacityBytes` / `CapacityMiB` | Drive / Volume | storage 크기 |
| `Status.{State, Health, HealthRollup}` | 모든 resource | 헬스 모니터링 |
| `Power.PowerSupplies[]` | Chassis/{id}/Power | power |
| `AverageConsumedWatts` | Power | power.consumption |
| `UpdateService/FirmwareInventory/Members[]` | UpdateService | firmware |
| `AccountService/Accounts/Members[]` | AccountService | users (BMC accounts) |

### Vendor OEM 분기 (실측)

```python
# redfish_gather.py에서 발견:
'Dell' / 'DellSystem' / 'DellVolume'  # Dell OEM
# (HPE / Lenovo / Supermicro / Cisco는 OEM 별도 처리 — adapter YAML)
```

## 실 lab 발견 — 비표준 BMC (2026-04-29 cycle-015)

cycle-015 첫 연결성 검증에서 사용자 라벨 vs 실 Manufacturer drift 2건 (DRIFT-011):

### AMI Redfish Server 1.11.0 (10.100.15.32)

- 사용자 라벨: dell (GPU 카드 설치)
- 실 응답: `Vendor='AMI', Product='AMI Redfish Server', RedfishVersion=1.11.0`
- 분류: AMI MegaRAC (Supermicro / Asrock / whitebox 가능)
- 현재 adapter 매칭: `redfish_generic.yml` 또는 `supermicro_bmc.yml` 후보 — Dell adapter 매칭 안 됨
- 후속: 물리 호스트 식별 필요 (OPS-12)

### TA-UNODE-G1 RedfishVersion 1.2.0 (10.100.15.2)

- 사용자 라벨: cisco
- 실 응답: `Product='TA-UNODE-G1', RedfishVersion=1.2.0`
- 분류: 표준 Cisco UCS Product 형식 아님 (UCS C-series는 보통 `Product='UCS C220 M5'`)
- 가능성: Cisco TelePresence / Tetration / 3rd party
- 후속: 제품 시리즈 식별 필요 (OPS-13)

### Cisco BMC 일시 장애

- 10.100.15.1 → 503 Service Unavailable
- 10.100.15.3 → timeout 5s
- 다음 일과시간 재확인 (OPS-11)

## 정본 reference

- `redfish-gather/library/redfish_gather.py` (정본 — 약 350줄, stdlib only)
- `docs/ai/references/redfish/redfish-spec.md`
- `docs/ai/references/redfish/python-clients.md` (stdlib vs library 비교)
- `docs/ai/references/redfish/vendor-bmc-guides.md` (5 vendor BMC)
- `docs/ai/references/winrm/pywinrm.md`
- `docs/ai/references/python/pyvmomi.md`
- `docs/ai/references/vmware/community-vmware-modules.md`
- `.claude/ai-context/external/integration.md`
