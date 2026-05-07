# M-I4 — network section 변형 매트릭스 (NIC OEM driver / SR-IOV / OCP)

> status: [PENDING] | depends: M-I3 | priority: P2 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "network section — NIC OEM driver / SR-IOV / OCP 변형 매트릭스." (cycle 진입 영역 I 마무리)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (network 수집 보강) + `normalize_standard.yml` |
| 영향 vendor | 9 vendor — 사이트 검증 4 vendor 영향 0 (Additive) |
| 함께 바뀔 것 | M-J1 OEM mapping |
| 리스크 top 3 | (1) NIC adapter path 차이 (`/EthernetInterfaces` vs `/NetworkAdapters`) / (2) SR-IOV 응답 형식 vendor 별 / (3) OCP NIC mezzanine 분기 |
| 진행 확인 | M-I3 후 진입 |

---

## Network 변형 매트릭스

### NIC adapter path

| vendor | generation | path | 비고 |
|---|---|---|---|
| Dell | iDRAC9+ | `/Systems/{id}/NetworkInterfaces` + `/Chassis/{id}/NetworkAdapters` | dual |
| HPE | iLO5+ | 동일 | dual |
| Lenovo | XCC+ | 동일 | dual |
| Cisco | UCS X-series | 동일 | dual |
| Supermicro | X12+ | `/Systems/{id}/EthernetInterfaces` | EthernetInterfaces 우선 |
| Supermicro | X9-X11 | `/Systems/{id}/EthernetInterfaces` | EthernetInterfaces only |
| Huawei iBMC | 2.x+ | dual | |
| Inspur | ISBMC | `/Systems/{id}/EthernetInterfaces` | EthernetInterfaces only |
| Fujitsu | iRMC S5+ | dual | |
| Quanta | QCT | `/Systems/{id}/EthernetInterfaces` | EthernetInterfaces only |
| 기타 legacy | | `/Systems/{id}/EthernetInterfaces` | legacy fallback |

### SR-IOV 응답

| vendor | path | 노출 |
|---|---|---|
| Dell | `Oem.Dell.NICDeviceFunctions.SRIOVCapable` | bool |
| HPE | `Oem.Hpe.NetworkAdapter.SRIOVConfig` | dict |
| Lenovo | `NetworkInterfaces/{id}/NetworkDeviceFunctions/{id}` 표준 | DSP0268 v1.6+ |
| 기타 | 표준 path 우선 |

### OCP NIC (Open Compute Project mezzanine)

| vendor | OCP NIC 노출 |
|---|---|
| Dell | iDRAC9 6.x+ — OCP 3.0 분기 |
| HPE | iLO6+ — OCP 3.0 분기 |
| Supermicro | X13+ — OCP 3.0 분기 |
| 기타 | 표준 NIC path 만 |

---

## 구현 (redfish_gather.py 보강 — Additive)

### Network 수집 — 2 path dual + SR-IOV + OCP

```python
def _collect_network(session, base_url, system_id, chassis_id, adapter_capabilities):
    """Network 수집 — EthernetInterfaces (system) + NetworkAdapters (chassis) dual.

    1. nic_strategy:
       - "ethernet_only" — legacy (X9-X11 / Inspur / Quanta) — /Systems/{id}/EthernetInterfaces 만
       - "dual" — 표준 — 두 path 모두 + merge

    2. SR-IOV:
       - 표준 NetworkDeviceFunctions 우선 (DSP0268 v1.6+)
       - vendor OEM (Dell.NICDeviceFunctions / Hpe.NetworkAdapter.SRIOVConfig) fallback

    3. OCP NIC:
       - chassis NetworkAdapters 의 LocationContext / SlotType 으로 OCP 식별

    rule 92 R2: 사이트 검증 4 vendor 영향 0.
    """
    nic_strategy = adapter_capabilities.get("nic_strategy", "dual")

    if nic_strategy == "ethernet_only":
        return _collect_network_ethernet(session, base_url, system_id)

    # dual
    ethernet = _collect_network_ethernet(session, base_url, system_id)
    try:
        adapters = _collect_network_adapters(session, base_url, chassis_id)
        return _merge_network(ethernet, adapters)
    except (HTTPError, KeyError):
        return ethernet
```

### normalize_standard.yml — network fragment 에 SR-IOV / OCP 추가

기존 network fragment 에 `sriov_capable` / `ocp_slot` 추가 (Additive — 표준 영역 변경 0).

---

## 회귀 / 검증

### 정적 검증

- [ ] `python -m py_compile` 통과
- [ ] `pytest tests/ -k network` 통과

### Additive only

- [ ] 기존 _collect_network_ethernet 변경 0
- [ ] 사이트 검증 4 vendor envelope shape 변경 0

### 동적 검증

- [ ] mock fixture 별 nic_strategy 분기 검증
- [ ] SR-IOV / OCP 노출 영역 추출

---

## risk

- (MED) NetworkAdapters path 응답이 NIC 카드 단위 — Drive 와 다른 cardinality. merge 로직 정확성
- (LOW) OCP NIC 노출 약함 — SlotType="OCP" 표시 펌웨어 별 차이

## 완료 조건

- [ ] redfish_gather.py _collect_network 함수 + 3 sub-helper (Additive)
- [ ] normalize_standard.yml network fragment 에 SR-IOV / OCP 추가
- [ ] 사이트 검증 4 vendor envelope shape 변경 0
- [ ] commit: `feat: [M-I4 DONE] network section 변형 매트릭스 + dual NIC path + SR-IOV + OCP`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-I5 (system / cpu / memory / users gap 검증).

## 관련

- M-I1 / M-I2 / M-I3 (gather sections 동일 패턴)
- rule 92 R2 (Additive)
- rule 96 R1 (DSP0268 NetworkInterfaces / NetworkAdapters spec)
