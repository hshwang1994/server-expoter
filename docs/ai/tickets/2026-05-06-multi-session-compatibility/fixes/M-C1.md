# M-C1 — Vault 동적 로딩 분석 (read-only)

> status: [PENDING] | depends: — | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

> "redfish 공통계정의 패스워드가 vault 가 변경됐다면 자동으로 변경되는지 확인하고."

→ vault/redfish/{vendor}.yml 파일 변경 시 다음 ansible 실행 때 자동 반영되는지 검증.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/tasks/load_vault.yml` (88 lines), `redfish-gather/site.yml` (vault 로딩 흐름), `vault/redfish/<vendor>.yml` (정본 — 자동 반영 대상) |
| 영향 vendor | 9 vendor 모두 (모두 동일한 load_vault.yml 사용) |
| 함께 바뀔 것 | (분석 only) |
| 리스크 | LOW (read-only) |
| 진행 확인 | M-C2 cache invalidation 분석 입력 |

## Session-0 분석 결과 (load_vault.yml flow)

### 정본: `redfish-gather/tasks/load_vault.yml`

```yaml
- name: "redfish | load_vault | include vault (primary)"
  ansible.builtin.include_vars:
    file: "{{ lookup('env','REPO_ROOT') }}/vault/redfish/{{ _rf_vault_profile }}.yml"
    name: _rf_vault_data
  no_log: true
  failed_when: false
```

### 핵심 메커니즘

1. **매 실행 마다 include_vars** — Ansible 의 `include_vars` 는 task run 마다 파일을 읽음 (캐시 없음)
2. **set_fact `_rf_accounts`** — vault 파일 내용을 task 변수로 정규화. 이 변수는 host facts cache 에 저장되지 않음 (task 변수, task run scope)
3. **fact_cache (Redis) 영향 없음** — `gather_facts` 결과만 fact_cache 됨. `set_fact` 는 host run scope (다음 실행 시 새로 set_fact)

### 결론 (예비)

- vault/redfish/{vendor}.yml 변경 시 → **다음 ansible-playbook 실행에서 자동 반영**
- ansible-vault encrypt/decrypt 도 매번 수행 (캐시 없음)
- single playbook run 내에서 vault 파일 중간 변경은 반영 안 됨 (이미 include_vars 한 후에는 `_rf_vault_data` 가 task 변수 캐시)

→ 사용자 질문 "자동으로 변경되는지" 의 답: **YES (다음 실행부터)**.

### 의심 영역 (M-C2 검증 대상)

1. **fact_cache (Redis) 의 영향** — `_rf_accounts` 가 set_fact 라 host facts 가 아닌데, 누군가 `cacheable: yes` 옵션 줬는지?
2. **Ansible host vars 영향** — vault profile (`_rf_vault_profile`) 이 `_selected_adapter.credentials.profile` 에서 오는데, adapter 자체가 캐시되는지?
3. **multi-account fallback** — vault accounts list[0] (primary) 변경 시 / list[1+] (recovery) 변경 시 어느 쪽이 사용?
4. **encrypted vault decrypt 캐시** — ansible-vault decrypt 결과 캐시되는지 (보통 X 이지만 검증)
5. **F50 phase4 권한 cache 손상 fix** — Lenovo XCC 권한 cache 가 vault 와 별개. 이는 BMC 측 cache 문제이지 vault 자동 반영 문제 아님

## 작업 spec

### (A) load_vault flow 다이어그램 (Mermaid — rule 41)

vault 파일 변경 → 다음 ansible 실행 시 자동 반영의 데이터 흐름. AS-IS / TO-BE 쌍 (현재 동작 / 변경 시나리오).

### (B) cache 영역 매트릭스

| 변수 / 캐시 | 캐시 위치 | TTL | invalidation trigger |
|---|---|---|---|
| `_rf_vault_data` | task scope | task run 종료 시 | 매 task 새로 |
| `_rf_accounts` | host scope (set_fact) | host run 종료 시 | 매 ansible run 새로 |
| `_rf_vault_profile` | host scope (set_fact) | 동일 | adapter 변경 시 |
| host facts (gather_facts) | fact_cache (Redis) | redis TTL | next run 또는 facts 변경 |
| BMC 측 권한 cache | BMC 펌웨어 | vendor 별 | F50 phase4 처리 |

### (C) 자동 반영 검증 시나리오

| 시나리오 | 입력 | 예상 동작 |
|---|---|---|
| (1) vault file primary password 변경 | `vault/redfish/dell.yml` accounts[0].password | 다음 run 부터 새 password 사용 |
| (2) vault file 새 account 추가 | accounts list 에 추가 | 다음 run 부터 multi-account fallback 후보로 등재 |
| (3) vault file accounts[0] role 변경 | role: primary → recovery | 다음 run 부터 primary 후보 변경 |
| (4) ansible-vault rekey | 새 vault password | 다음 run 부터 새 vault password 로 decrypt |
| (5) playbook run 중 vault 변경 | run 진행 중 file 수정 | 현 run 은 이미 include_vars 한 캐시 사용. 다음 run 새 로드 |

## 회귀 / 검증

- (분석 only)
- 정적 검증: yamllint load_vault.yml / Ansible syntax check

## risk

- (LOW) 분석 결과 부정확 시 M-C2 cache invalidation 검증 잘못된 가설
- (MED — 문서화) 사용자가 "single run 중 vault 변경" 기대했다면 — 본 분석으로 "그건 안 됨, 다음 run 부터" 명시 필요

## 완료 조건

- [ ] (A) load_vault flow Mermaid (rule 41 준수)
- [ ] (B) cache 영역 매트릭스 5 row
- [ ] (C) 자동 반영 시나리오 5건
- [ ] 사용자 질문 "자동 변경되는지" 의 명시 답변 (YES/PARTIAL/NO + 근거)
- [ ] commit: `docs: [M-C1 DONE] vault 동적 로딩 분석 + cache 매트릭스`

## 다음 세션 첫 지시 템플릿

```
M-C1 vault 동적 로딩 분석 진입.

읽기 우선순위:
1. fixes/M-C1.md (본 ticket)
2. redfish-gather/tasks/load_vault.yml (88 lines)
3. redfish-gather/site.yml (vault 로딩 흐름)
4. ansible.cfg (fact_cache / forks 설정)
5. F50 phase4 commit (3fa39dec — 권한 cache 손상 vs vault 자동 반영 분리)

산출물:
- (A) flow Mermaid
- (B) cache 매트릭스
- (C) 시나리오 5
- 사용자 답: 자동 반영 YES (다음 run 부터). single run 중은 NO.
```

## 관련

- rule 27 R3 (Vault 2단계 로딩)
- rule 41 (Mermaid)
- rotate-vault skill (vault 회전 절차)
