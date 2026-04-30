# Coverage Main — gather 영역별 외부 호환성 전수 조사

> 목적: 모든 gather 섹션이 외부 시스템 (Redfish API + OS Linux/Windows + ESXi vSphere)
> 의 다양한 펌웨어/버전 변종을 견고하게 수집하도록 호환성 매트릭스 구축.

## 영역 매트릭스 (13 영역 × 3 round)

| # | 영역 | 채널 | 진행 R1 | 진행 R2 | 진행 R3 | 비고 |
|---|---|---|---|---|---|---|
| 1 | system | Redfish + OS + ESXi | [TODO] | [TODO] | [TODO] | hardware/firmware level |
| 2 | bmc | Redfish only | [TODO] | [TODO] | [TODO] | Manager schema |
| 3 | cpu (processors) | Redfish + OS + ESXi | [TODO] | [TODO] | [TODO] | |
| 4 | memory | Redfish + OS + ESXi | [TODO] | [TODO] | [TODO] | |
| 5 | storage | Redfish + OS + ESXi | [TODO] | [TODO] | [TODO] | Storage / SimpleStorage / VMFS |
| 6 | network | Redfish + OS + ESXi | [TODO] | [TODO] | [TODO] | EthernetInterfaces |
| 7 | network_adapters | Redfish only | [TODO] | [TODO] | [TODO] | Chassis NA + NetworkPorts |
| 8 | firmware | Redfish + OS | [TODO] | [TODO] | [TODO] | UpdateService/FirmwareInventory |
| 9 | users | Redfish + OS | [TODO] | [TODO] | [TODO] | AccountService / passwd / Win users |
| 10 | power | Redfish only | [TODO] | [TODO] | [TODO] | Power / PowerSubsystem (DMTF 2020.4) |
| 11 | thermal | Redfish only (NEW) | [TODO] | [TODO] | [TODO] | Thermal / ThermalSubsystem / EnvironmentMetrics |
| 12 | hba_ib | OS Linux only | [TODO] | [TODO] | [TODO] | lspci / FibreChannel / InfiniBand |
| 13 | runtime | OS only | [TODO] | [TODO] | [TODO] | uptime / load / process |

## Round 정의

### Round 1 — DMTF / 표준 spec
- 각 영역의 표준 schema 위치 (URI / endpoint)
- 표준 변천 history (deprecation / 신규 schema)
- 필수 필드 vs 선택 필드

### Round 2 — Vendor 펌웨어 호환성
- Dell iDRAC (7/8/9 generation)
- HPE iLO (4/5/6)
- Lenovo XCC (1/2/3) + IMM2
- Supermicro (X9/X10/X11/X12/X14)
- Cisco CIMC (UCS C-Series)

### Round 3 — 알려진 사고 / 함정
- GitHub issue / 사용자 보고 사례
- 펌웨어 버그 / spec 위반
- 우리 코드의 가설 위반 risk

## 진행 규칙

1. 한 영역 R1 끝나면 coverage/{section}.md 갱신 + 다음 영역 R1
2. 모든 영역 R1 끝나면 R2 진입
3. 모든 영역 R2 끝나면 R3 진입
4. 추가 발견이 0건이면 cycle 종료

## 종합 매트릭스 (Round 끝나면 채움)

### 발견된 호환성 이슈 (cycle 진행 중 누적)

| # | 영역 | 발견 | 영향 | 우선 | 작업 ticket |
|---|---|---|---|---|---|
| (R1 결과) | | | | | |
| (R2 결과) | | | | | |
| (R3 결과) | | | | | |

### 신규 fix candidate

| # | 코드 위치 | 변경 종류 | 우선 |
|---|---|---|---|

## 갱신 history

- 2026-05-01: 본 매트릭스 생성, Round 1 진입 예정
