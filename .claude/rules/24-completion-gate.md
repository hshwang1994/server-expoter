# 완료 판정 게이트

> AI가 "완료"를 선언하려면 6 체크가 모두 PASS여야 한다.

## 적용 대상

- AI가 **"완료"**, **"끝났다"**, **"완결"** 등 종결 표현 사용 시

## 문제 배경

- AI가 "자기가 한 일"만으로 완료 판단 → 검증/후속/문서 누락
- 사용자가 "남은 작업?" 물으면 새 작업 꺼내는 반복 패턴

## 목표 규칙

### R1. 완료 체크리스트 (6 항목)

```
1. ☐ 정적 검증 전부 실행했나?
   - ansible-playbook --syntax-check (3-channel)
   - pytest tests/ (변경 영역)
   - yamllint (편집한 YAML)
   - python -m ast (편집한 Python)
   - 환경 제약으로 불가능한 것은 "환경 제약" 명시

2. ☐ 발견 가능한 버그 0건인가?
   - 테스트 실패 0건
   - schema validate FAIL 0건 (Jenkins Stage 3 등가)
   - baseline 회귀 FAIL 0건 (Jenkins Stage 4 등가)

3. ☐ 문서 4종 갱신했나?
   - docs/ai/CURRENT_STATE.md
   - docs/ai/catalogs/TEST_HISTORY.md (테스트 실행 결과)
   - 영향 docs/01~19 (해당 시)
   - 영향 ADR (docs/ai/decisions/, 결정 있을 시)

4. ☐ 후속 작업 식별 완료했나?
   - 있으면: docs/ai/NEXT_ACTIONS.md 갱신 또는 티켓 생성
   - 없으면: "후속 작업 없음" 명시

5. ☐ Git 태그 + push 완료했나?
   - 태그 (해당 시): `v{영역}-{상태}-{YYYYMMDD}` 포맷
   - 모든 commit이 origin/main에 반영 (PR/머지 후)

6. ☐ Schema/Baseline 변경 시 회귀 통과했나?
   - schema/sections.yml + field_dictionary.yml 변경 → 영향 vendor baseline 전수 회귀
   - JSON envelope 변경 → verify-json-output 통과
   - Fragment 변경 → validate-fragment-philosophy 통과
```

### R2. 금지어

6 체크 중 하나라도 미실행 상태에서 다음 단어 사용 금지:
- "완료" / "끝났다" / "완결" / "다 했다" / "진짜 끝"

대신:
- "ooo 까지 완료, △△ 남음"
- "현재 PASS, 환경 제약으로 □□ 미실행"

### R3. 사용자가 "남은 작업?" 물었을 때

3가지 답변:
1. AI 환경에서 아직 할 수 있는 것 (있으면 바로 제안)
2. AI 환경에서 할 수 없는 것 (사용자/팀 몫)
3. 의심되는 리스크

### R4. 완료 보고 포맷

```
## [PASS] 완료 (체크리스트 6/6)

- 정적 검증 : [결과]
- 버그 : [0건 / 수정 commit]
- 문서 : [4종 갱신 commit]
- 후속 : [없음 / 티켓 list]
- 태그 : v...
- 회귀 : [PASS — N vendor baseline 통과]

## [INFO] AI 환경 외 남은 것
- [사용자/팀 몫]
```

## 금지 패턴

- 6 체크 중 skip 후 "완료" — R1/R2
- "사용자/팀 몫" 라벨 남용 (AI가 할 수 있는 일 떠넘김)

## 리뷰 포인트

- [ ] 완료 보고에 체크리스트 6 항목 모두
- [ ] 금지어 사용 안 함

## 관련

- rule: `23-communication-style`
- 정본: `CLAUDE.md` Step 7
