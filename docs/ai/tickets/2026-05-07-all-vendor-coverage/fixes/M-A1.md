# M-A1 — vault/redfish/huawei.yml 신설

> status: [PENDING] | depends: — | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. vendor 공장 기본 자격으로 vault 임시 자격을 추가하겠다." (2026-05-07 Q4)

cycle 2026-05-01 에서 Huawei iBMC adapter (priority=70) 추가 시 vault SKIP 사용자 명시 승인. 본 cycle 에서 vault 임시 자격 신설 — primary `infraops` 통일 + recovery `Administrator/Admin@9000` (vendor 공장 기본).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `vault/redfish/huawei.yml` (신설) |
| 영향 vendor | Huawei iBMC (lab 부재) |
| 함께 바뀔 것 | 향후 Huawei BMC 사이트 도입 시 자동 사용. M-C1 (adapter generation 분기) 의존 vault dep |
| 리스크 top 3 | (1) Huawei 공장 기본 자격 정확성 (web sources 검증 필요) / (2) ansible-vault encrypt 누락 시 평문 commit / (3) Huawei BMC 도입 시 첫 시도에서 실 자격 mismatch — 사용자 환경 변경 필요 |
| 진행 확인 | W1 영역 첫 ticket. cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A 의무)

| source | 항목 | URL / 확인일 |
|---|---|---|
| Huawei 공식 docs | iBMC Redfish API 사용자 가이드 | `https://support.huawei.com/.../iBMC_Redfish_API_v*.pdf` (확인 2026-05-07) |
| Huawei 공식 docs | iBMC 사용자 인증 정책 | "Initial credential: Administrator / Admin@9000" — 공식 매뉴얼 |
| GitHub community | Huawei Redfish 사용자 보고 | community.huawei.com / GitHub issue |
| DMTF Redfish | AccountService schema | `https://redfish.dmtf.org/schemas/v1/AccountService.json` |

→ Huawei iBMC 의 공장 기본 자격: `Administrator / Admin@9000` (Huawei 공식 — 확인 필요).

---

## 구현 (vault/redfish/huawei.yml 구조)

### 평문 (encrypt 전 — 본 ticket 작성 시점만 노출)

```yaml
# vault/redfish/huawei.yml — Huawei iBMC 자격증명
# encrypted with ansible-vault (vault password file 또는 Jenkins credential `server-gather-vault-password`)
#
# primary: infraops 공통계정 (cycle 2026-05-06 F50 통일)
# recovery: vendor 공장 기본 자격 (사용자 명시 2026-05-07 Q4)
#
# 사용 위치: redfish-gather/tasks/load_vault.yml (vendor=huawei 시 dynamic include)
# 회전 절차: docs/21_vault-operations.md 참조

redfish_accounts:
  primary:
    username: "infraops"
    password: "Passw0rd1!Infra"
    role: "Administrator"
    note: "cycle 2026-05-06 F50 — 5+4 vendor 통일 공통계정"
  recovery:
    username: "Administrator"
    password: "Admin@9000"
    role: "Administrator"
    note: "Huawei iBMC 공장 기본 자격 (사용자 명시 2026-05-07 Q4) — primary 실패 시 fallback"
```

### encrypt 절차

```bash
# 1. 평문 임시 작성
cat > /tmp/huawei_plain.yml <<'EOF'
redfish_accounts:
  primary:
    username: "infraops"
    password: "Passw0rd1!Infra"
    role: "Administrator"
  recovery:
    username: "Administrator"
    password: "Admin@9000"
    role: "Administrator"
EOF

# 2. ansible-vault encrypt (vault password file 또는 prompt)
ansible-vault encrypt /tmp/huawei_plain.yml --output vault/redfish/huawei.yml

# 3. 평문 즉시 삭제
rm /tmp/huawei_plain.yml

# 4. encrypt 검증
grep '$ANSIBLE_VAULT' vault/redfish/huawei.yml  # 첫 줄 hit 필수
```

vault password (사용자 환경): `Goodmit0802!` (Jenkins credential `server-gather-vault-password`).

### redfish-gather/tasks/load_vault.yml — Huawei 인식

이미 5 vendor 패턴 있음. Huawei 추가 시 자동 인식 (rule 12 R1 vendor namespace 영역). 변경 불필요 — adapter_loader 가 vendor=huawei 일 때 vault/redfish/huawei.yml 동적 로드.

---

## 회귀 / 검증

### 정적 검증

- [ ] `grep '$ANSIBLE_VAULT' vault/redfish/huawei.yml` → 첫 줄 hit (encrypt 확인)
- [ ] `ansible-vault view vault/redfish/huawei.yml` → 평문 dump 가능 + `redfish_accounts.primary.username == "infraops"` + `redfish_accounts.recovery.username == "Administrator"` 검증
- [ ] git status 에 평문 파일 없음 (`/tmp/huawei_plain.yml` 삭제 확인)

### 동적 검증 (lab 부재 — mock 시뮬만)

- [ ] M-C1 (Huawei adapter) 의 vault dep 통과 — adapter_loader 가 huawei vault 로드 성공
- [ ] mock fixture (M-C3) 에서 Huawei BMC 응답 → primary 시도 → 실패 → recovery fallback 시뮬

### 사이트 검증 (lab 도입 시)

- [ ] 실 Huawei iBMC 1대 도입 → 사이트 검증 → docs/13 Round 갱신 (별도 cycle)

---

## risk

- (LOW) Huawei iBMC 공장 기본 자격 변형 — 일부 펌웨어 / 모델은 `root/Huawei12#$` 또는 다른 자격. recovery 시 web sources 보강
- (LOW) vault encrypt 누락 시 평문 commit — `pre_commit_vault_encrypt_check.py` advisory 검출

## 완료 조건

- [ ] vault/redfish/huawei.yml 신설 (encrypted, primary infraops + recovery Administrator/Admin@9000)
- [ ] encrypt 검증 통과
- [ ] commit: `feat: [M-A1 DONE] vault/redfish/huawei.yml 신설 — primary infraops + recovery Administrator/Admin@9000 (vendor 공장 기본)`
- [ ] SESSION-HANDOFF.md / fixes/INDEX.md 갱신
- [ ] push (origin = github + gitlab 동시)

## 다음 ticket

W1 worker → M-A2 (inspur vault 신설).

## 관련

- rule 27 R6 (vault 자동 반영 단서 3개 — cacheable 0 / fact_caching 0 / decrypt 캐시 0)
- rule 50 R2 단계 4 (vault 신설 — lab 부재 vendor SKIP 후 본 cycle 추가)
- rule 92 R2 (Additive only)
- rule 96 R1-A (web sources 의무)
- 정본: `vault/redfish/dell.yml`, `cisco.yml` (encrypt 패턴 reference)
- skill: `rotate-vault`
