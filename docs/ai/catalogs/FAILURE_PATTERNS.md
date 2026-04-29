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

## 2026-04-29 — user-label-vs-redfish-manufacturer-drift (cycle-015)

- 카테고리: external-contract-drift
- 발견 위치: `inventory/lab/redfish.json` ↔ 실 Redfish ServiceRoot 응답 (rule 27 R3 1단계)
- 증상: 사용자가 BMC IP에 vendor 라벨 부여 ("dell" / "cisco") 했으나 무인증 ServiceRoot 응답이 다른 Manufacturer로 회신 (`AMI` / `TA-UNODE-G1`)
- 원인:
  1. 사용자가 호스트 라벨을 OS / 사용 환경 기준으로 부여 (e.g. "이 머신에 Dell 서버 OS 깔려있음")하지만 실제 BMC는 별도 OEM
  2. Whitebox / GPU 호스트는 보드 OEM과 BMC OEM이 다른 케이스 잦음
  3. Cisco TelePresence / Tetration 같은 비-UCS 제품도 Cisco 그룹으로 통칭
- 영향:
  - rule 27 R3 1단계가 자동 검출 → graceful degradation 가능 (회귀 영향 0)
  - 단, 사용자 라벨에 의존한 inventory 작업 / vault 매핑은 잘못된 vendor 사용 위험
- 수정: 본 cycle 시점 inventory/lab/redfish.json은 `_vendor` 메타 보존 + DRIFT-011 entry로 추적. 실측 deep_probe 후 라벨 정정.
- 재발 방지:
  - **rule 27 R3 1단계 (무인증 ServiceRoot detect) 의무 — 이미 채택**
  - rule 96 R4 — drift 발견 시 3 곳 기록 의무 (이미 채택)
  - **신규 권장**: 새 BMC inventory 등록 시 사용자 라벨 + Redfish 실 응답 1회 확인 의무 (skill `add-new-vendor` 본문에 추가 권장 — 후속)
- 관련 rule: rule 27 R3 (Vault 2단계 — 1단계가 본 drift 검출), rule 96 R1 (외부계약 origin), rule 50 R1 (vendor 정규화)
- 관련 evidence: `tests/evidence/cycle-015/connectivity-2026-04-29.md` 5절

## 향후 가능 패턴 (Plan 1+2 도입 시점 예측)

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
