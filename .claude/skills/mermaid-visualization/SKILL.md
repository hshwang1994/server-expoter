---
name: mermaid-visualization
description: rule 41 mermaid 작성 가이드. 다이어그램 작성 / 검토 시 참조. 사용자가 "mermaid 가이드", "다이어그램 컨벤션" 등 요청 시. - 다이어그램 작성 시 rule 41 lookup 필요
---

# mermaid-visualization

본 skill은 rule 41 (mermaid-visualization)의 사용자 진입점. 정본은 rule 41.

## 핵심 (rule 41 요약)

- **R1**: 목적별 다이어그램 타입 선택 (flowchart / sequenceDiagram / stateDiagram / erDiagram / gantt / timeline / journey / quadrantChart / sankey / block-beta / mindmap / gitGraph)
- **R2**: `color:#000, stroke-width:2px, fill:<파스텔>`
- **R3**: 색상 팔레트 (OK `#dfd`, NG `#fdd`, 외부 시스템 `#def`)
- **R4**: 시작/종료 stadium, 외부 subroutine, 결정 diamond
- **R5**: 노드 ID 의미 기반
- **R6**: 한국어 라벨 + 특수문자 쌍따옴표
- **R7**: 30 노드 / 6 단계 이내
- **R8**: 성공 / 실패 / 재시도 모두
- **R9**: AS-IS / TO-BE 쌍
- **R10**: 벤더 분기 subgraph
- **R11**: 상단·하단 문맥 (`> 이 그림이 말하는 것:` / `> 읽는 법:`)
- **R12**: 범례 (3색+ 시)
- **R13**: classDef / style 중복 금지
- **R14-R17**: 타입별 (sequenceDiagram / stateDiagram-v2 / gantt / erDiagram)

## 적용 rule / 관련

- rule 41 (정본)
- skill: `write-feature-flowchart`, `visualize-flow`, `update-flowchart-after-change`
- agent: `feature-flowchart-designer`, `flowchart-reviewer`
