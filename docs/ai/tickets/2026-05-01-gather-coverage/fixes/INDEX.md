# Fix 후보 25건 개별 ticket

> 모든 fix는 **Additive only** — 기존 동작 유지 + 신 환경 호환만 (사용자 명시 2026-05-01).

## P1 — 다음 cycle 권장 (3건)

- [F05](./F05.md) — power EnvironmentMetrics fallback (PowerControl 보존)
- [F13](./F13.md) — Cisco CIMC AccountService 'not_supported' 분류
- [F23](./F23.md) — OS gather 'not_supported' 점진 전환

## P2 — lab 검증 / 사고 재현 후 (9건)

- [F02](./F02.md) — ProcessorType 'Accelerator'/'Core' 통과
- [F04](./F04.md) — HPE iLO 5 BaseNetworkAdapters fallback
- [F06](./F06.md) — thermal 섹션 신규 도입
- [F08](./F08.md) — Cisco CIMC AccountService 제한 (F13 묶음)
- [F10](./F10.md) — HPE Gen11 HBM memory enum
- [F12](./F12.md) — Cisco CIMC PowerSubsystem 검증
- [F17](./F17.md) — Schema 버전 errata 사용
- [F20](./F20.md) — backoff 1초 → 5초
- [F21](./F21.md) — paramiko 2.9.0+ + RHEL 9 ssh-rsa 호환

## P3 — 선제 변경 자제 (11건)

- [F01](./F01.md) — SystemType=DPU enum 통과 검증
- [F03](./F03.md) — IPv6 수집
- [F07](./F07.md) — lspci 부재 환경 'not_supported'
- [F09](./F09.md) — HPE Gen10/Gen10+/Gen11 BIOS Oem path 변경
- [F11](./F11.md) — F4와 묶음 — HPE BaseNetworkAdapters
- [F14](./F14.md) — Dell iDRAC 10 (17G) 호환성
- [F15](./F15.md) — Supermicro X9 adapter 정확성
- [F16](./F16.md) — CVE-2024-54085 패치/미패치 응답
- [F18](./F18.md) — 우리 5 vendor 외 비표준 BMC
- [F19](./F19.md) — TaskService 등 보조 service
- [F22](./F22.md) — WinRM TLS 1.3 호환성
- [F24](./F24.md) — pyvmomi thumbprint deprecated

## P4 — 운영 영역 (1건, 우리 코드 작업 없음)

- F25 — vSphere 7→8 upgrade path 제한 (사이트 운영팀)

## R4 추가 (2026-05-01 추가 검색 — 7건)

> 참고: 사용자 의도 (2026-05-01) "호환성 fallback only" 기준 R4 의 다수는 **새 데이터 수집 영역**.
> 호환성과 새 데이터 수집은 별도 영역으로 분리해야.

- [F26](./F26.md) — PCIeDevice 섹션 수집 (P3) — **새 섹션**
- [F27](./F27.md) — Sensor schema 활용 (P2 / F6 묶음) — **새 섹션**
- [F28](./F28.md) — VirtualMedia 수집 (P3 / scope 외) — **새 섹션**
- [F29](./F29.md) — BIOS Attribute Registry (P3) — **새 데이터**
- [F30](./F30.md) — Telemetry MetricReport (P3 / scope 외) — **새 섹션**
- [F31](./F31.md) — Huawei iBMC vendor 추가 (P3 / 9단계) — **새 vendor**
- [F32](./F32.md) — Linux storage deep 도구 (P2) — **새 데이터**

## R5 추가 (호환성 only — 사용자 의도 정확히 부합 — 4건)

- [F33](./F33.md) — Session 인증 (X-Auth-Token) Additive (Basic fallback) (P3)
- [F34](./F34.md) — Drive Protocol OEM enum 자동 통과 (이미 호환, 검증만 P3)
- [F35](./F35.md) — Manager URI 변종 (이미 호환, 검증만 P3)
- [F36](./F36.md) — HPE OEM fallback sensor (F6 묶음 P2)

## 종합 36건 fix 후보 — 호환성 vs 새 데이터 분리

### 호환성 fallback (사용자 의도 부합 — 18건)

| Priority | 항목 |
|---|---|
| P1 | F05 / F13 / F23 |
| P2 | F02 / F04 / F08 / F10 / F12 / F17 / F20 / F21 / F36 |
| P3 | F01 / F09 / F11 / F14 / F15 / F22 / F24 / F33 / F34 / F35 |

### 새 데이터 수집 (사용자 의도와 별도 영역 — 별도 cycle 권장)

| 영역 | 항목 |
|---|---|
| 새 섹션 | F06 / F26 / F27 / F28 / F30 |
| 새 데이터 | F03 / F19 / F29 / F32 |
| 새 vendor | F31 |

### 횡단 / 추적 (4건)
F07 / F16 / F18 / F25

## 종합 호환성 매트릭스

cycle 2026-04-30 + 2026-05-01 + 이전 누적 — **35건 호환성 fallback 이미 적용됨** (A~L 14 카테고리)

자세히: [../COMPATIBILITY-MATRIX.md](../COMPATIBILITY-MATRIX.md)

## Cold-start 가이드

각 ticket에:
- **현재 위치**: 파일 경로 + 라인
- **변경 (Additive)**: 정확한 코드 변경 형태
- **회귀**: lab fixture / 신규 fixture 필요 여부
- **검증**: pytest / sites 빌드 / 사고 재현
- **우선**: P1~P3
