# Session Prompts — Human Docs Overhaul

본 cycle 은 단일 세션 모드라 prompt 분리가 필요 없습니다.
컨텍스트 한계로 분리해야 할 경우의 진입 prompt 모음.

---

## H-A 시리즈 (루트 2종)

```
docs/ai/tickets/2026-05-06-human-docs-overhaul/fixes/H-A1.md (README) 와
H-A2.md (REQUIREMENTS) ticket 의 "변경 항목" 절을 적용해서 본문을 재작성해줘.
재작성 후 ticket 본문에 [DONE] 표기.
```

## H-B 시리즈 (운영 가이드 5종)

```
H-B1 ~ H-B5 (docs/01~05) ticket 을 순서대로 적용. 각 문서마다:
- 첫 머리 도입부 유지
- 본문 재구성 (무엇을/어떻게/왜 흐름)
- 약어 풀이
- 내부 cycle 번호 제거
- 트러블슈팅 절 추가 (해당 시)
```

## H-C 시리즈 (아키텍처 7종)

```
H-C1 ~ H-C7 (docs/06~12). fragment 철학, normalize 흐름, adapter 시스템 등
개발자가 처음 읽는다고 가정. ASCII 다이어그램 / 코드 블록 1줄 설명 보강.
```

## H-D 시리즈 (검증·결정·스키마 9종)

```
H-D1 ~ H-D9 (docs/13~22). decision-log 와 json-schema-fields 가 가장 큰 작업.
시간순 / 결정 기준 / 호출자 시야 우선.
```

## H-E 시리즈 (schema YAML 6종)

```
H-E1 ~ H-E6. 헤더뿐 아니라 각 field 의 description, display_name, help_ko/help_en
표현이 사람이 읽기에 자연스러운지 확인. 의미 변경 금지 (description 뉘앙스만).
```

## H-F 시리즈 (서브 README 5종)

```
H-F1 ~ H-F5. 폴더의 정체성 / 사용 시나리오 / 다른 폴더와의 차이를 명확히.
```

---

## 자율 진행 권한

- 본 cycle 의 모든 ticket 은 사용자 명시 승인 ("모든 파일 진행해주세요. 한 세션 내에서") 으로 자율 진행.
- 의미 변경 / 정본 코드 영향 / 호출자 계약 영향 발견 시는 정지 + 사용자 확인.
