# M-I5 — system / cpu / memory / users (표준 가까움) gap 검증

> status: [PENDING] | depends: M-I4 | priority: P2 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "system / cpu / memory / users — 표준 가까움 (effort 작음, gap 검증만)." (cycle 진입)

위 4 sections 은 DMTF Redfish 표준 path 우선 — vendor 별 변형 작음. 본 ticket 은 gap 검증 + AMD/ARM 변형 (Processor) 만.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (Processor 영역 AMD/ARM 분기 — 약함) + 검증 |
| 영향 vendor | 9 vendor — 표준 path 우선이라 영향 작음 |
| 함께 바뀔 것 | M-J1 OEM mapping (Processor.Oem.<vendor> 영역 일부) |
| 리스크 top 3 | (1) Processor.Manufacturer="AMD" / "Intel" / "Ampere" / "Microsoft" 분기 / (2) Memory 응답 형식 vendor 별 차이 (DIMM Slot 정보) / (3) AccountService 응답 형식 (RoleId enum 변형) |
| 진행 확인 | M-I4 후 진입 |

---

## gap 매트릭스 (4 sections)

### system section (`/Systems/{id}`)

표준 가까움. vendor 별 차이:
- ProcessorSummary / MemorySummary / Status — 표준
- Oem.<vendor>.SystemInfo — vendor 별 추가 정보 (M-I3 bmc 와 일부 중복)

→ 본 ticket 은 변경 없음. M-I3 OEM namespace 매핑으로 처리.

### cpu section (`/Systems/{id}/Processors/{id}`)

표준 가까움. 변형:
- Manufacturer = "Intel" / "AMD" / "Ampere" / "Microsoft Corporation" / "Marvell"
- ProcessorArchitecture = "x86_64" / "arm64" / "Power"
- InstructionSet = "x86-64" / "ARM-A64" / "MIPS"

→ Additive — Processor 응답 그대로 사용. 추가 분기 불필요.

### memory section (`/Systems/{id}/Memory/{id}`)

표준 가까움. 변형:
- DIMM 위치 정보 (Location.PartLocation.ServiceLabel) — vendor 별 라벨링 차이 (Dell "DIMM_A1" / HPE "P1-DIMM-A1" / Lenovo "DIMM 1")
- DIMM Type (DDR4 / DDR5 / LPDDR5) — 표준

→ 본 ticket 은 라벨링 변형 정규화 검토 (Additive — 추가 정규화 함수만).

### users section (`/AccountService/Accounts`)

표준 가까움. 변형:
- RoleId enum 차이 (Administrator / Operator / ReadOnly / Custom roles)
- vendor 별 default role:
  - Dell: Administrator / Operator / ReadOnly / None
  - HPE: Administrator / Operator / ReadOnly / VirtualMedia 등
  - Lenovo: Administrator / Operator / ReadOnly / Supervisor
  - Cisco: admin / readonly / user
  - Supermicro: Administrator / Operator / User / Callback
  - Huawei: Administrator / Operator / CommonUser
  - Fujitsu: Administrator / Operator
- enum 정규화 의무 (이미 cycle 2026-04-30 phase4 에서 일부 처리)

→ Additive — RoleId enum 매트릭스 매핑 추가 (`adapter_common.py` 또는 `field_mapper.py` 안).

---

## 구현 (Additive 보강)

### 1. Memory DIMM 라벨링 정규화 (선택적 — gap 발견 시만)

```python
# redfish_gather.py 또는 module_utils/adapter_common.py 안 (Additive)
def _normalize_dimm_label(raw_label, vendor):
    """DIMM ServiceLabel vendor 별 정규화 — 'DIMM A1' 형식 통일.

    Examples:
        "DIMM_A1" (Dell) → "DIMM A1"
        "P1-DIMM-A1" (HPE) → "DIMM A1"
        "DIMM 1" (Lenovo) → "DIMM 1"  # 위치 정보 보존
        "CPU0_DIMM_A1" (Supermicro) → "CPU0 DIMM A1"
    """
    # 기존 표준 응답 보존 (Additive — 정규화는 추가 필드)
    return {
        "raw": raw_label,
        "normalized": _apply_normalization(raw_label, vendor),
    }
```

### 2. RoleId enum 매트릭스 (이미 cycle 2026-04-30 부분 처리)

```yaml
# common/vars/role_id_normalization.yml (cycle 2026-04-30 phase4 에 이미 있음 — 본 ticket 검증만)
role_id_aliases:
  administrator:
    - "Administrator"
    - "admin"
    - "Supervisor"   # Lenovo
    - "ADMINISTRATOR"
  operator:
    - "Operator"
    - "operator"
    - "User"         # Supermicro
  readonly:
    - "ReadOnly"
    - "readonly"
    - "CommonUser"   # Huawei
    - "Callback"     # Supermicro (read-only)
```

본 ticket 은 검증만 — cycle 2026-04-30 의 정규화가 9 vendor 모두 cover 하는지 확인 + 누락 vendor (Fujitsu / Quanta) 추가.

---

## 회귀 / 검증

### 정적 검증

- [ ] `python -m py_compile` 통과
- [ ] RoleId enum 매트릭스 9 vendor cover 검증

### Additive only

- [ ] 기존 cpu / memory / users / system fragment 변경 0
- [ ] 사이트 검증 4 vendor envelope shape 변경 0

### 동적 검증

- [ ] AMD/ARM Processor mock 응답 → cpu fragment 정규 추출 (Manufacturer / ProcessorArchitecture 분기)
- [ ] DIMM 라벨링 정규화 (vendor 별 mock fixture)
- [ ] RoleId enum 정규화 (Fujitsu / Quanta 누락 시 추가)

---

## risk

- (LOW) cpu / memory / system 영역은 표준 가까움 — 변경 거의 없음. 검증만
- (LOW) RoleId enum 누락 vendor — 사이트 도입 시 발견 가능. 본 ticket 에서 web sources 기반 보강

## 완료 조건

- [ ] cpu / memory / system / users 표준 path 검증 — 9 vendor 모두 표준 응답으로 cover 확인
- [ ] (선택) DIMM 라벨링 정규화 보강
- [ ] RoleId enum 매트릭스 9 vendor 보강 (Fujitsu / Quanta 누락 검증)
- [ ] 사이트 검증 4 vendor envelope shape 변경 0
- [ ] commit: `feat: [M-I5 DONE] system/cpu/memory/users gap 검증 + RoleId enum 9 vendor 보강`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-J1 (OEM namespace mapping + Cisco vendor task 신설).

## 관련

- M-I3 (bmc OEM namespace mapping)
- M-J1 (OEM namespace 매트릭스)
- rule 92 R2 (Additive)
- 정본: cycle 2026-04-30 phase4 RoleId 정규화
