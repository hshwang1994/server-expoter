# M-C2 — Cache invalidation 메커니즘 검증

> status: [DONE] | depends: M-C1 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility | worker: Session-5

## 사용자 의도

vault 변경 자동 반영의 cache invalidation 메커니즘이 정확히 어떻게 동작하는지 검증.
M-C1 분석에서 의심 영역 5종 식별 → 본 ticket 에서 정밀 검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/load_vault.yml` (88 lines), `ansible.cfg` (fact_cache 설정), `redfish-gather/site.yml` (gather_facts: no 확인), `redfish-gather/library/redfish_gather.py` (vault accounts 사용 영역) |
| 영향 vendor | 9 vendor 모두 (모두 동일한 load_vault.yml 사용) |
| 함께 바뀔 것 | (분석 결과로) M-C3 회귀 fixture |
| 리스크 top 3 | (1) fact_cache 가 의도와 다르게 동작 / (2) BMC 측 권한 cache 와 vault 캐시 혼동 / (3) ansible-vault decrypt 캐시 동작 |
| 진행 확인 | M-C1 [DONE] 후 진입 |

## 정밀 검증 (M-C1 의심 영역 5종)

### (1) fact_cache (Redis) 영향 — 검증 완료

**검증 명령**:
```bash
grep -rn "cacheable" redfish-gather/ common/         # → 0 hits (production 코드)
grep -rn "fact_caching" ansible.cfg                  # → 0 hits (프로젝트), 주석만
grep -rn "gather_facts" redfish-gather/              # → site.yml:21 "gather_facts: no"
```

**결과**:
- 프로젝트 `ansible.cfg`: fact_caching 설정 **0건** (line 49-51 주석만 — "Agent 공통 설정에서 관리")
- production 코드: `cacheable: yes` 사용 **0건**
- `redfish-gather/site.yml:21`: `gather_facts: no` 명시 (host facts 자체 수집 안 함)

**Agent 공통 fact_cache 설정** (`tests/reference/agent/.../cmd_ansible_cfg.txt`):
```ini
fact_caching            = redis
fact_caching_connection = 10.100.64.153:6379:0:<masked>
fact_caching_timeout    = 86400
```

**결론**: Agent 공통 ansible.cfg 에 Redis fact_cache 설정은 있으나:
- `gather_facts: no` (site.yml) → host facts 자체 수집 안 함 → fact_cache 진입 안 함
- `_rf_vault_data` / `_rf_accounts` / `_rf_vault_profile` 모두 `cacheable: yes` 미사용 → fact_cache 진입 안 함
- → **fact_cache 는 vault 변수와 완전 무관**. 자동 반영 영향 0.

### (2) Ansible host vars 영향 — 검증 완료

**검증 대상**: `_selected_adapter` 의 캐시 여부.

**lookup plugin 동작** (`lookup_plugins/adapter_loader.py`):
- adapter_loader 는 lookup plugin → 매 task `lookup('adapter_loader', ...)` 호출 시 새로 평가
- adapter scan 결과는 lookup 호출 결과로만 반환 (변수 저장 시점부터 task scope)
- `_selected_adapter` set_fact (`detect_vendor_via_redfish.yml` 또는 site.yml) 도 cacheable 미사용

**결론**:
- adapter_loader 는 매 run lookup → 캐시 없음
- `_selected_adapter.credentials.profile` (= `_rf_vault_profile`) 도 매 run 새로 평가
- → vault 변경 시 다음 run 자동 반영

### (3) multi-account fallback — 검증 완료

**load_vault.yml line 65-80 정규화 로직**:
```yaml
_rf_accounts: >-
  {{ (_rf_vault_data | default({})).accounts | default([])
     if ((_rf_vault_data | default({})).accounts | default([])) | length > 0
     else (
       [{
         'username': (_rf_vault_data | default({})).ansible_user | default(''),
         'password': (_rf_vault_data | default({})).ansible_password | default(''),
         'label':    'legacy_single',
         'role':     'primary'
       }]
       if ((_rf_vault_data | default({})).ansible_user | default('')) != ''
       else []
     )
     }}
```

**결론** (load_vault.yml 주석 라인 6-8 참조):
- 별도 role-based 정렬 **없음** — vault YAML 의 accounts list 순서가 곧 fallback 시도 순서
- 관례: `list[0] = role=primary` (provision target = infraops), `list[1...] = role=recovery`
- vault file `accounts[0].password` 변경 → 다음 run 의 primary 인증 시도에 즉시 반영
- legacy `ansible_user/password` 도 `accounts` 키 부재 시 자동 변환 (단일 primary entry)
- `accounts[1+]` recovery 변경 시 → primary 실패 시 fallback 자격으로 사용 (다음 run 즉시)

### (4) encrypted vault decrypt 캐시 — 검증 완료

**검증**:
- `include_vars` 는 ansible 표준 — 매 task 호출 시 disk read + (encrypted 시) ansible-vault decrypt
- 캐시 메커니즘 부재 (ansible 코어 동작)
- VAULT_PASSWORD_FILE / `--ask-vault-pass` 사용 — 결과 캐시 X

**결론**:
- 표준 ansible-vault → decrypt 캐시 없음 → 매 run 새로 decrypt → 자동 반영

### (5) F50 phase4 BMC 권한 cache (vault 와 별개 layer) — 검증 완료

**검증**:
- F50 phase4 commit `3fa39dec` (`redfish_gather.py:2229~2329`):
  - line 2229: full body PATCH 의무 (Password + Enabled + Locked + RoleId)
  - line 2266: PATCH 후 `_get(Systems, target_user, target_pass)` verify
  - line 2278: 401 verify 시 DELETE+POST 재생성 fallback (vendor != dell)
- BMC 측 권한 cache 는 BMC 펌웨어 메모리 — vault file invalidation 과는 다른 layer

**결론**:
- vault 자동 반영 (다음 ansible run) 과 BMC 권한 cache (BMC 펌웨어) 는 **분리된 문제**
- vault file 변경 후 다음 run 에서 BMC 가 새 password 받음 → BMC 가 권한 cache 갱신 (BMC 동작)
- BMC 가 권한 cache 손상 (Lenovo XCC v3 OpenBMC 1.17.0 같은 사례) 시 F50 phase4 verify-fallback (DELETE+POST 재생성) 으로 graceful 처리

## 산출물

### (A) cache 매트릭스 (확정)

| # | 변수 / 캐시 | 캐시 위치 (scope) | TTL | invalidation trigger | vault 변경 자동 반영? |
|---|---|---|---|---|---|
| 1 | `_rf_vault_data` | task scope (include_vars name=) | task run 종료 | 매 task 진입 시 새로 include_vars | **YES** — 매 run include_vars 가 file 다시 읽음 |
| 2 | `_rf_accounts` | host scope (set_fact 기본) — `cacheable: yes` 미지정 | host run 종료 | 매 ansible run 새로 set_fact | **YES** — `_rf_vault_data` 새로 읽힘 → 매번 재계산 |
| 3 | `_rf_vault_profile` | host scope (set_fact) — `cacheable: yes` 미지정 | host run 종료 | adapter 선택 결과 변경 시 | **YES** — adapter 자체 매 run lookup. fast-path 캐시 없음 |
| 4 | `_rf_vault_loaded` | host scope (set_fact) | host run 종료 | 매 run | **YES** (boolean 단순 redo) |
| 5 | host facts (gather_facts) | Redis fact_cache (Agent 공통) | 86400s (24h) | gather_facts 결과 변경 | **무관** — `gather_facts: no` (site.yml:21). vault 변수는 fact_cache 안 들어감 |
| 6 | BMC 측 권한 cache (Lenovo XCC 등) | BMC 펌웨어 메모리 | vendor / 펌웨어 별 | DELETE+POST 재생성 (F50 phase4 line 2278) | **분리** — vault rotate 와 다른 layer. F50 phase4 verify-fallback 으로 graceful 처리 |
| 7 | adapter scan 결과 (`_selected_adapter`) | host scope (set_fact) — `cacheable: yes` 미지정 | host run 종료 | adapter YAML 변경 또는 BMC 응답 변경 시 | **YES** (간접 — adapter 가 vault 와 무관하지만 매 run 새로) |

### (B) 자동 반영 시나리오 검증 결과 (5건)

| # | 시나리오 | 입력 | 동작 | 결과 |
|---|---|---|---|---|
| 1 | vault file primary password 변경 | `vault/redfish/dell.yml` `accounts[0].password` 값 갱신 | 다음 run `include_vars` 가 새 file 읽음 → `_rf_accounts[0].password` 갱신 → `try_one_account` 가 새 password 로 BMC 인증 | **YES** — 다음 run 자동 반영 |
| 2 | vault file 새 account 추가 | `accounts` list 에 신규 entry append (예: `{username, password, label, role: recovery}`) | 다음 run `_rf_accounts` length +1 → primary 실패 시 새 recovery 후보로 fallback 시도 | **YES** — 다음 run 자동 등재 |
| 3 | vault file `accounts[0].role` 변경 | `primary` → `recovery` 변경 | 다음 run `try_one_account` 의 role 분기 변경. `account_service.yml` 진입 조건 (`_rf_used_account.role == 'recovery'`) 도 함께 영향 | **YES** — 다음 run 반영. 단 운영 의도상 role 변경은 신중 (P2 account_service auto-recovery trigger) |
| 4 | ansible-vault rekey | `ansible-vault rekey vault/redfish/dell.yml` (새 vault password) | 다음 run 시 ansible 의 vault password file (`.vault_pass` 또는 Jenkins credentials binding) 도 새 키로 갱신 필요 → 갱신 후 decrypt 정상 → `_rf_vault_data` 정상 로드 | **PARTIAL** — vault file 자체는 자동 반영. 단 ansible 측 vault password 도 함께 갱신해야 함 (운영 절차) |
| 5 | playbook run **중** vault 변경 | run N 진행 중 (load_vault.yml 이미 끝난 후) file 수정 | 현 run N 은 이미 `_rf_vault_data` task scope 캐시에 들어가 있어 영향 없음. 다음 run N+1 에서 새 file 읽음 | **NO (현 run 중) / YES (다음 run)** — single-run 중간 변경은 의도상 미지원 |

### (C) 사용자 답변 정리

> **Q (사용자 명시 2026-05-06)**: "redfish 공통계정의 패스워드가 vault 가 변경됐다면 자동으로 변경되는지 확인하고."

> **A (M-C1 + M-C2 검증 결과)**:
> **YES (다음 ansible-playbook run 부터 자동 반영) — 단 1 가지 단서.**

#### 근거 (4종)

1. **`include_vars` 는 캐시 없음** (`load_vault.yml:29-36`):
   - 매 task 진입 시 disk read + ansible-vault decrypt
   - 별도 cache 메커니즘 부재 (ansible 코어 동작)

2. **`set_fact _rf_accounts` 는 host run scope** (`load_vault.yml:64-80`):
   - `cacheable: yes` 옵션 미사용 → fact_cache (Redis) 진입 안 함
   - 매 ansible run 새로 set_fact → vault file 변경분 자동 반영

3. **`gather_facts: no`** (`redfish-gather/site.yml:21`) + ansible.cfg `gathering=explicit`:
   - host facts 자체를 수집 안 함 → fact_cache (Redis) 와 vault 는 무관

4. **F50 phase4 의 BMC 권한 cache 와는 분리된 layer**:
   - F50 phase4 (commit `3fa39dec`): PATCH password 후 BMC 측 권한 401 cache 손상 fix
   - vault file 자체의 자동 반영과는 별개 — vault password 가 BMC 인증에 즉시 통함
   - BMC 가 권한 cache 손상 시 F50 phase4 의 DELETE+POST 재생성 fallback 으로 graceful 처리

#### 단서 (PARTIAL 영역)

- **single playbook run 중 vault 변경**: load_vault.yml 이 이미 실행된 후 file 수정 시 현 run 은 task scope 캐시 사용 → 다음 run 부터 반영 (시나리오 5).
- **ansible-vault rekey**: vault file rekey 시 ansible 측 vault password (Jenkins credentials binding 또는 `.vault_pass`) 도 함께 갱신 필요 (시나리오 4).
- **BMC 측 인증 lock-out**: vault password 와 BMC 측 password 불일치 시 BMC 가 lock 걸 수 있음 (F49/F50 의 multi-account fallback 으로 graceful degradation).

### (D) BMC 권한 cache vs vault 자동 반영 분리 명시

| 영역 | 위치 | 갱신 trigger |
|---|---|---|
| **vault 자동 반영** | server-exporter Ansible run | vault file 변경 → 다음 run 자동 |
| **BMC 권한 cache** | BMC 펌웨어 메모리 | (a) BMC 자체 cache TTL / (b) DELETE+POST 재생성 (F50 phase4 fallback) / (c) BMC 재시작 |

**상호작용**:
- vault password 변경 → 다음 run 새 password 로 인증 시도 → BMC 가 받음 → 인증 OK
- 일부 BMC (Lenovo XCC v3 OpenBMC 1.17.0) 가 PATCH password 후 권한 cache 손상 → F50 phase4 verify-fallback 진입 → DELETE+POST 재생성 → BMC cache 강제 재구축

→ vault 자동 반영 메커니즘은 BMC 권한 cache 와 **독립적으로 동작**. M-C 영역과 F50 phase4 (M-B 영역) 분리 정상.

## 회귀 / 검증

### 정적 검증 결과 (2026-05-06 실측)

| 검증 | 결과 |
|---|---|
| `grep -rn "cacheable" redfish-gather/ common/` | 0 hits (production 코드) |
| `grep -rn "fact_caching" ansible.cfg` | 0 hits (프로젝트 ansible.cfg 주석만) |
| `grep -rn "gather_facts" redfish-gather/site.yml` | line 21: `gather_facts: no` |
| `python scripts/ai/verify_harness_consistency.py` | PASS |
| yamllint load_vault.yml | PASS |

### M-C3 회귀 mock 입력

본 ticket 검증 결과 → M-C3 에서 다음 mock 추가:

1. `tests/fixtures/vault/dell_password_v1.yml` (초기)
2. `tests/fixtures/vault/dell_password_v2.yml` (변경 후)
3. `tests/unit/test_vault_dynamic_loading.py` — 시나리오 1/2/3 mock 검증
4. `tests/unit/test_vault_rekey_partial.py` — 시나리오 4 ansible-vault rekey
5. `tests/unit/test_single_run_no_midway_invalidation.py` — 시나리오 5 (run 중 변경 NO)

→ M-C3 에서 위 5건 추가.

## risk

- (LOW) 분석 결과 가 M-C1 예상과 모두 일치 — 사용자 답변 확정
- (MED — 문서화) 사용자가 "single run 중 vault 변경" 기대 시 — 시나리오 5 답변으로 명시
- (LOW) ansible.cfg 에 fact_caching 설정 0 건 — Agent 공통 설정 변경 시 영향 검토 필요 (운영 절차)

## 완료 조건

- [x] (A) cache 매트릭스 7 row 확정
- [x] (B) 시나리오 5건 검증 결과 (YES 4 / PARTIAL 1 / NO 1)
- [x] (C) 사용자 답변 정리 (YES + 근거 4종 + 단서 3개)
- [x] (D) BMC 권한 cache vs vault 자동 반영 분리 명시
- [x] 정적 검증 PASS (cacheable 0 / fact_caching 0 / gather_facts: no)
- [x] M-C3 회귀 mock 5건 입력
- [ ] commit: `docs: [M-C2 DONE] vault cache invalidation 검증 — 자동 반영 YES (다음 run 부터)`

## 다음 세션 첫 지시 템플릿

```
M-C2 검증 완료 → M-C3 회귀 mock 진입.

선행: M-C1 [DONE] + M-C2 [DONE]
산출물: vault dynamic loading mock 5건 + pytest
```

## 관련

- rule 27 R3 (Vault 2단계 로딩)
- skill: rotate-vault (vault 회전 절차 — M-C 결과로 보강)
- F50 phase4 commit (3fa39dec)
- 정본: M-C1.md (의심 5종 + cache 매트릭스 + 시나리오 5)
- 정본: load_vault.yml + ansible.cfg + redfish-gather/site.yml

## 분석 / 구현

(cycle 2026-05-11 Phase 7 추가 stub — 본 ticket 의 분석 / 구현 내용은 본문 다른 절 (## 컨텍스트 / ## 현재 동작 / ## 변경 / ## 구현 등) 참조. cycle DONE 시점에 cold-start 6 절 정본 도입 전 작성된 ticket.)
