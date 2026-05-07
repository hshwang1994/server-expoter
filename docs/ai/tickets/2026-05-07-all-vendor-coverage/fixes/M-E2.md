# M-E2 — redfish-gather/tasks/vendors/fujitsu/{collect_oem.yml, normalize_oem.yml} 신설

> status: [PENDING] | depends: M-E1 | priority: P1 | worker: W3 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Fujitsu iRMC OEM tasks 신설 — Oem.ts_fujitsu / Oem.Fujitsu namespace 처리."

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/vendors/fujitsu/collect_oem.yml`, `normalize_oem.yml` (신설) |
| 영향 vendor | Fujitsu iRMC (lab 부재) |
| 함께 바뀔 것 | M-E1 oem_tasks 경로 dep, M-J1 OEM mapping |
| 리스크 top 3 | (1) Oem.ts_fujitsu vs Oem.Fujitsu 펌웨어별 변형 / (2) iRMC S5+ OEM 강화 영역 정확성 / (3) Fragment 철학 |
| 진행 확인 | M-E1 adapter 후 진입 |

---

## Web sources (rule 96 R1-A)

| source | 항목 |
|---|---|
| Fujitsu 공식 | iRMC Redfish API guide — OEM 절 |
| 영역 | Oem.ts_fujitsu.SystemInfo / FirmwareInfo / FanInfo / TemperatureInfo |
| Note | 일부 펌웨어는 `Oem.Fujitsu` (단순 표기) 변형 — fallback 의무 |

---

## 구현

### 1. collect_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/fujitsu/collect_oem.yml
# Fujitsu iRMC OEM 수집 — Oem.ts_fujitsu 또는 Oem.Fujitsu namespace
#
# source: Fujitsu iRMC Redfish API guide (확인 2026-05-07)
# Fragment 철학 (rule 22) — 자기 fragment 만
# lab: 부재 (사용자 명시 2026-05-01)

- name: "Fujitsu OEM — System / Chassis OEM data 수집 (best-effort)"
  block:
    - name: "Fujitsu OEM — System Oem.ts_fujitsu 우선 / Oem.Fujitsu fallback"
      ansible.builtin.set_fact:
        _fujitsu_oem_system: >-
          {{
            (_rf_raw_collect.systems[0].Oem.ts_fujitsu | default(_rf_raw_collect.systems[0].Oem.Fujitsu | default({})))
          }}

    - name: "Fujitsu OEM — Chassis Oem.ts_fujitsu / Oem.Fujitsu fallback"
      ansible.builtin.set_fact:
        _fujitsu_oem_chassis: >-
          {{
            (_rf_raw_collect.chassis[0].Oem.ts_fujitsu | default(_rf_raw_collect.chassis[0].Oem.Fujitsu | default({})))
          }}
  rescue:
    - name: "Fujitsu OEM — 영역 부재 (iRMC S2 가능성)"
      ansible.builtin.set_fact:
        _fujitsu_oem_system: {}
        _fujitsu_oem_chassis: {}
        _fujitsu_oem_errors:
          - section: bmc
            message: "Fujitsu OEM 영역 부재 (iRMC S2 가능성)"
            severity: warning
```

### 2. normalize_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/fujitsu/normalize_oem.yml

- name: "Fujitsu OEM — fragment 생성"
  ansible.builtin.set_fact:
    _data_fragment:
      bmc:
        oem_fujitsu:
          system_info: "{{ _fujitsu_oem_system | default(omit) }}"
          chassis_info: "{{ _fujitsu_oem_chassis | default(omit) }}"
    _sections_supported_fragment: ["bmc"]
    _sections_collected_fragment: "{{ ['bmc'] if (_fujitsu_oem_system or _fujitsu_oem_chassis) else [] }}"
    _sections_failed_fragment: []
    _errors_fragment: "{{ _fujitsu_oem_errors | default([]) }}"

- name: "Fujitsu OEM — fragment 누적 병합"
  ansible.builtin.include_tasks: "{{ playbook_dir }}/common/tasks/normalize/merge_fragment.yml"
```

---

## 회귀 / 검증

- [ ] `ansible-playbook --syntax-check` 통과
- [ ] `validate-fragment-philosophy` skill 통과
- [ ] `verify_vendor_boundary.py` 통과 (Fujitsu OEM 영역 — rule 12 R1 Allowed)
- [ ] Oem.ts_fujitsu / Oem.Fujitsu fallback 분기 검증

## risk

- (MED) iRMC S2 의 OEM 부재 — rescue block 으로 graceful
- (LOW) Oem.ts_fujitsu underscore variant 일부 펌웨어만 — fallback 으로 cover

## 완료 조건

- [ ] redfish-gather/tasks/vendors/fujitsu/ 디렉터리 신설
- [ ] collect_oem.yml + normalize_oem.yml 작성
- [ ] commit: `feat: [M-E2 DONE] Fujitsu OEM tasks 신설 — Oem.ts_fujitsu / Fujitsu fallback`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W3 → M-E3 (Fujitsu mock).

## 관련

- M-E1 (Fujitsu adapter)
- rule 22, rule 96 R1-A
- 정본: `redfish-gather/tasks/vendors/lenovo/collect_oem.yml`
