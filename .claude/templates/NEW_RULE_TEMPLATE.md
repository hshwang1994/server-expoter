# Rule NN-{kebab-slug}

> rule 00 R5 번호 가이드 표 따라 NN 선택. 본 템플릿 복사 후 채움.

## 규칙 표기 구조 (Tier 1 프레임)

본 rule의 각 항목은 **Default / Allowed / Forbidden + Why + 재검토 조건** 3단 구조.

## 적용 대상

- `<glob 패턴>` — {대상 영역}

## 현재 관찰된 현실

{왜 이 rule이 필요한지 — 실측 증거 / 사용자 피드백 / 사고 사례}

## 목표 규칙

### R1. {규칙 이름}

- **Default**: {기본 동작}
- **Allowed**: {예외 허용}
- **Forbidden**: {금지}
- **Why**: {근거 — 사고 / 회귀 / 위반 이력}
- **재검토 조건**: {언제 이 rule을 다시 보는가}

### R2. ...

(필요한 만큼 R3, R4, ... 추가)

## 금지 패턴

- {위반 사례 1} — {근거}
- {위반 사례 2} — {근거}

## 리뷰 포인트

- [ ] {check 1}
- [ ] {check 2}

## 테스트 포인트

- {테스트 명령 / 검증}

## 관련 문서

- skills: `<skill-name>`
- agents: `<agent-name>`
- policy: `.claude/policy/<file>.yaml`
- docs: `docs/...`
- 근거 이력: `docs/ai/catalogs/FAILURE_PATTERNS.md` 항목

## 승인 기록

| 일시 | 승인자 | 대상 | 비고 |
|---|---|---|---|
| YYYY-MM-DD | hshwang | 본 rule 신설 | {사유} |
