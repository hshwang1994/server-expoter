# Coverage — power 영역 (Power → PowerSubsystem)

## 채널

- **Redfish only** — `/redfish/v1/Chassis/{id}/Power` 또는 `/PowerSubsystem`
- OS / ESXi 채널은 power 미수집

## 표준 spec (R1)

### 구 path (Power schema, deprecated DMTF 2020.4)
- `/redfish/v1/Chassis/{id}/Power`
- `PowerSupplies[*]` — PSU info
- `PowerControl[*]` — system-level metric (PowerConsumedWatts / PowerCapacityWatts / PowerMetrics)

### 신 path (PowerSubsystem schema, DMTF 2020.4 권장)
- `/redfish/v1/Chassis/{id}/PowerSubsystem`
- `/PowerSupplies/{id}` (collection)
- `/PowerSupplyMetrics/{id}` (per-PSU metric)

### EnvironmentMetrics (system-level metric, PowerControl 대체)
- `/redfish/v1/Chassis/{id}/EnvironmentMetrics`
- PowerWatts (현재 power consumption), TemperatureCelsius 등

## Vendor 호환성 (R2)

| Vendor | Power | PowerSubsystem | EnvironmentMetrics |
|---|---|---|---|
| Dell iDRAC 7 | 미지원 다수 | — | — |
| Dell iDRAC 8 | Power만 (일부 모델 미지원) | — | — |
| Dell iDRAC 9 ≤4.x | Power만 | — | — |
| Dell iDRAC 9 ≥5.x | Power+PowerSubsystem | OK | 부분 |
| Dell iDRAC 10 | PowerSubsystem 권장 | OK | OK |
| HPE iLO 4 | Power만 | — | — |
| HPE iLO 5 | Power만 | 부분 (펌웨어별) | — |
| HPE iLO 6 (Gen11+/Gen12) | Power+PowerSubsystem | OK | OK |
| Lenovo IMM2 | Power만 | — | — |
| Lenovo XCC1 | Power+PowerSubsystem 가능 | 부분 | — |
| Lenovo XCC2-3 | PowerSubsystem 권장 | OK | OK |
| Supermicro X9~X11 | Power만 | — | — |
| Supermicro X12+ | Power+PowerSubsystem | OK | OK |
| Supermicro X14+ | PowerSubsystem 권장 | OK | OK |
| Cisco CIMC | Power | — (검증 필요 F12) | — |

## 알려진 사고 (R3)

### P1 — Cisco CIMC PSU power_capacity_w fallback
- **증상**: Cisco PowerSupplies[*].PowerCapacityWatts null. `InputRanges[0].OutputWattage` 에 PSU 정격
- **fix 적용됨**: cycle 2026-04-29 cisco-critical-review — fallback OK ✓

### P2 — Cisco PowerControl PowerCapacityWatts null
- **증상**: chassis level 도 null
- **fix 적용됨**: PSU power_capacity_w 합산 fallback ✓

### P3 — Critical/unhealthy_count 누락
- **fix 적용됨**: cycle 2026-04-29 fix B58 + B59 — health_rollup ✓

### P4 — capacity_unknown_count 분리
- **fix 적용됨**: PSU.PowerCapacityWatts=null 인 슬롯 별도 count ✓

### P5 — Dell iDRAC 8 일부 모델 Power 404
- **fix 적용됨**: cycle 2026-05-01 — 404 → unsupported 분류 ✓

### P6 — F5: PowerSubsystem fallback 시 PowerControl null
- **현재 코드 영향**: cycle 2026-05-01 `_gather_power_subsystem` PSU 만 매핑. PowerControl 정보 (power_consumed / capacity) null
- **우선**: P1 — EnvironmentMetrics fallback 추가

### P7 — F12: Cisco CIMC PowerSubsystem 지원 여부 미확인
- **우선**: P2 — Cisco CIMC 4.x lab 검증

### P8 — Power.PowerControl 비-dict 방어
- **fix 적용됨**: cycle 2026-04-29 — `pdata.get('PowerControl')` isinstance dict 가드 ✓

## fix 후보

### F5 — EnvironmentMetrics fallback (Additive)
- **현재 위치**: `redfish_gather.py` `_gather_power_subsystem` (cycle 2026-05-01 신규)
- **변경 (Additive)**: PowerSubsystem 응답 후 EnvironmentMetrics 도 시도. 200 OK면 PowerControl 정보 추출:
  ```python
  em_path = _p(chassis_uri) + '/EnvironmentMetrics'
  st_em, em_data, _ = _get(...)
  if st_em == 200:
      power_control['power_consumed_watts'] = _safe(em_data, 'PowerWatts', 'Reading')
      # ... etc
  # else: 미지원 — 기존 None 유지 (current 코드)
  ```
- **회귀**: 신 펌웨어 (Gen12 / XCC2-3) 에서 PowerControl 정보 채워짐. 구 펌웨어 영향 없음
- **우선**: P1

### F12 — Cisco PowerSubsystem 지원 검증 (Additive)
- **검증**: Cisco CIMC 4.x lab 에 `/Chassis/1/PowerSubsystem` GET 시도. 200이면 fallback 동작 확인 / 404면 기존 Power 만
- **변경 없음**: 우리 코드는 이미 Power 200 → 사용 / 404 → PowerSubsystem fallback. 자동 동작
- **우선**: P2

## 우리 코드 위치

- 라이브러리: `redfish_gather.py:1670` `gather_power` + `_gather_power_subsystem` (cycle 2026-05-01 신규)
- normalize summary: `normalize_standard.yml:370-404` `_rf_power_summary` (health_rollup / capacity_unknown_count)

## Sources

- [Redfish PowerControl in PowerSubsystem](https://redfishforum.com/thread/710/powercontrol-attribute-equivalent-powersubsystem)
- [DMTF 2020.4 release (Power deprecated)](https://www.dmtf.org/Redfish_Release_20204_Now_Available)
- [Supermicro Power and Thermal Resource Tree](https://www.supermicro.com/manuals/other/redfish-user-guide-4-0/Content/general-content/power-and-thermal-resource-tree.htm)

## 갱신 history

- 2026-05-01: R1+R2+R3 / P1~P8 / F5 P1 / F12 P2
