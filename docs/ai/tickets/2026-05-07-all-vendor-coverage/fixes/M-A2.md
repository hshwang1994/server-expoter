# M-A2 — vault/redfish/inspur.yml 신설

> status: [PENDING] | depends: — | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. vendor 공장 기본 자격으로 vault 임시 자격을 추가하겠다." (2026-05-07 Q4)

cycle 2026-05-01 에서 Inspur ISBMC adapter (priority=70) 추가 시 vault SKIP 사용자 명시 승인. 본 cycle 에서 vault 임시 자격 신설.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `vault/redfish/inspur.yml` (신설) |
| 영향 vendor | Inspur ISBMC (lab 부재) |
| 함께 바뀔 것 | M-D1 (Inspur OEM tasks) 의존 vault dep |
| 리스크 top 3 | (1) Inspur 공장 기본 자격 정확성 / (2) ansible-vault encrypt 누락 / (3) Inspur 도입 시 자격 mismatch |
| 진행 확인 | W1 영역. cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| source | 항목 |
|---|---|
| Inspur 공식 docs | ISBMC Redfish API guide / 사용자 매뉴얼 |
| GitHub community | Inspur Redfish 사용자 보고 |
| DMTF Redfish | AccountService schema |

→ Inspur ISBMC 공장 기본 자격: `admin / admin` (사용자 명시 Q4 — Inspur 공식 매뉴얼 확인 필요).

---

## 구현 (vault/redfish/inspur.yml)

### 평문 (encrypt 전)

```yaml
redfish_accounts:
  primary:
    username: "infraops"
    password: "Passw0rd1!Infra"
    role: "Administrator"
    note: "cycle 2026-05-06 F50 — 통일 공통계정"
  recovery:
    username: "admin"
    password: "admin"
    role: "Administrator"
    note: "Inspur ISBMC 공장 기본 자격 (사용자 명시 2026-05-07 Q4)"
```

### encrypt

```bash
ansible-vault encrypt vault/redfish/inspur.yml
grep '$ANSIBLE_VAULT' vault/redfish/inspur.yml  # 검증
```

---

## 회귀 / 검증

- [ ] `grep '$ANSIBLE_VAULT' vault/redfish/inspur.yml` → hit
- [ ] `ansible-vault view vault/redfish/inspur.yml` → primary infraops + recovery admin/admin
- [ ] git status 평문 0건

## risk

- (LOW) Inspur 공장 기본 자격 변형 — 일부 모델 다른 자격 가능. recovery 시 web sources 보강

## 완료 조건

- [ ] vault/redfish/inspur.yml 신설 (encrypted)
- [ ] commit: `feat: [M-A2 DONE] vault/redfish/inspur.yml 신설 — primary infraops + recovery admin/admin`
- [ ] SESSION-HANDOFF.md / fixes/INDEX.md 갱신
- [ ] push

## 다음 ticket

W1 → M-A3 (fujitsu vault).

## 관련

- M-A1 (huawei vault — encrypt 패턴 동일)
- rule 27 R6 / rule 50 R2 / rule 92 R2 / rule 96 R1-A
