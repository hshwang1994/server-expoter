# Coverage — thermal 영역 (Thermal → ThermalSubsystem) — 신규 검토

## 채널

- **Redfish only** — `/redfish/v1/Chassis/{id}/Thermal` 또는 `/ThermalSubsystem`
- 현재 server-exporter **미수집**. cycle 2026-05-01 신규 검토 영역.

## 표준 spec (R1)

### 구 path (Thermal schema, deprecated DMTF 2020.4)
- `/redfish/v1/Chassis/{id}/Thermal`
- `Temperatures[*]` — 센서 (CPU temp, ambient temp 등)
- `Fans[*]` — fan speed / health

### 신 path (ThermalSubsystem schema, DMTF 2020.4)
- `/redfish/v1/Chassis/{id}/ThermalSubsystem`
- `/Fans/{id}` (collection)
- `/EnvironmentMetrics` — TemperatureCelsius 등 (Power와 같은 path)

### Sensor schema (별도 path)
- `/redfish/v1/Chassis/{id}/Sensors/{sensor_id}`
- ReadingType (Temperature / Fan / Voltage / Current / Frequency / Power)

## Vendor 호환성 (R2)

| Vendor | Thermal | ThermalSubsystem | Sensors |
|---|---|---|---|
| Dell iDRAC 8/9 | OK | iDRAC 9 ≥5.x | 부분 |
| HPE iLO 5 | OK | 부분 | OK |
| HPE iLO 6 | OK | OK | OK |
| Lenovo XCC | OK | XCC2-3 OK | 부분 |
| Supermicro X11+ | OK | X12+ | 부분 |
| Cisco CIMC | OK | — (확인 필요) | 부분 |

## 알려진 사고 (R3)

### Th1 — Thermal/ThermalSubsystem coexist (구 펌웨어)
- 일부 펌웨어가 두 path 모두 응답 — 양쪽 같은 데이터 / 호환성 위해

### Th2 — Sensors collection은 별도 schema
- ReadingType 별 분리 — 쿼리 양 많아질 수 있음

### Th3 — Fan SpeedRPM / SpeedPercent 단위 차이
- vendor 별 enum 다름

## fix 후보 (thermal 영역)

### F6 — thermal 섹션 신규 도입 (Additive — 신규 섹션)
- **현재 상태**: schema/sections.yml에 thermal 섹션 없음. 미수집.
- **변경 (Additive)**: 신규 섹션 추가:
  1. `schema/sections.yml` 에 `thermal` 추가
  2. `schema/field_dictionary.yml` 에 thermal 필드 정의
  3. `redfish_gather.py` 에 `gather_thermal()` 함수 신규 추가
  4. `_collect_all_sections` 에 'thermal' dispatch 추가
  5. adapter 16개 capabilities `sections_supported` 에 'thermal' 추가
  6. baseline 7 vendor json 에 thermal section 추가
  7. normalize 에 thermal fragment 추가
- **fallback 패턴 (Power와 동일)**:
  ```python
  def gather_thermal(bmc_ip, chassis_uri, ...):
      thermal_path = _p(chassis_uri) + '/Thermal'
      st, data, err = _get(...)
      if st == 404:
          return _gather_thermal_subsystem(...)   # 신 schema fallback
      ...
  ```
- **회귀**: 7 vendor baseline 갱신 — schema 변경 (rule 92 R5 사용자 명시 승인 필수)
- **사용자 승인 의무 (rule 92 R5)**: schema 버전 변경
- **우선**: P2 — 사용자 승인 후

## 신규 섹션 vs 기존 power 섹션 분리

대안: 기존 power 섹션 안에 thermal 정보 합침 vs 별도 thermal 섹션
- **별도 권장**: rule 22 fragment 철학 — 각 섹션은 독립적 책임
- DMTF 표준도 별도 schema (Power vs Thermal)

## 우리 코드 위치 (현재)

- **없음** — thermal 미수집

## Sources

- [DMTF DSP2064 (Thermal Equipment)](https://www.dmtf.org/sites/default/files/standards/documents/DSP2064_1.0.0.pdf)
- [NVIDIA ThermalSubsystem design](https://github.com/NVIDIA/nvbmc-docs/blob/develop/Redfish%20APIs%20Design%20for%20ThermalSubsystem%20Management.md)
- [Supermicro Power and Thermal](https://www.supermicro.com/manuals/other/redfish-user-guide-4-0/Content/general-content/power-and-thermal-resource-tree.htm)

## 갱신 history

- 2026-05-01: R1+R2+R3 / Th1~Th3 / F6 P2 (사용자 승인 후)
