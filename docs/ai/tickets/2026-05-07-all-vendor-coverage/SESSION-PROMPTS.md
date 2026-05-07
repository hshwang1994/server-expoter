# Session Prompts — 2026-05-07 all-vendor-coverage

> **사용자 명시 (2026-05-07)**:
> - 5 worker 병렬 진행 — 권장 우선순위 + 한번에 모두 수행
> - **자율 진행 권한**: 작업 중 부가 작업 발생 시 승인 없이 무조건 진행
> - 사용자 결정 항목도 AI 합리적 default 결정 후 SESSION-HANDOFF 에 명시
> - 모두 [DONE] 후 cycle 종료 + commit + push (rule 93 R1+R4)

---

## 자율 진행 권한 정책 (모든 worker 세션 공통)

본 cycle 의 모든 worker 세션은 다음 권한을 보유:

1. **부가 작업 자율 진행** — ticket 진행 중 추가 발견되는 모든 작업은 승인 없이 진행
2. **사용자 결정 항목 default 진행** — 사용자 결정이 필요한 항목은 AI 가 합리적 default 결정 후 진행. 결정 사유는 SESSION-HANDOFF / decision-log 에 명시
3. **commit + push 자율** — 작업 완료 시 main 자율 commit + push (github + gitlab 동시 — rule 93 R1+R4+R7)
4. **rule 24 6 체크리스트** 통과 후 [DONE] 선언
5. **commit 마커**: `<type>: [M-X## DONE] <요약>` (rule 26 R7 / rule 90)

**예외 (자율 진행 금지)**:
- force push (`--force` / `-f`) — rule 93 R1
- envelope 13 필드 추가/삭제/리네임 (rule 96 R1-B) — 본 cycle Additive only 영역
- schema 변경 (sections.yml / field_dictionary.yml) — Q7 사용자 명시 즉시 confirm
- 사이트 PASS 4 vendor × 1 generation 코드 path 변경 — rule 92 R2

→ 본 cycle 은 **호환성 fallback 작성 cycle (Additive only)** — 위 예외 영역 진입 시에만 사용자 확인.

---

## Worker 1 (W1) cold-start prompt — vault + Supermicro

```
W1 worker 진입 — vault + Supermicro 영역 (10 ticket).

cold-start 순서:
1. docs/ai/tickets/2026-05-07-all-vendor-coverage/INDEX.md
2. docs/ai/tickets/2026-05-07-all-vendor-coverage/SESSION-HANDOFF.md
3. docs/ai/tickets/2026-05-07-all-vendor-coverage/DEPENDENCIES.md
4. docs/ai/tickets/2026-05-07-all-vendor-coverage/fixes/INDEX.md
5. fixes/M-A1.md (착수)

본 worker 영역 (10 ticket, 순서 의존):
- M-A1 huawei vault 신설 → M-A2 inspur → M-A3 fujitsu → M-A4 quanta → M-A5 5 vendor recovery → M-A6 vault docs
- M-B1 Supermicro X10 신설 → M-B2 6 gen capability → M-B3 AMD/ARM 변형 → M-B4 mock fixture

vault 임시 자격 정책 (Q4 사용자 명시):
- primary: infraops / Passw0rd1!Infra (cycle 2026-05-06 F50 통일)
- recovery: vendor 공장 기본 자격
  · Dell: root/calvin
  · HPE: admin/admin
  · Lenovo: USERID/PASSW0RD
  · Supermicro: ADMIN/ADMIN
  · Cisco: admin/password
  · Huawei iBMC: Administrator/Admin@9000 (web sources 검증)
  · Inspur: admin/admin (web sources 검증)
  · Fujitsu iRMC: admin/admin (web sources 검증)
  · Quanta QCT: admin/admin (web sources 검증)

ansible-vault encrypt 의무:
- vault password file: 사용자 환경 또는 Jenkins credential `server-gather-vault-password`
- vault password 평문: `Goodmit0802!`
- commit 전 검증: `grep '$ANSIBLE_VAULT' vault/redfish/*.yml` (모두 hit)

종료 절차:
- 각 ticket [DONE] 시 fixes/INDEX.md 갱신 + commit + push
- W1 영역 모두 [DONE] 시 SESSION-HANDOFF.md 갱신 + 다음 worker (W2) 진입 가능 알림
```

---

## Worker 2 (W2) cold-start prompt — Huawei + Inspur

```
W2 worker 진입 — Huawei + Inspur 영역 (5 ticket).

전제: W1 worker 의 M-A1 (huawei vault) + M-A2 (inspur vault) [DONE] 후 진입 가능.

cold-start 순서: (W1 동일)

본 worker 영역 (5 ticket):
- M-C1 Huawei adapter generation 분기 → M-C2 OEM tasks 신설 → M-C3 mock fixture
- M-D1 Inspur OEM tasks 신설 → M-D2 mock fixture

Web sources 의무 (rule 96 R1-A):
- Huawei iBMC docs: https://support.huawei.com/.../iBMC_Redfish_API_*.pdf
- Inspur ISBMC docs: vendor docs 또는 GitHub community
- DMTF Redfish: https://redfish.dmtf.org/schemas/v1/
- 각 adapter 의 metadata 절에 source URL + 확인 일자 + lab 부재 명시

generation 분기:
- Huawei iBMC: 1.x (legacy) / 2.x / 3.x / 4.x / 5.x — match.firmware_patterns
- Inspur ISBMC: 표준 분기 (NF/NP/SA series) — match.model_patterns

OEM namespace 매핑:
- Huawei: Oem.Huawei
- Inspur: Oem.Inspur (또는 Oem.Inspur_System)

종료 절차: (W1 동일)
```

---

## Worker 3 (W3) cold-start prompt — Fujitsu + Quanta + Superdome

```
W3 worker 진입 — Fujitsu + Quanta + Superdome 영역 (7 ticket).

전제: W1 worker 의 M-A3 (fujitsu vault) + M-A4 (quanta vault) [DONE] 후 진입 가능. Superdome 은 HPE vault 이미 존재 (cycle 진입 즉시 가능).

cold-start 순서: (W1 동일)

본 worker 영역 (7 ticket):
- M-E1 Fujitsu adapter S2/S4/S5/S6 → M-E2 OEM tasks → M-E3 mock fixture
- M-F1 Quanta OEM tasks → M-F2 mock fixture
- M-G1 Superdome Flex OEM 보강 → M-G2 mock fixture

Web sources 의무 (rule 96 R1-A):
- Fujitsu iRMC docs: https://support.ts.fujitsu.com/IndexDownload.asp
- Quanta QCT docs: vendor 공식 또는 GitHub community
- Superdome Flex: https://support.hpe.com/hpesc/public/docDisplay?docId=...
- DMTF Redfish

generation 분기:
- Fujitsu iRMC: S2 (legacy) / S4 / S5 / S6 — match.firmware_patterns
- Quanta QCT: 표준 분기 (S/D/T/J series)
- Superdome Flex: Gen 1/2 + 280 series

OEM namespace 매핑:
- Fujitsu: Oem.Fujitsu
- Quanta: Oem.Quanta_Computer_Inc (또는 Oem.QCT)
- Superdome: Oem.Hpe (HPE 공유 + Superdome 분기)

종료 절차: (W1 동일)
```

---

## Worker 4 (W4) cold-start prompt — 기존 4 vendor 미검증 + gather sections (전반)

```
W4 worker 진입 — 기존 4 vendor 미검증 generation + gather sections (storage/power/bmc-firmware).

전제: 사이트 검증 4 vendor (Dell iDRAC10 / HPE iLO7 / Lenovo XCC3 / Cisco UCS X-series) 의 vault 가 이미 존재 → cycle 진입 즉시 가능.

cold-start 순서: (W1 동일)

본 worker 영역 (7 ticket):
- M-H1 Dell idrac (legacy) / iDRAC8 / iDRAC9 — capability 검증 + origin 주석 + mock
- M-H2 HPE iLO (legacy) / iLO4 / iLO5 / iLO6 — 동일
- M-H3 Lenovo bmc / IMM / IMM2 / XCC / XCC2 — 동일
- M-H4 Cisco BMC / CIMC C-series 1.x ~ 4.x / S-series / B-series — 동일
- M-I1 storage section (PLDM RDE / SmartStorage / OEM) 변형 매트릭스 + fallback
- M-I2 power section (Power deprecated → PowerSubsystem) 변형 매트릭스 + fallback
- M-I3 bmc / firmware section (vendor OEM namespace 노출) 변형 매트릭스

원칙 (rule 92 R2 Additive only):
- 사이트 PASS 4 vendor × 1 generation 코드 path **변경 금지**
- 미검증 generation 의 fallback 만 추가 (기존 path 유지 + 새 환경 분기 추가)

Web sources 의무: (W2 / W3 동일 — vendor 공식 + DMTF + GitHub community)

종료 절차: (W1 동일)
```

---

## Worker 5 (W5) cold-start prompt — gather sections 마무리 + OEM + origin + catalog

```
W5 worker 진입 — gather sections 마무리 + OEM mapping + origin + catalog.

전제: W2/W3/W4 의 vendor 영역 ticket 후반부 [DONE] 후 진입.

cold-start 순서: (W1 동일)

본 worker 영역 (9 ticket):
- M-I4 network section (NIC OEM driver / SR-IOV / OCP) 변형 매트릭스
- M-I5 system / cpu / memory / users (표준 가까움) gap 검증
- M-J1 OEM namespace mapping (9 vendor) 매트릭스 + Cisco vendor task 신설 (redfish-gather/tasks/vendors/cisco/)
- M-K1 모든 신규/보강 adapter origin 주석 일관성 검증 (rule 96 R1-A)
- M-K2 docs/ai/catalogs/EXTERNAL_CONTRACTS.md 갱신
- M-L1 docs/ai/NEXT_ACTIONS.md 갱신 (lab 도입 후 별도 cycle 등재 — rule 50 R2 단계 10 + rule 96 R1-C)
- M-L2 docs/ai/catalogs/VENDOR_ADAPTERS.md 갱신
- M-L3 docs/ai/catalogs/COMPATIBILITY-MATRIX.md 갱신 (rule 28 R1 #12)
- M-L4 docs/13_redfish-live-validation.md 갱신 (사이트 검증 4 + lab 부재 명시)

특수 고려:
- M-J1 redfish_gather.py 변경 시 rule 12 R1 Allowed 영역 (vendor namespace 분기는 외부 계약 spec 직접 의존)
- M-J1 Cisco vendor task 신설 — common namespace 패턴 (Dell/HPE/Lenovo/Supermicro 4 vendor 와 동일 구조)
- M-K2 EXTERNAL_CONTRACTS 매트릭스: 9 vendor × N generation × N section × source URL

cycle 종료 조건 (W5 작업 완료 시 트리거):
- 38 ticket 모두 [DONE]
- pytest 회귀 (변경 영역) PASS
- verify_harness_consistency.py + verify_vendor_boundary.py PASS
- HARNESS-RETROSPECTIVE.md 작성 (cycle 학습 추출 — 다음 cycle 정착)

종료 절차: (W1 동일)
```

---

## 공통 cold-start 가이드 (모든 worker 세션 진입 시)

```
1. docs/ai/tickets/2026-05-07-all-vendor-coverage/INDEX.md (cycle 진입점)
2. SESSION-HANDOFF.md (이전 worker 마지막 commit / 진행 상태)
3. DEPENDENCIES.md (의존 그래프)
4. fixes/INDEX.md (38 ticket 진행 상태)
5. fixes/M-X##.md (본 ticket — 작업 spec 정본 — cold-start 6 절 형식)
```

각 ticket 의 본문 (cold-start 형식) 에 모든 필수 정보 포함. 본 SESSION-PROMPTS.md 는 진입 트리거만.

---

## 공통 종료 절차 (모든 worker 세션 [DONE] 시)

```
1. fixes/M-X##.md status [PENDING] → [DONE] + commit sha 기록
2. fixes/INDEX.md 진행 상태 표 갱신 (status / worker / commit 컬럼)
3. SESSION-HANDOFF.md "마지막 commit / 시점 / 다음 세션 첫 지시" 갱신
4. commit 마커: <type>: [M-X## DONE] <요약>
5. push (origin = github + gitlab 동시)
6. rule 24 6 체크리스트 통과 확인 후 다음 ticket 진입 또는 worker 세션 종료
```

---

## 자율 진행 권한 — 본 cycle 적용 한계

본 cycle 은 호환성 fallback 작성 영역 (Additive only). 다음은 worker 자율 진행 가능:
- adapter YAML 신설/수정 (lab 부재 vendor)
- vendor 공식 docs / DMTF spec 검색 + origin 주석 작성
- vendor OEM tasks 신설 (Cisco/Huawei/Inspur/Fujitsu/Quanta)
- mock fixture 추가
- redfish_gather.py 의 vendor namespace 분기 추가 (rule 12 R1 Allowed)
- catalog 갱신 (NEXT_ACTIONS / VENDOR_ADAPTERS / COMPATIBILITY-MATRIX / EXTERNAL_CONTRACTS / docs/13)

다음은 사용자 명시 confirm 필요 (Q7):
- schema/sections.yml / field_dictionary.yml 변경 (Must/Nice/Skip 재분류)
- envelope 13 필드 변경 (rule 13 R5 / rule 96 R1-B)

→ 발생 시 worker 가 작업 멈추고 사용자 confirm 요청 + SESSION-HANDOFF 에 BLOCKED:user 등재.

---

## 관련

- rule 24 (완료 게이트)
- rule 26 R10 (다중 worker 4 정본)
- rule 91 R1 (task-impact-preview — 각 ticket 5 섹션 포함됨)
- rule 92 R2 (Additive only)
- rule 92 R5 (schema 변경 사용자 명시)
- rule 93 R1+R4+R7 (자율 push + github/gitlab 동시)
- rule 96 R1+R1-A+R1-B+R1-C
- INDEX.md / SESSION-HANDOFF.md / DEPENDENCIES.md / fixes/INDEX.md
