# M-J1 — OEM namespace mapping (9 vendor) 매트릭스 + Cisco vendor task 신설

> status: [PENDING] | depends: B4, C3, D2, E3, F2, G2, H1~H4, I5 | priority: P1 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "9 vendor namespace 매트릭스 + Cisco vendor task 신설." (cycle 진입)

cycle 2026-05-06 검토 — Cisco vendor task (`redfish-gather/tasks/vendors/cisco/`) 부재. 본 ticket 에서 신설 + 9 vendor namespace 매트릭스 통합 검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/vendors/cisco/{collect_oem.yml, normalize_oem.yml}` (신설), `redfish-gather/library/redfish_gather.py` (vendor namespace 매핑 검증) |
| 영향 vendor | 9 vendor 통합 (Dell/HPE/Lenovo/Supermicro/Cisco/Huawei/Inspur/Fujitsu/Quanta) |
| 함께 바뀔 것 | 모든 영역 ticket 의 OEM tasks 통합 검증 |
| 리스크 top 3 | (1) Cisco vendor task 신설 — 패턴 일관성 (Dell/HPE/Lenovo/Supermicro 와 동일) / (2) namespace fallback 누락 vendor 발견 / (3) 9 vendor 매트릭스 매핑 정확성 |
| 진행 확인 | 모든 vendor 영역 ticket [DONE] 후 진입 |

---

## OEM namespace 매트릭스 (cycle 2026-05-07 정본)

| vendor | namespace 우선 | namespace fallback |
|---|---|---|
| Dell | `Oem.Dell` | (없음) |
| HPE | `Oem.Hpe` | `Oem.Hp` (iLO4 legacy) |
| Lenovo | `Oem.Lenovo` | (없음) |
| Cisco | `Oem.Cisco` | `Oem.Cisco_RackUnit` |
| Supermicro | `Oem.Supermicro` | (없음) |
| Huawei | `Oem.Huawei` | (없음) |
| Inspur | `Oem.Inspur` | `Oem.Inspur_System` |
| Fujitsu | `Oem.ts_fujitsu` | `Oem.Fujitsu` |
| Quanta | `Oem.Quanta_Computer_Inc` | `Oem.QCT` |

→ M-I3 의 `_oem_normalized` 매핑이 본 매트릭스 cover 확인.

---

## 구현

### 1. Cisco vendor task 신설 (`redfish-gather/tasks/vendors/cisco/`)

#### collect_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/cisco/collect_oem.yml
# Cisco UCS / CIMC OEM 수집 — Oem.Cisco 또는 Oem.Cisco_RackUnit namespace
#
# source: https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/ (확인 2026-05-07)
# Fragment 철학 (rule 22)
# 사이트 검증: UCS X-series (cycle 2026-05-06 PASS) / 그 외 lab 부재

- name: "Cisco OEM — System / Chassis OEM data 수집 (best-effort)"
  block:
    - name: "Cisco OEM — System Oem.Cisco / Oem.Cisco_RackUnit fallback"
      ansible.builtin.set_fact:
        _cisco_oem_system: >-
          {{
            (_rf_raw_collect.systems[0].Oem.Cisco | default(_rf_raw_collect.systems[0].Oem.Cisco_RackUnit | default({})))
          }}

    - name: "Cisco OEM — Chassis 동일 fallback"
      ansible.builtin.set_fact:
        _cisco_oem_chassis: >-
          {{
            (_rf_raw_collect.chassis[0].Oem.Cisco | default(_rf_raw_collect.chassis[0].Oem.Cisco_RackUnit | default({})))
          }}
  rescue:
    - name: "Cisco OEM — 영역 부재 (CIMC 1.x 가능성)"
      ansible.builtin.set_fact:
        _cisco_oem_system: {}
        _cisco_oem_chassis: {}
        _cisco_oem_errors: []   # graceful
```

#### normalize_oem.yml

```yaml
---
- name: "Cisco OEM — fragment 생성"
  ansible.builtin.set_fact:
    _data_fragment:
      bmc:
        oem_cisco:
          system_info: "{{ _cisco_oem_system | default(omit) }}"
          chassis_info: "{{ _cisco_oem_chassis | default(omit) }}"
    _sections_supported_fragment: ["bmc"]
    _sections_collected_fragment: "{{ ['bmc'] if (_cisco_oem_system or _cisco_oem_chassis) else [] }}"
    _sections_failed_fragment: []
    _errors_fragment: []

- name: "Cisco OEM — fragment 누적 병합"
  ansible.builtin.include_tasks: "{{ playbook_dir }}/common/tasks/normalize/merge_fragment.yml"
```

### 2. Cisco adapter 의 oem_tasks 경로 추가

`adapters/redfish/cisco_cimc.yml`, `cisco_ucs_xseries.yml`, `cisco_bmc.yml` 의 `collect.oem_tasks` 에 cisco/collect_oem.yml 경로 추가:

```yaml
collect:
  strategy: standard+oem
  oem_tasks: "redfish-gather/tasks/vendors/cisco/collect_oem.yml"
```

→ Additive — 기존 `standard_only` strategy 였으면 `standard+oem` 으로 변경 (UCS X-series 사이트 검증 envelope 영향 검증 의무).

**중요**: cisco_ucs_xseries.yml 변경 시 사이트 검증 envelope shape 영향 0 검증 필수 (rule 92 R2). OEM 영역만 추가 — 표준 영역 변경 0.

### 3. redfish_gather.py vendor namespace 매핑 검증

M-I3 의 `_oem_normalized` 매핑이 9 vendor 모두 cover 하는지 검증:

```bash
# 각 mock fixture 응답으로 _oem_normalized 추출 검증
pytest tests/e2e/test_oem_namespace_mapping.py -v

# 검증:
# - dell mock → Oem.Dell 추출
# - hpe iLO5+ mock → Oem.Hpe 추출
# - hpe iLO4 mock → Oem.Hp fallback 추출 (legacy)
# - lenovo mock → Oem.Lenovo 추출
# - cisco mock → Oem.Cisco / Oem.Cisco_RackUnit fallback
# - supermicro mock → Oem.Supermicro 추출
# - huawei mock → Oem.Huawei 추출
# - inspur mock → Oem.Inspur / Oem.Inspur_System fallback
# - fujitsu mock → Oem.ts_fujitsu / Oem.Fujitsu fallback
# - quanta mock → Oem.Quanta_Computer_Inc / Oem.QCT fallback
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `validate-fragment-philosophy` skill 통과 (Cisco OEM tasks)
- [ ] `verify_vendor_boundary.py` 통과 (Cisco vendor task 영역 — rule 12 R1 Allowed)
- [ ] `verify_harness_consistency.py` 통과

### Additive only

- [ ] cisco_ucs_xseries.yml 의 사이트 검증 envelope shape 변경 0 (envelope_change_check.py)
- [ ] 기존 4 vendor (Dell/HPE/Lenovo/Supermicro) OEM tasks 변경 0
- [ ] redfish_gather.py 표준 path 변경 0

### 동적 검증

- [ ] 9 vendor mock fixture 모두 OEM namespace 추출 PASS
- [ ] Cisco vendor task — UCS X-series mock 응답 정확히 처리 (사이트 검증 fixture 영향 0)

---

## risk

- (MED) cisco_ucs_xseries.yml 변경 시 사이트 검증 envelope 영향 — Additive 검증 의무
- (LOW) Cisco UCS B-series chassis-based 응답 — 본 ticket 범위 외. 사이트 도입 시 별도 cycle

## 완료 조건

- [ ] redfish-gather/tasks/vendors/cisco/ 디렉터리 신설 (collect_oem.yml + normalize_oem.yml)
- [ ] 3 Cisco adapter (cisco_bmc / cisco_cimc / cisco_ucs_xseries) 의 oem_tasks 경로 추가
- [ ] cisco_ucs_xseries 사이트 검증 envelope 영향 0 검증
- [ ] 9 vendor namespace 매핑 매트릭스 검증 PASS
- [ ] commit: `feat: [M-J1 DONE] OEM namespace mapping (9 vendor) + Cisco vendor task 신설`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-K1 (origin 주석 일관성 검증).

## 관련

- 모든 vendor 영역 ticket (B4, C3, D2, E3, F2, G2, H1~H4, I5)
- M-I3 (OEM namespace _oem_normalized 매핑)
- rule 12 R1 (vendor namespace 분기 — Allowed)
- rule 22 (Fragment 철학)
- rule 92 R2 (Additive)
- 정본: `redfish-gather/tasks/vendors/dell/collect_oem.yml`
