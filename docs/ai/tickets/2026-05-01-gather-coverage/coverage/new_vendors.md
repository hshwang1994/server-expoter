# Coverage — 신규 vendor (현재 5 vendor 외)

## 컨텍스트

현재 server-exporter 는 5 vendor 지원: Dell / HPE / Lenovo / Supermicro / Cisco. 추가 가능 vendor:

## 후보 vendor

### 1. Huawei (iBMC / FusionServer)
- **BMC**: iBMC
- **모델**: RH1288 V3, RH2288 V3, 1288H V5, 2288H V5, 2288 V5, 2488H V5, CH121 V3, CH242 V3, XH622 V3
- **신규**: TaiShan (ARM 기반)
- **Redfish 호환**: GET / PUT / PATCH / POST / DELETE 모두 표준 호환
- **Manufacturer alias**: "Huawei" / "HUAWEI" / "Huawei Technologies Co., Ltd."
- **OEM namespace**: `Oem.Huawei`

### 2. Inspur (NF8480M5 / NF5280M6 등)
- **BMC**: BMC + iBMC 일부
- **OEM**: `Oem.Inspur` / 일부 OpenBMC 기반
- **호환**: 표준 위주, OEM 부분

### 3. ASRock Rack (E3C246D4M-4L 등)
- **BMC**: AMI MegaRAC (CVE-2024-54085 영향)
- **OEM**: 부분
- **호환**: 표준

### 4. Asus (RS720A-E11-RS24U 등)
- **BMC**: AMI MegaRAC
- **호환**: 표준

### 5. NVIDIA (BlueField DPU)
- **SystemType**: DPU (신규 enum)
- **OEM**: `Oem.Nvidia`
- **호환**: 표준 + DPU specific

## fix 후보

### F31 — Huawei iBMC vendor 추가 (P3 — 운영 요구 시)
- **rule 50 R2** — 9단계 절차 따름:
  1. `common/vars/vendor_aliases.yml` 에 huawei alias 추가
  2. `adapters/redfish/huawei_*.yml` adapter 생성
  3. (선택) `redfish-gather/tasks/vendors/huawei/` OEM tasks
  4. `vault/redfish/huawei.yml` 생성
  5. `tests/baseline_v1/huawei_baseline.json` (실장비 검증 후)
  6. `.claude/ai-context/vendors/huawei.md`
  7. `.claude/policy/vendor-boundary-map.yaml` 갱신
  8. `docs/13_redfish-live-validation.md` Round 갱신
  9. `docs/19_decision-log.md` 추가
- **회귀**: 기존 5 vendor adapter priority / 영향 없음 (Additive)
- **사용자 명시 승인 필수** (rule 50 R4)
- **우선**: P3 (사이트 운영 요구 시)

### 다른 vendor — F31과 같은 절차 (별도 ticket 미작성, F31 패턴 따름)

## Sources

- [Huawei iBMC Redfish API](https://support.huawei.com/enterprise/en/doc/EDOC1000126992)
- [Huawei TaiShan iBMC](https://support.huawei.com/enterprise/en/doc/EDOC1100121685/abd953fa/redfish-interface)
- [Huawei iBMC Cmdlets (PowerShell)](https://github.com/IamFive/Huawei-iBMC-Cmdlets)

## 갱신 history

- 2026-05-01: 신규 영역 ticket / F31 P3 (Huawei + 4 후보 vendor)
