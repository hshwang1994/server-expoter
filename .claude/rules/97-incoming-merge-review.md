# 머지 후 들어온 코드 자동 검증 (Incoming Merge Review)

> 다른 브랜치에서 머지로 들어온 코드를 자동 비판적 검증.

## 적용 대상

- `git merge`, `git pull`, `git rebase`, `git merge --squash` 직후
- 자동 트리거: `post-merge` git hook → `scripts/ai/hooks/post_merge_incoming_review.py`
- 수동 트리거: `review-incoming-merge` skill

## 목표 규칙

### R1. 머지 직후 자동 비판적 검증

`post-merge` hook이 5종 자동 실행:

(a) **Jenkinsfile cron 변경** 검사 (rule 80 + 92 R5)
(b) **Ansible/Python/YAML 의심 패턴** (rule 95 R1)
   - raw 모듈 권한 미설정 (become: 누락)
   - vault 변수 평문 누설
   - 다른 gather의 fragment 침범 (rule 22)
(c) **Adapter YAML metadata 주석 누락** (rule 96 R1) — `CustomAction(Phase|Target|Resource|...)` 같은 enum이 server-exporter에는 없으므로 vendor list / firmware list / oem_path 메타가 origin 주석 없이 변경됐는지
(d) **schema/sections.yml + field_dictionary.yml 버전 충돌** (rule 92 R5) — 동시 변경
(e) **결과 보고**: `docs/ai/incoming-review/<YYYY-MM-DD>-<sha>.md` 자동 출력

### R2. Advisory — 머지 차단 금지

- **Default**: hook은 위반 발견해도 종료 코드 0. 머지 자체를 차단 안 함
- **Forbidden**:
  - 위반 시 머지 abort (이미 일어난 머지 되돌릴 수 없음)
  - 머지 직후 자동 코드 수정
- **Why**: 발견·보고가 안전 영역. 자동 fix는 사용자 의도 모른 채 외부 변경 덮어쓰기 위험

### R3. 보고서 → 후속 PR

- **Default**: HIGH 위반 1건 이상 발견 시 다음 작업으로 후속 작업 티켓 정리 제안
- **Forbidden**: HIGH 위반 보고서에만 두고 작업 종료

### R4. 자동 수정 금지

- **Default**: hook은 검출만. 자동 수정 안 함
- **Forbidden**:
  - 자동 origin 주석 생성 (담당자 / 마지막 동기화 정보 부재)
  - 자동 schema 충돌 해결
  - 자동 fragment 침범 정정

### R5. 검사 추가/삭제 절차

- **Default**: 검사 항목 추가/삭제는 본 rule + `post_merge_incoming_review.py` 동시 갱신
- **Forbidden**: 스크립트만 수정하고 rule 미갱신 (drift)

## 환경변수

- `INCOMING_REVIEW_SKIP=1` — 비활성화

## 금지 패턴

- hook 출력을 사용자에게 보고 안 함 — R1
- HIGH 위반 후속 PR 없이 닫음 — R3
- hook이 자동 수정 시도 — R4
- 검사 항목 추가 + rule 미갱신 — R5

## 리뷰 포인트

- [ ] 머지/pull/rebase 직후 docs/ai/incoming-review/ 보고서 생성
- [ ] HIGH 위반 후속 작업 티켓 연결
- [ ] hook 종료 코드 0 (advisory)

## 관련

- script: `scripts/ai/hooks/post_merge_incoming_review.py`
- skill: `review-incoming-merge`
- rule: `92-dependency-and-regression-gate` R5/R8, `95-production-code-critical-review` R1, `96-external-contract-integrity` R1, `93-branch-merge-gate`
- 보고서: `docs/ai/incoming-review/`
