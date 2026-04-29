# FAILURE_PATTERNS — server-exporter

> 발견된 실패 / 오탐 / 반복 실수 기록 (append-only, rule 70 트리거).
> 새 사례 발견 시 즉시 추가. 카테고리: scope-miss / ai-hallucination / external-contract-drift / vendor-boundary-violation / fragment-violation / vault-leak / convention-drift

## 형식

```
## YYYY-MM-DD — <한 줄 요약>

- 카테고리: scope-miss / ai-hallucination / ...
- 발견 위치: <파일 또는 commit>
- 증상: <관측>
- 원인: <분석>
- 영향: <범위>
- 수정: <commit / PR>
- 재발 방지: <rule / skill / hook 변경>
- 관련 rule: rule N
```

---

## (현재 비어있음 — 첫 사례 발견 시 추가)

Plan 1+2 도입 시점에는 server-exporter 자체 사례 미발견.
참고 — clovirone에서 학습한 일반 패턴은 rule 95 R1 (의심 패턴 11종)에 흡수됨.

### 향후 가능 패턴

1. **Fragment 침범** (rule 22): gather가 다른 섹션의 fragment 변수 set_fact
2. **Vendor 하드코딩** (rule 12): common 코드에 "Dell" 등 직접 분기
3. **외부 계약 drift** (rule 96): 펌웨어 업그레이드로 Redfish path 변경 → adapter origin 주석 stale
4. **Vault 누설** (운영 권장 — cycle-011: rule 60 해제, cycle-012 vault encrypt 채택): Jenkins console log에 BMC password 노출
5. **Schema 3종 일부만 갱신** (rule 13): sections.yml만 수정하고 field_dictionary / baseline 미갱신
6. **adapter score 동률** (rule 95 R1 #4): 의도와 다른 adapter 선택
7. **Linux raw fallback 미고려** (rule 10 R4): Python 3.6 환경에서 setup 모듈 가정
8. **callback URL 후행 슬래시** (이미 commit 4ccc1d7로 fix): 입력 URL 정규화 누락
9. **Jenkinsfile cron 사용자 승인 누락** (rule 80): AI 임의 cron 변경
10. **incoming-merge 위반 무시** (rule 97): 자동 검사 보고서를 후속 PR으로 정리 안 함
