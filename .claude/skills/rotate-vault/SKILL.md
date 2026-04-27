---
name: rotate-vault
description: 벤더별 또는 채널별 vault 자격증명 회전 절차. vault/{linux,windows,esxi}.yml + vault/redfish/{vendor}.yml의 password / username 갱신 안내. ansible-vault rekey 또는 외부 BMC 사용자 자체 변경. 사용자가 "Dell vault 회전", "vault password 변경", "rotate" 등 요청 시. - 분기/반기 정기 회전 / BMC 사용자 변경 / 보안 사고 대응 / 자격증명 stale 발견
---

# rotate-vault

## 목적

server-exporter Vault 자격증명을 안전하게 회전. 두 가지 시나리오:
1. **Vault password 회전**: ansible-vault password 자체를 변경 (`ansible-vault rekey`)
2. **자격증명 회전**: 외부 시스템(BMC / Linux user / vSphere)의 user/password 자체를 변경 → vault 다시 encrypt

## 입력

- 영향 vault 파일 (예: vault/redfish/dell.yml)
- 회전 종류 (vault password vs 자격증명)
- 새 자격증명 (외부 시스템 변경 후 확보)

## 출력 / 절차

### 시나리오 1: Vault password rekey (외부 자격증명 동일)

```bash
# 1. 백업 (안전)
cp vault/redfish/dell.yml /tmp/dell-vault.bak

# 2. 새 password로 rekey
ansible-vault rekey vault/redfish/dell.yml
# (기존 password 입력 → 새 password 입력 2회)

# 3. Jenkins credentials 갱신
# (Jenkins UI → Credentials → ANSIBLE_VAULT_PASSWORD 갱신)

# 4. 검증
ansible-vault view vault/redfish/dell.yml
# (새 password로 read 가능한지)
```

### 시나리오 2: 외부 BMC 사용자 자격증명 회전

```bash
# 1. 외부 시스템 (BMC / iDRAC / iLO)에서 사용자 password 변경
# → BMC 운영자가 수행 (server-exporter는 read-only)

# 2. 새 자격증명으로 vault 다시 encrypt
ansible-vault edit vault/redfish/dell.yml
# 안에서 vault_redfish_password 갱신

# 3. 검증
ansible-playbook redfish-gather/site.yml \
  -i ... -e "target_ip=10.x.x.1" \
  --vault-password-file ~/.vault_pass

# 4. evidence 기록
echo "2026-04-27: Dell vault rotation (BMC user 변경)" \
  >> tests/evidence/vault-rotation-log.md
```

### 시나리오 3: 벤더 추가 (새 vault 생성)

```bash
ansible-vault create vault/redfish/huawei.yml
# 안에 입력:
# vault_redfish_username: "service_account"
# vault_redfish_password: "..."
```

## 회전 주기 권고

| Vault | 권장 주기 |
|---|---|
| vault password (마스터) | 분기 |
| 자격증명 (BMC / Linux / Windows / ESXi) | 반기 또는 사고 시 |
| 새 vendor vault | 추가 시점 (rule 50 R2 9단계) |

## 검증 절차

1. `ansible-vault view <vault>` — 새 password로 read 가능
2. dry-run: `ansible-playbook --syntax-check`
3. 실장비 1대 대상 본 수집 시도 (target_type별)
4. callback 결과 envelope의 `meta.vendor` 정상
5. console log에 평문 password 노출 없음 확인 (rule 60)

## 보안 주의 (rule 60)

- 회전 절차 중 임시로 평문 password 메모는 메모리 only (파일 / clipboard 제거)
- Jenkins credentials는 server-exporter 외부 (Jenkins controller 권한 최소)
- 회전 이력은 `tests/evidence/vault-rotation-log.md` (날짜 + 대상만, password 자체는 절대 기록 안 함)
- ansible-vault password 파일 (`~/.vault_pass`)은 `chmod 600`

## 실패 / 오탐 처리

- rekey 후 일부 호스트 인증 실패 → BMC 측 password sync 안 됨 (외부 시스템 운영자에게 escalate)
- 회전 후 dry-run FAIL → 즉시 backup 으로 revert + 원인 분석
- vault edit 도중 vim 종료 → `.swp` 파일 잔재 (절대 commit 금지, .gitignore 확인)

## server-exporter 도메인 적용

- 영향 채널: rotation 대상에 따라 (주로 redfish — vendor별 vault)
- 영향 vendor: 회전 대상 1개 또는 다수
- 영향 schema: 없음

## 적용 rule / 관련

- **rule 60** (security-and-secrets) 정본
- rule 50 R2 (새 vendor 추가 시 vault 9단계)
- rule 70 (docs-and-evidence) — evidence 기록
- skill: `add-new-vendor`, `debug-precheck-failure` (auth 실패 시)
- agent: `vault-rotator` (이 skill의 메인 실행자), `security-reviewer`
- 정본: `docs/03_agent-setup.md` 보안 부분
- reference: `docs/ai/references/ansible/ansible-vault.md`

## Forbidden

- 평문 password를 chat / Jenkins log / commit에 노출
- vault edit 중 임시 파일 (.swp) commit
- Jenkins credentials를 server-exporter `.claude/` 안에 보관 (Jenkins controller 책임)
- AI가 자체적으로 vault 회전 결정 (사용자 명시 승인 필요)
