# M-C2 — Cache invalidation 메커니즘 검증

> status: [PENDING] | depends: M-C1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

vault 변경 자동 반영의 cache invalidation 메커니즘이 정확히 어떻게 동작하는지 검증.
M-C1 분석에서 의심 영역 5종 식별 → 본 ticket 에서 정밀 검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/load_vault.yml`, `ansible.cfg` (fact_cache 설정), `redfish-gather/library/redfish_gather.py` (vault accounts 사용 영역) |
| 영향 vendor | 9 vendor 모두 |
| 함께 바뀔 것 | (분석 결과로) M-C3 회귀 fixture |
| 리스크 top 3 | (1) fact_cache 가 의도와 다르게 동작 / (2) BMC 측 권한 cache 와 vault 캐시 혼동 / (3) ansible-vault decrypt 캐시 동작 |
| 진행 확인 | M-C1 [DONE] 후 진입 |

## 검증 대상 (M-C1 의심 영역 5종)

### (1) fact_cache (Redis) 영향

**검증**:
- `ansible.cfg` 의 `fact_caching = redis` + `fact_caching_timeout` 확인
- `_rf_vault_data` / `_rf_accounts` 가 host facts 인지 task 변수인지 명시
- `set_fact: cacheable: yes` 사용 여부 grep

**예상**:
- `_rf_vault_data` 는 `include_vars` 결과 → task 변수 (cacheable 옵션 없으면 cache 안 됨)
- `_rf_accounts` 는 `set_fact` (cacheable 옵션 미사용 → host run scope)
- → fact_cache 영향 없음

### (2) Ansible host vars 영향

**검증**:
- `_selected_adapter` 가 어디서 오는지 (lookup plugin / 동적 평가)
- adapter_loader 가 실행마다 동작하는지 캐시되는지
- `_rf_vault_profile` 의 source

**예상**:
- adapter_loader 는 매 run lookup → 캐시 없음
- `_selected_adapter.credentials.profile` 도 매 run 새로
- → 자동 반영

### (3) multi-account fallback

**검증**:
- `_rf_accounts` 는 list 순서 그대로 (load_vault.yml 주석)
- vault file `accounts` list 순서 = fallback 시도 순서
- list[0] = primary (= account_service_provision target), list[1+] = recovery (= 진입 자격)

**예상**:
- vault file `accounts[0].password` 변경 → 다음 run 의 primary 인증 시도에 즉시 반영
- account_service_provision 이 list[0] 의 새 password 로 인증 시도

### (4) encrypted vault decrypt 캐시

**검증**:
- ansible-vault encrypt 된 파일은 매 run decrypt (캐시 없음, 표준 동작)
- VAULT_PASSWORD_FILE / `--ask-vault-pass` 만 사용 — 결과 캐시 X

**예상**:
- 표준 ansible-vault → 캐시 없음 → 자동 반영

### (5) F50 phase4 BMC 권한 cache (vault 무관)

**검증**:
- F50 phase4 commit `3fa39dec` 은 BMC 측 권한 cache 손상 fix
- vault 자동 반영과 별개 (BMC 펌웨어 cache, 벤더별 차이)
- verify-fallback (account_service_provision 후 재인증 시도) 가 BMC cache 깨졌을 때 진입

**예상**:
- vault file 변경 자동 반영 영향 없음 (별 layer)
- 단, BMC 권한 cache 깨졌을 때 verify-fallback 이 새 vault credential 로 재시도

## 검증 spec (산출물)

### (A) cache invalidation 매트릭스 확정

M-C1 (B) 매트릭스를 정밀 검증 결과로 확정.

| 변수 / 캐시 | 캐시 위치 | TTL | invalidation | 자동 반영? |
|---|---|---|---|---|
| `_rf_vault_data` | task | task run | 매 task | YES |
| `_rf_accounts` | host run | host run | 매 ansible run | YES |
| `_rf_vault_profile` | host run | 동일 | 동일 | YES |
| host facts (gather_facts) | Redis | timeout | facts 변경 | (해당 없음 — vault 와 무관) |
| BMC 권한 cache | BMC 펌웨어 | vendor 별 | F50 phase4 verify-fallback | 부분 자동 (vendor 차이) |

### (B) 자동 반영 시나리오 검증 결과

M-C1 (C) 의 5 시나리오를 코드 기반으로 검증:

| 시나리오 | 자동 반영? | 근거 |
|---|---|---|
| (1) primary password 변경 | **YES** | include_vars 매 task 새로 |
| (2) 새 account 추가 | **YES** | accounts list 매 run 새로 |
| (3) accounts[0] role 변경 | **YES** | normalize 매 run |
| (4) ansible-vault rekey | **YES** | decrypt 캐시 없음 |
| (5) run 중 vault 변경 | **NO** | 이미 include_vars 한 캐시 사용 |

### (C) 사용자 답변 정리

> Q: vault 패스워드 변경 시 자동 반영되는지?
> A: **YES (다음 ansible-playbook 실행부터)**. single run 중간 변경은 NO. BMC 측 권한 cache 가 깨졌을 경우 verify-fallback (F50 phase4) 가 새 credential 로 재시도.

## 회귀 / 검증

- (분석 위주). M-C3 에서 mock fixture 기반 회귀 테스트 추가
- 정적 검증:
  - `grep -rn "cacheable" redfish-gather/ common/` (cacheable 사용 여부)
  - `grep -rn "fact_caching" ansible.cfg` (fact_cache 설정)
  - `python scripts/ai/verify_harness_consistency.py`

## risk

- (LOW) 검증 결과 가 M-C1 예상과 다를 경우 M-C3 시나리오 재구성
- (MED) ansible.cfg 에 `fact_caching` 설정이 의외 동작 시 추가 분석 필요

## 완료 조건

- [ ] (A) cache 매트릭스 확정
- [ ] (B) 시나리오 5건 검증 결과
- [ ] (C) 사용자 답변 정리 (YES/PARTIAL/NO + 근거)
- [ ] BMC 권한 cache vs vault 자동 반영 분리 명시 (F50 phase4 와 본 ticket 의 차이)
- [ ] commit: `docs: [M-C2 DONE] vault cache invalidation 검증 — 자동 반영 YES (다음 run)`

## 다음 세션 첫 지시 템플릿

```
M-C2 cache invalidation 검증 진입. M-C1 분석 결과 입력.

읽기 우선순위:
1. fixes/M-C2.md
2. M-C1 산출물 (cache 매트릭스 / 시나리오 5)
3. ansible.cfg (fact_caching 확인)
4. redfish-gather/library/redfish_gather.py (account_service_provision verify-fallback @ F50 phase4)

산출물:
- (A) cache 매트릭스 확정
- (B) 시나리오 5 검증
- (C) 사용자 답변 (YES + 근거)
```

## 관련

- rule 27 R3 (Vault 2단계 로딩)
- skill: rotate-vault (vault 회전 절차 — M-C 결과로 보강)
- F50 phase4 commit (3fa39dec)
