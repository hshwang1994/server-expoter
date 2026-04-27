# Convention Drift Log — server-exporter

> 발견된 컨벤션 위반 / drift / 임시 구현 기록 (append-only).
> rule 70 docs-and-evidence-policy + rule 92 R2 (즉시 수정 금지) 적용.
> drift 발견 시 즉시 추가, 마이그레이션 계획 수립 후 단계적 정리.

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

## (현재 비어있음 — drift 발견 시 추가)

Plan 1 작성 시점 기준 server-exporter는 신규 하네스 도입 단계로 자체 drift 미발견.
실제 drift는 다음 시점에 발생할 수 있음:
1. clovirone 출처 어휘가 일부 rule/skill/agent에 잔재로 남아있는 경우 (verify_harness_consistency.py가 검출)
2. 새 벤더 추가 시 origin 주석 누락 (rule 96)
3. 새 펌웨어로 외부 시스템 응답 변경 (Redfish path drift, rule 96 R4)
4. schema 변경이 baseline 갱신 누락한 경우 (rule 13)
5. Jenkins 파이프라인 cron 변경이 4-Stage 의무 우회 (rule 80)
