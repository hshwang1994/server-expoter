# Python netaddr — 네트워크 주소 처리

> Source: https://github.com/netaddr/netaddr
> Fetched: 2026-04-27
> Version: netaddr 1.3.0 (server-exporter 검증 기준)
> 사용 위치 (server-exporter): Ansible `ipaddr` 필터의 backend, filter_plugins (간접)

## 핵심 클래스

| Class | 용도 |
|---|---|
| `IPAddress` | 단일 IP (IPv4 / IPv6) |
| `IPNetwork` | CIDR (IP + 프리픽스) |
| `IPRange` | 비-CIDR 범위 |
| `EUI` | MAC / EUI-48 / EUI-64 |

## CIDR 연산

```python
from netaddr import IPNetwork, IPAddress

net = IPNetwork('10.100.64.0/24')
print(net.network)      # 10.100.64.0
print(net.broadcast)    # 10.100.64.255
print(net.netmask)      # 255.255.255.0
print(net.prefixlen)    # 24
print(net.size)         # 256

for host in net.iter_hosts():
    print(host)         # 254 hosts (broadcast 제외)
```

## Ansible `ipaddr` 필터 (실용)

server-exporter inventory_json의 IP 검증 + Jenkins Stage 1.

```yaml
- name: IP 형식 검증
  assert:
    that:
      - target_ip | ipaddr
      - target_ip | ipv4

- name: CIDR 분해
  set_fact:
    _network: "{{ '10.100.64.5/24' | ipaddr('network') }}"  # 10.100.64.0
    _host: "{{ '10.100.64.5/24' | ipaddr('address') }}"     # 10.100.64.5
    _netmask: "{{ '10.100.64.5/24' | ipaddr('netmask') }}"  # 255.255.255.0
    _prefix: "{{ '10.100.64.5/24' | ipaddr('prefix') }}"    # 24
```

## 집합 연산

```python
from netaddr import IPSet

s1 = IPSet(['10.100.64.0/24'])
s2 = IPSet(['10.100.64.128/25'])
print(s1 | s2)   # union
print(s1 & s2)   # intersection
print(s1 - s2)   # difference
```

## server-exporter 활용

- `inventory_json`의 `service_ip` / `bmc_ip` / `ip` 형식 검증
- loc별 inventory 분리 (ich / chj / yi가 다른 subnet)
- precheck 1단계 (ping) 전 IP 형식 사전 차단

## stdlib 대체 가능?

netaddr가 강력하지만 server-exporter `redfish-gather/library/redfish_gather.py`는 stdlib only (rule 10 R2):
- 단순 IP 파싱: `ipaddress` 표준 모듈로 충분
- CIDR 연산: `ipaddress.ip_network()` 사용

```python
import ipaddress

net = ipaddress.ip_network('10.100.64.0/24', strict=False)
for host in net.hosts():
    print(host)
```

filter_plugins / lookup_plugins는 ansible-core 의존성 안에서 netaddr 사용 OK.

## 적용 rule / 관련

- rule 10 R2 (stdlib 우선) — library 모듈은 stdlib `ipaddress`로
- rule 30 R3 (timeout) — IP 검증 후 외부 호출
- reference: `docs/ai/references/ansible/jinja-filters.md` (ipaddr 필터 예시)
