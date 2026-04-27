# HPE — 벤더 OEM 메모

## 식별

- **Manufacturer**: "HPE", "Hewlett Packard Enterprise", "Hewlett-Packard"
- **Aliases**: HPE, HP, Hewlett Packard Enterprise, iLO
- **BMC 이름**: iLO5 / iLO6
- **vendor_aliases.yml** 정규화: `hpe`

## Adapter 매핑

| Adapter | priority | 대상 |
|---|---|---|
| `adapters/redfish/hpe_ilo6.yml` | 100 | iLO6 |
| `adapters/redfish/hpe_ilo5.yml` | 80 | iLO5 |
| `adapters/redfish/hpe_synergy.yml` | 60 | HPE Synergy frame |
| `adapters/redfish/hpe_ilo.yml` | 10 | generic HPE fallback |

## OEM 특이사항

- **Smart Storage Administrator path**: HPE OEM `Oem.Hp.Links.SmartStorage`
- **Boot order**: OEM 별도 endpoint
- **Firmware inventory**: 표준 + OEM (Smart Components)

## Vault

- 위치: `vault/redfish/hpe.yml`
- 일반적 계정: `Administrator`
- 회전: `rotate-vault` skill

## 검증 이력

- Round 7-10: iLO5 펌웨어 2.x 검증 완료
- Baseline: `tests/baseline_v1/hpe_ilo5_baseline.json`

## Reference

- `docs/13_redfish-live-validation.md`
- HPE iLO Redfish API guide (외부)
