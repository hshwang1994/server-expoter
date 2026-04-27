# 실측 증거 lifecycle

> 매번 실측 vs 컨텍스트 낭비. TTL + 무효화 trigger를 미리 best-practice로 고정.

## 적용 대상

- AI가 코드 변경/설계/리팩토링 중 "현재 상태"를 참조하는 모든 장면
- 11종 측정 대상 (`.claude/policy/measurement-targets.yaml` 참조)

## 배경

- AI가 추정값을 실측값으로 착각하여 코드 작성
- 매번 전수 실측 시 컨텍스트/시간 낭비
- 실측했던 값이 stale 한 상태에서 재사용

## 목표 규칙

### R1. 측정 대상 카탈로그 (Best-Practice 고정)

서버-exporter 11종 (정본: `.claude/policy/measurement-targets.yaml`):

| # | 대상 | TTL | 무효화 trigger |
|---|---|---|---|
| 1 | 출력 schema (sections + field_dictionary) | 14일 | sections.yml/field_dictionary.yml/build_*.yml 수정 |
| 2 | PROJECT_MAP | 7일 | 디렉터리 추가/삭제 |
| 3 | 벤더 어댑터 매트릭스 | 14일 | adapters/*.yml/vendor_aliases.yml 수정 |
| 4 | callback URL endpoint | 7일 | Jenkinsfile* 수정 |
| 5 | Jenkinsfile cron 인벤토리 | 14일 | Jenkinsfile* cron 변경 |
| 6 | 하네스 표면 카운트 | 1일 | .claude/ 추가/삭제 |
| 7 | 벤더 baseline | 30일 | baseline JSON 수정 / 실장비 검증 |
| 8 | Fragment 토폴로지 | 14일 | gather/normalize 코드 수정 |
| 9 | 브랜치 갭 (origin/main) | 세션 동안 | merge/pull/branch 전환 |
| 10 | 벤더 경계 위반 | 커밋마다 | 커밋 |
| 11 | 외부 시스템 계약 (Redfish path 등) | 90일 | 펌웨어 업그레이드 / API path 변경 |

### R2. AI 실측 수행 절차

```
Step 1  저장 위치에서 캐시된 값 조회
Step 2  TTL / trigger 확인
        ├─ 만료/무효화 → 재측정 (Step 3)
        └─ 유효 → 재사용 (Step 4)
Step 3  재측정 + 저장 위치 갱신 + "재측정 수행" 명시
Step 4  캐시 사용 + "캐시 사용 (last measured: YYYY-MM-DD)" 명시
```

**Forbidden**:
- TTL/trigger 확인 없이 "대충 맞을 것" 가정
- 재측정 후 저장 위치 갱신 누락
- 캐시 사용 시 "언제 측정"을 사용자에게 알리지 않음

### R3. 새 측정 대상 추가 절차

1. rule 28 R1 표 + measurement-targets.yaml 동시 갱신
2. 필요 시 저장 위치 (docs/ai/catalogs/*.md) 신규
3. 필요 시 측정 스크립트 (scripts/ai/measure_*.py)
4. 사용자 승인 후 정식 반영

**Forbidden**: AI가 작업마다 즉흥으로 "이건 실측해두자" 판단.

### R4. 자동 재측정 trigger Hook

| Hook | trigger | 재측정 대상 |
|---|---|---|
| post-merge | merge/pull | #9 브랜치 갭 |
| post-commit | commit | #10 벤더 경계 (verify_vendor_boundary) |
| post-commit | commit | #6 하네스 표면 (pre_commit_harness_drift) |
| post-commit | schema 변경 | #1 출력 schema (post_commit_measurement_trigger) |

### R5. 컨텍스트 비용 관리

- 한 세션에서 같은 측정 대상은 1회만 재측정 (재방문 시 세션 캐시)
- 작은 수정 1건 위해 대상 3개 이상 전수 재측정 금지

### R6. 재검토 조건

- 6개월간 무효화 0건 → TTL 완화
- stale 캐시로 사고 2건 이상 → TTL 축소 + trigger 추가

## 금지 패턴

- TTL/trigger 확인 없이 측정 대상 참조 — R2
- 재측정 후 갱신 누락 — R2
- 캐시 사용 시 "언제 측정" 명시 안 함 — R2
- 매번 전수 재측정 — R5
- 즉흥 측정 대상 추가 — R3

## 리뷰 포인트

- [ ] 답변에 참조한 실측값의 측정 일자 명시
- [ ] 무효화 trigger 발생 후 재측정 수행
- [ ] 새 측정 대상이 R1 표 + YAML에 반영

## 관련

- skill: `measure-reality-snapshot`
- policy: `.claude/policy/measurement-targets.yaml`
- catalogs: docs/ai/catalogs/*
