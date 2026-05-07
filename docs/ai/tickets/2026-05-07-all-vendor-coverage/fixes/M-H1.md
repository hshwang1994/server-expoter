# M-H1 — Dell 미검증 generation (idrac legacy / iDRAC8 / iDRAC9) 보강

> status: [PENDING] | depends: — | priority: P1 | worker: W4 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "사이트 검증 안 된 generation 도 코드 path 깔자. lab 한계는 web sources로." (cycle 진입)

Dell 사이트 검증: iDRAC10 만. iDRAC (legacy) / iDRAC8 / iDRAC9 미검증 — capability 정합 + origin 주석 + mock fixture 보강.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/dell_idrac.yml`, `dell_idrac8.yml`, `dell_idrac9.yml` (origin + capability 보강), `tests/fixtures/redfish/dell_idrac/`, `dell_idrac8/`, `dell_idrac9/` (mock 디렉터리 신설) |
| 영향 vendor | Dell (lab 부재 — iDRAC10 외 generation) |
| 함께 바뀔 것 | M-I1, M-I2 (storage / power 변형 매트릭스 입력) |
| 리스크 top 3 | (1) iDRAC8 / 9 펌웨어 다양 (4.x ~ 7.x) — capability 분기 정확성 / (2) Additive 위반 시 iDRAC10 사이트 검증 영향 / (3) iDRAC (legacy) 응답 약함 — graceful 의무 |
| 진행 확인 | Dell vault 이미 존재 — cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| generation | URL | 펌웨어 매트릭스 |
|---|---|---|
| iDRAC (legacy) | `https://developer.dell.com/apis/2978/versions/1/docs/` (iDRAC7) | iDRAC7 1.x ~ 2.x (legacy) |
| iDRAC8 | `https://developer.dell.com/apis/2978/versions/2/docs/` | iDRAC8 2.x ~ 4.x |
| iDRAC9 | `https://developer.dell.com/apis/2978/versions/3/docs/` | iDRAC9 3.x ~ 7.x (Storage strategy 변동 큼) |
| iDRAC10 | (사이트 검증 — out of scope) | iDRAC10 6.x+ |

→ Dell iDRAC9 펌웨어 매트릭스 (Storage strategy):
- iDRAC9 3.x ~ 4.x: standard storage path
- iDRAC9 5.x+: PLDM RDE 우선 + standard fallback
- iDRAC9 6.x+: PLDM RDE only
- iDRAC10 (사이트 PASS): PLDM RDE only

→ iDRAC10 path 변경 0 (rule 92 R2 Additive). iDRAC9 5.x 이전 standard storage path fallback.

---

## 구현

### 1. dell_idrac.yml (legacy iDRAC7) origin 보강

```yaml
metadata:
  vendor: dell
  generation: idrac_legacy
  generation_year: "2010-2014"
  redfish_introduction: "DSP0268 v1.0+ (iDRAC7 1.30+ partial)"
  origin: "https://developer.dell.com/apis/2978/versions/1/docs/"
  lab_status: "부재 — iDRAC10 만 사이트 검증"
  next_action: "lab 도입 후 별도 cycle"
  tested_against: ["iDRAC7 1.30+", "iDRAC7 2.0+"]
  storage_strategy_evolution: "iDRAC7 — SimpleStorage only (Storage path 미지원)"
  power_strategy: "Power deprecated only"
```

### 2. dell_idrac8.yml capability 정합

```yaml
capabilities:
  redfish_version: "1.4+"
  power_subsystem: false
  storage_strategy: "standard"
  oem_strategy: "standard+oem"
  oem_namespace: "Oem.Dell"

metadata:
  vendor: dell
  generation: idrac8
  generation_year: "2014-2018"
  redfish_introduction: "DSP0268 v1.4+"
  origin: "https://developer.dell.com/apis/2978/versions/2/docs/"
  lab_status: "부재"
  tested_against: ["iDRAC8 2.30+", "iDRAC8 2.50+", "iDRAC8 2.70+"]
```

### 3. dell_idrac9.yml capability 정합 + Storage strategy 분기

```yaml
capabilities:
  redfish_version: "1.6+"
  power_subsystem: "conditional"     # iDRAC9 5.x+ 일부 지원
  storage_strategy: "conditional"     # 펌웨어 별 분기 (3.x: standard / 5.x+: PLDM RDE)
  oem_strategy: "standard+oem"
  oem_namespace: "Oem.Dell"

collect:
  storage_strategy: "pldm_rde_with_standard_fallback"   # iDRAC9 6.x+ PLDM RDE / 5.x dual / 3.x-4.x standard
  power_strategy: "subsystem_with_legacy_fallback"

metadata:
  vendor: dell
  generation: idrac9
  generation_year: "2018-2024"
  redfish_introduction: "DSP0268 v1.6+ ~ v1.13+"
  origin: "https://developer.dell.com/apis/2978/versions/3/docs/"
  lab_status: "부재"
  tested_against: ["iDRAC9 3.x", "iDRAC9 4.x", "iDRAC9 5.x", "iDRAC9 6.x", "iDRAC9 7.x"]
  storage_strategy_evolution:
    "3.x-4.x": "standard storage path"
    "5.x": "PLDM RDE 우선 + standard fallback"
    "6.x+": "PLDM RDE only"
```

### 4. mock fixture (3 디렉터리)

```
tests/fixtures/redfish/dell_idrac/   # iDRAC7 legacy
├── service_root.json (RedfishVersion: "1.0.0")
├── systems_1.json (SimpleStorage path 만)
└── ...

tests/fixtures/redfish/dell_idrac8/   # iDRAC8 (2014-2018)
└── ... (standard storage path)

tests/fixtures/redfish/dell_idrac9/   # iDRAC9 — 3 variants (3.x / 5.x / 7.x)
├── dell_idrac9_v3/ (standard storage)
├── dell_idrac9_v5/ (PLDM RDE + standard dual)
└── dell_idrac9_v7/ (PLDM RDE only)
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check` 통과
- [ ] `verify_harness_consistency.py` 통과
- [ ] 각 adapter `metadata.origin` 명시

### Additive only (rule 92 R2)

- [ ] dell_idrac10.yml 변경 0 (사이트 검증 baseline 영향 0)
- [ ] tests/fixtures/redfish/dell_idrac10/ 변경 0

### 동적 검증

- [ ] mock fixture 별로 redfish_gather.py 실행 → adapter 정확히 매칭 (iDRAC9 5.x → dell_idrac9.yml + storage strategy=PLDM RDE 분기)

---

## risk

- (MED) iDRAC9 5.x ~ 6.x 변경점 — Dell 공식 docs 변경 이력 추적 필요. lab 도입 시 보정
- (LOW) iDRAC7 legacy mock — 일부 endpoint 부재 (graceful)

## 완료 조건

- [ ] dell_idrac / dell_idrac8 / dell_idrac9 metadata + capability 보강
- [ ] mock fixture 3 디렉터리 (iDRAC9 는 3 variants — 시간 가용 시)
- [ ] iDRAC10 영향 0 검증
- [ ] commit: `feat: [M-H1 DONE] Dell 미검증 generation (idrac/8/9) capability + origin + mock`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W4 → M-H2 (HPE iLO/4/5/6).

## 관련

- M-I1 (storage 변형 — iDRAC9 매트릭스 입력)
- M-I2 (power 변형)
- rule 92 R2, rule 96 R1-A
