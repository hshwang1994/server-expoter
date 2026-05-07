# M-C2 — redfish-gather/tasks/vendors/huawei/{collect_oem.yml, normalize_oem.yml} 신설

> status: [PENDING] | depends: M-C1 | priority: P1 | worker: W2 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Huawei iBMC OEM tasks 신설 — Oem.Huawei namespace 처리." (cycle 진입 영역 J 와 일부 중복)

현재 vendor OEM tasks 4 vendor (Dell/HPE/Lenovo/Supermicro) 만 존재. Huawei OEM tasks 신설.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/vendors/huawei/collect_oem.yml` (신설), `normalize_oem.yml` (신설) |
| 영향 vendor | Huawei iBMC (lab 부재) |
| 함께 바뀔 것 | M-C1 adapter 의 oem_tasks 경로 dep 통과, M-J1 OEM mapping |
| 리스크 top 3 | (1) Oem.Huawei namespace 응답 형식 정확성 (web sources 검증) / (2) iBMC 1.x 의 OEM 약함 — graceful degradation / (3) Fragment 철학 (rule 22) — 자기 fragment 만 작성 |
| 진행 확인 | M-C1 adapter 갱신 후 진입 |

---

## Web sources (rule 96 R1-A)

| source | 항목 |
|---|---|
| Huawei 공식 | iBMC Redfish API guide — Oem.Huawei 절 |
| 영역 | Manufacturer info / Health / Boards / Firmware extra |

→ Oem.Huawei 주요 sub-namespace (web sources 기반):
- `Oem.Huawei.SystemInfo` — 시스템 추가 정보 (Health 상세)
- `Oem.Huawei.NetworkBindings` — NIC bonding 정보
- `Oem.Huawei.BoardInfo` — 메인보드 / 백플레인 정보
- `Oem.Huawei.SmartProvisioning` — Provisioning 상태

---

## 구현 (collect_oem.yml + normalize_oem.yml — Dell/HPE 패턴 따름)

### 1. collect_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/huawei/collect_oem.yml
# Huawei iBMC OEM 데이터 수집 — Oem.Huawei namespace
#
# source: Huawei iBMC Redfish API guide (확인 2026-05-07)
# Fragment 철학 (rule 22) — 자기 fragment 만, 다른 gather 침범 금지
# lab: 부재 — mock fixture 기반 (M-C3)

- name: "Huawei OEM — System OEM data 수집 (best-effort)"
  block:
    - name: "Huawei OEM — Systems index 의 Oem.Huawei 영역 수집 (이미 _rf_raw_collect 안에 있음)"
      ansible.builtin.set_fact:
        _huawei_oem_system: "{{ (_rf_raw_collect.systems[0].Oem.Huawei | default({})) }}"

    - name: "Huawei OEM — Chassis Oem.Huawei.BoardInfo 추출"
      ansible.builtin.set_fact:
        _huawei_oem_board: "{{ (_rf_raw_collect.chassis[0].Oem.Huawei.BoardInfo | default({})) }}"
  rescue:
    - name: "Huawei OEM — 일부 endpoint 미지원 (iBMC 1.x 시 정상)"
      ansible.builtin.set_fact:
        _huawei_oem_system: {}
        _huawei_oem_board: {}
        _huawei_oem_errors:
          - section: bmc
            message: "Huawei OEM 영역 일부 미수집 (iBMC 1.x 가능성)"
            severity: warning
```

### 2. normalize_oem.yml

```yaml
---
# redfish-gather/tasks/vendors/huawei/normalize_oem.yml
# Huawei OEM 정규화 — fragment 형식
#
# Fragment 변수 (rule 22 R1+R7+R8) — 자기 fragment 만:
#   _data_fragment, _sections_supported_fragment, _sections_collected_fragment,
#   _sections_failed_fragment, _errors_fragment

- name: "Huawei OEM — fragment 생성"
  ansible.builtin.set_fact:
    _data_fragment:
      bmc:
        oem_huawei:
          system_health: "{{ _huawei_oem_system.SystemHealth | default(omit) }}"
          board_serial: "{{ _huawei_oem_board.BoardSerialNumber | default(omit) }}"
          provisioning: "{{ _huawei_oem_system.SmartProvisioning | default(omit) }}"
    _sections_supported_fragment: ["bmc"]
    _sections_collected_fragment: "{{ ['bmc'] if (_huawei_oem_system or _huawei_oem_board) else [] }}"
    _sections_failed_fragment: "{{ [] if (_huawei_oem_system or _huawei_oem_board) else ['bmc'] }}"
    _errors_fragment: "{{ _huawei_oem_errors | default([]) }}"

- name: "Huawei OEM — fragment 누적 병합"
  ansible.builtin.include_tasks: "{{ playbook_dir }}/common/tasks/normalize/merge_fragment.yml"
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `validate-fragment-philosophy` skill 통과 (rule 22 R1~R9)
- [ ] yamllint 통과
- [ ] `verify_vendor_boundary.py` 통과 — Huawei vendor 분기는 OEM tasks 영역 (rule 12 R1 Allowed)

### Fragment 철학 (rule 22) 검증

- [ ] 자기 fragment 만 (`_data_fragment.bmc.oem_huawei` — 다른 섹션 침범 0)
- [ ] 5 fragment 변수 모두 명시 (rule 22 R7)
- [ ] `merge_fragment.yml` 호출 (rule 22 R3)
- [ ] 누적 변수 (`_collected_data` 등) 직접 수정 0 (rule 22 R1)

### 동적 검증 (mock 기반)

- [ ] M-C3 mock fixture 의 Oem.Huawei 영역 응답 → _data_fragment.bmc.oem_huawei 정확히 추출
- [ ] iBMC 1.x mock (OEM 약함) → rescue block 동작 → _huawei_oem_errors 에 warning 등재

---

## risk

- (MED) Oem.Huawei sub-namespace 응답 형식 펌웨어 별 차이 — web sources 기반 가정. 사이트 도입 시 보정
- (LOW) iBMC 1.x 의 일부 펌웨어는 Oem.Huawei 영역 자체 부재 — rescue block 으로 graceful

## 완료 조건

- [ ] redfish-gather/tasks/vendors/huawei/ 디렉터리 신설
- [ ] collect_oem.yml + normalize_oem.yml 작성 (위 본문)
- [ ] Fragment 철학 검증 통과
- [ ] commit: `feat: [M-C2 DONE] Huawei OEM tasks 신설 — Oem.Huawei namespace 처리`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W2 → M-C3 (Huawei mock fixture).

## 관련

- M-C1 (Huawei adapter)
- M-J1 (OEM mapping)
- rule 22 (Fragment 철학)
- rule 96 R1-A (web sources)
- 정본: `redfish-gather/tasks/vendors/dell/collect_oem.yml` (패턴 reference)
