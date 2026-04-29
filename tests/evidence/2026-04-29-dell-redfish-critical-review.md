# Dell Redfish 비판적 검증 — Round 11 reference vs 코드

> **일자**: 2026-04-29
> **사용자 의도**: "실제 데이터가 수집안되는게 많다거나 부분은 공통 json에는 있지만 데이터는 없는 경우를 의미한다. json키를 늘릴 이유는 없음. 그리고 버그가있다면 묻지말고 모두 fix해서 개선해라"
> **검증 방식**: Round 11 실측 reference (Dell R760, 10.100.15.27, iDRAC 7.10.70.00, 1624 endpoints crawl) ↔ `redfish-gather/library/redfish_gather.py` + `redfish-gather/tasks/normalize_standard.yml` ↔ `schema/baseline_v1/dell_baseline.json`

---

## 검증 환경

| 항목 | 값 |
|---|---|
| Reference 위치 | `tests/reference/redfish/dell/10_100_15_27/` |
| Vendor / Model | Dell Inc. / PowerEdge R760 (16G Monolithic) |
| iDRAC Firmware | 7.10.70.00 |
| BIOS | 2.3.5 |
| Redfish | 1.20.1 |
| 수집 endpoint 수 | 1624 (OK 1621 / Fail 3) |
| 비교 대상 baseline | `schema/baseline_v1/dell_baseline.json` (LENOVO01 R740, 14G Monolithic, iDRAC 4.00.00.00 — 다른 host) |

---

## 발견 26건 분류

| Tier | 건수 | 사용자 정의 fix 대상? |
|---|---|---|
| CRITICAL — 수집 자체가 깨짐 | 2 | 일부 (envelope 키 있는 것만) |
| HIGH — envelope 키 미채움 / 위생 | 11 | 7건 fix |
| MEDIUM — 정합성 / fallback | 5 | 일부 |
| LOW / 의도 | 8 | skip |

---

## fix 적용 7건 (envelope 키 미채움 / 명확한 버그)

### BUG-1 (CRIT) — Dell `EstimatedExhaustTemperatureCel` 키 오타

**파일**: `redfish-gather/library/redfish_gather.py:_extract_oem_dell`
**raw 키**: `Oem.Dell.DellSystem.EstimatedExhaustTemperatureCelsius` (R760 raw 에는 `null` 반환 — 펌웨어/플랫폼별 가용성)
**코드 키**: `EstimatedExhaustTemperatureCel` (오타) → 항상 None
**영향**: 모든 Dell 호스트 `data.hardware.oem.estimated_exhaust_temp` 항상 None
**fix**: Celsius 우선 + Cel fallback 둘 다 시도

### BUG-12 (HIGH) — `hardware.bios_date` 하드코딩 null

**파일**: `redfish-gather/tasks/normalize_standard.yml`
**문제**: `bios_date: null` 하드코딩. raw 에서 가용한 `Oem.Dell.DellSystem.BIOSReleaseDate` ("09/10/2024") 무시
**fix**: `_rf_d_system.oem.bios_release_date` fallback 사용. vendor OEM 에서 노출된 `bios_release_date` 키 활용

### BUG-13 (HIGH) — `cpu.cores_physical / logical_threads` ProcessorSummary fallback 없음

**파일**: `redfish-gather/library/redfish_gather.py:gather_system` + `normalize_standard.yml`
**문제**: per-processor `TotalCores / TotalThreads` 합산만. 누락 펌웨어에서 0 또는 cores 와 동일값
**raw R760**: `ProcessorSummary.CoreCount=24, LogicalProcessorCount=48` (HT 켜짐 ground truth)
**fix**: 라이브러리 `cpu_summary` 에 `core_count / logical_processor_count` 추출 추가 (envelope 영향 X) + normalize 에서 sum 0 시 fallback

### BUG-14 (HIGH) — `memory.total_mb / installed_mb` MemorySummary fallback 없음

**파일**: `redfish-gather/tasks/normalize_standard.yml`
**문제**: per-DIMM `CapacityMiB` 합산만. Absent 슬롯 다수 또는 응답 누락 펌웨어에서 0
**raw R760**: `MemorySummary.TotalSystemMemoryGiB=256` (BIOS visible — 가장 정확)
**fix**: per-DIMM sum 0 시 `MemorySummary.TotalSystemMemoryGiB * 1024` fallback

### BUG-15 (HIGH) — `volume.boot_volume` Dell-only 처리

**파일**: `redfish-gather/library/redfish_gather.py:_extract_storage_volumes`
**문제**: 표준 Redfish `Volume.BootVolume` 무시, `Oem.Dell.DellVolume.BootVolumeSource` 만 사용 → HPE/Lenovo/Supermicro 항상 None
**raw R760 BOSS volume**: `BootVolume: null` (표준 필드, Dell 도 미사용 — Dell 은 OEM 만 채움)
**fix**: 표준 BootVolume 우선 (None != false 구분), Dell OEM fallback. 다른 vendor 표준 응답 정상 처리

### BUG-16 (MED) — Volume Name trailing whitespace

**파일**: `redfish-gather/library/redfish_gather.py:_extract_storage_volumes`
**raw R760**: `Name: 'VD_0   '` (trailing 3 spaces). 코드 strip 안 함 → envelope 'VD_0   '
**fix**: `_safe(vdata, 'Name').strip()` 적용

### BUG-19 (MED) — Volume health HealthRollup fallback 누락 (drive 와 비대칭)

**파일**: `redfish-gather/library/redfish_gather.py:_extract_storage_volumes`
**문제**: drive 추출은 `Status.Health` → `HealthRollup` fallback (`redfish_gather.py:818`) 있는데 volume 은 누락
**fix**: 동일 패턴 적용

---

## fix 미적용 19건 (envelope 키 추가 필요 → 사용자 정의로 skip)

| # | 영역 | 누락 정보 | skip 사유 |
|---|---|---|---|
| BUG-2 | storage.controllers[] | controller_model / controller_firmware / controller_manufacturer / controller_health (라이브러리는 추출, normalize 가 무시) | envelope 키 추가 필요 |
| BUG-3 | power.power_supplies[] | PartNumber / PowerInputWatts / LineInputVoltage / LineInputVoltageType / SparePartNumber / HotPluggable | envelope 키 추가 필요 |
| BUG-4 | power.power_control | PowerLimit (LimitInWatts / LimitException / CorrectionInMs) | envelope 키 추가 필요 |
| BUG-5 | firmware[] | ReleaseDate / Manufacturer / Status / LowestSupportedVersion | envelope 키 추가 필요 |
| BUG-6 | storage.physical_disks[] | HotspareType / EncryptionAbility / EncryptionStatus / RotationSpeedRPM / Revision (drive firmware) | envelope 키 추가 필요 |
| BUG-7 | storage.logical_volumes[] | BlockSizeBytes / OptimumIOSizeBytes / Encrypted / ReadCachePolicy / WriteCachePolicy | envelope 키 추가 필요 |
| BUG-8 | memory.slots[] | VolatileSizeMiB / NonVolatileSizeMiB (PMem 구분) / MemoryMedia | envelope 키 추가 필요 |
| BUG-9 | network.interfaces[] | PermanentMACAddress / InterfaceEnabled / Status (Health/State) | envelope 키 추가 필요 |
| BUG-10 | network.adapters[] | Status (Health/HealthRollup/State) / Identifiers | envelope 키 추가 필요 |
| BUG-11 | (신 sub-section) | BIOS Attributes 571 entries (BootMode / MemoryEncryption / SystemMemorySize / Sriov 등) | envelope sub-section 추가 필요 + 데이터 비대화 |
| BUG-17 | storage.controllers[].drives[] | serial / manufacturer (physical_disks 와 비대칭) | envelope 키 추가 필요 |
| BUG-18 | (SimpleStorage) | manufacturer | envelope 키 추가 필요 |

---

## 검증 결과

| 검증 | 결과 |
|---|---|
| `python -m py_compile redfish-gather/library/redfish_gather.py` | PASS |
| `yaml.safe_load(open('redfish-gather/tasks/normalize_standard.yml'))` | PASS |
| `python -m pytest tests/ --tb=short` | **158 passed in 17.20s** |
| `python scripts/ai/verify_harness_consistency.py` | PASS (rules 28 / skills 43 / agents 49 / policies 9) |
| `python scripts/ai/verify_vendor_boundary.py` | PASS |

---

## 다음 cycle 후속

1. **Round 12 실 BMC 검증** (사용자 제공 권한 — agent 10.100.64.154 SSH):
   - Dell 1대 ansible 트리거 → 실제 fix 후 envelope 변경 확인
   - 영향 vendor baseline 갱신 (`schema/baseline_v1/dell_baseline.json` `hardware.bios_date` / `oem.estimated_exhaust_temp` 2 필드)
   - HPE/Lenovo 영향 영역 (BUG-15 boot_volume 표준 우선화) baseline 갱신 확인
2. **사용자 결정 필요** (envelope 키 추가 19건 — BUG-2~11/17/18):
   - 호출자가 PSU PartNumber / Firmware ReleaseDate / NIC PermanentMAC 등 정보를 정말 원하는지
   - 운영 정책으로 envelope 키 확장 ADR 작성 또는 의도적 미수집 명시

---

**참고 문서**:
- `docs/ai/CURRENT_STATE.md` — Dell Redfish bug-fix 절
- `docs/ai/catalogs/TEST_HISTORY.md` — 본 cycle 테스트 결과
- rule 95 R1 (production code critical review) — 11 의심 패턴 스캔
- rule 96 R1 (external contract integrity) — adapter origin 주석
