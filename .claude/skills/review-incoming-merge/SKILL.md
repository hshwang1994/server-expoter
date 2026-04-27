---
name: review-incoming-merge
description: 머지 / pull / rebase로 들어온 신규 코드를 자동 비판적 검증 + 후속 작업 가이드. rule 97 진입점. 사용자가 "머지로 들어온 코드 리뷰", "들어온 변경 검사" 등 요청 시 또는 자동 hook이 발동 안 한 환경에서 수동. - merge / pull / rebase 직후 / 다른 브랜치 동기화 직후 검증
---

# review-incoming-merge

## 목적

`scripts/ai/hooks/post_merge_incoming_review.py` 자동 hook의 사용자 진입점. 머지 차단 안 함 (advisory).

## 자동 검사 5종 (rule 97 R1)

(a) **Jenkinsfile cron 변경** (rule 80 + 92 R5)
(b) **Ansible/Python/YAML 의심 패턴** (rule 95 R1):
   - raw 모듈 권한 (become 누락)
   - vault 변수 평문 누설
   - 다른 gather의 fragment 침범 (rule 22)
(c) **Adapter YAML metadata origin 주석 누락** (rule 96 R1)
(d) **schema/sections.yml + field_dictionary.yml 동시 변경** (버전 충돌 의심)
(e) **결과 보고**: docs/ai/incoming-review/<날짜>-<sha>.md

## 절차

1. **post_merge_incoming_review.py 실행** (자동 또는 수동):
   ```bash
   python scripts/ai/hooks/post_merge_incoming_review.py
   ```
2. **결과 보고서 출력 위치**: docs/ai/incoming-review/<날짜>-<sha>.md
3. **HIGH 위반 1건 이상**:
   - rule 97 R3에 따라 후속 작업 티켓 정리 제안
   - docs/ai/NEXT_ACTIONS.md에 P1 추가
4. **clean인 경우**: 보고서에 "자동 검출 위반 없음" 기록

## Forbidden (rule 97 R2-R4)

- 위반 발견 시 머지 abort (이미 일어난 머지)
- 자동 코드 수정 (사용자 의도 모른 채 외부 변경 덮어쓰기)
- HIGH 위반을 보고서에만 두고 작업 종료

## 적용 rule / 관련

- **rule 97** (incoming-merge-review) 정본
- rule 92 R5 / R8, rule 95 R1, rule 96 R1, rule 22, rule 80
- script: `scripts/ai/hooks/post_merge_incoming_review.py`
- 보고서: `docs/ai/incoming-review/`
