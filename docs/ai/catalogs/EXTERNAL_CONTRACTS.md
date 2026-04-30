# EXTERNAL_CONTRACTS — server-exporter

> 외부 시스템 (Redfish / IPMI / SSH / WinRM / vSphere) 계약 카탈로그. rule 28 #11 측정 대상 (TTL 90일). rule 96 origin 주석 정본.

## 일자: 2026-04-30 (vendor detection robustness — Lenovo XCC2/XCC3 namespace prefix + BMC product hints + TLS legacy 호환) / 2026-04-30 (probe HTTP status_code 정합 매트릭스 추가) / 2026-04-28 (cycle-006 + full-sweep)

## ServiceRoot vendor detection — DMTF 표준 + vendor 동작 (2026-04-30 추가)

> 출처: [DSP0266 v1.15.0](https://redfish.dmtf.org/schemas/DSP0266_1.15.0.html), [DSP2046](https://www.dmtf.org/sites/default/files/standards/documents/DSP2046_2022.3.html), HPE/Lenovo/Dell/Cisco vendor 공식 문서.

### DMTF Redfish ServiceRoot 표준 필드 (top-level)
- `Vendor` 필드: ServiceRoot **v1.5.0+** 부터 표준 (str)
- `Product` 필드: ServiceRoot **v1.3.0+** 부터 표준 (str)
- `Manufacturer`는 ServiceRoot에 **없음** — Chassis/Managers/System 리소스에 표준
- `Oem` 객체: 표준 (vendor namespace 규약은 reverse-DNS 권장이지만 단순 vendor명도 허용)
- 무인증 접근 의무: `Services shall not require authentication to retrieve the service root and /redfish resources`

### Vendor별 ServiceRoot 동작 매트릭스

| Vendor | Oem 키 | Product 시그니처 | Vendor 필드 | Name 필드 | 비고 |
|---|---|---|---|---|---|
| Dell iDRAC9 5.x+ | `Oem.Dell` | "Integrated Dell Remote Access Controller" | "Dell Inc." (펌웨어별) | "Root Service" | v1.3+ ServiceRoot |
| HPE iLO5/6 | `Oem.Hpe` | "iLO 5" / "ProLiant" | "HPE" (iLO5 2.x+) | "Root Service" | iLO4는 `Oem.Hp` (legacy) |
| Lenovo XCC | `Oem.Lenovo` | "XClarity Controller" | "Lenovo" (펌웨어별) | "Root Service" | 표준 |
| Lenovo XCC2/XCC3 | **`Oem.Lenovo_xxx`** (namespace prefix) | "XClarity Controller" / "ThinkSystem" | 펌웨어별 | "Root Service" | namespace prefix 펌웨어 多 |
| Supermicro AMI MegaRAC | `Oem.Supermicro` 또는 부재 | "AMI MegaRAC SP" | 펌웨어별 | 펌웨어별 | X11/X12 펌웨어별 차이 |
| Cisco CIMC | Oem 부재인 펌웨어 多 | "Cisco UCS" / "CIMC" | 펌웨어별 | **"Cisco RESTful Root Service"** | Name 의존 |

### 구버전 펌웨어 (ServiceRoot v1.0~1.4)

- `Vendor` / `Product` 표준 필드 자체 부재
- 매칭 가능 단서: `Oem` 키, `Name` 필드, Manufacturer (Chassis/Managers fallback)
- 영향 BMC: 구 iDRAC7/8 펌웨어, iLO 4, IMM2

### server-exporter 매칭 알고리즘 (`redfish_gather._detect_vendor_from_service_root`)

1. **Oem 정확 매칭** — `Oem.{vendor}` 키 정확 매칭 (vendor_aliases.yml + _FALLBACK_VENDOR_MAP)
2. **Oem namespace prefix** — `{alias}_xxx` / `{alias}.xxx` (cycle 2026-04-30 추가, Lenovo XCC2/XCC3 호환)
3. **Vendor 필드 정확 매칭** (v1.5+ 표준)
4. **Product 필드 부분 일치** + `_BMC_PRODUCT_HINTS` (idrac/ilo/proliant/xclarity/thinksystem/xcc/imm2/megarac/cimc/ucs)
5. **Name 필드 부분 일치** + `_BMC_PRODUCT_HINTS` (Cisco "Cisco RESTful Root Service" catch)
6. 모두 fail → `None` (호출자가 unknown 처리)

### 적용 완료 (cycle 2026-04-30)

- **G1**: Oem 정확 매칭 + namespace prefix 매칭 (`Lenovo_xxx`, `Hpe_iLO` 등 호환)
- **G2**: `_BMC_PRODUCT_HINTS` 도입 — Product/Name 필드에 idrac/ilo/proliant/xclarity/thinksystem/xcc/imm2/megarac/cimc/ucs 매칭
- **G3**: ServiceRoot vendor=unknown 시 Chassis → Managers → Systems 의 Manufacturer fallback 순회
- **G4**: TLS legacy renegotiation + `DEFAULT@SECLEVEL=0` (verify=False 한정)
- **G5**: probe_redfish — payload=None (URLError/timeout/SSLError) 시 1초 backoff + 1회 retry
- **G6**: 401/403 응답의 `WWW-Authenticate: Basic realm="..."` 헤더에서 vendor hint (마지막 fallback)
- **G7**: Vendor 필드 — 정확 매칭 (원형 + trailing dot 제거 두 형식) + substring 매칭으로 보강 (`Dell Inc.`, `Cisco Systems Inc.` 등)

## TLS handshake 호환성 (2026-04-30 추가)

> 출처: Python 3.12 changelog (OpenSSL 3.x), CVE-2023-0286 / CVE-2009-3555 컨텍스트.

### 문제

- Python 3.12 + OpenSSL 3.x default `ssl.create_default_context()`:
  - TLS 1.2 미만 / weak cipher / legacy renegotiation **차단**
  - 구 BMC (HPE iLO4, Lenovo IMM2, 일부 iDRAC7/8 펌웨어) handshake 실패
  - precheck Stage 3 → URLError → "Redfish 미지원" 오판정 (curl `-k`는 통과)

### 해결 (cycle 2026-04-30)

`precheck_bundle._build_ssl_context` + `redfish_gather._ctx` 둘 다 verify=False 시:

```python
if hasattr(ssl, 'OP_LEGACY_SERVER_CONNECT'):
    ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
try:
    ctx.set_ciphers('DEFAULT@SECLEVEL=0')
except ssl.SSLError:
    pass
```

- 적용 영역: **verify=False 한정** (사내 BMC self-signed 망)
- 보안 trade-off: verify=True (운영 외 환경 — 본 시스템에선 미사용) 시 영향 없음
- curl `-k` 와 동등한 관용성

## HTTP status_code → protocol_supported 정합 매트릭스 (2026-04-30 추가)

> precheck Stage 3 (probe_*) 및 본 수집 endpoint 호출 시 의미. 200 외 응답이 모두 fail 이 아니라는 외부 계약. 본 매트릭스는 5 commits (c23d185f / 31178f8c / a60e42b5 / 6ea2c292 / 9d5c957b) 의 root reference.

### Redfish ServiceRoot (`GET /redfish/v1/`)

| status_code | 의미 | server-exporter 처리 | 발생 BMC 예시 |
|---|---|---|---|
| 200 | 정상 무인증 응답 (표준) | protocol_supported=True, JSON 추출 | Dell iDRAC 9 5.x+, HPE iLO5 표준, Lenovo XCC, Supermicro |
| 401 | 인증 필요 (보안 강화 펌웨어) | protocol_supported=True, requires_auth_at_root=true | HPE iLO5/6 일부 펌웨어, Lenovo XCC 일부 |
| 403 | IP 화이트리스트 / 권한 부족 | protocol_supported=True, requires_auth_at_root=true | 관리망 제한 환경 |
| 404 | path 자체 없음 = 진짜 미지원 | protocol_supported=False | Redfish 미지원 BMC |
| 500 | BMC 내부 오류 (응답 깨짐) | protocol_supported=False | 펌웨어 버그 |
| 503 | 일시 과부하 / 부팅 직후 | protocol_supported=True (재시도 가능) | BMC 재시작 직후 / 일시 과부하 |
| timeout | 응답 무 | protocol_supported=False | 네트워크 / BMC 다운 |
| SSL fail | TLS 호환성 | protocol_supported=False | 구형 BMC TLS 1.0만 |

### vSphere `/sdk` (`GET https://{ip}/sdk`)

| status_code | 의미 | server-exporter 처리 |
|---|---|---|
| 200 | 정상 응답 | OK |
| 301/302 | 리다이렉트 | OK (서비스 살아있음) |
| 401/403 | 인증 / 권한 (vCenter SSO) | OK (Stage 4 또는 본 수집 처리) |
| 404 | ESXi 7+ GET /sdk 정상 동작 (POST SOAP만 허용) | OK |
| 405 | Method Not Allowed (정상) | OK |
| 500 | SOAP fault (정상 — discover 응답) | OK |
| 503 | 일시 과부하 | OK (재시도) |
| timeout / SSL fail | 실 장애 | fail |

### WinRM `/wsman` (`GET https://{ip}:5986/wsman`)

| status_code | 의미 | server-exporter 처리 |
|---|---|---|
| 200 | 정상 응답 | OK |
| 401 | 인증 필요 (WinRM 표준) | OK |
| 403 | SPN 불일치 / 잠긴 계정 | OK (서비스 살아있음) |
| 405 | GET 메서드 미지원 (정상 — POST(SOAP) 본 수집) | OK |
| 503 | IIS 재시작 중 | OK (재시도) |
| 404 / connection refused | 진짜 WinRM 미지원 | fail |

### Storage Controllers fetch (`GET /redfish/v1/Systems/<id>/Storage/<sid>/Controllers`)

본 endpoint 는 인증 후 호출. 401/403/503 은 권한 부족 / 일시 상태 → controller_fetch_status 메타 + errors[] 누적 (a60e42b5 fix). 빈 dict 만 반환하지 않음.

### timeout 정책

| 단계 | 기본값 | 비고 |
|---|---|---|
| precheck Stage 1+2 (TCP) | 3.0s | 빠른 차단 |
| precheck Stage 3 (protocol) | **15.0s** (이전 6.0s) | 노후 BMC 응답 시간 대응 (31178f8c) |
| precheck Stage 4 (auth) | 8.0s | |
| 본 수집 (redfish_gather) | 30s | site.yml `_rf_timeout` |

### 위 매트릭스의 운영 의미

이전 구현 (2026-04-30 이전)은 200 외 응답을 모두 fail로 분류 → 인증 강화 BMC / vCenter SSO / 일시 과부하 환경에서 false negative 빈발. 본 매트릭스가 정본.

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

### ~~AMI Redfish Server 1.11.0 (10.100.15.32)~~ — RESOLVED

- ~~사용자 라벨: dell (GPU 카드 설치)~~
- ~~실 응답: `Vendor='AMI', Product='AMI Redfish Server', RedfishVersion=1.11.0`~~
- **resolved (cycle-015)**: 사내 lab 부재 확인 → `inventory/lab/redfish.json` + `vault/.lab-credentials.yml`에서 제거. OPS-12 closed.
- 보존 이유: AMI Redfish 1.11.0 응답 형식은 향후 AMI MegaRAC BMC (Supermicro 등) 추가 시 reference로 활용

### ~~TA-UNODE-G1 RedfishVersion 1.2.0 (10.100.15.2)~~ — RESOLVED

- ~~사용자 라벨: cisco~~
- ~~실 응답: `Product='TA-UNODE-G1', RedfishVersion=1.2.0`~~
- **resolved (cycle-015)**: 사내 lab 부재 확인 → 제거. OPS-13 closed.
- 보존 이유: 표준 Cisco UCS 응답과 다른 형식 reference

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
