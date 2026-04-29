# ESXi 잔류 미세 이슈 4건 fix — Round 12 후속 (보강 cycle)

> 일시: 2026-04-29
> 환경: agent 10.100.64.154, ansible-core 2.20.3, community.vmware 6.2.0, ESXi 7.0.3
> 사용자 명시 결정: "권장 작업 모두 수행"

---

## 1. 배경

Round 12 (ESXi BUG #1/#2/#4 fix) 종료 후 잔류 미세 이슈 4건:

| # | 잔류 이슈 | 영향 |
|---|---|---|
| 1 | `network.dns_servers=[]` / `default_gateways=[]` | DNS / gateway 정보 미제공 |
| 2 | `network.adapters[].speed_mbps` int (10000) / "N/A" string 혼재 | 호출자 cross-channel 타입 일관성 깨짐 |
| 3 | `cpu.architecture` / `system.architecture` / `cpu.max_speed_mhz` null | facts 미반환 시 폴백 부재 |
| 4 | `include_vars name:` reserved-name 경고 4곳 | callback 영역 밖 stderr noise |

---

## 2. 진단 (raw 응답 캡처)

### vmware_host_dns_info 모듈 (community.vmware 6.2.0 + ESXi 7.0.3)

`esxi_hostname` 파라미터 필수 (생략 시 `cluster_name or esxi_hostname required` error).

응답 형태:
```json
{
  "hosts_dns_info": {
    "esxi01": {
      "dhcp": false,
      "host_name": "esxi01",
      "domain_name": "",
      "ip_address": ["10.100.64.251"],
      "search_domain": [],
      "virtual_nic_device": null
    }
  }
}
```

→ `ip_address` 가 DNS 서버 list. `search_domain` 추가 (envelope 키 안 추가, 잠재 활용).

### vmk0 raw (vmware_host_facts)

`ansible_vmk0` keys: `['device', 'ipv4', 'macaddress', 'mtu']` — `gateway` / `active` 키 없음. → default_gateway 는 별도 source 필요 (vmware_host_dns_info 에도 없음, ESXi shell 수준 접근 필요). **이번 cycle 에서는 보류**. dns_servers 만 fix.

---

## 3. 코드 fix

### Fix 1: DNS 추출 (`vmware_host_dns_info` 도입)

- `esxi-gather/tasks/collect_dns.yml` (NEW) — vmware_host_dns_info 호출, `_e_raw_dns` / `_e_dns_ok`
- `esxi-gather/site.yml` — collect_dns task 추가 (collect_datastores 이후)
- `esxi-gather/tasks/normalize_network.yml` — `_e_dns_servers` 추출 로직: `_e_raw_dns` 1순위, 기존 `_e_raw_config` drill-in 폴백. `_e_search_domains` 추가 (잠재 활용).

### Fix 2: speed_mbps 타입 정규화

- `esxi-gather/tasks/collect_network_extended.yml` — adapters loop 에서 `actual_speed` int 캐스팅:
  - number → int
  - string ("1000 Mbps" 등) → digit 추출 후 int
  - "N/A" / 빈 → None
- `actual_duplex` 도 "N/A" → None 정규화

### Fix 3: cpu.architecture / max_speed_mhz / system.architecture 폴백

- `esxi-gather/tasks/normalize_system.yml`:
  - `system.architecture` / `cpu.architecture` / `summary.groups[].architecture`: `ansible_machine` 미반환 시 `'x86_64'` (ESXi 7.x 는 모두 x86_64, ARM/Apple 서버 미지원)
  - `cpu.max_speed_mhz` / `summary.groups[].max_speed_mhz`: `ansible_processor_mhz` 미반환 시 CPU model 의 `@ N.NGHz` 패턴에서 추출 (Intel/AMD 표준 표기)

### Fix 4: `include_vars name:` reserved keyword 경고 우회 (2곳)

- `esxi-gather/site.yml` 의 vendor_aliases 로드 → `set_fact + lookup('file') | from_yaml`
- `redfish-gather/tasks/detect_vendor.yml` 의 vendor_aliases 로드 → 동일 패턴

vault 파일 (`redfish-gather/tasks/load_vault.yml` 의 2곳)은 ansible-vault encrypt 라 `lookup('file')` 우회 불가 (`include_vars` 만 자동 decrypt). **2곳 잔류 — 호출자 영향 0**.

---

## 4. 실 ESXi 검증 (10.100.64.1)

| 필드 | 이전 | 현재 |
|---|---|---|
| `system.architecture` | null | `x86_64` |
| `cpu.architecture` | null | `x86_64` |
| `cpu.max_speed_mhz` | null | `2200` (Intel E5-2699 v4 @ 2.20GHz 추출) |
| `cpu.summary.groups[0].max_speed_mhz` | null | `2200` |
| `cpu.summary.groups[0].architecture` | null | `x86_64` |
| `network.dns_servers` | `[]` | `["10.100.64.251"]` |
| `network.adapters[].speed_mbps` (Connected) | `10000` (int) | `10000` (int, 동일) |
| `network.adapters[].speed_mbps` (Disconnected) | `"N/A"` (string) | `null` (정규화됨) |
| `network.adapters[].duplex` (Disconnected) | `"N/A"` (string) | `null` |

10.100.64.2 (esxi02) 도 동일 패턴 검증 완료 (dns=`['10.100.64.251']`, arch=`x86_64`, mhz=`2200`).

---

## 5. 검증 (정적)

- pytest **158/158 PASS**
- `verify_harness_consistency.py` PASS (rules 28 / skills 43 / agents 49 / policies 9)
- `verify_vendor_boundary.py` PASS (vendor 하드코딩 0건)
- `ansible-playbook --syntax-check esxi-gather/site.yml` PASS

---

## 6. baseline 갱신

`schema/baseline_v1/esxi_baseline.json` (esxi02 실측 재수집):
- `system.architecture: null → "x86_64"`
- `cpu.architecture: null → "x86_64"`
- `cpu.max_speed_mhz: null → 2200`
- `cpu.summary.groups[0].architecture: null → "x86_64"`, `.max_speed_mhz: null → 2200`
- `network.dns_servers: [] → ["10.100.64.251"]`
- `network.adapters[].speed_mbps`: Disconnected = `"N/A" → null`
- `network.adapters[].duplex`: Disconnected = `"N/A" → null`

---

## 7. 잔류 (이번 cycle에서 보류)

- **`default_gateways=[]`**: vmware_host_facts / dns_info / vmk0 raw 모두 gateway 미반환. ESXi shell 수준 (`esxcfg-route -l`) 접근 필요. 별도 cycle.
- **`include_vars name:` 경고 2곳 (vault)**: `redfish-gather/tasks/load_vault.yml` — vault 자동 decrypt 의존이라 `lookup('file')` 우회 불가. ansible-core upstream 개선 대기.
- **`interfaces[].link_status="unknown"`**: `ansible_vmk0` 에 `active` 필드 없음. esxi shell 또는 `vmware_vmkernel_info` 추가 호출 필요.

---

## 8. 변경 파일

```
esxi-gather/site.yml                              (+5 lines)   — collect_dns task + include_vars 우회
esxi-gather/tasks/collect_dns.yml                 (NEW, 39 lines) — vmware_host_dns_info 호출
esxi-gather/tasks/normalize_system.yml            (+15 lines)  — architecture/max_speed_mhz 폴백
esxi-gather/tasks/normalize_network.yml           (+15 lines)  — _e_dns_servers _e_raw_dns 우선
esxi-gather/tasks/collect_network_extended.yml    (+12 lines)  — speed_mbps int 정규화
redfish-gather/tasks/detect_vendor.yml            (+3 lines)   — include_vars 우회
schema/baseline_v1/esxi_baseline.json             (실측 갱신)
tests/evidence/2026-04-29-esxi-residual-fixes.md  (NEW, 본 문서)
```

---

## 9. ADR 트리거 (rule 70 R8) 평가

| Trigger | 해당? |
|---|---|
| rule 본문 의미 변경 | NO |
| 표면 카운트 변경 | NO |
| 보호 경로 정책 변경 | NO |

→ ADR 작성 불필요.
