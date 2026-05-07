# M-K1 — 모든 신규/보강 adapter origin 주석 일관성 검증

> status: [PENDING] | depends: M-J1 | priority: P1 | worker: W5 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "모든 adapter origin 주석 일관성 검증 (rule 96 R1-A)." (cycle 진입)

본 cycle 의 모든 신규/보강 adapter 의 origin 주석 (rule 96 R1+R1-A) 일관성 검증 — vendor 공식 docs / DMTF spec / GitHub community / 사이트 실측 4종 sources 중 1개 이상 + 확인 일자 + lab_status.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `adapters/redfish/*.yml` (29개 — Supermicro X10 신설 후) |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | M-K2 EXTERNAL_CONTRACTS.md 입력 |
| 리스크 top 3 | (1) origin 주석 누락 vendor / (2) 확인 일자 stale (cycle 진입 전 작성된 것) / (3) lab_status 일관성 |
| 진행 확인 | M-J1 후 진입 |

---

## 검증 항목 (rule 96 R1)

각 adapter 의 metadata 절에 다음 키 필수:

| 키 | 의무 | 예시 |
|---|---|---|
| `vendor` | 필수 | "dell" |
| `generation` | 필수 | "idrac9" |
| `generation_year` | 권장 | "2018-2024" |
| `redfish_introduction` | 권장 | "DSP0268 v1.6+" |
| `origin` | **필수** (rule 96 R1) | "https://developer.dell.com/apis/2978/versions/3/docs/" |
| `lab_status` | **필수** (rule 96 R1-A) | "PASS — 사이트 검증" 또는 "부재 — 사용자 명시 ..." |
| `tested_against` | 권장 | ["iDRAC9 5.x", "iDRAC9 6.x"] |
| `next_action` | lab 부재 시 필수 (rule 96 R1-C) | "lab 도입 후 별도 cycle" |

→ Web sources 4종 중 1개 이상 origin 명시 의무 (rule 96 R1-A):
1. vendor 공식 docs URL
2. DMTF Redfish spec URL
3. GitHub community / issue URL
4. 사이트 실측 (`tests/evidence/<날짜>-<vendor>.md` reference)

---

## 검증 절차

### 1. 자동 검증 스크립트 (advisory)

```bash
# scripts/ai/hooks/verify_adapter_origin.py (신설 또는 기존 verify_harness_consistency 확장)
python scripts/ai/hooks/verify_adapter_origin.py

# 검증:
# - 29 adapter 모두 metadata.origin 존재
# - 사이트 검증 4 vendor (idrac10/ilo7/xcc3/ucs_xseries) — lab_status: "PASS"
# - 그 외 adapter — lab_status: "부재" + next_action 명시
# - 확인 일자 (origin URL 옆) 6개월 이내
```

### 2. 수동 검증 (29 adapter)

| adapter | 사이트 / lab | origin source 의무 |
|---|---|---|
| redfish_generic.yml | (generic fallback) | DMTF DSP0268 |
| dell_idrac.yml / 8 / 9 | 부재 (M-H1) | Dell 공식 + DMTF |
| dell_idrac10.yml | **PASS** (사이트 5대) | Dell 공식 + 사이트 evidence |
| hpe_ilo.yml / 4 / 5 / 6 | 부재 (M-H2) | HPE 공식 + DMTF |
| hpe_ilo7.yml | **PASS** (사이트 1대) | HPE 공식 + 사이트 evidence |
| hpe_superdome_flex.yml | 부재 (M-G1) | HPE 공식 + GitHub community |
| lenovo_bmc / imm2 / xcc | 부재 (M-H3) | Lenovo 공식 + DMTF |
| lenovo_xcc3.yml | **PASS** (사이트 1대) | Lenovo 공식 + 사이트 evidence |
| supermicro_bmc / x9 / x10 / x11 / x12 / x13 / x14 | 부재 (M-B1, M-B2, M-B3) | Supermicro 공식 + DMTF |
| cisco_bmc / cimc | 부재 (M-H4) | Cisco 공식 + DMTF |
| cisco_ucs_xseries.yml | **PASS** (사이트 1대) | Cisco 공식 + 사이트 evidence |
| huawei_ibmc.yml | 부재 (M-C1) | Huawei 공식 + GitHub |
| inspur_isbmc.yml | 부재 (M-D1, M-D2) | Inspur 공식 + GitHub community |
| fujitsu_irmc.yml | 부재 (M-E1) | Fujitsu 공식 |
| quanta_qct_bmc.yml | 부재 (M-F1) | Quanta 공식 + GitHub community |

→ 29 adapter — origin 주석 일관성 검증.

---

## 구현

### 1. verify_adapter_origin.py 스크립트 신설 (또는 기존 확장)

```python
# scripts/ai/hooks/verify_adapter_origin.py
"""adapter metadata.origin + lab_status 일관성 advisory 검증.

rule 96 R1 + R1-A + R1-C 의무 검사.
"""

import re
from pathlib import Path
import yaml

ADAPTERS_DIR = Path("adapters/redfish")
SITE_VERIFIED = {"dell_idrac10.yml", "hpe_ilo7.yml", "lenovo_xcc3.yml", "cisco_ucs_xseries.yml"}

def verify():
    issues = []
    for adapter_file in sorted(ADAPTERS_DIR.glob("*.yml")):
        with open(adapter_file) as f:
            data = yaml.safe_load(f)
        meta = data.get("metadata", {})

        if "origin" not in meta:
            issues.append(f"{adapter_file.name}: metadata.origin 누락 (rule 96 R1)")

        if "lab_status" not in meta:
            issues.append(f"{adapter_file.name}: metadata.lab_status 누락 (rule 96 R1-A)")
            continue

        if adapter_file.name in SITE_VERIFIED:
            if "PASS" not in meta["lab_status"]:
                issues.append(f"{adapter_file.name}: 사이트 검증인데 lab_status='{meta['lab_status']}'")
        else:
            if "부재" not in meta["lab_status"]:
                issues.append(f"{adapter_file.name}: lab 부재인데 lab_status='{meta['lab_status']}'")
            if "next_action" not in meta:
                issues.append(f"{adapter_file.name}: lab 부재인데 next_action 누락 (rule 96 R1-C)")

    if issues:
        print("[WARN] adapter origin/lab_status 검증 실패:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("[PASS] 29 adapter origin/lab_status 일관성 PASS")
    return 0

if __name__ == "__main__":
    exit(verify())
```

### 2. 누락 vendor adapter 보강

본 cycle 의 worker 들이 작성한 adapter (M-B1~B3, M-C1, M-E1, M-G1, M-H1~H4) 의 metadata 가 위 검증 통과하도록 보강.

---

## 회귀 / 검증

### 정적 검증

- [ ] verify_adapter_origin.py 통과 (29 adapter 모두 PASS)
- [ ] 사이트 검증 4 adapter — lab_status: "PASS"
- [ ] lab 부재 25 adapter — lab_status: "부재" + next_action 명시

### Additive only

- [ ] 본 ticket 은 검증 + 보강 (Additive — 기존 capability collect strategy 변경 0)

---

## risk

- (LOW) origin 주석 stale (확인 일자 6개월 이상 경과) — advisory 표시 후 후속 cycle 갱신
- (LOW) origin URL dead link — 검증 시 발견. 후속 cycle 갱신

## 완료 조건

- [ ] verify_adapter_origin.py 신설 또는 기존 verify_harness_consistency 확장
- [ ] 29 adapter origin / lab_status 일관성 PASS
- [ ] 누락 adapter 보강
- [ ] commit: `feat: [M-K1 DONE] adapter origin 주석 일관성 검증 (29 adapter) + verify_adapter_origin.py 신설`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W5 → M-K2 (EXTERNAL_CONTRACTS).

## 관련

- M-J1 (OEM mapping)
- rule 96 R1+R1-A+R1-C (origin / web sources / NEXT_ACTIONS 등재)
- 정본: rule 96 본문 + cycle 2026-05-01 학습 (4 vendor lab 부재 origin 패턴)
