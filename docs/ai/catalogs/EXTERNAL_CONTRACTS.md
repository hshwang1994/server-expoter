# EXTERNAL_CONTRACTS — server-exporter

> 외부 시스템 (Redfish / IPMI / SSH / WinRM / vSphere) 계약 카탈로그. rule 28 #11 측정 대상 (TTL 90일). rule 96 origin 주석 정본.

## 일자: 2026-04-27 (Plan 3 초기 골격)

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

## 정본 reference

- `docs/ai/references/redfish/redfish-spec.md`
- `docs/ai/references/winrm/pywinrm.md`
- `docs/ai/references/python/pyvmomi.md`
- `docs/ai/references/vmware/community-vmware-modules.md`
- `.claude/ai-context/external/integration.md`
