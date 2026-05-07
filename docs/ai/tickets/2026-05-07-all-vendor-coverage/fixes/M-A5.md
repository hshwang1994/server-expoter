# M-A5 — 5 사이트 검증 vendor recovery 자격 추가

> status: [PENDING] | depends: — | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "vendor 공장 기본 자격으로 vault 임시 자격을 추가하겠다." (2026-05-07 Q4)

기존 5 vendor (Dell/HPE/Lenovo/Supermicro/Cisco) vault 에 primary `infraops` 만 있고 recovery 자격 없음. primary 실패 시 fallback 가능하도록 vendor 공장 기본 자격을 recovery 로 추가.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `vault/redfish/dell.yml`, `vault/redfish/hpe.yml`, `vault/redfish/lenovo.yml`, `vault/redfish/supermicro.yml`, `vault/redfish/cisco.yml` |
| 영향 vendor | 사이트 검증 5 vendor — Additive only (primary 변경 없음) |
| 함께 바뀔 것 | (없음 — 향후 사이트 BMC 자격 변경 시 fallback 동작) |
| 리스크 top 3 | (1) primary `infraops` 변경 위험 (Out of scope — Additive only) / (2) encrypt 손상 / (3) recovery 자격이 사이트 BMC 자격과 mismatch (사이트 customer-specific 자격) |
| 진행 확인 | W1 영역. cycle 진입 즉시 가능 |

---

## Vendor 공장 기본 자격 (사용자 명시 Q4)

| vendor | 공장 기본 자격 | 출처 |
|---|---|---|
| Dell | `root / calvin` | Dell PowerEdge / iDRAC 공식 매뉴얼 (역사적 default) |
| HPE | `admin / admin` | HPE iLO User Guide (legacy default — iLO5+는 첫 로그인 변경 강제) |
| Lenovo | `USERID / PASSW0RD` | Lenovo XCC / IMM User Guide ('0' 은 영문자 O 가 아닌 숫자 zero) |
| Supermicro | `ADMIN / ADMIN` | Supermicro BMC User Guide (BMC 일부 펌웨어는 sticker 별도 자격) |
| Cisco | `admin / password` | Cisco UCS / CIMC User Guide |

→ 본 자격은 **vendor 공식 default** — 사이트 BMC 가 customer-specific 자격으로 변경됐을 가능성 높음. recovery 는 BMC reset 후 default 회복 시점에 작동.

---

## 구현 절차 (5 vendor 동일 패턴)

### 1. dell.yml

```bash
# 1. decrypt 평문 임시
ansible-vault decrypt vault/redfish/dell.yml --output /tmp/dell_plain.yml

# 2. recovery 절 append
cat >> /tmp/dell_plain.yml <<'EOF'

# recovery 자격 추가 (cycle 2026-05-07 M-A5 사용자 명시)
# vendor 공장 기본 자격 — primary 실패 시 BMC reset 후 default 회복 시점에 fallback
EOF

# 3. 본문 수정 (수동) — primary 절 유지 + recovery 절 추가:
#   redfish_accounts:
#     primary:
#       username: "infraops"
#       password: "Passw0rd1!Infra"
#       role: "Administrator"
#     recovery:
#       username: "root"
#       password: "calvin"
#       role: "Administrator"
#       note: "Dell iDRAC 공장 기본 (사용자 명시 2026-05-07 Q4)"

# 4. encrypt
ansible-vault encrypt /tmp/dell_plain.yml --output vault/redfish/dell.yml

# 5. 평문 삭제 + 검증
rm /tmp/dell_plain.yml
grep '$ANSIBLE_VAULT' vault/redfish/dell.yml
ansible-vault view vault/redfish/dell.yml | grep -E '(primary|recovery)' | wc -l  # 2 hit 필수
```

### 2. hpe.yml

primary `infraops` 유지 + recovery `admin / admin` 추가. encrypt 동일.

### 3. lenovo.yml

primary `infraops` 유지 + recovery `USERID / PASSW0RD` 추가.

### 4. supermicro.yml

primary `infraops` 유지 + recovery `ADMIN / ADMIN` 추가.

### 5. cisco.yml

primary `infraops` 유지 + recovery `admin / password` 추가.

---

## 회귀 / 검증

### 정적 검증

- [ ] 5 vendor vault 모두 encrypted (`grep '$ANSIBLE_VAULT' vault/redfish/*.yml` 9 hit — 5 사이트 + 4 신설)
- [ ] 각 vault view → `redfish_accounts.primary.username == "infraops"` (Additive 검증 — primary 변경 없음)
- [ ] 각 vault view → `redfish_accounts.recovery.username` 존재 + vendor 공장 기본 자격 일치
- [ ] git diff vault/ → encrypt 변경만 (평문 0건)

### 동적 검증 (lab 도입 시)

- [ ] 사이트 BMC 1대 reset → default 자격 회복 → recovery fallback 동작 확인 (별도 cycle)

### Additive only 검증 (rule 92 R2)

- [ ] 사이트 검증 4 vendor 의 envelope shape 변경 0 (`scripts/ai/hooks/envelope_change_check.py`)
- [ ] redfish-gather/library/redfish_gather.py 변경 0 (vault 만 변경 — library 미변경)
- [ ] `pytest tests/ -k redfish_account` PASS (M-B2/M-B3 cycle 2026-05-06 회귀 fixture 그대로 통과)

---

## risk

- (MED) 사이트 BMC 가 customer-specific 자격으로 변경된 상태 — recovery `default` 자격은 reset 후만 작동. 사이트 운영 정책 (BMC reset 가능 여부) 별도 협의
- (LOW) 일부 펌웨어 (HPE iLO5+, Lenovo XCC2+, Supermicro X12+) 는 first-login 강제 변경 — default 자격 즉시 변경됨. recovery fallback 의 의미 약함

## 완료 조건

- [ ] 5 vendor vault 모두 recovery 절 추가 + encrypt
- [ ] primary `infraops` 변경 0 (Additive only 검증)
- [ ] commit: `feat: [M-A5 DONE] 5 사이트 검증 vendor recovery 자격 추가 — Dell/HPE/Lenovo/Supermicro/Cisco 공장 기본`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 → M-A6 (vault docs 갱신).

## 관련

- M-A1~A4 (4 신설 vault 패턴)
- rule 27 R6 (vault 자동 반영 단서)
- rule 92 R2 (Additive only)
- rule 96 R1-A (web sources)
- 정본: `docs/21_vault-operations.md` (M-A6 갱신 대상)
