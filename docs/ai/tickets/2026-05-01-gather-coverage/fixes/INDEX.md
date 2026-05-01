# Fix 후보 — 호환성 fallback 영역

> 사용자 명시 (2026-05-01):
> - "호환성 fallback only — 새 데이터 (json) 추가 아님"
> - "redfish 모델/버전에 따라 api 경로/데이터 다를 수 있어서 다양한 환경 대비"
> - "lab 한계 → web 검색이 fixture 대체"
>
> 모든 fix 는 **Additive only** — 기존 동작 유지 + 신 환경 호환만.

## ✓ 호환성 fallback (사용자 의도 부합 — 진짜 작업 영역)

### P1 — [DONE] cycle 2026-05-01 P1 follow-up 완료

- [F05](./F05.md) [DONE] — power EnvironmentMetrics fallback (코드 적용 + 회귀 5건)
- [F13](./F13.md) [DONE] — Cisco CIMC AccountService 'not_supported' (코드 적용 + 회귀 4건)
- [F23](./F23.md) [DONE] — OS gather 'not_supported' 점진 전환 (Linux/Windows users + 회귀 9건)

### P2 — lab 검증 / 사고 재현 후 (10건)

- [F02](./F02.md) [DONE] — ProcessorType 'CORE' enum 통과 (commit 36c40db9, normalize_standard.yml)
- [F04](./F04.md) [BLOCKED:lab-fixture] — HPE iLO 5 BaseNetworkAdapters fallback (구 펌웨어 fixture 필요)
- [F08](./F08.md) [DONE via F13] — Cisco CIMC AccountService 제한 (F13 통합 적용)
- [F10](./F10.md) [VERIFIED-COMPATIBLE] — HPE Gen11 HBM memory enum (코드 자동 호환 — fixture 검증만)
- [F12](./F12.md) [VERIFIED-COMPATIBLE] — Cisco CIMC PowerSubsystem (코드 fallback 이미 존재 — lab 확인만)
- [F17](./F17.md) [TRACKING-ONLY] — Schema errata (코드 변경 없음 — DMTF 정기 추적 정책)
- [F20](./F20.md) [DONE] — backoff 1초 → 5초 (commit 36c40db9, try_one_account.yml)
- [F21](./F21.md) [DONE] — paramiko 2.9.0+ + RHEL 9 ssh-rsa (commit 36c40db9, ansible.cfg ssh_args)

### P3 — 사고 재현 시 / 검증만 (10건)

- [F01](./F01.md) [VERIFIED-COMPATIBLE] — SystemType=DPU enum (raw passthrough — 검증만)
- [F09](./F09.md) [TRACKING-ONLY] — HPE BIOS Oem path 변경 (현재 영향 없음)
- [F11](./F11.md) [DONE via F04 묶음] — (F04 적용 시 자동 해소)
- [F14](./F14.md) [DONE via F41] — Dell iDRAC 10 (17G) → cycle-019 phase 1 dell_idrac10.yml
- [F15](./F15.md) [BLOCKED:lab-fixture] — Supermicro X9 adapter 정확성 검증
- [F22](./F22.md) [BLOCKED:incident] — WinRM TLS 1.3 호환 추적
- [F24](./F24.md) [TRACKING-ONLY] — pyvmomi thumbprint (보안 강화 결정 시)
- [F33](./F33.md) [BLOCKED:incident] — Session 인증 (X-Auth-Token) — 사고 발생 시 적용
- [F34](./F34.md) [VERIFIED-COMPATIBLE] — Drive Protocol OEM enum (raw passthrough)
- [F35](./F35.md) [VERIFIED-COMPATIBLE] — Manager URI 변종 (동적 lookup — 모든 vendor 자동 호환)

## 신규 vendor 코드 생성 ticket (F44~F47, 사용자 명시 2026-05-01)

> "신규 장비 도입 의향 있다 다만 lab 장비 없다. vault 만들지 말고 코드 생성 ticket 만"

- [F44](./F44.md) — Huawei iBMC adapter (vault 미생성)
- [F45](./F45.md) — Inspur ISBMC adapter (vault 미생성)
- [F46](./F46.md) — Fujitsu iRMC adapter (vault 미생성)
- [F47](./F47.md) — Quanta QCT BMC adapter (vault 미생성)

## audit 발견 ticket (F41~F145 — WEB-COMPATIBILITY-AUDIT + WEB-EXTENDED-AUDIT-10R 본문 참조)

본 fixes/ 디렉터리는 P1/P2/P3 분류된 cold-start 가능 ticket 만 보관. F48~F90 / F91~F145 의 audit ID 는 audit 문서 본문 내부 ID.

audit 문서:
- [WEB-COMPATIBILITY-AUDIT-2026-05-01.md](../WEB-COMPATIBILITY-AUDIT-2026-05-01.md) — 7-loop F41~F90
- [WEB-EXTENDED-AUDIT-10R-2026-05-01.md](../WEB-EXTENDED-AUDIT-10R-2026-05-01.md) — 10-round F91~F145

신 vendor (F44~F47) 외의 audit 발견 항목은 다음 cycle 진입 시 본 INDEX 에 P1 각각 추가 fixes/F##.md 작성.

### R6 InfiniBand 호환성 (4건 신규)

- [F37](./F37.md) [BLOCKED:schema-out-of-scope] — Linux IB 도구 부재 graceful (hba_ib는 storage/network sub-key, schema section 신설 필요)
- [F38](./F38.md) [BLOCKED:lab-fixture] — Windows IB NIC 분류 fallback (Mellanox WinOF host 필요)
- [F39](./F39.md) [BY-DESIGN] — ESXi IB skip (의도된 기술 제약, P4)
- [F40](./F40.md) [VERIFIED-COMPATIBLE] — Redfish ConnectX VPI mode (raw passthrough — 검증만)

### R7 추가 호환성 (3건 신규 — 2026-05-01 추가 검색)

- [F41](./F41.md) [TRACKING-ONLY] — community.vmware 6.2.0 → 7.0.0 호환성 (정기 추적)
- [F42](./F42.md) [TRACKING-ONLY] — Redfish v2 path 향후 호환성 (DMTF release 추적)
- [F43](./F43.md) [BLOCKED:rhel10-adoption] — RHEL 10 crypto policy SHA-1 (RHEL 10 lab 도입 시)

### 횡단 / 추적 (2건)

- [F07](./F07.md) [DONE via F23 부분] — lspci 부재 환경 'not_supported' (users 섹션 적용 / hba_ib는 schema 영역 외)
- [F16](./F16.md) [TRACKING-ONLY] — CVE-2024-54085 패치/미패치 응답 추적 (advisory)

## ⚠️ 호환성 영역 외 — 별도 cycle (10건)

> 사용자 의도 "호환성 fallback only" 와 별개 영역. 새 데이터 / 새 섹션 / 새 vendor 추가는 **본 cycle scope 외**.

| # | 영역 | 분류 | 이유 |
|---|---|---|---|
| F03 | network | 새 데이터 | IPv6 수집 — 신규 데이터 추가 |
| F06 | thermal | 신규 섹션 | thermal 섹션 자체 신설 |
| F19 | 횡단 | 신규 섹션 | TaskService / EventService 등 |
| F25 | ESXi | 운영 영역 | vSphere upgrade path |
| F26 | pcie | 신규 섹션 | PCIeDevice 섹션 신설 |
| F27 | sensors | 신규 섹션 (F6 묶음) | Sensor schema 신설 |
| F28 | virtualmedia | 신규 섹션 | VirtualMedia 수집 |
| F29 | bios | 새 데이터 | BIOS Attribute Registry 신규 필드 |
| F30 | telemetry | 신규 섹션 | TelemetryService 신설 |
| F31 | new vendor | 새 vendor | Huawei iBMC 추가 |
| F32 | OS storage | 새 데이터 | nvme-cli / LVM / mdadm 신규 필드 |
| F18 | 횡단 | 추적만 | 5 vendor 외 비표준 BMC |

## 종합 — 호환성 fix 후보 분류 (cycle-019 phase 3 close 시점 — 2026-05-01)

- **호환성 fallback (사용자 의도)**: 22건 (R5+R6 포함)
  - **[DONE]**: 9건
    - P1: F05/F13/F23 (P1 follow-up cycle)
    - 호환성 일괄: F02/F20/F21 (commit 36c40db9)
    - 묶음: F08/F11/F14 (다른 ticket에 통합)
  - **[VERIFIED-COMPATIBLE]**: 5건 (F01/F10/F12/F34/F35/F40) — 코드 자동 호환 / lab 검증만 잔여
  - **[TRACKING-ONLY]**: 5건 (F09/F16/F17/F24/F41/F42) — 정기 추적 정책
  - **[BLOCKED:lab-fixture]**: 3건 (F04/F15/F38)
  - **[BLOCKED:incident]**: 2건 (F22/F33)
  - **[BY-DESIGN]**: 1건 (F39)
  - **[BLOCKED:rhel10-adoption]**: 1건 (F43)
  - **[BLOCKED:schema-out-of-scope]**: 1건 (F37) — hba_ib section 신설 필요 (호환성 외)
- **호환성 영역 외**: 12건 (별도 cycle, 호환성 fallback 영역 외)
- **신규 vendor (lab 부재 + 사용자 도입 의향)**: F44~F47 — adapter/aliases 적용 완료, vault/baseline/OEM/Round 외부 의존 잔여

### 코드 변경 완료 12건 vs 외부 의존 13건

**AI 환경에서 적용한 코드 변경**: 12건 (P1 3 + 호환성 일괄 3 + 묶음 3 + neighbouring 3)
**외부 의존 잔여**: 13건 (lab fixture 4 + 사고 재현 2 + tracking 5 + design 2)

## 호환성 적용 종합

cycle 2026-04-30 + 2026-05-01 + 이전 누적 — **35건 호환성 fallback 이미 적용**:
[../COMPATIBILITY-MATRIX.md](../COMPATIBILITY-MATRIX.md) — A~L 14 카테고리

## 추가 검색 종료 조건 (사용자 명시)

R1: DMTF 표준 / R2: 5 vendor 펌웨어 / R3: 사고 함정 / R4: 새 영역 (scope 외) / R5: 호환성 추가 / **R6: InfiniBand 4 채널** ← 여기까지 검색.

호환성 영역에서 더 검색할 항목:
- DateTime 형식 변종 → 이미 raw passthrough
- Numeric vs string → 이미 _safe_int
- Empty/null/missing → 이미 _safe + default
- charset/encoding → 이미 errors='replace'
- HTTP redirect → 표준 urllib 자동 처리

→ **호환성 영역 추가 검색 효용 적음**. 종료 조건 도달.
