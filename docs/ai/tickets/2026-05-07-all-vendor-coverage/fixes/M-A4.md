# M-A4 — vault/redfish/quanta.yml 신설

> status: [PENDING] | depends: — | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "vendor 공장 기본 자격으로 vault 임시 자격을 추가하겠다." (2026-05-07 Q4)

cycle 2026-05-01 Quanta QCT adapter (priority=70) 추가 시 vault SKIP. 본 cycle 신설.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `vault/redfish/quanta.yml` (신설) |
| 영향 vendor | Quanta QCT BMC (lab 부재) |
| 함께 바뀔 것 | M-F1, M-F2 의존 vault dep |
| 리스크 top 3 | (1) Quanta QCT 공장 기본 변형 (model별 차이) / (2) encrypt 누락 / (3) ODM 모델 자격 mismatch |
| 진행 확인 | W1 영역. cycle 진입 즉시 가능 |

---

## Web sources (rule 96 R1-A)

| source | 항목 |
|---|---|
| Quanta QCT 공식 | BMC User Guide (S/D/T/J series) |
| 공장 기본 | `admin / admin` (Quanta QCT BMC — 사용자 명시 Q4) |
| Note | Quanta 는 ODM 사업 — 일부 모델은 customer-specific 자격 (예: Microsoft Azure / Meta — 다른 자격) |

---

## 구현 (vault/redfish/quanta.yml)

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
    note: "Quanta QCT BMC 공장 기본 (사용자 명시 2026-05-07 Q4) — ODM 모델은 customer-specific 자격 가능"
```

### encrypt

```bash
ansible-vault encrypt vault/redfish/quanta.yml
```

---

## 회귀 / 검증

- [ ] encrypt + view 검증

## risk

- (LOW) Quanta ODM 모델 자격 mismatch — 사이트 도입 시 customer-specific 자격 별도 vault entry 필요 가능

## 완료 조건

- [ ] vault/redfish/quanta.yml 신설 (encrypted)
- [ ] commit: `feat: [M-A4 DONE] vault/redfish/quanta.yml 신설`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 → M-A5 (5 vendor recovery 자격 추가).

## 관련

- M-A1~A3 (encrypt 패턴)
- rule 27 R6 / rule 50 R2 / rule 92 R2 / rule 96 R1-A
