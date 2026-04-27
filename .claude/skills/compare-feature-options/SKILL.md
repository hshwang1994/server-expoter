---
name: compare-feature-options
description: 후보안 2개 이상이 있을 때 영향 / 리스크 / 비용 축으로 비교 매트릭스. 사용자가 "두 방법 비교", "어떤 게 나아?" 등 요청 시. - 후보안 2+ / 비교 근거 필요
---

# compare-feature-options

## 목적

server-exporter 후보안 비교. quadrantChart 또는 매트릭스로 시각화.

## 비교 축 (server-exporter)

- **영향 vendor 수**: 1 / 일부 / 전수
- **회귀 비용**: baseline 갱신 vendor 수
- **외부 계약 영향**: rule 96 origin 주석 갱신 필요?
- **schema 변경**: 3종 동반 필요?
- **Jenkinsfile 영향**: 4-Stage / cron
- **Vault 영향**: 회전 / 신규 vendor vault
- **구현 시간**: 견적

## 출력 (matrix)

```markdown
## 후보안 비교 — Huawei 추가 방식

| 축 | 안 A: standard_only | 안 B: standard+OEM | 안 C: 보류 |
|---|---|---|---|
| 영향 vendor | Huawei (신규 1) | Huawei (신규 1) | 없음 |
| 회귀 비용 | LOW | MED | 없음 |
| 외부 계약 | 표준만 | OEM origin 주석 | 없음 |
| schema 변경 | 없음 | Nice 필드 일부 | 없음 |
| 구현 시간 | 0.5d | 2d | 0d |
| 추천도 | ★★ | ★★★ | ★ |

### 추천: B (standard+OEM)
- 근거: Huawei iBMC OEM이 BMC 사용자 정보 등 풍부 → standard만 시 sections 일부 빈약
- 대안 A는 초기 빠른 도입 후 follow-up PR로 OEM 추가 가능
```

## 적용 rule / 관련

- skill: `analyze-new-requirement`, `recommend-product-direction`, `task-impact-preview`
- agent: `option-generator`, `product-planner`
- rule: 41 (mermaid quadrantChart)
