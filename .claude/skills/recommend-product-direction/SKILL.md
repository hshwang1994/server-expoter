---
name: recommend-product-direction
description: 후보안 비교 후 1개 추천안 + 근거 제시. 사용자가 "추천해줘", "결정 마비 상태" 등 요청 시. - compare-feature-options 출력 후 결정 단계
---

# recommend-product-direction

## 목적

`compare-feature-options` 매트릭스를 입력으로 받아 1개 추천안 + 근거 + 대안 위치 명시.

## 출력

```markdown
## 추천 — 안 B (standard+OEM)

### 근거 (정량)
- 영향 vendor 1 (신규)
- 회귀 비용 MED (신규 vendor만 baseline 신규)
- 구현 시간 2d (PO 일정 수용 가능)
- 외부 계약: rule 96 origin 주석 정확히 반영 → drift 없음

### 근거 (정성)
- Huawei OEM이 BMC 사용자 정보 등 풍부 → standard만 시 users 섹션 빈약
- 호출자 시스템 (Portal)에서 users 섹션 주요 활용 → OEM 통합 가치 큼

### 대안 위치
- A (standard_only): 초기 빠른 도입 후 follow-up PR로 OEM 추가 가능
- C (보류): 다음 분기 우선순위 재평가

### 결정 주체
- 제가(AI) 위 비교를 통해 안 B를 **초안 제안**합니다.
- **PO 님의 결정**이 필요합니다 (안 B / A / C 중 선택).

### 다음 skill
- 안 B 채택 시 → `plan-product-change` 또는 `add-new-vendor` 직접 진입
```

## 적용 rule / 관련

- rule 23 R3 (결정 주체 명시)
- skill: `compare-feature-options`, `analyze-new-requirement`, `plan-product-change`
- agent: `product-planner`
