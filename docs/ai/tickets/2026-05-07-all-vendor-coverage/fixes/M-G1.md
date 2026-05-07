# M-G1 — redfish-gather/tasks/vendors/hpe/collect_oem.yml — Superdome Flex 분기 보강

> status: [PENDING] | depends: — | priority: P1 | worker: W3 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Superdome Flex (Gen 1/2 + 280 series) OEM 분기 보강." (cycle 진입 — cycle 2026-05-06 M-E2 adapter 신설 후 후속)

cycle 2026-05-06 에 `hpe_superdome_flex.yml` adapter (priority=95) 신설됨. 본 ticket 에서 HPE OEM tasks (`redfish-gather/tasks/vendors/hpe/collect_oem.yml`) 안에 Superdome Flex 분기 추가 (Additive — iLO 시리즈 영역 변경 0).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/vendors/hpe/collect_oem.yml`, `normalize_oem.yml` (보강 — Superdome 분기 추가) |
| 영향 vendor | HPE Superdome Flex (lab 부재) — iLO 시리즈는 변경 0 |
| 함께 바뀔 것 | M-G2 mock fixture |
| 리스크 top 3 | (1) Superdome OEM 영역이 iLO OEM 과 다름 (Partition / FlexNode 정보) / (2) Additive 위반 시 iLO 영향 / (3) Gen 1 / Gen 2 / 280 분기 |
| 진행 확인 | HPE vault 이미 존재 — cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| source | 항목 | URL |
|---|---|---|
| HPE 공식 | Superdome Flex 매뉴얼 | `https://support.hpe.com/hpesc/public/docDisplay?docId=...` |
| HPE 공식 | Flex 280 series | (Gen 1/2 별도 URL) |
| HPE 공식 | iLO 5/6/7 + Superdome 통합 매뉴얼 | (Oem.Hpe namespace 공통) |

→ Superdome Flex 의 OEM 영역 특이점:
- `Oem.Hpe.PartitionInfo` — 파티션 분할 정보 (mission-critical)
- `Oem.Hpe.FlexNodeInfo` — Flex Node 구성 정보
- `Oem.Hpe.GlobalConfiguration` — Superdome 전역 설정
- 일반 iLO Oem.Hpe 영역과 분리 — 모델별 분기 의무

---

## 구현 (collect_oem.yml + normalize_oem.yml 보강)

### 1. collect_oem.yml — Superdome 분기 추가

기존 HPE OEM 수집 안에 다음 분기 추가:

```yaml
# 기존 iLO 시리즈 OEM 수집 (변경 0 — Additive)
# ...

# Superdome Flex 분기 (cycle 2026-05-07 M-G1)
- name: "HPE OEM — Superdome Flex 분기 (model_patterns 매칭 시)"
  block:
    - name: "Superdome — PartitionInfo 추출"
      ansible.builtin.set_fact:
        _hpe_superdome_partition: "{{ (_rf_raw_collect.systems[0].Oem.Hpe.PartitionInfo | default({})) }}"

    - name: "Superdome — FlexNodeInfo 추출"
      ansible.builtin.set_fact:
        _hpe_superdome_flex_node: "{{ (_rf_raw_collect.chassis[0].Oem.Hpe.FlexNodeInfo | default({})) }}"

    - name: "Superdome — GlobalConfiguration 추출"
      ansible.builtin.set_fact:
        _hpe_superdome_global: "{{ (_rf_raw_collect.systems[0].Oem.Hpe.GlobalConfiguration | default({})) }}"
  rescue:
    - name: "Superdome — OEM 영역 부재 (정상 — Superdome 가 아닌 경우)"
      ansible.builtin.set_fact:
        _hpe_superdome_partition: {}
        _hpe_superdome_flex_node: {}
        _hpe_superdome_global: {}
  when:
    - "(_rf_detected_model | default('')) | regex_search('Superdome|Flex')"
```

### 2. normalize_oem.yml — Superdome fragment 추가

기존 HPE iLO 시리즈 fragment 와 분리 (Additive):

```yaml
# 기존 iLO 시리즈 fragment (변경 0)
# ...

# Superdome Flex fragment 추가 (cycle 2026-05-07 M-G1)
- name: "Superdome Flex — fragment 추가"
  ansible.builtin.set_fact:
    _data_fragment:
      bmc:
        oem_hpe_superdome:
          partition: "{{ _hpe_superdome_partition | default(omit) }}"
          flex_node: "{{ _hpe_superdome_flex_node | default(omit) }}"
          global: "{{ _hpe_superdome_global | default(omit) }}"
  when:
    - "(_rf_detected_model | default('')) | regex_search('Superdome|Flex')"
    - _hpe_superdome_partition or _hpe_superdome_flex_node or _hpe_superdome_global
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `validate-fragment-philosophy` skill 통과 (Superdome fragment 가 HPE iLO fragment 침범 0)
- [ ] iLO 시리즈 OEM 수집 로직 변경 0 (Additive 검증 — git diff)

### Additive only (rule 92 R2)

- [ ] HPE iLO5/6/7 사이트 검증 영역 영향 0 (사이트 PASS HPE iLO7 envelope 변경 0)
- [ ] Superdome 분기는 model_patterns 매칭 시만 동작 (when 조건)

### 동적 검증 (mock 기반)

- [ ] M-G2 Superdome mock fixture 응답 → _hpe_superdome_partition / flex_node / global 추출
- [ ] iLO 시리즈 mock fixture (사이트 검증 iLO7) → Superdome 분기 skip (when 조건 미매칭)

---

## risk

- (MED) Superdome model_patterns 매칭 정확성 — `Superdome` / `Flex` 정규식이 다른 HPE 모델과 충돌 가능성. when 조건 검증
- (LOW) Gen 1 vs Gen 2 vs 280 응답 차이 — 본 ticket 은 generic Superdome OEM 만. 세부 분기는 lab 도입 후

## 완료 조건

- [ ] redfish-gather/tasks/vendors/hpe/collect_oem.yml 보강 (Superdome 분기 추가)
- [ ] redfish-gather/tasks/vendors/hpe/normalize_oem.yml 보강 (Superdome fragment 추가)
- [ ] iLO 시리즈 영역 변경 0 (Additive 검증)
- [ ] commit: `feat: [M-G1 DONE] HPE OEM tasks Superdome Flex 분기 보강 — Partition / FlexNode / Global`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W3 → M-G2 (Superdome mock).

## 관련

- adapters/redfish/hpe_superdome_flex.yml (cycle 2026-05-06 M-E2)
- M-G2 (Superdome mock)
- rule 22 (Fragment 철학)
- rule 92 R2 (Additive only)
- rule 96 R1-A (web sources)
