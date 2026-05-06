# M-B1 — Redfish 공통계정 (account_provision) flow 분석 (read-only)

> status: [PENDING] | depends: — | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "redfish 공통계정 생성 및 그것을 이용한 개더링부터 검증해봐."

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (account_service_provision @ line 2157, 호출 @ line 2581), `redfish-gather/tasks/account_service.yml`, `redfish-gather/tasks/load_vault.yml` |
| 영향 vendor | 5 vendor (Dell / HPE / Lenovo / Supermicro / Cisco). F49/F50 호환성 + 신규 vendor 4 (Huawei / Inspur / Fujitsu / Quanta) |
| 함께 바뀔 것 | (분석 only) |
| 리스크 | LOW (read-only) |
| 진행 확인 | M-B2 5 vendor 매트릭스 검증 입력 |

## 사전 컨텍스트 (F49/F50 commit history)

| commit | 의미 |
|---|---|
| `13bcbd5a` | feat: F49 redfish account_provision 호환성 강화 |
| `7144073e` | feat: F50 Cisco AccountService 표준 지원 + infraops 5 vendor 통일 |
| `e6d69538` | feat: F50 phase3 전 vendor 호환성 + Dell BMC OEM DelliDRACCard |
| `3fa39dec` | feat: F50 phase4 Lenovo XCC 권한 cache 손상 fix + verify-fallback |

→ 본 ticket = F49+F50 phase1~4 코드의 5 vendor flow 정적 분석.

## 분석 대상 (Session-0 grep 결과)

### 정의

- `redfish_gather.py:2157` — `def account_service_provision(...)`
- `redfish_gather.py:2581` — 호출 site

### Ansible task

- `redfish-gather/tasks/account_service.yml` (128 lines)
  - flow: vault accounts (role=primary) → vendor 분기 (account_service_provision invoke) → meta 기록 (password 미포함)
- `redfish-gather/tasks/load_vault.yml` (88 lines)
  - flow: `vault/redfish/{profile}.yml` → `_rf_accounts` (vault file 의 list 순서 유지)

### Vault 2단계 (rule 27 R3)

1. ServiceRoot 무인증 GET → vendor 추출
2. vendor 결정 후 `vault/redfish/{vendor}.yml` 동적 로드
3. 인증 본 수집 + account_service_provision (옵션)

## 작업 spec (Session-0 분석 → 산출물)

### (A) account_service_provision flow 다이어그램 (Mermaid — rule 41)

5 vendor 분기 + 권한 cache + verify-fallback 분기 모두 표현. AS-IS / TO-BE 쌍 (F49 → F50 phase4 비교).

### (B) 5 vendor × 단계 매트릭스

| 단계 / vendor | Dell iDRAC | HPE iLO | Lenovo XCC | Supermicro | Cisco CIMC |
|---|---|---|---|---|---|
| AccountService endpoint | `/redfish/v1/AccountService/Accounts` | 동일 | 동일 | 동일 | 동일 |
| OEM extension | `Oem.Dell.DellAccount` | `Oem.Hpe.Privileges` | `Oem.Lenovo.OemAccountService` | (없음) | `LoginRole / RemoteRole` (M5+) |
| 권한 cache | iDRAC 8 / 9 / 10 차이 | iLO 5 / 6 / 7 차이 | XCC v2 / v3 차이 + F50 phase4 손상 fix | AMI MegaRAC | F50 phase 통일 |
| verify-fallback | (있음, F50 phase4) | (있음, F50 phase4) | (있음, F50 phase4) | (있음) | (있음) |

→ 본 매트릭스 = M-B2 입력. F49 / F50 phase1~4 변경 추적.

### (C) infraops_account_provision (cycle 2026-05-01 새 어휘)

`infraops_account_provision` 가 5 vendor 통일 후 어떻게 동작하는지:
- vendor 분기 → 통일 path
- F50 phase3 commit `e6d69538` 에서 infraops 통일

→ 매트릭스 (B) 의 "통일 후" 컬럼 추가.

### (D) 신규 vendor 4 (Huawei / Inspur / Fujitsu / Quanta) 의 account_service 동작

cycle-019 phase 2 추가된 4 vendor (priority=80, lab 부재) 에서:
- AccountService endpoint 표준 따라가는지
- OEM 분기 필요 여부 (web 검색 origin 주석 — rule 96 R1-A)

→ M-D2 web 검색과 연계.

## 회귀 / 검증

- (분석 only)
- 정적 검증: `python -m ast` redfish_gather.py / yamllint account_service.yml

## risk

- (LOW) 분석 누락 시 M-B2 매트릭스 부정확 → M-B3 회귀 불완전

## 완료 조건

- [ ] (A) account_service_provision flow Mermaid (rule 41 준수: 30 노드 이내, AS-IS/TO-BE 쌍, ASCII 태그)
- [ ] (B) 5 vendor × 단계 매트릭스 (10 row × 5 col)
- [ ] (C) infraops 통일 후 동작 명시
- [ ] (D) 신규 vendor 4 의 account_service 동작 추정 + web 검색 후속 trigger
- [ ] commit: `docs: [M-B1 DONE] account_provision flow 5+4 vendor 매트릭스`

## 다음 세션 첫 지시 템플릿

```
M-B1 account_provision flow 분석 진입.

읽기 우선순위:
1. fixes/M-B1.md (본 ticket)
2. redfish-gather/library/redfish_gather.py:2157 (정의)
3. redfish-gather/library/redfish_gather.py:2581 (호출)
4. redfish-gather/tasks/account_service.yml (128 lines)
5. redfish-gather/tasks/load_vault.yml (88 lines)
6. F49 / F50 phase1~4 commit (git log --grep='F49\|F50' --oneline)

산출물 (M-B1.md 의 "작업 spec" 절 채움):
- (A) flow 다이어그램
- (B) 5 vendor 매트릭스
- (C) infraops 통일 동작
- (D) 신규 4 vendor 추정 + web 검색 trigger
```

## 관련

- rule 12 R1 (vendor 경계 — Allowed 영역)
- rule 27 R3 (Vault 2단계 로딩)
- rule 41 (Mermaid 시각화)
- skill: validate-fragment-philosophy
- 정본: `docs/13_redfish-live-validation.md`
