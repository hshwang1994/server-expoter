# M-A3 — vault/redfish/fujitsu.yml 신설

> status: [PENDING] | depends: — | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "vendor 공장 기본 자격으로 vault 임시 자격을 추가하겠다." (2026-05-07 Q4)

cycle 2026-05-01 Fujitsu iRMC adapter (priority=70) 추가 시 vault SKIP. 본 cycle 신설.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `vault/redfish/fujitsu.yml` (신설) |
| 영향 vendor | Fujitsu iRMC (lab 부재) |
| 함께 바뀔 것 | M-E1, M-E2, M-E3 의존 vault dep |
| 리스크 top 3 | (1) Fujitsu 공장 기본 자격 변형 (S2/S4/S5/S6 모델별 차이) / (2) encrypt 누락 / (3) 도입 시 자격 mismatch |
| 진행 확인 | W1 영역. cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| source | 항목 |
|---|---|
| Fujitsu 공식 docs | iRMC S* User Guide (PRIMERGY 매뉴얼) |
| URL | `https://support.ts.fujitsu.com/IndexDownload.asp` (확인 2026-05-07) |
| 공장 기본 | `admin / admin` (Fujitsu iRMC 공식 — 사용자 명시 Q4) |

→ Fujitsu iRMC 일부 펌웨어는 첫 로그인 시 강제 변경 — recovery 자격은 reset 후 default 로 회복.

---

## 구현 (vault/redfish/fujitsu.yml)

```yaml
redfish_accounts:
  primary:
    username: "infraops"
    password: "Passw0rd1!Infra"
    role: "Administrator"
    note: "cycle 2026-05-06 F50 통일"
  recovery:
    username: "admin"
    password: "admin"
    role: "Administrator"
    note: "Fujitsu iRMC 공장 기본 자격 (사용자 명시 2026-05-07 Q4)"
```

### encrypt

```bash
ansible-vault encrypt vault/redfish/fujitsu.yml
```

---

## 회귀 / 검증

- [ ] encrypt 검증 (`grep '$ANSIBLE_VAULT' vault/redfish/fujitsu.yml`)
- [ ] view 검증 (primary + recovery 4 필드 모두 존재)

## risk

- (LOW) iRMC S6 (최신) 일부 펌웨어 — 강제 변경 정책 활성화 시 default `admin/admin` 작동 안 함. 사이트 도입 시 별도 자격 환경 변수

## 완료 조건

- [ ] vault/redfish/fujitsu.yml 신설 (encrypted)
- [ ] commit: `feat: [M-A3 DONE] vault/redfish/fujitsu.yml 신설`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 → M-A4 (quanta vault).

## 관련

- M-A1, M-A2 (encrypt 패턴 동일)
- rule 27 R6 / rule 50 R2 / rule 92 R2 / rule 96 R1-A
