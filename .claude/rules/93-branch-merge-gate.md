# Branch / Merge / Push 게이트

## 적용 대상
- 저장소 전체 (`**`) — 모든 branch 간 merge / cherry-pick / push

## Branch 역할 (단순 운영)

| 브랜치 | 역할 | AI 권한 |
|---|---|---|
| `main` (운영 기준선) | 모든 변경의 최종 도착점 | 직접 push 금지 (force / 비공식 push). PR 또는 사용자 명시 승인 후만 |
| `feature/<name>` | 기능 추가 | AI 자유 작업 |
| `fix/<name>` | 버그 수정 | AI 자유 작업 |
| `vendor/<name>` | 새 벤더 추가 | AI 자유 작업 |
| `docs/<name>` | 문서 작업 | AI 자유 작업 |
| `harness/<name>` | 하네스 변경 | AI 자유 작업 |

## 목표 규칙

### R1. 작업 브랜치 외 브랜치 push 금지

- **Default**: AI는 현재 체크아웃된 브랜치에만 push. `git push origin <다른브랜치>` 금지
- **Forbidden**:
  - `git push --all`
  - `git push --force` / `-f` / `--force-with-lease`
  - `git push origin main` (사용자 명시 승인 외)

### R2. Branch 간 merge 사용자 승인

- **Default**: 모든 `git merge`, `git rebase <다른브랜치>`, `git cherry-pick` 작업은 **실행 전 사용자 승인** 필수
- **Allowed**: 사용자가 4 요소 명시 후 승인:
  1. 소스 브랜치
  2. 타겟 브랜치
  3. 포함 commit 범위 (예상 diff 요약)
  4. 영향 (vendor / 채널 / Jenkins pipeline)
- **Forbidden**:
  - 승인 없는 git merge
  - "로컬 merge만 하니까" — push 직전 추가 승인 필요
  - `git pull origin <다른브랜치>` (실질적 merge)

### R3. 현재 브랜치 확인 의무

- **Default**: 모든 git 작업 시작 전 `git branch --show-current` 확인
- **Forbidden**: 브랜치 이름 추정만으로 작업

### R4. main 보호

- main에 직접 commit / push 금지 (사용자 명시 승인 외)
- force push 금지
- direct push 시 사용자 명시 재확인

### R5. 머지 전략 (default: squash)

배포/main으로의 머지는 squash 기본:

| 머지 대상 | 기본 전략 | 이유 |
|---|---|---|
| main | squash | 1개 의미 있는 커밋으로 history 깔끔 |
| feature 간 (개인) | merge / rebase 자유 | 개인 작업 |

**예외 (fast-forward)**: feature의 모든 커밋이 의미 있는 단일 변경이고 main history에 그대로 남길 가치 있을 때만. 사용자 명시 "fast-forward로" 지시 필요.

승인 요청 시 머지 방식 선택지 제시:
```
머지 방식 선택:
(A) squash   — N개 commit을 1개 "<요약>"으로 압축 (main 추천)
(B) fast-forward — N개 그대로 전파
(C) merge commit — 병합 commit 추가
```

### R6. 승인 요청 포맷

```
# 머지 승인 요청

무엇: <소스 브랜치> → <타겟 브랜치> 머지
왜:   <목적, 1-2 문장>
영향: <commit 개수> commit 포함, 영향 vendor: <list>, 영향 채널: <list>
      주요 변경: <bullet 3줄>
결정 필요: 진행 / 조정 / 취소 (squash / ff / merge 중)
```

## 금지 패턴

- 현재 브랜치 확인 없이 git 작업 — R3
- 다른 브랜치 push — R1
- 승인 없는 merge — R2
- main 직접 commit — R4
- 여러 브랜치 일괄 push (`--all`) — R1
- 승인 포맷 생략 — R6

## 리뷰 포인트

- [ ] 모든 merge/push에 사용자 승인 기록
- [ ] 4 요소 명시 (소스/타겟/범위/영향)
- [ ] 현재 브랜치 확인 흔적
- [ ] force / --all 사용 없음

## 관련

- rule: `00-core-repo`, `50-vendor-adapter-policy`
