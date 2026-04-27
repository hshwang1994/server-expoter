# VENDOR_ADAPTERS — server-exporter

> 5 vendor x 채널별 adapter 매트릭스 (rule 28 #3 측정 대상, TTL 14일).

## 일자: 2026-04-27 (Plan 3 초기 골격)

## Redfish 채널 (14 adapter)

| Vendor | Adapter | priority | specificity | tested_against | OEM tasks | Vault |
|---|---|---|---|---|---|---|
| Dell | dell_idrac9.yml | 100 | (model_patterns) | 5.x / 6.x | yes | vault/redfish/dell.yml |
| Dell | dell_idrac8.yml | 50 | (model_patterns) | 2.40+ | yes | (동일) |
| Dell | dell_idrac.yml | 10 | (generic Dell) | — | — | (동일) |
| HPE | hpe_ilo6.yml | 100 | — | 1.x | yes | vault/redfish/hpe.yml |
| HPE | hpe_ilo5.yml | 80 | — | 2.x | yes | (동일) |
| HPE | hpe_synergy.yml | 60 | (Synergy frame) | — | yes | (동일) |
| HPE | hpe_ilo.yml | 10 | (generic HPE) | — | — | (동일) |
| Lenovo | lenovo_xcc.yml | 100 | — | XCC 1.x | yes | vault/redfish/lenovo.yml |
| Lenovo | lenovo_xcc_legacy.yml | 50 | (구 IMM2) | — | yes | (동일) |
| Supermicro | supermicro_x12.yml | 100 | — | X12 | yes | vault/redfish/supermicro.yml |
| Supermicro | supermicro_x11.yml | 80 | — | X11 | yes | (동일) |
| Supermicro | supermicro_legacy.yml | 30 | (X10 이하) | — | — | (동일) |
| Cisco | cisco_cimc.yml | 100 | — | 4.x / 5.x | yes | vault/redfish/cisco.yml |
| Generic | redfish_generic.yml | 0 | (fallback) | — | — | vault/redfish/generic.yml |

## OS 채널 (7 adapter)

`adapters/os/` — linux_*/windows_*. 상세는 추후 갱신.

## ESXi 채널 (4 adapter)

| Adapter | 대상 |
|---|---|
| esxi_8x.yml | ESXi 8.x |
| esxi_7x.yml | ESXi 7.x |
| esxi_6x.yml | ESXi 6.x |
| esxi_generic.yml | fallback |

## 갱신 trigger (rule 28 #3)

- TTL 14일
- adapters/*.yml 수정
- vendor_aliases.yml 수정
- 새 vendor 추가 (rule 50 R2)

## 측정 명령

```bash
ls adapters/redfish/*.yml | wc -l
grep -E "^priority:|^specificity:|tested_against:" adapters/redfish/*.yml
```

## 정본 reference

- `.claude/policy/vendor-boundary-map.yaml` (구조)
- `.claude/ai-context/vendors/{vendor}.md` (OEM 메모)
- `docs/13_redfish-live-validation.md` (Round 검증 결과)
- `docs/10_adapter-system.md` (점수 시스템)
