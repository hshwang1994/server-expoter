# Fix 후보 — 호환성 fallback 영역

> 사용자 명시 (2026-05-01):
> - "호환성 fallback only — 새 데이터 (json) 추가 아님"
> - "redfish 모델/버전에 따라 api 경로/데이터 다를 수 있어서 다양한 환경 대비"
> - "lab 한계 → web 검색이 fixture 대체"
>
> 모든 fix 는 **Additive only** — 기존 동작 유지 + 신 환경 호환만.

## ✓ 호환성 fallback (사용자 의도 부합 — 진짜 작업 영역)

### P1 — 다음 cycle 즉시 권장 (3건)

- [F05](./F05.md) — power EnvironmentMetrics fallback (PowerControl 보존)
- [F13](./F13.md) — Cisco CIMC AccountService 'not_supported' 분류
- [F23](./F23.md) — OS gather 'not_supported' 점진 전환

### P2 — lab 검증 / 사고 재현 후 (10건)

- [F02](./F02.md) — ProcessorType 'Accelerator'/'Core' 통과
- [F04](./F04.md) — HPE iLO 5 BaseNetworkAdapters fallback
- [F08](./F08.md) — Cisco CIMC AccountService 제한 (F13 묶음)
- [F10](./F10.md) — HPE Gen11 HBM memory enum (자동 통과 검증)
- [F12](./F12.md) — Cisco CIMC PowerSubsystem 검증
- [F17](./F17.md) — Schema 버전 errata 사용
- [F20](./F20.md) — backoff 1초 → 5초 (BMC lockout 회피)
- [F21](./F21.md) — paramiko 2.9.0+ + RHEL 9 ssh-rsa 호환

### P3 — 사고 재현 시 / 검증만 (10건)

- [F01](./F01.md) — SystemType=DPU enum 통과 (이미 호환)
- [F09](./F09.md) — HPE Gen10/Gen10+/Gen11 BIOS Oem path 변경 (현재 영향 없음)
- [F11](./F11.md) — F4 묶음
- [F14](./F14.md) — Dell iDRAC 10 (17G) — 신규 adapter
- [F15](./F15.md) — Supermicro X9 adapter 정확성
- [F22](./F22.md) — WinRM TLS 1.3 호환 추적
- [F24](./F24.md) — pyvmomi thumbprint 호환
- [F33](./F33.md) — Session 인증 (X-Auth-Token) Additive
- [F34](./F34.md) — Drive Protocol OEM enum 자동 통과 (검증만)
- [F35](./F35.md) — Manager URI 변종 (이미 호환, 검증만)

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

- [F37](./F37.md) — Linux IB 도구 부재 graceful (P3 / F07 묶음)
- [F38](./F38.md) — Windows IB NIC 분류 fallback (P3)
- [F39](./F39.md) — ESXi IB skip (의도된 기술 제약, P4)
- [F40](./F40.md) — Redfish ConnectX VPI mode 호환 (이미 호환, 검증만 P3)

### R7 추가 호환성 (3건 신규 — 2026-05-01 추가 검색)

- [F41](./F41.md) — community.vmware 6.2.0 → 7.0.0 호환성 (P2)
- [F42](./F42.md) — Redfish v2 path 향후 호환성 (P3 추적)
- [F43](./F43.md) — RHEL 10 crypto policy SHA-1 호환 (P3 검증)

### 횡단 / 추적 (2건)

- [F07](./F07.md) — lspci 부재 환경 'not_supported' (F23 묶음)
- [F16](./F16.md) — CVE-2024-54085 패치/미패치 응답 추적

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

## 종합 — 호환성 fix 후보 분류

- **호환성 fallback (사용자 의도)**: 22건 (R5+R6 포함)
  - P1: 3 / P2: 8 / P3: 11 (검증만 또는 사고 재현 시)
- **호환성 영역 외**: 12건 (별도 cycle)

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
