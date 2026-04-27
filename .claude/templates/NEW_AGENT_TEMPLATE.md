---
name: <agent-name>
description: {WHAT: agent의 역할}. **호출 시점**: {언제 이 agent를 호출하는가}.
tools: ["Read", "Grep", "Glob"]
model: {sonnet | opus | haiku}
---

# {Agent 한국어 이름} ({english-name})

당신은 server-exporter의 **{역할}** 전문 에이전트다.

## 역할

{1-3 줄로 무엇을 하는 agent인가}

1. {담당 1}
2. {담당 2}
3. {담당 3}

## 입력

- {input from caller agent or user}

## 출력 형식

```markdown
## {결과 섹션}
- ...
```

## 절차

1. {step}
2. {step}

## server-exporter 도메인 적용

- 주 대상: {channel / module / file pattern}
- 영향 vendor: {agnostic / specific}
- 호출 빈도: {high / medium / low}

## 절대 하지 말 것

- {forbidden 1}
- {forbidden 2}

## 자가 검수 금지 (rule 25 R7)

본인이 수정한 결과를 본인이 검수/승인하지 말 것. 검수는 지정된 별도 reviewer에게 위임.

## 분류

- 도메인 워커 / 리뷰어 / 코디네이터 / 자기개선 / 신규 server-exporter 고유 중 하나

## 참조 Skill

- {skill-name}

## 위임 규칙

- {다음 단계 누구에게 위임}
