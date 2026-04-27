# VENDOR_ADAPTERS — server-exporter

> 5 vendor x 채널별 adapter 매트릭스 (rule 28 #3 측정 대상, TTL 14일).
> 실측 (`grep adapter_id|priority adapters/`) — 2026-04-27.

## Redfish 채널 (14 adapters)

| Adapter | adapter_id | priority | Vendor | 비고 |
|---|---|---|---|---|
| `dell_idrac9.yml` | redfish_dell_idrac9 | 100 | Dell | iDRAC9 (5.x / 6.x / 7.x) |
| `dell_idrac8.yml` | redfish_dell_idrac8 | 50 | Dell | iDRAC8 (2.40+) |
| `dell_idrac.yml` | redfish_dell_idrac | 10 | Dell | generic Dell fallback |
| `hpe_ilo6.yml` | redfish_hpe_ilo6 | 100 | HPE | iLO6 |
| `hpe_ilo5.yml` | redfish_hpe_ilo5 | 100 | HPE | iLO5 |
| `hpe_ilo4.yml` | redfish_hpe_ilo4 | 50 | HPE | iLO4 (2.30+) |
| `hpe_ilo.yml` | redfish_hpe_ilo | 10 | HPE | generic HPE fallback |
| `lenovo_xcc.yml` | redfish_lenovo_xcc | 100 | Lenovo | XCC (XClarity Controller) |
| `lenovo_imm2.yml` | redfish_lenovo_imm2 | 50 | Lenovo | 구 IMM2 (IBM 인수 전) |
| `supermicro_x11.yml` | redfish_supermicro_x11 | 100 | Supermicro | X11 generation |
| `supermicro_x9.yml` | redfish_supermicro_x9 | 50 | Supermicro | X9 generation |
| `supermicro_bmc.yml` | redfish_supermicro_bmc | 10 | Supermicro | generic SMC |
| `cisco_cimc.yml` | redfish_cisco_cimc | 100 | Cisco | CIMC (UCS C-Series) |
| `redfish_generic.yml` | redfish_generic | 0 | (any) | fallback |

총 14 adapter (5 vendor + generic fallback).

## OS 채널 (7 adapters)

| Adapter | 대상 |
|---|---|
| `linux_rhel.yml` | RHEL / CentOS / Rocky / Alma |
| `linux_ubuntu.yml` | Ubuntu |
| `linux_suse.yml` | SUSE / SLES |
| `linux_generic.yml` | 기타 Linux fallback |
| `windows_2022.yml` | Windows Server 2022 |
| `windows_2019.yml` | Windows Server 2019 |
| `windows_generic.yml` | 기타 Windows fallback |

## ESXi 채널 (4 adapters)

| Adapter | 대상 |
|---|---|
| `esxi_8x.yml` | ESXi 8.x |
| `esxi_7x.yml` | ESXi 7.x |
| `esxi_6x.yml` | ESXi 6.x |
| `esxi_generic.yml` | fallback |

## 점수 일관성 검증 (rule 12 R2)

각 vendor 내부 priority 차등 — 역전 없음:

| Vendor | 차등 |
|---|---|
| Dell | 10 < 50 < 100 (generic < idrac8 < idrac9) ✓ |
| HPE | 10 < 50 < 100 (generic < ilo4 < ilo5/6) ✓ |
| Lenovo | 50 < 100 (imm2 < xcc) ✓ |
| Supermicro | 10 < 50 < 100 (generic < x9 < x11) ✓ |
| Cisco | 100 (단일) ✓ |

**[PASS]** 모든 vendor priority 역전 없음.

## 갱신 trigger (rule 28 #3)

- TTL 14일
- adapters/*.yml 수정
- vendor_aliases.yml 수정
- 새 vendor 추가 (rule 50 R2)

## 측정 명령

```bash
ls adapters/redfish/*.yml | wc -l
for f in adapters/redfish/*.yml; do
  echo "$(basename $f): $(grep -E '^priority:' $f)"
done
```

## 정본 reference

- `.claude/policy/vendor-boundary-map.yaml`
- `.claude/ai-context/vendors/{vendor}.md`
- `docs/13_redfish-live-validation.md`
- `docs/10_adapter-system.md`
- `docs/ai/references/redfish/vendor-bmc-guides.md`
