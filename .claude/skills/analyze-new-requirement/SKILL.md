---
name: analyze-new-requirement
description: 새 요구사항 (새 vendor / 새 섹션 / 새 호출자 / Round 검증)을 받아 영향 / 변경 대상 / 테스트 / 리스크 분석. 사용자가 "이 요구사항 분석해줘", "새 기능 영향" 등 요청 시. - 새 요구사항 entry / PO 단계 / task-impact-preview 보다 더 구조화된 분석 필요 시
---

# analyze-new-requirement

## 목적

server-exporter 새 요구사항을 6 축으로 구조화 분석. PO 의사결정 + 후속 plan-* skill 입력.

## 6 축

1. **요구 의도** (사용자 flow 3 가지: a 사용자 flow / b 핵심 결정 / c 기존 시스템 제약)
2. **영향 범위**: 채널 / vendor / schema / vault / Jenkinsfile / 외부 시스템
3. **변경 대상 파일** (실측 grep)
4. **테스트 범위**: 단위 / 통합 / 회귀 / 실장비 (Round)
5. **리스크 top 3**: HIGH / MED / LOW
6. **진행 확인** (사용자 선택지)

## 출력

`.claude/templates/REQUIREMENT_ANALYSIS.template.md` 형식

## 후속 skill 라우팅

- 단순 변경 → `task-impact-preview` → `implement-safe-change`
- 옵션 비교 필요 → `compare-feature-options`
- 큰 변경 / HIGH 리스크 → `write-impact-brief` + `plan-feature-change`
- PO 기획 단계 → `plan-product-change`
- DB / schema → `plan-schema-change`
- 새 벤더 → `add-new-vendor`

## 적용 rule / 관련

- **rule 91** (task-impact-gate) — 자동 호출
- skill: `task-impact-preview`, `discuss-feature-direction`, `compare-feature-options`, `recommend-product-direction`
- agent: `discovery-facilitator`, `product-planner`, `change-impact-analyst`
- template: `.claude/templates/REQUIREMENT_ANALYSIS.template.md`
