# M-D1 — redfish-gather/tasks/vendors/inspur/{collect_oem.yml, normalize_oem.yml} 신설

> status: [PENDING] | depends: M-A2 | priority: P1 | worker: W2 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Inspur ISBMC OEM tasks 신설 — Oem.Inspur namespace 처리." (cycle 진입)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/vendors/inspur/collect_oem.yml` (신설), `normalize_oem.yml` (신설) |
| 영향 vendor | Inspur ISBMC (lab 부재) |
| 함께 바뀔 것 | M-D2 mock fixture, M-J1 OEM mapping |
| 리스크 top 3 | (1) Oem.Inspur namespace 정확성 (web sources 약함) / (2) ISBMC vs iBMC (Inspur 내부 분기) / (3) NF/NP/SA series 분기 |
| 진행 확인 | M-A2 vault 신설 후 진입 |

---

## Web sources (rule 96 R1-A)

| source | 항목 |
|---|---|
| Inspur 공식 | NF/NP/SA series Redfish API guide (영문 docs 약함 — community 보강) |
| GitHub community | Inspur Redfish 사용자 보고 (DMTF 영역) |
| DMTF Redfish | DSP0268 표준 영역 (Inspur OEM 약함 — 표준 가까움) |

→ Inspur 의 OEM 영역은 다른 vendor (Dell/HPE) 보다 약함. 표준 Redfish path 우선 + Oem.Inspur sub-namespace 일부:
- `Oem.Inspur.SystemInfo` — 시스템 추가 정보 (CPLD / BIOS 별도)
- `Oem.Inspur.NetworkInfo` — NIC 추가 정보
- `Oem.Inspur_System` — 일부 펌웨어 사용 (`Inspur_System` underscore 변형)

---

## 구현 (collect_oem.yml + normalize_oem.yml)

### 1. collect_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/inspur/collect_oem.yml
# Inspur ISBMC OEM 수집 — Oem.Inspur 또는 Oem.Inspur_System namespace
#
# source: Inspur 공식 매뉴얼 + GitHub community (확인 2026-05-07)
# Fragment 철학 (rule 22) — 자기 fragment 만
# lab: 부재 (cycle 2026-05-01 명시)

- name: "Inspur OEM — System / Chassis OEM data 수집 (best-effort)"
  block:
    - name: "Inspur OEM — System Oem.Inspur 영역"
      ansible.builtin.set_fact:
        _inspur_oem_system: "{{ (_rf_raw_collect.systems[0].Oem.Inspur | default(_rf_raw_collect.systems[0].Oem.Inspur_System | default({}))) }}"

    - name: "Inspur OEM — Chassis Oem.Inspur 영역"
      ansible.builtin.set_fact:
        _inspur_oem_chassis: "{{ (_rf_raw_collect.chassis[0].Oem.Inspur | default(_rf_raw_collect.chassis[0].Oem.Inspur_System | default({}))) }}"
  rescue:
    - name: "Inspur OEM — 영역 부재 (정상 — Inspur OEM 약함)"
      ansible.builtin.set_fact:
        _inspur_oem_system: {}
        _inspur_oem_chassis: {}
        _inspur_oem_errors: []  # graceful — Inspur 는 OEM 약함이 정상
```

### 2. normalize_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/inspur/normalize_oem.yml
# Inspur OEM 정규화 — fragment 형식

- name: "Inspur OEM — fragment 생성"
  ansible.builtin.set_fact:
    _data_fragment:
      bmc:
        oem_inspur:
          system_info: "{{ _inspur_oem_system | default(omit) }}"
          chassis_info: "{{ _inspur_oem_chassis | default(omit) }}"
    _sections_supported_fragment: ["bmc"]
    _sections_collected_fragment: "{{ ['bmc'] if (_inspur_oem_system or _inspur_oem_chassis) else [] }}"
    _sections_failed_fragment: []  # Inspur OEM 부재는 정상 — fail 아님
    _errors_fragment: []

- name: "Inspur OEM — fragment 누적 병합"
  ansible.builtin.include_tasks: "{{ playbook_dir }}/common/tasks/normalize/merge_fragment.yml"
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `validate-fragment-philosophy` skill 통과
- [ ] `verify_vendor_boundary.py` 통과 — Inspur 분기는 OEM tasks 영역 (rule 12 R1 Allowed)

### Fragment 철학 검증 (rule 22)

- [ ] 자기 fragment 만 (`_data_fragment.bmc.oem_inspur` 만)
- [ ] 5 fragment 변수 모두 명시
- [ ] merge_fragment.yml 호출

### Inspur 분기 (Oem.Inspur vs Oem.Inspur_System)

- [ ] 두 namespace 모두 fallback 처리 — `Oem.Inspur` 우선, 부재 시 `Oem.Inspur_System` fallback

---

## risk

- (MED) Inspur OEM namespace 변형 (Oem.Inspur vs Oem.Inspur_System) — 펌웨어 별 차이. 두 fallback 처리로 cover
- (LOW) Inspur 영문 docs 약함 — web sources 가용성 낮음. lab 도입 시 보정

## 완료 조건

- [ ] redfish-gather/tasks/vendors/inspur/ 디렉터리 신설
- [ ] collect_oem.yml + normalize_oem.yml 작성
- [ ] Fragment 철학 검증 통과
- [ ] commit: `feat: [M-D1 DONE] Inspur OEM tasks 신설 — Oem.Inspur / Inspur_System fallback`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W2 → M-D2 (Inspur mock fixture).

## 관련

- M-A2 (Inspur vault — dep)
- M-J1 (OEM mapping)
- rule 22 (Fragment 철학)
- 정본: `redfish-gather/tasks/vendors/dell/collect_oem.yml`
