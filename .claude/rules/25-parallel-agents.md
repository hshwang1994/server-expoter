# 병렬 Agent 활용 규칙

> 작업이 독립적이면 순차 처리 대신 Agent tool로 병렬 호출.

## 적용 대상

- 독립적이고 병행 가능한 작업 2개 이상

## 목표 규칙

### R1. 병렬 가능성 판정

```
병렬 가능 = (작업 A의 완료가 B의 시작에 필요하지 않음)
        AND (A와 B가 서로 다른 파일 영역 수정)
```

예시:
- ✅ 새 vendor adapter 작성 + tests/fixtures 추가 → 파일 영역 독립
- ❌ schema/sections.yml 추가 + field_dictionary 갱신 → field_dictionary가 sections 참조

### R2. Agent tool 활용 우선

병렬 가능 시 **같은 세션 내 Agent tool**:
```python
Agent(description="adapter Huawei", subagent_type="adapter-author", prompt="...")
Agent(description="vendor README", subagent_type="docs-sync-worker", prompt="...")
```

### R3. 세션 분리는 예외

다음 경우에만 별도 Claude CLI 세션:
1. 작업 규모가 단일 컨텍스트 윈도우 초과
2. 장기 작업이라 세션 중단 후 재개 필요
3. 작업자가 다른 사람

### R4. Agent isolation 권장

파일 수정 Agent는 `isolation: "worktree"`:
- 자동 worktree 생성 → 메인 index 오염 방지
- 변경 없으면 worktree 자동 정리

### R5. 결과 집계는 메인 세션 책임

- 각 Agent 종료 후 메인이 결과 통합
- 사용자는 메인 세션과만 대화

### R6. 작업 단위 토큰 관리

- **Default**: Agent 1회당 파일 2~3개 / 출력 20000 토큰 이내
- **Allowed**: 읽기/분석만 (수정 없음): 5~10개
- **Forbidden**: Agent 1회에 5개 이상 vendor adapter 일괄 생성

### R7. Agent 결과 실측 검증

#### R7-A. 파일/테스트 실측

- **Default**: Agent가 "파일 생성/테스트 통과" 보고 시 메인이 `find` / `pytest` / `git status`로 실측 검증
- **검증 3항목**: 파일 존재 / 내용 유효 / 실행 통과
- **Forbidden**: Agent 보고만 믿고 다음 단계

#### R7-B. 추정 → 실측 격상 금지

- **Default**: Agent 출력에 "추정 / likely / probably / 정보 부족" 등 표현 있으면 "실측"으로 격상 금지. 사용자 확인 또는 추가 실측 후만 "확정"
- **Forbidden**: 추정 결론을 가설 확장의 근거로 사용

## 금지 패턴

- 독립 작업 순차 처리 — R1/R2
- 작은 작업에 별도 CLI 세션 — R3
- Agent 호출 후 결과 통합 없이 다음 호출 — R5
- Agent에 5개 이상 파일 수정 일괄 — R6
- Agent 보고 실측 없이 신뢰 — R7-A
- 추정 결론을 실측으로 격상 — R7-B

## 리뷰 포인트

- [ ] 병렬 판정 명시
- [ ] 세션 분리 예외 사유 기록
- [ ] Agent 보고 후 실측 검증 흔적

## 관련

- rule: `26-multi-session-guide`, `96-external-contract-integrity`
