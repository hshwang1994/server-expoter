# 다중 세션 운영 가이드

> 꼭 필요한 경우에만 별도 Claude CLI 세션. 기본은 단일 세션 + Agent tool 병렬 (rule 25).

## 적용 대상

한 브랜치에서 여러 Claude CLI 세션 동시 운영.

## 언제 필요한가

1. 작업 규모가 단일 컨텍스트 윈도우 초과
2. 장기 작업의 세션 중단 후 재개
3. 사용자가 2 환경 (노트북 + 데스크톱)에서 병행

그 외에는 Agent tool.

## 세션 준비 체크리스트

작업 지시자(사용자)가 각 세션에 다음 순서:

1. "CONTINUATION.md 먼저 읽고 너의 담당 영역 확인해줘."
   - 위치: `docs/ai/handoff/<날짜>-<주제>.md` 또는 `docs/tickets/<...>/CONTINUATION.md`
2. "다른 세션의 작업 범위를 건드리지 마. 네 오너십 파일만."
3. "완료 시 commit 메시지에 [SUB-N DONE] 마커 넣어줘."

## 세션 간 동기화 메커니즘

### 방법 A: Git 마커 polling

```bash
# scripts/ai/wait_for_markers.sh (예시)
MARKER="[SUB-3 DONE]"
while ! git log --grep "$MARKER" -1 --oneline >/dev/null 2>&1; do
    git fetch origin
    sleep 30
done
```

### 한계

- Claude Code CLI 간 실시간 이벤트 공유 불가
- polling 간격 최소 30초

## 파일 오너십 충돌 방지

### R1. 오너십 표를 handoff 문서에 명시

```markdown
| 세션 | 담당 영역 | 오너십 파일 |
|---|---|---|
| A | adapter Huawei 신규 | adapters/redfish/huawei_*.yml + redfish-gather/tasks/vendors/huawei/ |
| B | tests/fixtures Huawei | tests/fixtures/huawei_*.json |
| C | docs 갱신 | .claude/ai-context/vendors/huawei.md + docs/13_redfish-live-validation.md |
```

### R2. 커밋은 `git commit <pathspec>`

다른 세션의 staged 파일 오염 방지.

### R3. 공용 파일은 순차 편집

`schema/sections.yml`, `schema/field_dictionary.yml`, `vault/redfish/{vendor}.yml` 같은 공용 파일은 한 세션이 먼저 + 다른 세션은 pull 후 append.

## CONTINUATION.md 필수 섹션

1. 현재 상태 (각 영역 완결 여부)
2. 세션별 담당 (오너십 표)
3. 세션 간 의존성
4. 다음 세션 첫 지시 템플릿
5. 에스컬레이션 포인트

## 금지 패턴

- 오너십 정의 없이 다중 세션 시작
- CONTINUATION.md 갱신 없이 세션 종료
- 세션 간 staged 파일 오염

## 리뷰 포인트

- [ ] CONTINUATION.md에 오너십 표 + 의존성
- [ ] 각 세션 commit에 [SUB-N] 태그
- [ ] 세션 종료 전 CONTINUATION.md 갱신

## 관련

- rule: `25-parallel-agents`
- 정본: `docs/ai/handoff/`
