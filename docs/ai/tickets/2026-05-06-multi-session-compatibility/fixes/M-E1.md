# M-E1 — HPE Superdome web 검색 (Flex / Flex 280 / 2 / X / Integrity)

> status: [DONE] | depends: — | priority: P1 | cycle: 2026-05-06-multi-session-compatibility | worker: Session-E1 (web-evidence-collector / opus)

## 사용자 의도

> "superdome 하드웨어도 벤더 추가해줘. 추가하고 web 검색 다해서 여기 개더링프로젝트에 추가해줘."

→ HPE Superdome 시리즈 web 검색으로 BMC 정보 + Redfish 지원 + 모델 별 차이 식별. lab 부재 → web sources 만 (rule 96 R1-A).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | (산출물) `docs/ai/tickets/2026-05-06-multi-session-compatibility/fixes/M-E1.md` 의 검색 결과 절 + EXTERNAL_CONTRACTS.md 갱신 |
| 영향 vendor | HPE (기존 vendor — Superdome 은 HPE 의 high-end 라인) — vendor 별도 분류 결정 (M-E2 입력) |
| 함께 바뀔 것 | M-E2 adapter 작성 입력 |
| 리스크 top 3 | (1) Superdome 시리즈가 일반 ProLiant 와 management infrastructure 다름 / (2) 일부 (Integrity Itanium) 은 Redfish 미지원 가능 / (3) Flex 의 RMC (Rack Management Controller) 가 별도 — iLO 와 차이 |
| 진행 확인 | 사용자 명시 (2026-05-06) "벤더 추가해줘" 승인 받음 |

## HPE Superdome 시리즈 정리 (사전 지식)

| 모델 | 출시 | 아키텍처 | management |
|---|---|---|---|
| **HPE Superdome Flex 280** | 2020+ | x86 (Intel Xeon SP) | iLO 5 + Rack Management Controller (RMC) |
| **HPE Superdome Flex** | 2017+ | x86 (Intel Xeon SP) | RMC + iLO 5 (각 컴퓨트 모듈) |
| HPE Superdome 2 | 2010~2017 | Itanium / IA-64 | Onboard Administrator (OA) — Redfish 미지원 가능 |
| HPE Superdome X | 2014~ | x86 (Xeon E7) | iLO 4 + OA |
| HPE Integrity Superdome | ~2010 | Itanium | OA only (legacy) |

→ **본 cycle 대상**: Superdome Flex 280 + Superdome Flex (현행 운영 가능 모델). Superdome 2 / X / Integrity 는 legacy → fallback 또는 N/A 분류.

## 검색 sources (rule 96 R1-A)

### 1. HPE 공식 docs

| URL | 내용 |
|---|---|
| https://support.hpe.com/.../HPE_Superdome_Flex_Family/ | Superdome Flex / Flex 280 manuals |
| https://support.hpe.com/.../iLO_5/ | iLO 5 Redfish API (Superdome Flex 280 의 BMC 표준) |
| https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/ | iLO 5 Redfish reference |
| https://support.hpe.com/.../Superdome_Flex_RMC/ | Rack Management Controller (RMC) docs |
| https://support.hpe.com/.../Onboard_Administrator/ | OA (legacy Superdome 2 / X) |

### 2. DMTF Redfish 표준

- https://redfish.dmtf.org/ — Superdome RMC 가 Redfish 표준 따라가는지
- https://redfish.dmtf.org/profiles/ — HPE profile

### 3. GitHub / Community

- https://github.com/HewlettPackard/python-redfish-utility — HPE Redfish CLI
- https://github.com/HewlettPackard/python-ilorest-library

### 4. 사용자 사이트 실측

- 본 cycle 은 lab 0 → web sources 만

## 검색 spec (산출물)

> 검색 일자: 2026-05-06 / 검색자: Session-E1 (web-evidence-collector) / sources 종류: vendor docs (HPE) + DMTF + GitHub

### (A) Manufacturer string

**검색 결과**:

| 위치 | 값 (실측 / 추정) | 근거 |
|---|---|---|
| ServiceRoot.Vendor (v1.5+ 표준) | `"HPE"` (추정 — 일반 ProLiant iLO 5 와 동일) | sdflexutils PyPI: "Hewlett Packard Enterprise" 사용. iLO 5 표준 동작 |
| ServiceRoot.Product (v1.3+ 표준) | `"iLO 5"` 또는 `"Superdome Flex"` (RMC 응답 시) | HPE Superdome Flex Redfish 호스트는 RMC. Product 시그니처는 Flex 별도 |
| Chassis.Manufacturer | `"HPE"` 또는 `"Hewlett Packard Enterprise"` | sdflexutils PyPI 명시 |
| Oem 키 | `Oem.Hpe` | HPE 표준 — "Data types prefixed with Hpe are HPE added value extensions to the DMTF Redfish specification" |

**결론**: server-exporter 의 기존 HPE vendor_aliases.yml 매핑 (`"HPE", "Hewlett Packard Enterprise"`) 으로 Manufacturer 정규화 정상 동작 예상. 별도 alias 추가 불필요.

**추정 근거**: lab 부재 — 사이트 실측 시 결과 변경 가능 (rule 25 R7-A-1).

### (B) Model 식별

| model_pattern | 매칭 BMC | Redfish 지원 | 비고 |
|---|---|---|---|
| `^Superdome Flex 280` | RMC + iLO 5 (per node) | YES (1.x+ 표준) | sdflexutils 1.5.1 (2022-11) 지원. OpenStack Ironic sdflex-redfish hardware type |
| `^Superdome Flex(?! 280)` | eRMC / RMC + iLO 5 (per compute module) | YES | 4~32 socket scale-up. 8 chassis 까지 |
| `^Superdome 2` | OA (Onboard Administrator) | NO (Itanium/IA-64, legacy) | 2010~2017 EOL. fallback adapter `redfish_generic.yml` 적용 또는 N/A |
| `^Superdome X` | iLO 4 + OA | 부분 (iLO 4 한정) | 2014~ Xeon E7. iLO 4 Redfish 1.0~1.1 — `hpe_ilo4.yml` priority=50 으로 fallback 가능 |
| `^Integrity Superdome` | OA (legacy) | NO | ~2010 Itanium. server-exporter 범위 외 |

→ M-E2 adapter `match.model_patterns` 입력: `["^Superdome Flex.*", "^Superdome Flex 280.*"]`

### (C) Redfish endpoint 차이 (vs 일반 ProLiant iLO 5)

| Endpoint | 일반 iLO 5 (ProLiant) | Superdome Flex | 차이 |
|---|---|---|---|
| ServiceRoot | `/redfish/v1/` | `/redfish/v1/` (RMC host) | 동일 — RMC IP 가 `redfish_address` |
| Systems collection | `/redfish/v1/Systems/1` (단일) | `/redfish/v1/Systems/Partition0`, `Partition1`, ... | **다중 partition** (nPAR) — ID = `Partition<N>` |
| Chassis | `/redfish/v1/Chassis/1` | `/redfish/v1/Chassis/<chassis_id>` | RMC aggregation — Base + Expansion (최대 8 chassis) |
| Managers | `/redfish/v1/Managers/1` (iLO) | `/redfish/v1/Managers/<RMC_id>` (RMC) + per-node iLO 5 | **dual-manager** — RMC + 각 컴퓨트 모듈 iLO 5 |
| FirmwareInventory | 표준 | 표준 + complex/nPar firmware bundles | sdflex-ironic-driver wiki 명시 |

**핵심 차이 (HIGH risk)**:
- Systems ID 는 `1` 이 아니라 `Partition0` (sdflexutils 실측 — `'redfish/v1/Systems/Partition0'`)
- Multi-partition 시 Members[] 에 여러 Partition entry. server-exporter `redfish_gather.py` 의 Systems Members[0] 단일 진입 패턴은 첫 partition 만 수집 가능

→ M-E2 adapter `capabilities.endpoints` 입력. server-exporter 현재 구조에서는 첫 partition 만 수집 (multi-partition 전수 수집은 별도 cycle).

### (D) OEM extension

| 위치 | OEM 키 | 비고 |
|---|---|---|
| ServiceRoot / System / Chassis / Manager | `Oem.Hpe` | HPE 표준 OEM namespace. iLO 5 와 동일 |
| Storage / RAID | `Oem.Hpe.Links.SmartStorage` (iLO 5 과 동일) | sdflex-ironic-driver "RAID/disk management through OEM extensions" |
| Partition 전용 | `Oem.Hpe.Partition*` (추정 — 미확인) | Superdome Flex Partitioning Guide 존재. lab 실측 시 키 확인 필요 |
| Firmware | 표준 + complex/nPar firmware bundles | sdflex-ironic-driver 명시 |

→ M-E2 adapter `normalize.oem_path` 입력: 기존 HPE OEM 경로 (`redfish-gather/tasks/vendors/hpe/`) 재사용. 추가 partition 전용 OEM 은 별도 cycle.

### (E) 펌웨어 호환성

| 펌웨어 / 컴포넌트 | 버전 | Redfish 지원 | 근거 |
|---|---|---|---|
| RMC firmware | 3.10.164 (2021-03 release) | YES — DMTF Redfish 표준 | thelinuxcluster.com firmware upgrade 기록 |
| RMC firmware | 2.x | YES — Redfish 표준 (확인 미실 — 추정) | sdflexutils 1.5.1 호환 |
| iLO 5 (per compute module) | 2.x ~ 3.x | YES | 표준 iLO 5 동작 |
| OA 4.x (Superdome 2/X) | — | NO / 부분 | OA 는 Redfish 미지원 (legacy) |
| OpenStack Ironic sdflex-redfish | — | sdflexutils 1.5.1 (2022-11-29) 기준 | PyPI 등재 |

### (F) 결정 — (a) HPE sub-line 채택

**결정**: **(a) HPE sub-line** — `adapters/redfish/hpe_superdome_flex.yml` 신규 (priority=95)

**근거**:

1. **Manufacturer string 동일** — ServiceRoot.Vendor / Chassis.Manufacturer 모두 `"HPE"` / `"Hewlett Packard Enterprise"` 사용 (sdflexutils PyPI 표기). 별도 vendor 분리 시 vendor_aliases.yml 충돌 위험.
2. **OEM namespace 동일** — `Oem.Hpe` 표준 사용. 기존 `redfish-gather/tasks/vendors/hpe/` 재사용 가능.
3. **인증 동일** — vault `vault/redfish/hpe.yml` 그대로 사용 가능 (별도 vault 불필요).
4. **adapter 점수 일관성 (rule 12 R2)**:
   - `hpe_ilo7.yml` priority=120 (Gen12, 최신)
   - `hpe_ilo6.yml` priority=100 (Gen11)
   - `hpe_superdome_flex.yml` priority=**95** (Superdome Flex / Flex 280 — Flex line 별도 식별)
   - `hpe_ilo5.yml` priority=90 (Gen10/10+)
   - `hpe_ilo4.yml` priority=50 (Gen9 legacy)
   - `hpe_ilo.yml` priority=10 (generic fallback)
   - **Superdome Flex 는 iLO 5 보다 한 칸 위** — model_patterns `^Superdome Flex.*` 매치 시 우선 선택. 일반 ProLiant 는 그대로 `hpe_ilo5.yml`.
5. **vault / OEM tasks / 인증 흐름 모두 HPE 와 동일** — rule 50 R2 9단계 중 4 (vault) / 5 (baseline) / 6 (ai-context) 만 추가 필요. 대부분 HPE 패턴 재사용.

**(b) 별도 vendor 거절 사유**: Manufacturer string 충돌 + vendor_aliases.yml 정규화 모호. ServiceRoot.Vendor="HPE" 인 응답을 별도 vendor 로 분리 시 detect_vendor 로직 우회 필요 → rule 12 R1 위반 위험.

## sources URL list (rule 96 R1-A — 3종 sources)

> 확인 일자: 2026-05-06. lab 부재 (사용자 실측 X) → vendor docs + DMTF + GitHub 3종 사용. 사용자 실측 가능 시 rule 25 R7-A-1 우선 적용.

### 1. HPE 공식 docs (vendor docs)

| URL | 용도 | 확인 일자 |
|---|---|---|
| https://support.hpe.com/hpesc/public/docDisplay?docId=a00119177en_us&docLocale=en_US&page=GUID-FE270127-0E58-4AB8-9D90-FB84DC571827.html | Remote management with Redfish — HPE Superdome Flex Server Administration Guide. RMC 가 Redfish API host 명시 | 2026-05-06 |
| https://support.hpe.com/hpesc/public/docDisplay?docId=sf000075513en_us | HPE Superdome Flex Redfish API (공식 reference, 접근 가능 시) | 2026-05-06 |
| https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/ | iLO 5 Redfish API Reference (per compute module BMC) | 2026-05-06 |
| https://www.hpe.com/us/en/collaterals/collateral.a00026242enw.html | HPE Superdome Flex QuickSpecs (4-32 socket, 8 chassis 까지, nPars) | 2026-05-06 |
| https://itpfdoc.hitachi.co.jp/manuals/rv3000/hard/SDF/Server/SDF280/P06150-401a.pdf | HPE Superdome Flex Server Administration Guide P06150-401a (PDF) | 2026-05-06 |
| https://servermanagementportal.ext.hpe.com/docs/concepts/gettingstarted | HPE Server Management Portal — Redfish getting started | 2026-05-06 |

### 2. DMTF Redfish 표준

| URL | 용도 | 확인 일자 |
|---|---|---|
| https://redfish.dmtf.org/schemas/DSP0266_1.15.0.html | DSP0266 v1.15.0 — Redfish Specification (ServiceRoot.Vendor v1.5+ 표준) | 2026-05-06 |
| http://redfish.dmtf.org/schemas/DSP0266_1.5.0.html | DSP0266 v1.5.0 — ServiceRoot.Vendor / Product 표준화 시점 | 2026-05-06 |

### 3. GitHub / Community

| URL | 용도 | 확인 일자 |
|---|---|---|
| https://github.com/HewlettPackard/sdflexutils | HPE 공식 — Superdome Flex 280 / Superdome Flex 관리 라이브러리. `redfish/v1/Systems/Partition0` 명시 | 2026-05-06 |
| https://github.com/HewlettPackard/sdflex-ironic-driver | HPE 공식 — OpenStack Ironic sdflex-redfish hardware type | 2026-05-06 |
| https://github.com/HewlettPackard/sdflex-ironic-driver/wiki | sdflex-ironic-driver wiki — `redfish_system_id=/redfish/v1/Systems/<PARTITION-ID>` + RMC management | 2026-05-06 |
| https://pypi.org/project/sdflexutils/ | sdflexutils 1.5.1 (2022-11-29) — "Hewlett Packard Enterprise" Manufacturer 표기 | 2026-05-06 |
| https://thelinuxcluster.com/2020/05/06/upgrading-firmware-for-super-dome-flex/ | RMC firmware 3.10.164-20210329 release 기록 | 2026-05-06 |
| https://github.com/HewlettPackard/ilo-rest-api-docs/blob/master/source/includes/_ilo5_adaptation.md | iLO 5 Redfish adaptation reference | 2026-05-06 |

### 4. 사용자 사이트 실측 (rule 25 R7-A-1)

- **lab 부재 / 사이트 미보유**. 본 cycle 은 sources 1~3 만으로 결론. 사이트 실측 시 본 결과 정정 가능.

## M-E2 adapter spec 도출 (4 필드 초안)

> M-E2 (worker 진입 시) 입력. 기존 HPE adapter 패턴 (`hpe_ilo5.yml`) 기반 + Superdome Flex 차별 적용.

### `match` (Superdome Flex 식별)

```yaml
match:
  vendor: ["HPE", "Hewlett Packard Enterprise"]
  # Product / Manager.Model 시그니처 — sdflexutils 명시 "Superdome Flex 280" / "Superdome Flex"
  model_patterns:
    - "^Superdome Flex 280.*"
    - "^Superdome Flex(?! 280).*"
    - ".*Superdome.*Flex.*"  # 펌웨어 별 다른 표기 대비
  # 펌웨어: RMC 2.x ~ 3.x (Superdome Flex) + iLO 5 2.x~3.x (per compute module)
  firmware_patterns:
    - "^[23]\\.[0-9]+\\..*"  # RMC firmware 2.x / 3.x
```

### `capabilities`

```yaml
capabilities:
  sections_supported:
    - system     # /Systems/Partition<N> 첫 partition 만 수집 (현재 server-exporter 구조)
    - hardware   # /Chassis/<id> RMC aggregation
    - bmc        # /Managers/<RMC_id> + iLO 5 (dual-manager — RMC 우선 진입)
    - cpu
    - memory
    - storage
    - network
    - firmware   # complex/nPar firmware bundles 포함 (raw passthrough)
    - power
    # users (AccountService) — RMC 수준 지원 추정 (lab 부재 — 사이트 실측 시 정정)
```

### `collect`

```yaml
collect:
  strategy: standard_plus_oem
  standard_tasks: "redfish-gather/tasks/collect_standard.yml"
  oem_tasks: "redfish-gather/tasks/vendors/hpe/collect_oem.yml"
  # Superdome Flex 전용 OEM tasks 신규 작성 보류 (lab 부재) — HPE 공통 OEM 재사용
  # 향후 Partition 전용 OEM 추가 시 `redfish-gather/tasks/vendors/hpe/collect_superdome_oem.yml` 별도
```

### `normalize`

```yaml
normalize:
  standard_tasks: "redfish-gather/tasks/normalize_standard.yml"
  oem_tasks: "redfish-gather/tasks/vendors/hpe/normalize_oem.yml"
  # 첫 Partition 만 수집되는 한계 명시 — diagnosis.details 에 multi_partition_warning emit 권장
```

### `priority` / `metadata` (origin 주석 — rule 96 R1)

```yaml
adapter_id: redfish_hpe_superdome_flex
channel: redfish
priority: 95   # iLO 5 (90) < Superdome Flex (95) < iLO 6 (100) < iLO 7 (120) — model_patterns 매치 시 iLO 5 우선
# ── Origin metadata (rule 96 R1) ──────────────────────────────────────────────
# Vendor: HPE / Hewlett Packard Enterprise
# Firmware: RMC 2.x~3.x + iLO 5 (per compute module)
# Origin: HPE Superdome Flex Server Admin Guide + sdflexutils GitHub
# Last sync: 2026-05-06 (M-E1 web search)
# Lab: 부재 — web sources 만 (rule 96 R1-A)
# Tested against: 미확인 — 사이트 실측 권장 (rule 25 R7-A-1)
# source: https://github.com/HewlettPackard/sdflexutils (RMC + Partition0 명시)
# source: https://support.hpe.com/.../GUID-FE270127-0E58-4AB8-9D90-FB84DC571827.html (Remote management with Redfish)
# source: DSP0266 v1.15.0 (ServiceRoot.Vendor 표준)
# Notes: Systems ID = Partition<N>. Multi-partition 시 첫 partition 만 수집 (한계).
#        nPAR / Oem.Hpe.Partition* 영역은 향후 lab 보유 시 별도 cycle 확장.
# DRIFT 추적: Manufacturer string 사이트 실측 시 정정 가능
# ──────────────────────────────────────────────────────────────────────────────
```

### `credentials` / `auth` / `graceful_degradation` / `diagnosis`

기존 `hpe_ilo5.yml` 패턴 그대로 재사용 (vault `hpe`, session+basic auth, abort on auth_fail, recovery account `hp_admin_hpinvent1`).

### legacy 모델 처리 (Superdome 2 / X / Integrity)

| 모델 | 대응 adapter | 비고 |
|---|---|---|
| Superdome 2 | `redfish_generic.yml` (priority=0) | OA Redfish 미지원 → graceful degradation status=failed |
| Superdome X | `hpe_ilo4.yml` (priority=50) — 일반 iLO 4 fallback | iLO 4 부분 Redfish 지원 |
| Integrity Superdome | `redfish_generic.yml` | Itanium legacy — N/A 분류 |

**별도 adapter 작성 불필요** — 기존 fallback 으로 cover.

## 회귀 / 검증

- (분석 only) — M-E2 adapter 작성 후 M-E6 에서 mock fixture 회귀

## risk

- (HIGH) Superdome Flex 의 multi-partition 시 nPAR 정보 — 일반 ProLiant gather 패턴 적용 가능 여부 검증 필요
- (HIGH) RMC 가 별도 BMC — Manager 가 iLO 5 + RMC 두개? 어떻게 정규화할지 (M-E2 adapter spec)
- (MED) Superdome 2 / X / Integrity 는 legacy → fallback 적용 또는 N/A 분류 (사용자 결정)
- (LOW) Manufacturer string 표준 따라가면 (a) 결정 자동

## 완료 조건

- [x] (A) Manufacturer string 검색 결과 — `"HPE"` / `"Hewlett Packard Enterprise"` (기존 vendor_aliases 재사용)
- [x] (B) 모델 매트릭스 (Flex 280 / Flex / 2 / X / Integrity) + BMC 매핑
- [x] (C) Redfish endpoint 차이 (vs 일반 iLO 5) — Systems ID `Partition<N>`, dual-manager (RMC + iLO 5)
- [x] (D) OEM extension 식별 — `Oem.Hpe` (기존 HPE OEM 재사용 가능)
- [x] (E) 펌웨어 호환성 — RMC 2.x/3.x + iLO 5 2.x/3.x
- [x] (F) 결정 — **(a) HPE sub-line** 채택 (priority=95)
- [x] sources URL list (rule 96 R1-A) — vendor docs 6 + DMTF 2 + GitHub 6 = **14 URL**
- [x] EXTERNAL_CONTRACTS.md 갱신 (HPE Superdome entry)
- [x] M-E2 adapter spec 도출 (match / capabilities / collect / normalize 4 필드)
- [ ] commit: 메인 세션 일괄 처리 (worker 세션 commit 안 함)

## 다음 세션 첫 지시 템플릿

```
M-E1 HPE Superdome web 검색 진입.

읽기 우선순위:
1. fixes/M-E1.md (본 ticket)
2. adapters/redfish/hpe_*.yml (5 generation 기존 패턴)
3. rule 50 R2 (vendor 추가 9단계)
4. rule 96 R1-A (web sources 4종)

도구:
- WebSearch / WebFetch
- agent: web-evidence-collector (model: opus)
- skill: web-evidence-fetch

산출물:
- (A) Manufacturer / (B) 모델 매트릭스 / (C) endpoint / (D) OEM / (E) 펌웨어
- (F) 결정 (a/b)
- sources URL list
- M-E2 adapter spec
```

## 관련

- rule 50 R2 (vendor 추가 9단계)
- rule 96 R1-A (web sources)
- agent: web-evidence-collector
- skill: web-evidence-fetch, add-new-vendor
