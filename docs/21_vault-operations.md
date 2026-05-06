# Vault 운영 가이드

> 정본 — M-C 학습 형식화 (cycle 2026-05-06-post). vault 자동 반영 메커니즘 + 회전 절차 + 검증 명령.
>
> 관련 rule: rule 27 R6 (vault 자동 반영 단서 3개), rule 50 R2 (vendor 추가 9단계)
> 관련 skill: rotate-vault, debug-precheck-failure
> 정본 코드: `redfish-gather/tasks/load_vault.yml` (88 lines)
> 회귀: M-C3 commit (9건 mock — vault rekey / vault edit / vendor 추가 시나리오)

---

## 1. 사용자 의도 (M-C 학습)

> "redfish 공통계정의 패스워드가 vault 가 변경됐다면 자동으로 변경되는지 확인하고."
> — cycle 2026-05-06 사용자 의심

→ vault/redfish/{vendor}.yml 파일 변경 시 다음 ansible 실행에서 자동 반영되는지 검증.

## 2. 결론 (1줄)

**YES — 다음 ansible-playbook 실행부터 자동 반영. 별도 캐시 무효화 작업 불필요.**

근거: vault 자동 반영 보장 3 단서 (rule 27 R6 정본).

---

## 3. Vault 종류

| 채널 | vault 파일 | 용도 |
|---|---|---|
| Linux | `vault/linux.yml` | SSH 자격증명 (host 공통) |
| Windows | `vault/windows.yml` | WinRM 자격증명 (host 공통) |
| ESXi | `vault/esxi.yml` | vSphere 자격증명 (host 공통) |
| Redfish | `vault/redfish/{vendor}.yml` | BMC 자격증명 (vendor별) |

**vendor 9 vault** (cycle 2026-05-06 시점):
- dell.yml, hpe.yml, lenovo.yml, supermicro.yml, cisco.yml (5 base vendor)
- huawei.yml, inspur.yml, fujitsu.yml, quanta.yml (cycle 2026-05-01 신규 4 vendor — vault SKIP, 사용자 명시 승인)

## 4. Vault 자동 반영 메커니즘 (rule 27 R6)

### 4.1 자동 반영 보장 3 단서

vault 변경 시 다음 run 자동 반영을 보장하는 3 단서. 회전 후 / 의심 시 검증:

#### 단서 1: include_vars cacheable 옵션 부재

```bash
grep -rn 'cacheable' redfish-gather/tasks/load_vault.yml
# 기대: 0 결과
```

- `cacheable: yes` 시 fact_cache (Redis) 에 host facts 로 저장 → 다음 run 에서도 stale vault 사용 위험
- 정본: `redfish-gather/tasks/load_vault.yml:29-36` (`include_vars` 호출에 `cacheable` 옵션 없음 — 매 run 디스크 read)

#### 단서 2: set_fact host facts 미등록

```bash
grep -rn 'cacheable' redfish-gather/tasks/load_vault.yml common/tasks/normalize/
# 기대: 0 결과
```

- `_rf_accounts` / `_rf_vault_data` 변수는 task scope 만
- host facts (`ansible_facts.*`) 또는 `cacheable: yes` 등록 금지
- 정본: `redfish-gather/tasks/load_vault.yml:64-81` (`set_fact` 에 `cacheable` 옵션 없음)

#### 단서 3: ansible-vault decrypt 캐시 부재

```bash
grep -rn 'vault_password_file\|vault_identity\|VAULT_PASSWORD_FILE' ansible.cfg
# 기대: vault_password_file 만 있어야 함 (decrypt 캐시 옵션 없음)
```

- Ansible 은 vault decrypt 결과 캐시 안 함 (default)
- vault password file 만 있고 decrypt 결과 캐시 옵션 없으면 매 run 새로 decrypt

### 4.2 자동 반영 흐름 (Mermaid)

> 이 그림이 말하는 것: vault/redfish/{vendor}.yml 파일을 매 ansible run 마다 새로 읽어 `_rf_accounts` 로 정규화한다. 캐시 없음 — 다음 run 자동 반영.

```mermaid
flowchart TD
    EDIT([vault/redfish/dell.yml<br/>password 변경]):::ok
    RUN_END([현재 run 종료<br/>_rf_vault_data / _rf_accounts 폐기]):::default
    NEW_RUN([ansible-playbook run N+1 시작]):::ok
    INC[["include_vars<br/>vault/redfish/dell.yml<br/>(디스크 read — 캐시 없음)"]]:::ext
    DECRYPT[["ansible-vault decrypt<br/>(매 run 수행 — 캐시 없음)"]]:::ext
    DATA[/"_rf_vault_data<br/>(task scope, no_log)"/]:::default
    NORM["set_fact _rf_accounts<br/>= vault.accounts list<br/>(task scope, no host facts)"]:::default
    USE([try_one_account.yml<br/>새 password 로 BMC 인증]):::ok

    EDIT --> RUN_END --> NEW_RUN --> INC
    INC --> DECRYPT --> DATA --> NORM --> USE

    classDef ok fill:#dfd,stroke:#3c3,stroke-width:2px,color:#000
    classDef default fill:#eee,stroke:#999,stroke-width:2px,color:#000
    classDef ext fill:#def,stroke:#39c,stroke-width:2px,color:#000
```

### 4.3 단일 run 내 vault 변경 (반영 안 됨)

- 한 run 시작 후 vault 파일을 mid-run 변경해도 같은 run 내 반영 안 됨 (이미 include_vars 한 후 task 변수 캐시)
- 다음 run 부터 반영
- → **회전은 ansible-playbook 종료 후 수행 권장**

## 5. Vault 회전 시나리오

상세 절차는 `rotate-vault` skill 참조. 본 절은 운영 요약.

### 5.1 시나리오 A: ansible-vault password rekey (vault 자체 password 변경)

```bash
# 1. 백업
cp vault/redfish/dell.yml /tmp/dell-vault.bak

# 2. 새 password 로 rekey
ansible-vault rekey vault/redfish/dell.yml

# 3. Jenkins credentials 갱신 (ANSIBLE_VAULT_PASSWORD)
# 4. 검증
ansible-vault view vault/redfish/dell.yml
```

### 5.2 시나리오 B: 외부 BMC 사용자 자격증명 회전

```bash
# 1. 외부 시스템 (BMC iDRAC / iLO / XCC / CIMC) 에서 사용자 password 변경
#    (BMC 운영자가 수행 — server-exporter 는 read-only)

# 2. 새 자격증명으로 vault 다시 encrypt
ansible-vault edit vault/redfish/dell.yml
#    안에서 vault_redfish_password 또는 accounts[].password 갱신

# 3. 검증 — 다음 ansible run 에서 자동 반영
ansible-playbook redfish-gather/site.yml \
  -i ... -e "target_ip=10.x.x.1" \
  --vault-password-file ~/.vault_pass

# 4. evidence 기록
echo "$(date +%Y-%m-%d): Dell vault rotation (BMC user 변경)" \
  >> tests/evidence/vault-rotation-log.md
```

### 5.3 시나리오 C: 새 vendor vault 추가

`rule 50 R2` 9단계 중 4단계.

```bash
ansible-vault create vault/redfish/{vendor}.yml
# 안에 입력:
# accounts:
#   - username: "infraops"
#     password: "..."
#     label: "primary"
#     role: "primary"
#   - username: "admin"
#     password: "..."
#     label: "recovery"
#     role: "recovery"
```

## 6. 회전 주기 권고

| Vault | 권장 주기 |
|---|---|
| ansible-vault password (마스터) | 분기 |
| BMC / Linux / Windows / ESXi 자격증명 | 반기 또는 사고 시 |
| 새 vendor vault | 추가 시점 (rule 50 R2 9단계) |

## 7. accounts 정규화 (P1 cycle 2026-04-28)

vault file 내 accounts list 순서 = multi-account fallback 시도 순서. 별도 role 정렬 없음.

```yaml
# vault/redfish/dell.yml (예시)
accounts:
  - username: "infraops"
    password: "..."
    label: "primary"
    role: "primary"      # provision target
  - username: "admin"
    password: "..."
    label: "recovery"
    role: "recovery"     # provision 진입용
```

→ `_rf_accounts` 로 정규화. legacy 호환 (`ansible_user` / `ansible_password` → primary 1개).

## 8. 의심 / 사고 대응

### 8.1 자동 반영 안 되는 의심

- 단서 3개 (4.1) 검증 → 0 결과 / 옵션 없음 확인
- ansible run 1회 더 시도 (mid-run 변경은 반영 안 됨)
- vault 파일 디스크 sync 확인 (`ls -la vault/redfish/{vendor}.yml` → mtime 업데이트)
- ansible-vault decrypt 명령 직접 실행 → 새 내용 read 가능 확인

### 8.2 일부 host 인증 실패

- BMC 측 password sync 안 됨 → 외부 시스템 운영자에게 escalate
- multi-account fallback 의 recovery (`accounts[1+]`) 가 동작하는지 확인
- evidence 기록

### 8.3 vault edit 도중 swap 파일 잔재

- `vault/.swp`, `vault/redfish/.{vendor}.yml.swp` 파일 잔재 시 절대 commit 금지
- `.gitignore` 에 `*.swp` 등록 (이미 적용)

## 9. 검증 절차 (회전 후 의무)

1. `ansible-vault view <vault>` — 새 password 로 read 가능
2. dry-run: `ansible-playbook --syntax-check redfish-gather/site.yml`
3. **자동 반영 3 단서 검증** (rule 27 R6) — 4.1 명령 3개
4. 실장비 1대 대상 본 수집 시도 (target_type별)
5. callback 결과 envelope `meta.vendor` 정상
6. console log 평문 password 노출 없음 확인

## 10. 보안 주의

- 회전 절차 중 임시 평문 password 메모는 메모리 only (파일 / clipboard 제거)
- Jenkins credentials 는 server-exporter 외부 (Jenkins controller 권한 최소)
- 회전 이력 = `tests/evidence/vault-rotation-log.md` (날짜 + 대상만, password 자체는 절대 기록 안 함)
- ansible-vault password file (`~/.vault_pass`) 은 `chmod 600`

## 11. 관련 문서

| 문서 | 용도 |
|---|---|
| `rule 27 R6` | vault 자동 반영 단서 3개 정본 |
| `rule 50 R2` | 새 vendor 추가 9단계 |
| `skill: rotate-vault` | 회전 절차 상세 |
| `skill: add-new-vendor` | vendor 추가 시 vault 생성 단계 |
| `skill: debug-precheck-failure` | auth 실패 시 |
| `redfish-gather/tasks/load_vault.yml` | vault 로딩 정본 코드 |
| `docs/03_agent-setup.md` | Agent 보안 설정 |
| `docs/ai/references/ansible/ansible-vault.md` | ansible-vault 명령 reference |
