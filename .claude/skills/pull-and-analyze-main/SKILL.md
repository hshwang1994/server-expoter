---
name: pull-and-analyze-main
description: origin/main 최신 변경을 fetch하여 자동 분석. 갭 / rule 95 의심 / 하네스 기준 준수 / 영향 vendor 식별. 사용자가 "main 최신 가져와서 체크", "origin 분석", "최근 변경 봐줘" 등 요청 시. - main 최신 동기화 / feature 브랜치 작업 시작 전 / 다른 작업자 머지 후
---

# pull-and-analyze-main

## 목적

server-exporter는 단일 main + feature/* 운영 (단순 브랜치 정책). main 최신 동기화 시 변경 분석.

## 입력

- (선택) commit range (예: 최근 N개)

## 절차

```bash
# 1. fetch
git fetch origin main

# 2. 갭 분석
python scripts/ai/check_gap_against_main.py

# 3. 변경 요약
git log HEAD..origin/main --oneline
git diff --stat HEAD..origin/main

# 4. rule 95 의심 패턴 스캔 (변경 파일 대상)
git diff --name-only HEAD..origin/main | xargs python scripts/ai/hooks/post_merge_incoming_review.py  # (가상 dry-run)
```

## 출력

```markdown
## origin/main 분석

### 갭
- ahead: 0 (내 브랜치)
- behind: 5 (origin/main 앞섬)

### 신규 commit (최근 5개)
- abc1234 feat: HPE iLO6 펌웨어 2.5 검증
- def5678 fix: precheck protocol TLS fallback
- ...

### 영향 영역
- adapters/redfish/hpe_ilo6.yml (수정)
- common/library/precheck_bundle.py (수정)

### rule 95 의심 패턴 자동 스캔
- 발견 0건 (clean)
- 또는 list

### 권고
- 내 작업 브랜치에 머지: git merge origin/main (rule 93 사용자 승인 절차 거쳐)
- 또는 rebase: git rebase origin/main
```

## 자동 호출 시점

- session_start hook이 갭 출력 (작은 단위)
- 사용자 명시 요청 시 본 skill (대규모 분석)

## 적용 rule / 관련

- **rule 50** (vendor-adapter-policy) — branch 정책
- rule 93 (branch-merge-gate) — 머지 시 사용자 승인
- rule 95 R4 (Cross-branch 검증)
- rule 97 (incoming-merge-review) — 머지 후 자동 검증
- skill: `review-incoming-merge`, `task-impact-preview`
- agent: `change-impact-analyst`
- script: `scripts/ai/check_gap_against_main.py`
