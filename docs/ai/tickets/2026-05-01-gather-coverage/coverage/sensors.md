# Coverage — sensors 영역 (Sensor schema) — 신규 검토

## 채널

- **Redfish only** — Chassis 안 standalone Sensor 모델 (DMTF 신규 — Thermal/Power 의 통합 alt)

## 표준 spec (R1)

### 표준 path
- `/redfish/v1/Chassis/{id}/Sensors/{sensor_id}` (standalone)
- ThermalSubsystem / PowerSubsystem 의 Sensor reference

### Sensor schema 필드
- `ReadingType` (Temperature / Voltage / Frequency / Power / Current / **Fan**)
- `Reading` (실 값), `ReadingUnits`
- `Status.Health` / `State`
- `LowerThresholdCritical` / `UpperThresholdCritical`
- `LowerThresholdNonCritical` / `UpperThresholdNonCritical`

### 2024.1 신규 필드
- Manufacturer / Model / SKU / SerialNumber / PartNumber / SparePartNumber / UserLabel

### Reading Categories
1. Thermal — Temperature 센서
2. Power — PowerWatts / EnergyJoules
3. Voltage — system board / PSU
4. Frequency — clock / fan RPM (별도 ReadingType=Fan)

## 우리 코드 영향

### 현재 미수집
sensors 섹션 자체 없음. 향후 thermal 섹션 도입 (F6) 시 통합 검토.

## fix 후보

### F27 — Sensor schema 활용 (F6 묶음)
- **묶음**: F6 (thermal 섹션 신규 도입) 작업 시 함께 ThermalSubsystem 안 Fan + Sensor 통합
- **변경 (Additive)**: thermal 섹션 안 sub-key 또는 신규 sensors 섹션
- **우선**: P2 (F6 묶음)

## Sources

- [DMTF Redfish Telemetry / Sensor architecture](https://github.com/openbmc/docs/blob/master/architecture/sensor-architecture.md)
- [DMTF 2024.1 Sensor part identification](https://www.dmtf.org/content/redfish-release-20241-now-available)

## 갱신 history

- 2026-05-01: 신규 영역 ticket / F27 P2 (F6 묶음)
