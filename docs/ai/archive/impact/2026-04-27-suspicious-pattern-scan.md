# 의심 패턴 스캔 보고서 — 2026-04-27 (cycle-003)

> rule 95 R1 11 패턴 자동 스캔 (`scripts/ai/scan_suspicious_patterns.py`) 첫 실행 결과.

## 요약

총 7 패턴에서 의심 발견 — 대부분 advisory (정상 동작 코드의 일반 패턴), 한 건은 실 의심 (rule 96 R1 위반).

## 결과

| Pattern # | 이름 | 카운트 | 평가 |
|---|---|---|---|
| 1 | Ansible default(omit) 누락 | 1 | False positive 가능성 (특정 task의 의도된 단순 참조) |
| 2 | set_fact 재정의 (fragment 침범 의심) | 122 | 대부분 **정상** — common/tasks/normalize/ 안의 builder가 누적 변수 set_fact 하는 것은 rule 11 R1 허용. 단 gather 디렉터리에서 발견 시 추가 검토 필요 |
| 4 | Adapter priority 동률 | 25 | **False positive** — 다른 vendor 간 priority는 비교 무의미. 같은 vendor 내 비교 필요 (score-adapter-match로 확인) |
| 5 | is none / length == 0 혼동 | 13 | 대부분 **정상** — merge_fragment.yml 등 Ansible 정합 분기 |
| 7 | int() cast 미방어 | 10 | **검토 권장** — redfish-gather/library/redfish_gather.py의 capacity 변환. 일부는 `if cap`로 None 가드, 일부는 무방어 |
| 9 | adapter_loader self-reference | 1 | **False positive** — docstring 주석 |
| 11 | **Adapter origin 주석 누락 (rule 96 R1)** | **13** | **실 의심** — 다음 cycle 정리 후보 |

## 실 의심 (rule 96 R1) — 13 adapter origin 주석 누락

```
adapters/registry.yml
adapters/esxi/esxi_6x.yml
adapters/esxi/esxi_7x.yml
adapters/esxi/esxi_8x.yml
adapters/esxi/esxi_generic.yml
... (13건)
```

각 adapter 첫 30줄에 다음 주석 형식 권장 (rule 96 R1):

```yaml
# Vendor: Dell Inc. / iDRAC9
# Firmware: tested_against ["5.x", "6.x", "7.x"]
# Origin: Dell support.dell.com / Redfish API guide
# Last sync: 2026-04-27 (hshwang)
# OEM path: /redfish/v1/Dell/...
```

### 후속 작업 (다음 cycle)

- DRIFT-001/002/003 정리 cycle 일환으로 13 adapter에 origin 주석 추가
- vendor-onboarding-worker가 새 adapter 추가 시 의무 적용 (rule 50 R2)

## 정밀화 후보 (P2)

본 도구의 false positive 줄이기:
- Pattern #2: `common/tasks/normalize/` 디렉터리는 builder 패턴이라 제외 (rule 11 R1 허용)
- Pattern #4: 같은 vendor 내 그룹화 후 동률 비교
- Pattern #9: docstring 주석 (`#`) 라인 제외
- Pattern #1: 더 정밀한 grep (예: 명시적 vendor-specific 변수만)

## 적용 rule

- rule 95 R1 (의심 패턴 11종 자동 스캔)
- rule 96 R1 (adapter origin 주석 의무)
- skill: write-quality-tdd, review-existing-code

## 도구 사용

```bash
python scripts/ai/scan_suspicious_patterns.py            # advisory
python scripts/ai/scan_suspicious_patterns.py --strict    # exit 2 if 의심 발견
python scripts/ai/scan_suspicious_patterns.py --target adapters/  # 특정 영역만
```
