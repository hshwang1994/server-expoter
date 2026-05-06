# HPE — 벤더 OEM 메모

## 식별

- **Manufacturer**: "HPE", "Hewlett Packard Enterprise", "Hewlett-Packard"
- **Aliases**: HPE, HP, Hewlett Packard Enterprise, iLO
- **BMC 이름**: iLO5 / iLO6
- **vendor_aliases.yml** 정규화: `hpe`

## Adapter 매핑

| Adapter | priority | 대상 |
|---|---|---|
| `adapters/redfish/hpe_ilo7.yml` | 120 | iLO7 (Gen12, 2026-05-01 신규) |
| `adapters/redfish/hpe_ilo6.yml` | 100 | iLO6 |
| `adapters/redfish/hpe_superdome_flex.yml` | 95 | Superdome Flex / Flex 280 (2026-05-06 신규, lab 부재) |
| `adapters/redfish/hpe_ilo5.yml` | 90 | iLO5 |
| `adapters/redfish/hpe_synergy.yml` | 60 | HPE Synergy frame |
| `adapters/redfish/hpe_ilo4.yml` | 50 | iLO4 (Gen9 legacy) |
| `adapters/redfish/hpe_ilo.yml` | 10 | generic HPE fallback |

## Superdome 시리즈 (cycle 2026-05-06 추가 — M-E1/M-E2)

### 모델 / BMC

| 모델 | 출시 | 아키텍처 | management | Redfish |
|---|---|---|---|---|
| Superdome Flex 280 | 2020+ | x86 (Intel Xeon SP) | RMC + iLO 5 (per node) | YES (RMC host, 표준) |
| Superdome Flex | 2017+ | x86 (Intel Xeon SP) | eRMC/RMC + iLO 5 (per compute module) | YES (RMC host, 표준) |
| Superdome 2 (legacy) | 2010~2017 | Itanium / IA-64 | OA (Onboard Administrator) | NO — `redfish_generic.yml` fallback |
| Superdome X (legacy) | 2014~ | x86 (Xeon E7) | iLO 4 + OA | 부분 — `hpe_ilo4.yml` (50) fallback |
| Integrity Superdome (legacy) | ~2010 | Itanium | OA only | NO — `redfish_generic.yml` (N/A) |

### Redfish 차이 (vs 일반 ProLiant iLO 5)

| Endpoint | 일반 iLO 5 | Superdome Flex | 시그니처 |
|---|---|---|---|
| Systems collection | `/Systems/1` (단일) | `/Systems/Partition0`, `Partition1`, ... | **Multi-partition (nPAR)** — sdflexutils 실측 |
| Managers | `/Managers/1` (iLO) | `/Managers/<RMC_id>` + per-node iLO 5 | **Dual-manager** — RMC primary |
| Chassis | `/Chassis/1` | `/Chassis/<chassis_id>` | RMC aggregation (Base + Expansion 최대 8) |
| FirmwareInventory | 표준 | 표준 + complex/nPar firmware bundles | sdflex-ironic-driver wiki 명시 |
| OEM 키 | `Oem.Hpe` | `Oem.Hpe` | HPE 표준 namespace 재사용 |

### 한계 / 주의

- **Multi-partition (nPAR)**: server-exporter 의 Systems Members[0] 단일 진입 패턴 — **첫 partition (Partition0) 만 수집**. 전체 partition 수집은 별도 cycle.
- **Dual-manager**: RMC = primary AccountService host. per-node iLO 5 는 보조.
- **Vendor 분류**: HPE sub-line — Manufacturer = "HPE". 별도 vendor 아님 (M-E1 결정 (a)).
- **vault**: `vault/redfish/hpe.yml` 재사용 (별도 vault 불필요).
- **OEM tasks**: `redfish-gather/tasks/vendors/hpe/` 재사용 (Oem.Hpe 동일 namespace).
- **lab**: 부재 — web sources 14건만 (rule 96 R1-A). 사이트 실측 시 정정 가능.

### 후속 작업 (lab 도입 시)

1. Multi-partition 전수 수집 (별도 cycle — Systems Members[0] 단일 진입 변경)
2. nPAR / `Oem.Hpe.Partition*` 키 식별 (lab 응답 캡처 후)
3. Manufacturer string / Product 시그니처 정정 (web sources 추정 vs 실측)

## OEM 특이사항

- **Smart Storage Administrator path**: HPE OEM `Oem.Hp.Links.SmartStorage`
- **Boot order**: OEM 별도 endpoint
- **Firmware inventory**: 표준 + OEM (Smart Components)
- **Superdome Flex**: complex/nPar firmware bundles (raw passthrough)

## Vault

- 위치: `vault/redfish/hpe.yml`
- 일반적 계정: `Administrator`
- 회전: `rotate-vault` skill

## 검증 이력

- Round 7-10: iLO5 펌웨어 2.x 검증 완료
- Round 11 (2026-04-28): iLO 6 v1.73 (10.50.11.231) Baseline 캡처
- cycle 2026-05-06 (M-E2): Superdome Flex / Flex 280 adapter 추가 (lab 부재, web sources 14건)
- Baseline: `tests/baseline_v1/hpe_ilo5_baseline.json`, `tests/baseline_v1/hpe_baseline.json`

## Reference

- `docs/13_redfish-live-validation.md`
- HPE iLO Redfish API guide (외부)
- `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` (M-E1 entry — Superdome Flex 14 sources)
- `docs/ai/tickets/2026-05-06-multi-session-compatibility/fixes/M-E1.md` (web 검색 결과)
- `docs/ai/tickets/2026-05-06-multi-session-compatibility/fixes/M-E2.md` (adapter spec)
