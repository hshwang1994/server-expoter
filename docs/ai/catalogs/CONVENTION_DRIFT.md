# CONVENTION_DRIFT — server-exporter

> 발견된 컨벤션 위반 / 임시 구현 / 외부 계약 drift 기록 (DRIFT-XXX).
> rule 92 R2 (즉시 수정 금지) — 정상 동작 중이면 마이그레이션 계획 후 단계적 정리.

## 형식

```
## DRIFT-XXX (YYYY-MM-DD)

- 발견 위치: <file:line>
- 분류: convention-violation / temporary-impl / external-contract-drift
- 설명: <1-2줄>
- 영향: <범위>
- 제안: <수정 방향>
- 상태: open / planned / migrating / resolved
- 관련: rule N / skill X / agent Y
```

---

## (현재 비어있음)

Plan 1+2 도입 시점에는 server-exporter 자체 drift 미발견.

### 향후 가능 drift

- vendor adapter origin 주석 일부 누락 (rule 96 R1)
- Jenkinsfile 3종 4-Stage 일부 차이 (refactor 권장)
- baseline JSON 일부 vendor의 Must 필드 형식 일관성
