# M-F1 — redfish-gather/tasks/vendors/quanta/{collect_oem.yml, normalize_oem.yml} 신설

> status: [PENDING] | depends: M-A4 | priority: P1 | worker: W3 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Quanta QCT BMC OEM tasks 신설 — Oem.Quanta_Computer_Inc namespace."

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/vendors/quanta/collect_oem.yml`, `normalize_oem.yml` (신설) |
| 영향 vendor | Quanta QCT (lab 부재) |
| 함께 바뀔 것 | M-F2 mock, M-J1 OEM mapping |
| 리스크 top 3 | (1) Quanta OEM namespace 변형 (Oem.Quanta_Computer_Inc / Oem.QCT) / (2) ODM 모델 customer-specific OEM (Microsoft Azure / Meta) / (3) Quanta OEM 약함 — graceful 의무 |
| 진행 확인 | M-A4 vault 후 진입 |

---

## Web sources (rule 96 R1-A)

| source | 항목 |
|---|---|
| Quanta QCT 공식 | BMC User Guide |
| GitHub community | Quanta Redfish 사용자 보고 (ODM 영역) |
| DMTF Redfish | DSP0268 표준 (Quanta OEM 약함 — 표준 가까움) |

→ Quanta OEM namespace 변형:
- `Oem.Quanta_Computer_Inc` — 일반 vendor 표기
- `Oem.QCT` — 단축 표기
- ODM 모델 (Microsoft Olympus / Open Compute Project) 은 customer-specific 변형

---

## 구현

### 1. collect_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/quanta/collect_oem.yml
# Quanta QCT BMC OEM 수집 — Oem.Quanta_Computer_Inc 또는 Oem.QCT namespace
#
# source: Quanta QCT 공식 + GitHub community (확인 2026-05-07)
# Fragment 철학 (rule 22)
# lab: 부재 (사용자 명시 2026-05-01)

- name: "Quanta OEM — System / Chassis OEM data 수집"
  block:
    - name: "Quanta OEM — System Oem.Quanta_Computer_Inc / Oem.QCT fallback"
      ansible.builtin.set_fact:
        _quanta_oem_system: >-
          {{
            (_rf_raw_collect.systems[0].Oem.Quanta_Computer_Inc | default(_rf_raw_collect.systems[0].Oem.QCT | default({})))
          }}

    - name: "Quanta OEM — Chassis 동일 fallback"
      ansible.builtin.set_fact:
        _quanta_oem_chassis: >-
          {{
            (_rf_raw_collect.chassis[0].Oem.Quanta_Computer_Inc | default(_rf_raw_collect.chassis[0].Oem.QCT | default({})))
          }}
  rescue:
    - name: "Quanta OEM — 영역 부재 (정상 — Quanta OEM 약함)"
      ansible.builtin.set_fact:
        _quanta_oem_system: {}
        _quanta_oem_chassis: {}
        _quanta_oem_errors: []  # graceful — Quanta OEM 부재는 정상
```

### 2. normalize_oem.yml

```yaml
---
- name: "Quanta OEM — fragment 생성"
  ansible.builtin.set_fact:
    _data_fragment:
      bmc:
        oem_quanta:
          system_info: "{{ _quanta_oem_system | default(omit) }}"
          chassis_info: "{{ _quanta_oem_chassis | default(omit) }}"
    _sections_supported_fragment: ["bmc"]
    _sections_collected_fragment: "{{ ['bmc'] if (_quanta_oem_system or _quanta_oem_chassis) else [] }}"
    _sections_failed_fragment: []
    _errors_fragment: []

- name: "Quanta OEM — fragment 누적 병합"
  ansible.builtin.include_tasks: "{{ playbook_dir }}/common/tasks/normalize/merge_fragment.yml"
```

---

## 회귀 / 검증

- [ ] `ansible-playbook --syntax-check` 통과
- [ ] `validate-fragment-philosophy` skill 통과
- [ ] Oem.Quanta_Computer_Inc / Oem.QCT fallback 분기 검증

## risk

- (MED) ODM 모델 customer-specific OEM (Microsoft Azure / Meta) — 별도 분기 가능. lab 도입 시 보정
- (LOW) Quanta OEM 약함 — rescue block graceful 충분

## 완료 조건

- [ ] redfish-gather/tasks/vendors/quanta/ 디렉터리 신설
- [ ] collect_oem.yml + normalize_oem.yml
- [ ] commit: `feat: [M-F1 DONE] Quanta OEM tasks 신설 — Oem.Quanta_Computer_Inc / QCT fallback`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W3 → M-F2 (Quanta mock).

## 관련

- M-A4 (Quanta vault), M-J1, rule 22, rule 96 R1-A
- 정본: `redfish-gather/tasks/vendors/supermicro/collect_oem.yml`
