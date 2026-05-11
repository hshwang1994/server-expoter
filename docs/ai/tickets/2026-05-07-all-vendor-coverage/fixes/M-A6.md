# M-A6 — docs/21_vault-operations.md 갱신 (vendor 공장 기본 자격 정책 명문화)

> status: [PENDING] | depends: M-A1, M-A2, M-A3, M-A4, M-A5 | priority: P2 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "vendor 공장 기본 자격으로 vault 임시 자격을 추가하겠다." (2026-05-07 Q4)

vault 임시 자격 정책 (primary infraops + recovery vendor 공장 기본) 을 docs/21 에 명문화. 향후 worker / 사용자 reference.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `docs/21_vault-operations.md` (변경 — 절 추가) |
| 영향 vendor | 9 vendor (Dell/HPE/Lenovo/Supermicro/Cisco/Huawei/Inspur/Fujitsu/Quanta) |
| 함께 바뀔 것 | (없음 — 문서만) |
| 리스크 top 3 | (1) 정책 명문화 누락 시 worker 가 다른 자격 사용 / (2) docs/21 stale / (3) vendor 공장 기본 자격 변경 시 docs 갱신 누락 |
| 진행 확인 | M-A1~A5 [DONE] 후 진입 |

---

## 갱신 절 (docs/21_vault-operations.md)

다음 절 추가 (existing docs/21 본문 뒤에):

```markdown
## 임시 자격 정책 (cycle 2026-05-07 사용자 명시 Q4)

### Primary + Recovery 2단계

- **primary**: `infraops / Passw0rd1!Infra` — cycle 2026-05-06 F50 통일 공통계정 (9 vendor 모두 동일)
- **recovery**: vendor 공장 기본 자격 — primary 실패 시 fallback (BMC reset 후 default 회복 시점)

### Vendor 공장 기본 자격 매트릭스

| vendor | 공장 기본 | 출처 |
|---|---|---|
| Dell | `root / calvin` | Dell PowerEdge / iDRAC 공식 매뉴얼 |
| HPE | `admin / admin` | HPE iLO User Guide (legacy default) |
| Lenovo | `USERID / PASSW0RD` | Lenovo XCC / IMM User Guide ('0' 은 숫자 zero) |
| Supermicro | `ADMIN / ADMIN` | Supermicro BMC User Guide (일부 펌웨어 sticker 별도 자격) |
| Cisco | `admin / password` | Cisco UCS / CIMC User Guide |
| Huawei iBMC | `Administrator / Admin@9000` | Huawei iBMC Redfish API guide |
| Inspur ISBMC | `admin / admin` | Inspur 공식 매뉴얼 |
| Fujitsu iRMC | `admin / admin` | Fujitsu iRMC S* User Guide (PRIMERGY) |
| Quanta QCT | `admin / admin` | Quanta QCT BMC User Guide (ODM 모델 customer-specific 가능) |

### 사용 시점

- primary 시도 → 401 / 403 응답 → recovery fallback (`redfish-gather/tasks/load_vault.yml` 의 `_rf_accounts` 변수)
- recovery 도 실패 → status=failed + diagnosis.details.auth = "primary + recovery 모두 실패"
- 사이트 BMC reset 후 default 자격 회복 시점에 recovery 가 작동

### 회전 절차

primary `infraops` 회전 시:
1. BMC 측에서 infraops 자격 변경
2. vault/redfish/{vendor}.yml decrypt → primary.password 갱신 → encrypt
3. Jenkins 빌드 → primary 시도 PASS 확인
4. 회전 시점은 분기/반기 정기 (rule 60 cycle-011 해제 후 사용자 운영 정책)

recovery 자격은 vendor 공장 기본 — 변경 0 (BMC firmware default 따름). 단 first-login 강제 변경 펌웨어 (HPE iLO5+, Lenovo XCC2+, Supermicro X12+) 는 변경 즉시 default 자격 무효화 → recovery 의미 약함. 운영 정책 별도 협의.

### 보안 고려 (rule 60 cycle-011 해제 후 advisory)

- vault 평문 commit 금지 (`grep '$ANSIBLE_VAULT' vault/redfish/*.yml` 모두 hit)
- vault password file 또는 Jenkins credential `server-gather-vault-password` 만 사용
- 평문 vault decrypt 임시 파일 작성 시 즉시 삭제

### 자동 반영 보장 (rule 27 R6)

vault 변경 시 다음 ansible 실행에서 자동 반영. 의심 시 단서 3 검증:
1. `redfish-gather/tasks/load_vault.yml` 의 `include_vars` 호출에 `cacheable: yes` 옵션 부재 (`grep -rn 'cacheable' redfish-gather/tasks/load_vault.yml` → 0 결과)
2. `_rf_accounts` / `_rf_vault_data` 변수가 host facts (`ansible_facts.*`) 에 등록 안 됨
3. `ansible-vault decrypt` 결과 캐시 옵션 부재 (Ansible default — 매 run 새로 decrypt)
```

---

## 회귀 / 검증

### 정적 검증

- [ ] `docs/21_vault-operations.md` 본문 새 절 추가 — 위 마크다운 그대로
- [ ] 기존 본문 변경 0 (Additive 검증 — git diff 본 ticket 변경)

### 의미 검증

- [ ] vendor 공장 기본 자격 매트릭스 9 vendor 모두 등재
- [ ] 사용 시점 / 회전 절차 / 보안 고려 / 자동 반영 보장 4 절 모두 작성
- [ ] rule 27 R6 단서 3 명시

---

## risk

- (LOW) docs/21 stale 위험 — vendor 공장 기본 자격 변경 시 docs 갱신 의무. 향후 cycle 에서 vendor 도입 시 본 절 갱신 명시

## 완료 조건

- [ ] docs/21_vault-operations.md 새 절 ("임시 자격 정책") 추가
- [ ] 9 vendor 매트릭스 모두 등재
- [ ] commit: `docs: [M-A6 DONE] docs/21 임시 자격 정책 명문화 — 9 vendor 공장 기본`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 → M-B1 (Supermicro X10 신설).

## 관련

- M-A1~A5 (vault 신설/추가)
- rule 27 R6 (vault 자동 반영 단서)
- rule 60 (cycle-011 보안 정책 해제 — advisory only)
- 정본: docs/21_vault-operations.md (본 ticket 갱신 대상)

## 분석 / 구현

(cycle 2026-05-11 Phase 7 추가 stub — 본 ticket 의 분석 / 구현 내용은 본문 다른 절 (## 컨텍스트 / ## 현재 동작 / ## 변경 / ## 구현 등) 참조. cycle DONE 시점에 cold-start 6 절 정본 도입 전 작성된 ticket.)
