# M-I3 — bmc / firmware section 변형 매트릭스 (vendor OEM namespace 노출)

> status: [PENDING] | depends: M-I2 | priority: P1 | worker: W4 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "bmc / firmware section 변형 큼 — vendor OEM namespace 노출 매트릭스." (cycle 진입)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (bmc / firmware 수집 강화 — OEM namespace 매핑), `redfish-gather/tasks/normalize_standard.yml` |
| 영향 vendor | 9 vendor (OEM namespace 차이 큼) |
| 함께 바뀔 것 | M-J1 OEM namespace mapping (본 ticket 의 매트릭스 입력) |
| 리스크 top 3 | (1) OEM namespace 9 vendor 변형 — 매핑 누락 위험 / (2) UpdateService 응답 형식 vendor 별 차이 / (3) 사이트 검증 4 vendor 영향 0 |
| 진행 확인 | M-I2 후 진입 |

---

## bmc / firmware OEM namespace 매트릭스

### bmc section (`/Managers/{id}` + `Oem.<vendor>`)

| vendor | namespace | sub-keys |
|---|---|---|
| Dell | `Oem.Dell` | `DellManager` (firmware/license/network info) |
| HPE | `Oem.Hpe` (legacy `Oem.Hp` fallback) | `iLOServiceTime`, `Links.NetworkServices` |
| Lenovo | `Oem.Lenovo` | `LenovoSubsystemHealth`, `LenovoSecurityDescriptor` |
| Cisco | `Oem.Cisco` | `RackUnit`, `CiscoSerialNumber` |
| Supermicro | `Oem.Supermicro` | `SmartFan`, `SmartHeartbeat` (X11+ 만) |
| Huawei iBMC | `Oem.Huawei` | `SystemHealth`, `BoardInfo` |
| Inspur | `Oem.Inspur` (또는 `Oem.Inspur_System`) | `SystemInfo`, `NetworkInfo` |
| Fujitsu iRMC | `Oem.ts_fujitsu` (또는 `Oem.Fujitsu`) | `Sources`, `FanInfo` |
| Quanta QCT | `Oem.Quanta_Computer_Inc` (또는 `Oem.QCT`) | OEM 약함 |

### firmware section (`/UpdateService/FirmwareInventory` + OEM)

| vendor | path | OEM 노출 |
|---|---|---|
| Dell | 표준 + `Oem.Dell.DellFirmwareInventory` | iDRAC firmware version + license |
| HPE | 표준 + `Oem.Hpe.SmartUpdate` | iLO + BIOS + iLO 5/6 dual fw |
| Lenovo | 표준 | XCC firmware version 만 |
| Cisco | 표준 + `Oem.Cisco.CiscoServerFirmware` | CIMC + BIOS + adapter fw |
| Supermicro | 표준 | BMC firmware 만 |
| Huawei | 표준 + `Oem.Huawei.FirmwareInfo` | iBMC + BIOS + CPLD |
| Inspur | 표준 (OEM 약함) | ISBMC firmware |
| Fujitsu | 표준 + `Oem.ts_fujitsu.FirmwareInfo` | iRMC firmware |
| Quanta | 표준 | QCT firmware |

---

## 구현 (redfish_gather.py 보강 + normalize_standard.yml)

### 1. redfish_gather.py — bmc OEM namespace 매핑

기존 `_collect_managers` 함수 안에 OEM namespace fallback 추가 (rule 12 R1 Allowed — Redfish OEM spec 직접 의존):

```python
# 기존 _collect_managers 함수 안 (Additive)
def _collect_managers(session, base_url):
    # ... 기존 표준 수집
    managers = ...

    # OEM namespace 매핑 (cycle 2026-05-07 M-I3 — Additive)
    for mgr in managers:
        oem = mgr.get("Oem", {})
        # vendor namespace fallback (rule 12 R1 Allowed — OEM spec 직접 의존)
        mgr["_oem_normalized"] = (
            oem.get("Dell")
            or oem.get("Hpe")
            or oem.get("Hp")           # iLO4 legacy fallback
            or oem.get("Lenovo")
            or oem.get("Cisco")
            or oem.get("Cisco_RackUnit")  # Cisco 변형
            or oem.get("Supermicro")
            or oem.get("Huawei")
            or oem.get("Inspur")
            or oem.get("Inspur_System")  # Inspur 변형
            or oem.get("ts_fujitsu")
            or oem.get("Fujitsu")        # Fujitsu 변형
            or oem.get("Quanta_Computer_Inc")
            or oem.get("QCT")            # Quanta 변형
            or {}
        )
    return managers
```

### 2. normalize_standard.yml — bmc section emit 시 _oem_normalized 사용

기존 normalize_standard.yml 의 bmc fragment 생성 부분에 `_oem_normalized` 영역 추가 (Additive — 기존 표준 영역 변경 0):

```yaml
# 기존 bmc fragment 생성 부분 (변경 0)
# ...

# OEM namespace fragment 추가 (cycle 2026-05-07 M-I3 — Additive)
- name: "BMC OEM namespace fragment 생성"
  ansible.builtin.set_fact:
    _data_fragment:
      bmc:
        oem_normalized: "{{ _rf_raw_collect.managers[0]._oem_normalized | default({}) }}"
  when:
    - _rf_raw_collect.managers is defined
    - _rf_raw_collect.managers[0]._oem_normalized is defined
```

### 3. firmware section — UpdateService 표준 + OEM 영역

기존 `_collect_firmware` 함수 안에 OEM 영역 추가 (Additive 동일 패턴).

---

## 회귀 / 검증

### 정적 검증

- [ ] `python -m py_compile redfish_gather.py` 통과
- [ ] `verify_vendor_boundary.py` 통과 (rule 12 R1 Allowed 영역 — OEM namespace 매핑은 Redfish spec 직접 의존)
- [ ] `pytest tests/ -k bmc` + `-k firmware` 통과

### Additive only

- [ ] 기존 _collect_managers / _collect_firmware 표준 path 변경 0
- [ ] 사이트 검증 4 vendor envelope shape 변경 0

### 동적 검증

```bash
pytest tests/e2e/test_bmc_oem_namespace.py -v

# 검증:
# - 각 mock fixture (9 vendor) 의 bmc 응답 → _oem_normalized 정확히 추출
# - Oem.Hp / Oem.Hpe fallback (iLO4 vs iLO5+)
# - Oem.Inspur / Oem.Inspur_System fallback
# - Oem.ts_fujitsu / Oem.Fujitsu fallback
# - Oem.Quanta_Computer_Inc / Oem.QCT fallback
```

---

## risk

- (MED) OEM namespace 매핑 누락 — 새 vendor 도입 시 fallback list 갱신 의무 (M-J1 mapping 매트릭스 동기화)
- (LOW) `_oem_normalized` 라는 새 키 추가 — envelope 13 필드 영향 0 (data.bmc.oem_normalized sub-key, envelope shape 보존)

## 완료 조건

- [ ] redfish_gather.py 의 _collect_managers + _collect_firmware OEM namespace 매핑 추가 (Additive)
- [ ] normalize_standard.yml 의 bmc fragment 에 oem_normalized 추가
- [ ] 사이트 검증 4 vendor envelope shape 변경 0
- [ ] pytest 회귀 PASS
- [ ] commit: `feat: [M-I3 DONE] bmc / firmware OEM namespace 매핑 (9 vendor) + fallback 분기`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W4 영역 종료. 다음 worker (W5 — gather sections 마무리 + OEM + origin + catalog) 진입 알림.

## 관련

- M-I1, M-I2 (gather sections 동일 패턴)
- M-J1 (OEM namespace mapping — 본 ticket 의 매트릭스 입력)
- rule 12 R1 (vendor namespace 분기 — Allowed 영역)
- rule 92 R2 (Additive)
- rule 96 R1+R1-A (Redfish OEM spec)
