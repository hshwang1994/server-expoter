# 외부 시스템 계약 무결성 (External Contract Integrity)

> server-exporter 내부 enum / 상수 / DTO / VO가 외부 시스템 (Redfish API path / IPMI sensor / SSH 명령 출력 / WinRM session / vSphere API)의 실제 지원 집합과 drift 차단.

## 적용 대상

- 외부 시스템 연동 변수 / 상수 / 매핑 — adapter YAML의 vendor list / firmware list, vendor_aliases.yml, redfish_gather.py의 endpoint 매핑
- 외부 시스템 연동 기능 디버깅

## 목표 규칙

### R1. 외부 계약 origin 주석 의무

외부 시스템 지원 집합 / 스키마 / URL 구조를 반영하는 내부 enum / 상수는 **origin 주석** 필수:

```yaml
# adapters/redfish/dell_idrac9.yml
# 이 adapter는 Dell iDRAC9 Redfish API 5.x / 6.x 펌웨어 기준.
# 원본 위치: Dell support.dell.com / Redfish API guide
# 마지막 동기화 확인: 2026-04-27 (hshwang)
# tested_against: ["5.10.x", "6.5.x"]
# oem_path: /redfish/v1/Dell/...
priority: 100
match:
  manufacturer: ["Dell Inc.", "Dell EMC"]
  model_patterns: ["PowerEdge R7*", "PowerEdge R6*"]
  ...
```

**Allowed**: 원본 접근 불가한 경우 "문의 채널" 또는 "담당자" 명시.

**Forbidden**: 외부 시스템 반영 enum / vendor list에 origin 주석 없이 신규 값 추가/삭제/리네임.

**재검토**: origin 자동 대조 CI job (Redfish probe로 실 펌웨어와 비교) 도입 시 주석 의무 완화.

### R2. 외부 연동 기능 디버깅 시 외부 계약 질의 우선

- **Default**: 외부 시스템 연동 enum / 상수가 관여하는 버그 조사 시 **사용자에게 외부 계약 먼저 질의**. 코드만으로 추론 시작 금지
- **질의 포맷** (rule 23 WHY+WHAT+IMPACT):
  ```
  외부 계약 확인 필요 — <기능명>
  - 연동 시스템: Redfish / IPMI / vSphere / ...
  - 확인 항목: 지원 endpoint / 응답 schema / 펌웨어 지원
  - 왜: 내부 코드에 <enum/상수 경로> 있지만 외부 원본 접근권 없음
  - 결정 필요: 사용자 / 담당 개발자가 <구체 계약> 알려주시면 코드 가설 검증 1턴에 가능
  ```
- **Allowed**: 외부 계약이 `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` 또는 명시 주석에 이미 기록 있으면 질의 생략
- **Forbidden**:
  - 외부 계약 확인 없이 "내부 코드 분석만으로" 근본 원인 확정
  - 외부 원본 접근 불가로 판단하여 가설 계속 확장 (2턴 이상 연쇄 추측)

### R3. 외부 연동 enum 값 변경 시 영향 범위

외부 연동 enum (예: target_type, vendor list, sections list) 값 변경 시 **쓰임 모든 경로** 자동 탐색:

- 해당 enum을 참조하는 모든 Python / Ansible YAML 파일
- adapter 매칭 metadata (vendor / firmware / model_patterns)
- vault path (`vault/redfish/{vendor}.yml`)
- 화면이 없으므로 i18n / message 영향 없음
- baseline_v1/{vendor}_baseline.json
- vendor 별 OEM tasks (`redfish-gather/tasks/vendors/{vendor}/`)

**Forbidden**: 외부 연동 enum 값 변경 시 위 탐색 skip.

### R4. 외부 계약 drift 발견 시 기록

외부 계약 ↔ 내부 enum drift 발견 시 **3 곳에 즉시 기록**:

1. `docs/ai/catalogs/FAILURE_PATTERNS.md` — `external-contract-drift` / `external-contract-unverified` append-only
2. `docs/ai/catalogs/CONVENTION_DRIFT.md` — drift 번호 (DRIFT-XXX)
3. 해당 enum / 상수 / adapter 파일 — origin 주석에 `# DRIFT 발견 YYYY-MM-DD: <요약>` 추가

**Forbidden**: drift 발견 후 "다음 PR에서 고치면 됨"으로 기록 skip.

### R5. 재검토 (rule 자체)

- 6개월간 external-contract drift 사고 0건 → R1 주석 의무를 "리팩토링 시 append" 수준 완화
- `EXTERNAL_CONTRACTS.md` 카탈로그 완결되면 R2 질의 빈도 감소

## 금지 패턴

- adapter / vendor enum에 origin 주석 없이 추가 — R1
- 외부 연동 디버깅 시 외부 계약 질의 skip — R2
- enum 값 변경 + 영향 탐색 skip — R3
- drift 발견 + 기록 skip — R4

## 리뷰 포인트

- [ ] adapter YAML에 origin 주석 (vendor / firmware / tested_against / oem_path)
- [ ] 외부 연동 디버그 PR에 외부 계약 질의 흔적
- [ ] enum 값 변경 PR에 쓰임 탐색 결과
- [ ] drift 발견 시 3 곳 기록

## 관련

- rule: `23-communication-style` (WHY+WHAT+IMPACT), `91-task-impact-gate` R3 (외부 시스템 항목), `92-dependency-and-regression-gate` R6 (코드 우선 — 외부 시스템 예외), `95-production-code-critical-review` R1 #11, `25-parallel-agents` R7-B (Agent 추정 격상 금지)
- skill: `debug-external-integrated-feature`, `task-impact-preview`, `write-quality-tdd`
- catalog: `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` (신설), `FAILURE_PATTERNS.md`, `CONVENTION_DRIFT.md`
