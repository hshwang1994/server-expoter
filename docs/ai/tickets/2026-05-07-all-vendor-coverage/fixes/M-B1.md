# M-B1 — adapters/redfish/supermicro_x10.yml 신설

> status: [PENDING] | depends: M-A6 | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Supermicro X9 / X10 / X11 / X12 / X13 / X14 모든 generation 코드 path 깔자." (2026-05-07 cycle 진입)

현재 Supermicro adapter: BMC / X9 / X11 / X12 / X13 / X14 (6개). **X10 generation adapter 누락**. 본 ticket 에서 X10 신설.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/supermicro_x10.yml` (신설) |
| 영향 vendor | Supermicro X10 generation (lab 부재) |
| 함께 바뀔 것 | adapter_loader 가 X10 모델 매칭 시 본 adapter 선택 |
| 리스크 top 3 | (1) X10 model_patterns 정확성 (web sources 검증) / (2) X9 / X11 priority 동률 위험 / (3) X10 펌웨어 응답 형식 미검증 |
| 진행 확인 | M-A6 vault docs 갱신 후 진입 |

---

## Web sources (rule 96 R1-A 의무)

| source | 항목 | 확인일 |
|---|---|---|
| Supermicro 공식 | X10 BMC User Guide (BMC 펌웨어 1.x ~ 3.x) | 2026-05-07 |
| URL | `https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X10.pdf` | 확인 필요 |
| DMTF Redfish | DSP0268 v1.0 ~ v1.6 (X10 시기 spec) | 2026-05-07 |
| Note | X10 펌웨어 BMC 1.x ~ 3.x — Redfish 부분 지원 (legacy IPMI 우선) |

→ Supermicro X10 generation: 2014~2018 — Redfish 도입 초기 (DSP0268 v1.0 ~ v1.6 수준). 일부 endpoint 미지원 (PowerSubsystem 없음, Storage 는 SimpleStorage 만).

---

## 구현 (adapters/redfish/supermicro_x10.yml)

### 점수 정책 (rule 12 R2 / rule 50 R3)

- priority: **75** (X9 priority=70 < **X10 priority=75** < X11 priority=80)
- specificity: 50 (model_patterns 명시)
- 최종 score = 75 × 1000 + 50 × 10 + match_score

### 본문

```yaml
---
# adapters/redfish/supermicro_x10.yml
# Supermicro X10 generation BMC adapter
#
# source: https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X10.pdf (확인 2026-05-07)
# source: https://redfish.dmtf.org/schemas/v1/ (DSP0268 v1.0~v1.6 영역)
# lab: 부재 (사용자 명시 2026-05-07 Q2 — Supermicro 사이트 BMC 0대)
# tested_against: ["BMC 1.x", "BMC 2.x", "BMC 3.x"] (web sources 기반 — 실 lab 검증 보류)
# 사이트 도입 시 별도 cycle (rule 50 R2 단계 10 + rule 96 R1-C)

priority: 75
specificity: 50

match:
  manufacturer: ["Supermicro", "Super Micro Computer, Inc.", "Super Micro Computer", "SMCI"]
  model_patterns:
    - "X10*"          # X10SDV / X10DRH / X10DRT / X10QBL 등 X10 platform
    - "*X10*"         # 모델 이름에 X10 포함
    - "SYS-1018*"     # SYS-1018 series (X10 platform)
    - "SYS-2028*"     # SYS-2028 series (X10 platform)
    - "SYS-6028*"     # SYS-6028 series (X10 platform)

capabilities:
  redfish_version: "1.0+"           # X10 BMC 펌웨어는 DSP0268 v1.0+ 부분 지원
  power_subsystem: false             # X10 미지원 — Power deprecated path 만
  storage_strategy: "simple_storage" # X10 SimpleStorage 만 지원
  oem_strategy: "none"               # OEM 약함 — 표준 path 만

collect:
  strategy: standard_only            # OEM tasks 없음 (X10 generation 변형 약함)
  systems_path: "/redfish/v1/Systems"
  chassis_path: "/redfish/v1/Chassis"
  managers_path: "/redfish/v1/Managers"
  storage_strategy: "simple_storage_fallback"  # Storage path 미지원 → SimpleStorage path fallback
  power_strategy: "power_legacy_only"          # PowerSubsystem 미지원 → Power deprecated path 만

normalize:
  bmc_name: "BMC"                    # X10 generation 은 단순 "BMC" 표시명 (Aspeed AST 기반)
  vendor_namespace: "Oem.Supermicro"

metadata:
  vendor: supermicro
  generation: x10
  generation_year: "2014-2018"
  redfish_introduction: "DSP0268 v1.0+"
  origin: "https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X10.pdf"
  lab_status: "부재 — 사용자 명시 2026-05-07 Q2 (Supermicro 사이트 BMC 0대)"
  next_action: "lab 도입 후 별도 cycle — 실 X10 BMC 검증 후 capabilities 보정 (rule 50 R2 단계 10)"
```

---

## adapter score 검증 (rule 12 R2 — priority 일관성)

```bash
python scripts/ai/score-adapter-match.py \
  --vendor supermicro \
  --model "X10DRH-CT" \
  --manufacturer "Super Micro Computer, Inc."

# 예상 결과:
#  supermicro_x10.yml      → priority=75 + specificity=50 + match=20  → score=75520 ★
#  supermicro_bmc.yml      → priority=10 + specificity=10 + match=20  → score=10120
#  redfish_generic.yml     → priority=0  + specificity=0  + match=20  → score=20
```

→ X10 model_patterns 매칭 시 supermicro_x10.yml 선택. priority 역전 없음 (X9=70 < X10=75 < X11=80).

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과 (adapter YAML 파싱 오류 없음)
- [ ] `python scripts/ai/verify_vendor_boundary.py` 통과 (vendor 하드코딩 0건)
- [ ] `python scripts/ai/verify_harness_consistency.py` 통과 (adapter 카운트 28 → 29)
- [ ] adapter score 매칭 (위 절)

### 동적 검증 (lab 부재 — mock 시뮬만)

- [ ] M-B4 mock fixture 에서 X10 모델 응답 → supermicro_x10.yml 선택 검증
- [ ] PowerSubsystem 미지원 path → power legacy fallback 동작
- [ ] SimpleStorage fallback path 동작

### Additive only 검증 (rule 92 R2)

- [ ] 기존 supermicro_x9.yml / x11.yml priority 변경 0
- [ ] 사이트 검증 4 vendor 영향 0

---

## risk

- (MED) X10 펌웨어 BMC 버전 다양 (1.x / 2.x / 3.x) — Redfish 지원 수준 차이. 본 adapter 는 최소공배수 (DSP0268 v1.0+) — 일부 BMC 1.x 펌웨어는 Redfish 미지원 → graceful degradation 필요 (precheck 4단계 protocol fail)
- (LOW) X10SDV 같은 ATOM/Xeon-D 모델 model_patterns 일부 누락 가능 — 사이트 도입 시 model_patterns 보정

## 완료 조건

- [ ] adapters/redfish/supermicro_x10.yml 신설 (위 본문)
- [ ] adapter score 매칭 검증 (X10 모델 → supermicro_x10.yml 선택)
- [ ] verify_harness_consistency.py / verify_vendor_boundary.py 통과
- [ ] commit: `feat: [M-B1 DONE] adapters/redfish/supermicro_x10.yml 신설 — priority=75 + DSP0268 v1.0+`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 → M-B2 (6 generation capability 정합).

## 관련

- M-A6 (vault docs — dep 통과)
- rule 12 R2 (adapter priority 일관성)
- rule 50 R2 단계 10 (lab 부재 vendor — NEXT_ACTIONS 등재)
- rule 96 R1-A (web sources 의무)
- 정본: `adapters/redfish/supermicro_x9.yml`, `supermicro_x11.yml` (priority 일관성 reference)
- skill: `score-adapter-match`, `add-vendor-no-lab`
