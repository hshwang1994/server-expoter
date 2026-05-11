# Fixes INDEX — 2026-05-07 all-vendor-coverage

> 38 ticket 분류 + 진행 상태 추적. worker 세션은 본 INDEX 보고 [PENDING] + 의존 통과 ticket 선택.

---

## 진행 상태 (38 ticket)

| ticket | 영역 | 우선 | 의존 | status | worker | commit |
|---|---|---|---|---|---|---|
| **M-A1** | huawei vault 신설 (primary infraops/Password123! + recovery Administrator/Admin@9000) | P1 | — | **[DONE]** | W1 | 2026-05-11 |
| **M-A2** | inspur vault 신설 (primary infraops/Password123! + recovery admin/admin) | P1 | — | **[DONE]** | W1 | 2026-05-11 |
| **M-A3** | fujitsu vault 신설 (primary infraops/Password123! + recovery admin/admin) | P1 | — | **[DONE]** | W1 | 2026-05-11 |
| **M-A4** | quanta vault 신설 (primary infraops/Password123! + recovery admin/admin) | P1 | — | **[DONE]** | W1 | 2026-05-11 |
| **M-A5** | 5 기존 vendor primary infraops/Password123! 통일 + Supermicro recovery 추가 (ADMIN/ADMIN) + HPE/Lenovo/Cisco 공장 기본 자격 append (Additive) | P1 | — | **[DONE]** | W1 | 2026-05-11 |
| **M-A6** | docs/21_vault-operations.md 갱신 (9 vendor 매트릭스 + Password123! 정책 + account_service 자동 생성 메커니즘) | P2 | A1, A2, A3, A4, A5 | **[DONE]** | W1 | 2026-05-11 |
| **M-B1** | adapters/redfish/supermicro_x10.yml 신설 (현재 누락) | P1 | A6 | **[DONE]** | W1-Agent | 2026-05-11 |
| **M-B2** | Supermicro 6 generation (BMC/X9/X10/X11/X12/X13/X14) capability 정합 + origin 주석 강화 | P1 | B1 | **[DONE]** | W1-Agent | 2026-05-11 |
| **M-B3** | H11/H12/H13/H14 (AMD) + ARS (ARM) 변형 — model_patterns 확장 + supermicro_ars.yml 신설 | P2 | B2 | **[DONE]** | W1-Agent | 2026-05-11 |
| **M-B4** | Supermicro mock fixture (X10/X12/X14 — 우선순위 1~3) | P1 | B3 | **[DONE]** | W1-Agent | 2026-05-11 |
| **M-C1** | Huawei iBMC adapter generation 분기 (1.x ~ 5.x) + Atlas model_patterns + capabilities 분기 | P1 | A1 | **[DONE]** | W2-Agent | 2026-05-11 |
| **M-C2** | redfish-gather/tasks/vendors/huawei/{collect_oem.yml, normalize_oem.yml} 신설 (Oem.Huawei.{SystemInfo, SmartProvisioning, NetworkBindings, BoardInfo}) | P1 | C1 | **[DONE]** | W2-Agent | 2026-05-11 |
| **M-C3** | Huawei mock fixture (iBMC v2/v4 + Atlas) | P1 | C2 | **[DONE]** | W2-Agent | 2026-05-11 |
| **M-D1** | redfish-gather/tasks/vendors/inspur/{collect_oem.yml, normalize_oem.yml} 신설 (Oem.Inspur primary + Oem.Inspur_System fallback) | P1 | A2 | **[DONE]** | W2-Agent | 2026-05-11 |
| **M-D2** | Inspur mock fixture (NF5280M5) | P1 | D1 | **[DONE]** | W2-Agent | 2026-05-11 |
| **M-E1** | Fujitsu iRMC S2/S4/S5/S6 generation 분기 + PRIMEQUEST model_patterns + capabilities | P1 | A3 | **[DONE]** | W3-Agent | 2026-05-11 |
| **M-E2** | redfish-gather/tasks/vendors/fujitsu/{collect_oem.yml, normalize_oem.yml} 신설 (Oem.ts_fujitsu primary + Oem.Fujitsu fallback) | P1 | E1 | **[DONE]** | W3-Agent | 2026-05-11 |
| **M-E3** | Fujitsu mock fixture (iRMC S5 PRIMERGY + S6 PowerSubsystem) | P1 | E2 | **[DONE]** | W3-Agent | 2026-05-11 |
| **M-F1** | redfish-gather/tasks/vendors/quanta/{collect_oem.yml, normalize_oem.yml} 신설 (Oem.Quanta_Computer_Inc → Oem.QCT → Oem.OpenBmc 3-tier fallback) | P1 | A4 | **[DONE]** | W3-Agent | 2026-05-11 |
| **M-F2** | Quanta mock fixture (QuantaGrid D54Q-2U) | P1 | F1 | **[DONE]** | W3-Agent | 2026-05-11 |
| **M-G1** | redfish-gather/tasks/vendors/hpe/collect_oem.yml — Superdome Flex 분기 보강 (PartitionInfo + FlexNodeInfo + GlobalConfiguration, Additive when 조건) | P1 | — | **[DONE]** | W3-Agent | 2026-05-11 |
| **M-G2** | Superdome Flex mock fixture (Gen 1/2 generic, dual-manager + Partition0) | P1 | G1 | **[DONE]** | W3-Agent | 2026-05-11 |
| **M-H1** | Dell idrac (legacy) / iDRAC8 / iDRAC9 — capability + origin + mock 3건 | P1 | — | **[DONE]** | W4-Agent | 2026-05-11 |
| **M-H2** | HPE iLO (legacy) / iLO4 / iLO5 / iLO6 — capability + origin + mock 4건 | P1 | — | **[DONE]** | W4-Agent | 2026-05-11 |
| **M-H3** | Lenovo bmc / IMM2 / XCC — XCC2 firmware_patterns 추가 (Additive 분기, 새 adapter 회피) + mock 3건 | P1 | — | **[DONE]** | W4-Agent | 2026-05-11 |
| **M-H4** | Cisco BMC / CIMC 2.x/3.x/4.x — S-series model_patterns 추가 + mock 4건 | P1 | — | **[DONE]** | W4-Agent | 2026-05-11 |
| **M-I1** | storage section (PLDM RDE / SmartStorage / OEM Drive / Volume / SimpleStorage) 변형 매트릭스 + fallback | P1 | H1, H2, H3, H4 | [PENDING] | W4 | — |
| **M-I2** | power section (Power deprecated → PowerSubsystem 마이그레이션) 변형 매트릭스 + fallback | P1 | I1 | [PENDING] | W4 | — |
| **M-I3** | bmc / firmware section (vendor OEM namespace 노출) 변형 매트릭스 | P1 | I2 | [PENDING] | W4 | — |
| **M-I4** | network section (NIC OEM driver / SR-IOV / OCP) 변형 매트릭스 | P2 | I3 | [PENDING] | W5 | — |
| **M-I5** | system / cpu / memory / users (표준 가까움) gap 검증 | P2 | I4 | [PENDING] | W5 | — |
| **M-J1** | OEM namespace mapping (9 vendor) redfish_gather.py 분기 매트릭스 + Cisco vendor task 신설 | P1 | B4, C3, D2, E3, F2, G2, H1~H4, I5 | [PENDING] | W5 | — |
| **M-K1** | 모든 신규/보강 adapter origin 주석 일관성 검증 (rule 96 R1-A) | P1 | J1 | [PENDING] | W5 | — |
| **M-K2** | docs/ai/catalogs/EXTERNAL_CONTRACTS.md 갱신 (9 vendor × N gen × N section × source URL) | P1 | K1 | [PENDING] | W5 | — |
| **M-L1** | docs/ai/NEXT_ACTIONS.md 갱신 (lab 도입 후 별도 cycle 등재 — rule 50 R2 단계 10 + rule 96 R1-C) | P1 | K2 | [PENDING] | W5 | — |
| **M-L2** | docs/ai/catalogs/VENDOR_ADAPTERS.md 갱신 (29 adapter 매트릭스) | P2 | L1 | [PENDING] | W5 | — |
| **M-L3** | docs/ai/catalogs/COMPATIBILITY-MATRIX.md 갱신 (rule 28 R1 #12) | P2 | L2 | [PENDING] | W5 | — |
| **M-L4** | docs/13_redfish-live-validation.md 갱신 (사이트 검증 4 + lab 부재 명시) | P1 | L3 | [PENDING] | W5 | — |

총 **38 ticket**.

---

## 우선 분류

- **P1 (cycle 본 영역, 33건)**: M-A1~A5, M-B1~B2, M-B4, M-C1~C3, M-D1~D2, M-E1~E3, M-F1~F2, M-G1~G2, M-H1~H4, M-I1~I3, M-J1, M-K1~K2, M-L1, M-L4
- **P2 (보강, 5건)**: M-A6, M-B3, M-I4~I5, M-L2~L3

---

## 영역별 묶음

### A: Vault 임시 정책 (W1, 6건)
- 사용자 명시 (Q4 2026-05-07): vendor 공장 기본 자격으로 vault 임시 자격 추가
- 4 vendor 신설 (Huawei/Inspur/Fujitsu/Quanta) + 5 vendor recovery 자격 추가 (Dell/HPE/Lenovo/Supermicro/Cisco) + docs

### B: Supermicro 6 generation 보강 (W1, 4건)
- X10 adapter 누락 신설 + 6 gen capability + AMD/ARM 변형 + mock

### C: Huawei iBMC 보강 (W2, 3건)
- adapter generation 분기 (1.x ~ 5.x) + OEM tasks 신설 + mock

### D: Inspur ISBMC 보강 (W2, 2건)
- OEM tasks 신설 + mock

### E: Fujitsu iRMC 보강 (W3, 3건)
- adapter S2/S4/S5/S6 분기 + OEM tasks 신설 + mock

### F: Quanta QCT 보강 (W3, 2건)
- OEM tasks 신설 + mock

### G: HPE Superdome Flex 보강 (W3, 2건)
- OEM 분기 보강 (Gen 1/2 + 280) + mock

### H: 기존 4 vendor 미검증 generation (W4, 4건)
- Dell/HPE/Lenovo/Cisco 의 사이트 검증되지 않은 generation 보강 (capability + origin + mock)

### I: gather 10 sections × all vendor 변형 (W4 + W5, 5건)
- M-I1 storage / M-I2 power / M-I3 bmc-firmware / M-I4 network / M-I5 system-cpu-mem-users
- 변형 매트릭스 + fallback (Additive only)

### J: OEM namespace mapping (W5, 1건)
- 9 vendor namespace 매트릭스 + Cisco vendor task 신설 (현재 부재)

### K: origin + EXTERNAL_CONTRACTS (W5, 2건)
- adapter origin 주석 일관성 + 카탈로그

### L: catalog 갱신 (W5, 4건)
- NEXT_ACTIONS / VENDOR_ADAPTERS / COMPATIBILITY-MATRIX / docs/13

---

## status 의미

| status | 의미 |
|---|---|
| [PENDING] | 의존 통과 → worker 진입 가능 |
| [BLOCKED:dep] | 의존 ticket 미완료 |
| [IN-PROGRESS] | worker 진행 중 |
| [DONE] | 완료 + commit |
| [SKIP] | 진행 불필요 (사유 commit 컬럼 명시) |
| [BLOCKED:user] | 사용자 결정 대기 (Q7 schema 변경 trigger 등) |
| [BLOCKED:lab] | lab 검증 대기 (cycle 종료까지) |

---

## worker 진입 절차

1. 본 INDEX 읽고 [PENDING] + 의존 통과 ticket 선택 (worker 컬럼 일치 확인)
2. 해당 ticket M-X##.md 읽기
3. status 갱신: [PENDING] → [IN-PROGRESS], worker 컬럼 채움 (이미 채워져 있으면 변경 없음)
4. 작업 진행
5. 완료 시: status 갱신 [IN-PROGRESS] → [DONE], commit sha 기록
6. SESSION-HANDOFF.md 갱신
7. commit + push (rule 93 R1+R4)

---

## 관련

- ../INDEX.md
- ../SESSION-HANDOFF.md
- ../DEPENDENCIES.md
- ../SESSION-PROMPTS.md
- ../COMPATIBILITY-MATRIX.md
