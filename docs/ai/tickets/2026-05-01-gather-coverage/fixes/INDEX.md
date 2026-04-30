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

## Cold-start 가이드

각 ticket에:
- **현재 위치**: 파일 경로 + 라인
- **변경 (Additive)**: 정확한 코드 변경 형태
- **회귀**: lab fixture / 신규 fixture 필요 여부
- **검증**: pytest / sites 빌드 / 사고 재현
- **우선**: P1~P3
