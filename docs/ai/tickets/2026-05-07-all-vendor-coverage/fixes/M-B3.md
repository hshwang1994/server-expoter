# M-B3 — Supermicro AMD (H11~H14) + ARM (ARS) 변형 model_patterns 확장

> status: [PENDING] | depends: M-B2 | priority: P2 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Supermicro 의 H11/H12/H13/H14 (AMD) + ARS (ARM) 변형도 코드 path 깔자."

Supermicro 는 Intel platform (X9~X14) 외 AMD platform (H11~H14) + ARM platform (ARS) 운영. 본 ticket 에서 model_patterns 확장 (Additive — 기존 priority 변경 0).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/supermicro_x11.yml`, `supermicro_x12.yml`, `supermicro_x13.yml`, `supermicro_x14.yml` (H 시리즈 model_patterns 추가) + 신규 `adapters/redfish/supermicro_ars.yml` (ARM, 선택적) |
| 영향 vendor | Supermicro (lab 부재) |
| 함께 바뀔 것 | M-B4 mock fixture (H 시리즈 + ARS 응답) |
| 리스크 top 3 | (1) AMD platform Redfish 응답 형식 차이 (Intel vs AMD) / (2) ARM platform 별 BMC 펌웨어 차이 / (3) model_patterns 정확성 — H1*A vs H1*B 같은 변형 누락 가능 |
| 진행 확인 | M-B2 capability 정합 후 진입 |

---

## Web sources (rule 96 R1-A)

| platform | source | 확인일 |
|---|---|---|
| H11 (AMD EPYC Naples 1세대) | `https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_H11.pdf` | 2026-05-07 |
| H12 (AMD EPYC Rome/Milan) | `https://www.supermicro.com/manuals/superserver/IPMI/H12_BMC_RedfishRefGuide.pdf` | 2026-05-07 |
| H13 (AMD EPYC Genoa) | `https://www.supermicro.com/manuals/superserver/H13/H13_BMC_RedfishRefGuide.pdf` | 2026-05-07 |
| H14 (AMD EPYC 신세대) | 확인 필요 (출시 가까움) | — |
| ARS (ARM Ampere Altra / Cobalt) | `https://www.supermicro.com/manuals/superserver/ARS/` | 확인 필요 |

→ AMD platform 의 BMC 펌웨어는 Intel 동세대 platform 과 거의 동일 (BMC 펌웨어 공통). Redfish 응답 차이는 Processor 영역만 (Manufacturer="AMD" 표시 + cpu features 차이). Storage / Power / Network 등 다른 section 은 Intel 동세대 와 동일.

---

## 구현 절차

### 1. X11~X14 adapter model_patterns 확장 (Additive)

각 adapter 의 `match.model_patterns` 에 H 시리즈 추가:

```yaml
# adapters/redfish/supermicro_x11.yml (또는 X12/X13/X14 동일 패턴)
match:
  manufacturer: ["Supermicro", "Super Micro Computer, Inc.", "Super Micro Computer", "SMCI"]
  model_patterns:
    # 기존 Intel platform (변경 0)
    - "X11*"
    # AMD platform 추가 (cycle 2026-05-07 M-B3)
    - "H11*"
```

X12 → H12 추가 / X13 → H13 추가 / X14 → H14 추가.

### 2. supermicro_ars.yml 신설 (ARM platform — 선택적)

ARM platform 은 Intel/AMD 와 분기 큼 (Processor architecture 다름). 별도 adapter 신설:

```yaml
---
# adapters/redfish/supermicro_ars.yml
# Supermicro ARM platform (Ampere Altra / Microsoft Cobalt 100) BMC adapter
#
# source: https://www.supermicro.com/manuals/superserver/ARS/ (확인 필요)
# lab: 부재 (사용자 명시 2026-05-07 Q2)

priority: 80
specificity: 50

match:
  manufacturer: ["Supermicro", "Super Micro Computer, Inc.", "Super Micro Computer", "SMCI"]
  model_patterns:
    - "ARS*"          # ARS-211 / ARS-221 등 ARM Server platform
    - "*Altra*"       # Ampere Altra 모델
    - "*Cobalt*"      # Microsoft Cobalt 100 모델

capabilities:
  redfish_version: "1.10+"           # ARM platform 은 최신 BMC 펌웨어
  power_subsystem: true              # PowerSubsystem 지원
  storage_strategy: "standard"
  oem_strategy: "weak"
  cpu_architecture: "arm64"          # ARM 표시 — Processor 영역에서 Manufacturer 가 "Ampere" 또는 "Microsoft" 로 응답

collect:
  strategy: standard_only
  systems_path: "/redfish/v1/Systems"
  chassis_path: "/redfish/v1/Chassis"
  managers_path: "/redfish/v1/Managers"

normalize:
  bmc_name: "BMC"
  vendor_namespace: "Oem.Supermicro"

metadata:
  vendor: supermicro
  generation: ars
  generation_year: "2023+"
  redfish_introduction: "DSP0268 v1.10+"
  origin: "https://www.supermicro.com/manuals/superserver/ARS/"
  lab_status: "부재 — 사용자 명시 2026-05-07 Q2"
  next_action: "lab 도입 후 별도 cycle — ARM Processor 영역 capability 보정"
```

### 3. adapter score 일관성

ARS priority=80 — X11 (80) 와 동률. 단 ARS 는 model_patterns 다름 (`ARS*` / `*Altra*` / `*Cobalt*`). 동시 매칭 가능성 0.

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `verify_harness_consistency.py` 통과 (adapter 카운트 29 → 30, ARS 신설 시)
- [ ] `verify_vendor_boundary.py` 통과
- [ ] X11~X14 adapter 의 model_patterns 에 H 시리즈 추가 확인 (Additive — 기존 Intel patterns 변경 0)

### adapter score 매칭

```bash
python scripts/ai/score-adapter-match.py --vendor supermicro --model "H12DSU-iN+"
# 예상: supermicro_x12.yml (priority=90) 선택 — H 시리즈 X12 와 동등 BMC

python scripts/ai/score-adapter-match.py --vendor supermicro --model "ARS-221-NEL"
# 예상: supermicro_ars.yml (priority=80) 선택
```

### Additive only

- [ ] X11~X14 의 priority 변경 0
- [ ] capabilities 변경 0 (model_patterns 만 추가)

---

## risk

- (MED) AMD platform 의 Redfish Processor 영역 응답 차이 — Manufacturer="AMD" / cpu features list 다름. M-I5 (system/cpu/mem/users) 에서 AMD vs Intel 분기 처리 검토
- (LOW) ARS platform 의 BMC 펌웨어 다양 — Ampere Altra 와 Microsoft Cobalt 차이 가능. ARS 도입 시 model_patterns 추가 분기 가능

## 완료 조건

- [ ] X11~X14 adapter 의 `match.model_patterns` 에 H11~H14 추가 (Additive)
- [ ] (선택) supermicro_ars.yml 신설
- [ ] adapter score 매칭 검증 (H 시리즈 → 동세대 X 시리즈 adapter 선택)
- [ ] commit: `feat: [M-B3 DONE] Supermicro AMD (H11~H14) model_patterns 추가 + ARM (ARS) adapter 신설`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 → M-B4 (mock fixture).

## 관련

- M-B1, M-B2 (Supermicro generation 매트릭스)
- M-I5 (system/cpu/mem/users — AMD vs Intel 분기)
- rule 12 R2 (priority 일관성)
- rule 96 R1-A (web sources)
