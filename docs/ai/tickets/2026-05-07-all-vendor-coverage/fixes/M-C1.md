# M-C1 — Huawei iBMC adapter generation 분기 (1.x ~ 5.x)

> status: [PENDING] | depends: M-A1 | priority: P1 | worker: W2 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Huawei iBMC 1.x ~ 5.x 모든 generation 코드 path." (cycle 진입)

현재 `huawei_ibmc.yml` (priority=70) 단일 adapter — generation 분기 없음. 본 ticket 에서 firmware_patterns 분기 보강 (Additive — 단일 adapter 안에서 capability 변형 + match.firmware_patterns 추가).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/huawei_ibmc.yml` (capability + firmware_patterns 보강) |
| 영향 vendor | Huawei iBMC (lab 부재) |
| 함께 바뀔 것 | M-C2 (OEM tasks), M-C3 (mock fixture) |
| 리스크 top 3 | (1) iBMC generation 별 응답 형식 차이 — 단일 adapter 로 cover 가능한지 / (2) FusionServer Pro vs Atlas 모델별 분기 / (3) lab 부재 — 정확성 web sources 의존 |
| 진행 확인 | M-A1 vault 신설 후 진입 |

---

## Web sources (rule 96 R1-A)

| source | 항목 | URL / 확인일 |
|---|---|---|
| Huawei 공식 | iBMC Redfish API guide | `https://support.huawei.com/.../iBMC_Redfish_API_v*.pdf` (확인 2026-05-07) |
| Huawei 공식 | FusionServer Pro 매뉴얼 | `https://support.huawei.com/enterprise/en/servers/fusionserver-pro` |
| Huawei 공식 | Atlas 시리즈 (AI 서버) | `https://www.huawei.com/en/products/cloud-computing-dc/atlas` |
| DMTF Redfish | DSP0268 v1.0 ~ v1.10 | iBMC generation 매핑 |

→ Huawei iBMC generation 매트릭스:
- **iBMC 1.x** (2014-2016): DSP0268 v1.0 부분 지원, OEM 영역 약함
- **iBMC 2.x** (2016-2019): DSP0268 v1.4+, OEM Oem.Huawei 강화
- **iBMC 3.x** (2019-2021): DSP0268 v1.8+, PowerSubsystem 일부 지원
- **iBMC 4.x** (2021-2023): DSP0268 v1.10+, 표준 가까움
- **iBMC 5.x** (2023+): DSP0268 v1.13+, Atlas AI 서버 추가 분기

---

## 구현 (adapters/redfish/huawei_ibmc.yml 갱신)

### 갱신 후 본문

```yaml
---
# adapters/redfish/huawei_ibmc.yml
# Huawei iBMC 1.x ~ 5.x generation adapter
#
# source: https://support.huawei.com/.../iBMC_Redfish_API_v*.pdf (확인 2026-05-07)
# source: https://support.huawei.com/enterprise/en/servers/fusionserver-pro
# source: https://www.huawei.com/en/products/cloud-computing-dc/atlas
# source: https://redfish.dmtf.org/schemas/v1/ (DSP0268 v1.0 ~ v1.13)
# lab: 부재 (사용자 명시 2026-05-01 — 4 신규 vendor lab 부재 명시 승인)
# tested_against: ["iBMC 1.x", "iBMC 2.x", "iBMC 3.x", "iBMC 4.x", "iBMC 5.x"] (web sources 기반)

priority: 70
specificity: 50

match:
  manufacturer: ["Huawei", "HUAWEI", "Huawei Technologies Co., Ltd.", "Huawei Technologies"]
  model_patterns:
    # FusionServer Pro
    - "*RH*"          # RH 시리즈 (RH2288 / RH5885 등 — Rack)
    - "*FusionServer*"
    - "*Pro*"
    - "*XH*"          # XH 시리즈 (XH628 / XH320 — Density)
    - "*BH*"          # BH 시리즈 (블레이드)
    # Atlas AI 서버
    - "*Atlas*"
    - "*5800*"        # Atlas 800 — AI training
    - "*9000*"        # 9000 시리즈 (mission-critical)
  firmware_patterns:
    - "iBMC*1.*"      # iBMC 1.x (2014-2016)
    - "iBMC*2.*"      # iBMC 2.x (2016-2019)
    - "iBMC*3.*"      # iBMC 3.x (2019-2021)
    - "iBMC*4.*"      # iBMC 4.x (2021-2023)
    - "iBMC*5.*"      # iBMC 5.x (2023+)

capabilities:
  redfish_version: "1.0+"            # iBMC 1.x 의 최소 버전 — 5.x 는 1.13+
  power_subsystem: "conditional"      # iBMC 3.x+ 부분 지원 / 4.x+ 완전 지원
  storage_strategy: "conditional"     # iBMC 1.x: simple_storage / 2.x+: standard
  oem_strategy: "standard+oem"
  oem_namespace: "Oem.Huawei"

collect:
  strategy: standard+oem
  systems_path: "/redfish/v1/Systems"
  chassis_path: "/redfish/v1/Chassis"
  managers_path: "/redfish/v1/Managers"
  oem_tasks: "redfish-gather/tasks/vendors/huawei/collect_oem.yml"   # M-C2 신설 dep
  storage_strategy: "standard_with_simple_fallback"   # iBMC 1.x 시 SimpleStorage fallback
  power_strategy: "subsystem_with_legacy_fallback"    # iBMC 3.x- 시 Power legacy fallback

normalize:
  bmc_name: "iBMC"
  vendor_namespace: "Oem.Huawei"
  oem_normalize: "redfish-gather/tasks/vendors/huawei/normalize_oem.yml"

metadata:
  vendor: huawei
  generation: ibmc
  generation_year: "2014-2024+"
  redfish_introduction: "DSP0268 v1.0+ (1.x) ~ v1.13+ (5.x)"
  origin: "https://support.huawei.com/.../iBMC_Redfish_API_v*.pdf"
  lab_status: "부재 — 사용자 명시 2026-05-01"
  next_action: "lab 도입 후 별도 cycle — generation 별 capability 보정 (rule 50 R2 단계 10)"
  generation_matrix:
    "1.x": "DSP0268 v1.0 부분 / OEM 약함 / SimpleStorage / Power legacy"
    "2.x": "DSP0268 v1.4+ / OEM 강화 / standard storage / Power legacy"
    "3.x": "DSP0268 v1.8+ / PowerSubsystem 부분"
    "4.x": "DSP0268 v1.10+ / 표준 가까움"
    "5.x": "DSP0268 v1.13+ / Atlas 분기"
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `ansible-playbook --syntax-check redfish-gather/site.yml` 통과
- [ ] `verify_harness_consistency.py` 통과
- [ ] `verify_vendor_boundary.py` 통과
- [ ] adapter `metadata.origin` 존재 + web sources 4종 명시

### adapter score 매칭

```bash
python scripts/ai/score-adapter-match.py --vendor huawei --model "RH2288 V5"
# 예상: huawei_ibmc.yml (priority=70) 선택

python scripts/ai/score-adapter-match.py --vendor huawei --model "Atlas 800"
# 예상: huawei_ibmc.yml (priority=70) 선택 (Atlas 모델 model_patterns 추가됨)
```

### Additive only

- [ ] 기존 priority=70 변경 0
- [ ] capabilities 내 storage / power 가 "conditional" 명시 — generation 별 fallback (M-C2 OEM tasks 의존)

---

## risk

- (MED) iBMC 1.x (2014-2016) 펌웨어 응답 형식 매우 약함 — Redfish 미지원 BMC 도 있음 (IPMI only). graceful degradation (precheck protocol fail) 필요
- (LOW) Atlas AI 서버는 Compute server 와 응답 다름 — model_patterns 별도 분기 가능. 사이트 도입 시 보정

## 완료 조건

- [ ] huawei_ibmc.yml 갱신 (firmware_patterns 5 generation + capabilities + metadata)
- [ ] M-C2 OEM tasks dep 명시
- [ ] commit: `feat: [M-C1 DONE] Huawei iBMC 1.x~5.x generation 분기 + Atlas model_patterns`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W2 → M-C2 (Huawei OEM tasks).

## 관련

- M-A1 (Huawei vault — dep 통과)
- rule 12 R2 (priority 일관성)
- rule 96 R1-A (web sources)
- skill: `add-vendor-no-lab`
