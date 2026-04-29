---
name: handoff-driven-implementation
description: 다른 세션 / 다른 작업자에게서 인계받은 티켓을 이어받아 구현. 의도 + 제약 + fidelity 판단. 사용자가 "이 티켓 이어받자", "다른 세션 작업 이어가" 등 요청 시. - docs/ai/handoff/ 문서 받아 구현 착수 / 다중 세션 (rule 26)
---

# handoff-driven-implementation

## 목적

세션 간 작업 인계받기. server-exporter는 prototype 없음 → 티켓 + 명세 + ai-context 기반 인계.

## 절차

1. **handoff 문서 Read**: `docs/ai/handoff/<날짜>-<주제>.md`
2. **핵심 의도 3 가지 추출**:
   - (a) 호출자 flow
   - (b) 핵심 결정사항
   - (c) 기존 시스템 제약
3. **자료 훑기** (rule 26 R1 오너십 표):
   - 인계자가 명시한 영역 / 파일 list
   - 그 외 영역은 절대 수정 금지 (다른 세션 영역 침범 금지)
4. **차이 검증**: 인계 문서 vs 현재 코드 (브랜치 머지 / drift 발생했는지)
5. **수행 가능 여부 판단**: 컨텍스트 / 도구 / 의존성 모두 갖추어졌는지
6. **사용자 확인** (애매한 부분):
   - 외부 시스템 계약 (rule 96 R2)
   - 의존성 변경 (rule 92 R1)
   - vault / Jenkinsfile / schema baseline 변경 (cycle-011 보안 정책 해제 후에도 운영 권장 수준 보호)
7. **구현 진입**: task-impact-preview → 적절한 plan-* skill → implement

## Forbidden

- 인계자 오너십 외 파일 수정 (rule 26 R1)
- 인계 문서 미확인 후 즉시 구현
- 외부 계약 미확인 후 가설 확장 (rule 25 R7-B)

## 적용 rule / 관련

- rule 25 (parallel-agents)
- rule 26 (multi-session-guide)
- rule 91 (task-impact-preview)
- skill: `task-impact-preview`, `plan-feature-change`, `debug-external-integrated-feature`
- 정본: `docs/ai/handoff/`
