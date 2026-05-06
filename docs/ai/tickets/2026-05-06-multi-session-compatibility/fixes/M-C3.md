# M-C3 — Vault 자동 반영 회귀 mock fixture

> status: [PENDING] | depends: M-C2 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility

## 사용자 의도

M-C2 검증 결과 (자동 반영 YES, 다음 run 부터) 를 mock fixture + pytest 회귀로 보장.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/<vendor>/vault_*.yml` (mock vault — 평문 OK, fixture 영역), `tests/redfish-probe/test_vault_dynamic_load.py` (신규 또는 확장) |
| 영향 vendor | 9 vendor (모두 동일 load_vault.yml 사용 → vendor 1개로 충분히 검증 가능) |
| 함께 바뀔 것 | pytest 결과 |
| 리스크 | LOW (mock 만, 실 vault 영향 없음) |

## 작업 spec

### (A) Mock fixture (평문 — fixture 영역)

```yaml
# tests/fixtures/vault/dell_v1.yml — 초기 vault 상태
# source: M-C3 mock (자동 반영 검증용)
accounts:
  - username: "infraops"
    password: "old_password_v1"
    label: "primary"
    role: "primary"
  - username: "admin"
    password: "recovery_v1"
    label: "recovery"
    role: "recovery"
```

```yaml
# tests/fixtures/vault/dell_v2.yml — primary password 변경
accounts:
  - username: "infraops"
    password: "new_password_v2"  # 변경
    label: "primary"
    role: "primary"
  - username: "admin"
    password: "recovery_v1"
    label: "recovery"
    role: "recovery"
```

```yaml
# tests/fixtures/vault/dell_v3.yml — 새 account 추가
accounts:
  - username: "infraops"
    password: "new_password_v2"
    label: "primary"
    role: "primary"
  - username: "admin"
    password: "recovery_v1"
    label: "recovery"
    role: "recovery"
  - username: "backup"  # 신규
    password: "backup_v3"
    label: "secondary_recovery"
    role: "recovery"
```

### (B) pytest 회귀 케이스

```python
# tests/redfish-probe/test_vault_dynamic_load.py

def test_vault_v1_loads_old_password(monkeypatch):
    """초기 vault 로드 → primary password = old_password_v1"""
    ...

def test_vault_v2_reflects_password_change(monkeypatch):
    """vault 파일 dell_v1 → dell_v2 교체 → 새 password 자동 반영"""
    # fixture v1 로 초기 로드
    accounts_v1 = load_vault_mock("dell_v1.yml")
    assert accounts_v1[0]["password"] == "old_password_v1"
    
    # fixture v2 로 교체 (실 환경의 vault 파일 변경 시뮬)
    accounts_v2 = load_vault_mock("dell_v2.yml")
    assert accounts_v2[0]["password"] == "new_password_v2"
    
    # 즉, include_vars 결과가 매번 새로 로드됨 (캐시 없음)

def test_vault_v3_adds_new_account():
    """vault accounts list 추가 → 다음 run 에서 multi-account 후보 +1"""
    accounts_v3 = load_vault_mock("dell_v3.yml")
    assert len(accounts_v3) == 3
    assert accounts_v3[2]["username"] == "backup"

def test_vault_role_change_reflects():
    """accounts[0] role 변경 → primary 후보 변경"""
    ...

def test_vault_run_in_progress_no_reflect():
    """single run 중 vault 변경은 반영 안 됨 (이미 include_vars 한 캐시 사용)"""
    # 이건 task scope 캐시 검증 — 단일 run 에서 두 번 include_vars 시도해도 첫번째 결과 유지 검증
    ...
```

### (C) ansible-vault encrypt mock (선택)

실제 vault 는 encrypt 된 파일. mock 에서는 평문 OK 이지만 한 케이스는 encrypt simulation:
- `tests/fixtures/vault/dell_encrypted.yml` (ansible-vault encrypt 한 파일)
- decrypt key 는 환경변수 (`VAULT_PASSWORD`) — mock 에서는 알려진 값
- 검증: encrypt 된 vault rekey 후에도 자동 반영

## 회귀 / 검증

- pytest 신규 5건 PASS
- pytest 전체 (108 + 5) PASS
- `python scripts/ai/verify_harness_consistency.py` PASS

## risk

- (LOW) mock fixture 가 실 ansible-vault 의 동작 모방. 일부 edge case (vault password file 회전 etc) 는 실 검증 시 보강

## 완료 조건

- [ ] mock fixture 3 종 (v1/v2/v3) + (선택) encrypted 1
- [ ] pytest 회귀 5건 추가
- [ ] pytest PASS
- [ ] commit: `test: [M-C3 DONE] vault 동적 로딩 mock 회귀 5건`

## 다음 세션 첫 지시 템플릿

```
M-C3 vault 자동 반영 회귀 진입.

읽기 우선순위:
1. fixes/M-C3.md
2. M-C2 산출물 (시나리오 5 검증)
3. tests/fixtures/redfish/ (기존 fixture 패턴)

작업:
1. tests/fixtures/vault/dell_v1.yml ~ v3.yml (mock)
2. tests/redfish-probe/test_vault_dynamic_load.py (5 테스트)
3. pytest PASS

선행: M-C2 [DONE]
```

## 관련

- rule 21 R2 (Fixture 출처 기록)
- rule 27 R3 (Vault 2단계 로딩)
