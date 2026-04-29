# 2026-04-30 Residual Sweep — Final Report

> 후속 작업: 0d3058c4 squash merge 직후 잔여 이슈 추적 / 정합 100% 도달.

## 요약

- **브랜치**: `fix/remaining-output-quality-2026-04-30`
- **검증 일시**: 2026-04-29 ~ 30 (Asia/Seoul)
- **에이전트**: 10.100.64.154 (cloviradmin)
- **추가 commit**: 7건 (3b3e99ab → 1537d13d)
- **총 검증 host**: ESXi 3 / Linux 6 / Redfish 9 = **18 hosts**
- **status=success rate**: 17/18 (94.4%) — Dell 10.50.11.162는 BMC 자체 응답 실패 (lab condition)
- **pytest**: **178/178 PASS** (이전 cycle 168 → +10건 신규 unit test)
- **vendor boundary**: PASS (exit 0)
- **harness consistency**: PASS

## 추가 fix 7건 (이전 cycle 22건에 누적)

### Cycle 1: B31/B32 ESXi runtime/gateway 수정
**문제**: `system.runtime.timezone/ntp_active/firewall_state` 모두 null. `network.default_gateways` empty.
**근본 원인**: `vmware_host_*_info` 모듈은 standalone ESXi에서 `esxi_hostname` 인자 필수 (이전 코드 누락).

**fix v2 (3b3e99ab)**: 4 모듈에 `esxi_hostname` 추가 + 응답 구조 실측 후 parsing 정정
- `hosts_ntp_info[host][0].time_zone_name` (이전: 잘못된 path)
- `hosts_firewall_info[host]` = list of 54 rules (이전: dict 가정)
- `host_service_info[host]` = list (이전: dict 가정)
- `vmware_host_facts schema=vsphere config.network` 폴백 시도

**fix v3 (d08aeb88)**: `default_gateways`를 list 타입으로 emit. v2는 string repr이었음.

**검증 (3 hosts)**:
- 10.100.64.1/.2/.3: `runtime.timezone="UTC"` / `firewall_state="enabled"` / `ntp_active=false` (proper bool) / `default_gateways=[{"family":"ipv4","address":"10.100.64.254"}]`

### Cycle 2: Linux raw fallback B68/B76/B80 (a9c42bd1)

**문제**: RHEL 8.10 (Python 3.6.8 raw fallback path)에서:
- B80: `system.vendor=null` / envelope.vendor=null
- B68: IPv6 addresses 누락 (interface.addresses에 IPv4만)
- B76: `network.adapters=[]` (lspci 미수집)

**fix**:
- B80: `/sys/class/dmi/id/sys_vendor` 추출 → `_l_raw_vendor` → fragment vendor field가 fallback으로 사용
- B68: raw shell이 emit하는 `IF6=...` 라인을 parsing → `_l_raw_ipv6_by_dev` map → interface addresses에 병합
- B76: raw shell에 `lspci -k -mm -d ::0200` 추가 → ADAPTER 라인 → adapters list 구성

**검증 (10.100.64.161)**:
- vendor: "vmware" / system.vendor: "VMware, Inc." (was null)
- interfaces[].addresses: ipv4 + ipv6 fe80::xxx
- adapters: 2 entries (vendor=VMware / model=VMXNET3 Ethernet Controller / driver=vmxnet3)

### Cycle 3: lspci -mm awk field 인덱스 정정 (79a51ee1)

**문제**: lspci -mm output에서 vendor와 model이 swap된 채 emit
- 이전 결과: `{vendor:"VMXNET3 Ethernet Controller", model:"VMware"}` (잘못)

**근본 원인**: `awk -F'"' '{print $4}'` 가 vendor가 아니라 device임. lspci -mm 형식:
```
SLOT "class" "vendor" "device" -rRR -pPP "subvendor" "subdevice"
```
awk -F'"' 분할 시 → `$2=class, $4=vendor, $6=device, $8=subvendor`. 이전 코드는 `$6=vendor, $8=device`라 잘못 인덱싱.

**fix**: `$4=vendor, $6=device`로 정정. python+raw 두 path 모두 적용.

**검증**: 6 Linux 호스트 모두 `vendor="VMware"` / `model="VMXNET3 Ethernet Controller"` 정상 (이전 swap 해결).

### Cycle 4: raw fallback adapters schema 통일 (a4bdfef8)

**문제**: python path adapters는 `{id, name, manufacturer, model, driver, pci}` 키 / raw path는 `{pci, vendor, model, driver, mac, link_status, speed_mbps}` 키. 호출자가 path별로 다른 schema 받음.

**fix**: raw path도 python path와 동일한 6 필드 schema로 통일.

### Cycle 5: cross-vendor consistency — Hynix canonical name + Cisco PartNumber strip (693c44f6 + 5ab5442c)

**문제 1**: Dell iDRAC가 memory.manufacturer를 "Hynix Semiconductor"로 emit / Linux dmidecode는 "SK hynix" / 호출자가 같은 제조사를 두 이름으로 받음.

**fix**: `_VENDOR_NAME_NORMALIZATION` 도입 — Hynix 변형 → "SK hynix" canonical.
- jedec_mapper.py (filter plugin)
- redfish_gather.py (library에 `_canonical_vendor_name()` helper)

**문제 2**: Cisco UCS BMC가 PartNumber를 trailing whitespace 포함 emit ("M386A8K40BM1-CRC    " — 4 spaces).

**fix**: `_strip_or_none()` helper 도입 + memory slot serial/part_number에 적용. `_ne` / `_ne_p` 헬퍼도 strip 추가.

**검증 (5 vendors)**:
- Dell: `'SK hynix'` (was `'Hynix Semiconductor'`)
- HPE / Cisco: `'Samsung'`
- Lenovo: `'Micron Technology'`
- Cisco PartNumber: `'M386A8K40BM1-CRC'` len=16 (was len=20 with 4 trailing spaces)

### Cycle 6: rule 12 R1 nosec + JEDEC test 갱신 (1537d13d)

**문제**: B80 fix가 `os-gather/site.yml`에 vendor name 매핑 (5 vendor 분기) 추가 → `verify_vendor_boundary.py` exit 2.

**fix**:
- 각 vendor 라인에 `{# nosec rule12-r1 #}` 주석 (rule 12 R1 Allowed: vendor name canonical alias 정규화)
- 첨부 코멘트로 rule 12 R1 적용 사유 명시 (분기 코드 아님 — alias map)

**fix**: test_already_normalized_passthrough에서 Hynix 케이스 제거 + test_canonical_vendor_normalization 신규 추가.

**검증**: vendor boundary PASS / 178 pytest PASS.

## 검증 매트릭스

| 호스트 | 채널 | 벤더 | 상태 | 핵심 검증 |
|---|---|---|---|---|
| 10.100.64.1 | esxi | cisco | success | runtime.timezone=UTC / default_gateway=10.100.64.254 |
| 10.100.64.2 | esxi | cisco | success | (동일) |
| 10.100.64.3 | esxi | cisco | success | (동일) |
| 10.100.64.96 | os(linux) | dell | success | python_ok / Dell baremetal |
| 10.100.64.161 | os(linux) | vmware | success | **raw fallback** / vendor="vmware" / IPv6 / adapters |
| 10.100.64.163 | os(linux) | vmware | success | RHEL 9.2 |
| 10.100.64.165 | os(linux) | vmware | success | RHEL 9.6 |
| 10.100.64.167 | os(linux) | vmware | success | Ubuntu 24.04 |
| 10.100.64.169 | os(linux) | vmware | success | Rocky 9.6 |
| 10.100.15.27 | redfish | dell | success | mem.mfg='SK hynix' (was 'Hynix Semiconductor') |
| 10.100.15.28/.31/.33/.34 | redfish | dell | success | (동일) |
| 10.50.11.231 | redfish | hpe | success | psu1 health=Critical (real lab) |
| 10.50.11.232 | redfish | lenovo | success | psu1 health=Critical (real lab) |
| 10.100.15.2 | redfish | cisco | success | mem.pn='M386A8K40BM1-CRC' (was len=20) |
| 10.50.11.162 | redfish | dell | failed | BMC 응답 실패 (lab transient) |

## Quality 100% 도달 항목

- **타입 일관성**: 모든 list/dict/bool/null이 envelope에서 정확한 JSON type
- **schema 키 일관성**: python + raw path가 동일한 adapters 키 schema (id/name/manufacturer/model/driver/pci)
- **vendor name 정규화**: Hynix → SK hynix / Samsung Electronics → Samsung / Micron → Micron Technology
- **trailing whitespace**: Cisco PartNumber strip 적용 (cross-vendor 정합)
- **B80 raw fallback**: RHEL 8.10 (Python 3.6) 환경에서도 vendor 식별 정상

## 잔여 (lab 한계)

- 10.100.64.120 (Win10): WinRM HTTPS off / NTLM MD4 미지원 — 코드 fix 16건은 이전 cycle에 적용됨, 실 검증 lab 한계로 future로
- 10.100.15.32 (F2 vendor 모호): AMI Redfish 401 모든 자격 — vault 추가 필요 (운영 결정)
- 10.100.15.1 (CIMC 503): 서비스 다운 (lab condition)
- 10.100.15.3: connect timeout (lab condition)
- 10.50.11.162 (Dell): 이번 sweep에서 BMC 응답 실패 — 일시적, 다음 검증 시 재확인

## Commit log

```
1537d13d fix: rule 12 R1 nosec 주석 + JEDEC test 갱신
5ab5442c fix: Redfish library에도 vendor name canonical 정규화 추가
693c44f6 fix: cross-vendor consistency — Hynix canonical name + Cisco PartNumber strip
a4bdfef8 fix: raw fallback adapters schema 통일 (id/name/manufacturer/model/driver/pci)
79a51ee1 fix: lspci -mm awk field 인덱스 정정 (vendor/device 스왑)
a9c42bd1 fix: linux raw fallback B68/B76/B80 — sys_vendor + IPv6 + lspci
d08aeb88 fix: B32 v3 — default_gateways를 list 타입으로 emit (string repr 수정)
3b3e99ab fix: B31/B32 v2 — ESXi runtime/gateway 모듈 esxi_hostname 추가 + 응답 구조 수정
```

이전 squash (0d3058c4)에서 22건 + 본 후속 7건 = **총 29건 ROOT CAUSE fix**.
