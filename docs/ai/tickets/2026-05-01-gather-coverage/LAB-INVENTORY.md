# Lab Inventory — 우리 lab 보유 / 부재 장비

> 사용자 명시 (2026-05-01): "lab 한계 → web 검색이 fixture 대체"
> 우리 lab 의 한계를 명시 + web 검색 의존 영역 명확화.

## A. lab 보유 (실 검증 가능)

### Redfish BMC (5 vendor)

| Vendor | 모델 | 펌웨어 | Redfish ver | 비고 |
|---|---|---|---|---|
| Dell | PowerEdge R760 | iDRAC 9 (5.x+) | 1.x | cycle 2026-04-29 fix B01 검증 (Tesla T4 GPU) |
| Dell | PowerEdge R740 | iDRAC 9 (5.x) | 1.x | |
| Dell | PowerEdge R640 | iDRAC 9 (5.x) | 1.x | |
| HPE | ProLiant DL380 Gen11 | iLO 6 v1.73 | 1.20.0 | 10.50.11.231 — Round 11 reference |
| HPE | ProLiant Compute DL380 Gen12 | iLO 6 (1.x) | 1.20.0 | 사용자 사이트 검증 |
| Lenovo | ThinkSystem SR650 V2 | XCC1 | 1.15.0 | NetworkAdapter placeholder 검증 |
| Supermicro | (정확 모델 확인 필요) | X11+ | 1.x | |
| Cisco | UCS C-series CIMC | 4.x | 1.0.1+ | trailing whitespace 정규화 검증 |

### OS

| OS | 모델 | 비고 |
|---|---|---|
| RHEL 8.10 | py3.6 (raw fallback 검증) | Round 2 |
| RHEL 9.2 / 9.6 | Python 3.9+ | |
| Rocky Linux 9.6 | Python 3.9+ | |
| Ubuntu 24.04 | Python 3.12 | |
| Windows Server (2019/2022) | WinRM HTTPS 5986 | |

### ESXi

| ESXi 버전 | 비고 |
|---|---|
| 7.0 U3 | community.vmware 6.2.0 호환 |
| 8.0 | pyvmomi 9.0.0 |

### 네트워크 환경

- 기본 IPv4
- 사내 BMC self-signed 인증서
- 5 vendor 모두 같은 망

## B. lab 부재 (web 검색 의존)

### Redfish BMC (모델/펌웨어)

| 영역 | 상황 | 영향 fix 후보 | web sources |
|---|---|---|---|
| Dell iDRAC 7 (구) | 사이트 운영 정책상 단종 | F15 (정상 미지원 분류) | Dell PowerEdge 12G/11G docs |
| Dell iDRAC 8 | lab 없음 | F15 (Power 미지원) | iDRAC 8 v2.40 Redfish guide |
| Dell iDRAC 10 (17G PowerEdge, 2024-) | 신규 | F14 | developer.dell.com/iDRAC10 |
| HPE iLO 4 (Gen9) | 단종 | (영향 없음) | HPE iLO 4 OEM docs |
| HPE iLO 5 (구 펌웨어 2.x 초기) | lab 없음 | F04 (BaseNetworkAdapters fallback) | iLO 5 1.10+ docs |
| Lenovo IMM2 (구) | 단종 | (영향 없음) | Lenovo Press tips0849 |
| Lenovo XCC2 / XCC3 | lab 없음 | (사용자 사이트 1.17.0 후보) | XCC2/XCC3 REST API guide |
| Supermicro X9/X10 | lab 없음 | F15 (X9 미지원 분류) | Supermicro 공식 매트릭스 |
| Supermicro X14 (PowerSubsystem) | lab 없음 | F12 (PowerSubsystem 검증) | Supermicro Redfish 4.0+ docs |
| Cisco CIMC 신 펌웨어 | 일부 펌웨어만 | F13 (AccountService 제한) | Cisco UCS C-series API guide 4.3 |

### 신규 vendor (5 vendor 외)

| Vendor | 운영 | sources |
|---|---|---|
| Huawei iBMC | 사이트 운영 안 함 | Huawei iBMC API docs (EDOC1000126992) |
| Inspur | 운영 안 함 | OpenBMC 기반 일부 |
| ASRock Rack | 운영 안 함 | AMI MegaRAC |
| Asus | 운영 안 함 | AMI MegaRAC |
| NVIDIA BlueField DPU | SmartNIC 영역 (server-exporter scope 외) | NVIDIA nvbmc-docs |

### InfiniBand (R6 신규)

| 채널 | lab | 영향 fix | sources |
|---|---|---|---|
| Redfish IB | **없음** | F40 (이미 호환 — 검증만) | NVIDIA Mellanox docs / Lenovo XCC docs |
| Linux IB | **없음** (HBA만) | F37 (graceful) | ArchWiki / RHEL 8 IB guide |
| Windows IB | **없음** | F38 (Mellanox VEN_15B3 분류) | Mellanox WinOF docs / Microsoft Get-NetAdapter |
| ESXi IB | **없음** | F39 (skip 의도) | VMware vSphere 8 IB white paper |

### OS 환경 (변종)

| 환경 | lab | 영향 |
|---|---|---|
| RHEL 7 (구) | 없음 | (단종 — 영향 없음) |
| **RHEL 10 (2026-)** | 없음 | F43 (crypto policy 호환 추적) |
| Alpine container / busybox | 없음 | F07 / F23 (graceful) |
| HPC Windows IB | 없음 | F38 (Mellanox 분류) |
| Windows Server 2008 R2 | 없음 | (단종 — 영향 없음) |

### ESXi 변종

| 환경 | lab |
|---|---|
| ESXi 6.5 / 6.7 (구) | 없음 |
| ESXi 8.x 신 펌웨어 | 일부 |
| vCenter 통합 | 없음 (호스트 직접 수집) |

## C. lab 한계 → 검증 전략

### 1. web 검색 신뢰 영역 (직접 적용 가능)
- DMTF 표준 spec
- vendor 공식 docs (HPE iLO docs / Dell developer.dell.com / Lenovo pubs.lenovo.com / Cisco docs)
- 다수 GitHub repo 검증된 동작

### 2. web 검색 + 사이트 검증 필요 영역
- **HPE iLO 5 구 펌웨어 BaseNetworkAdapters 응답 형식** (F04)
- **Cisco CIMC PowerSubsystem 응답** (F12)
- **Cisco CIMC AccountService 미지원 펌웨어** (F13)
- **Dell iDRAC 8 일부 모델 Power/NetworkAdapters 미지원** (사용자 사이트 보고됨)
- **Lenovo XCC3 1.17.0 ServiceRoot 응답** (사용자 사이트)

### 3. lab 부재 + web 부족 (사용자 보고 의존)
- Windows IB 환경 (F38)
- HPE Gen11 HBM memory (F10)
- Dell iDRAC 10 (F14)

### 4. skip 영역 (vendor 의도)
- **ESXi InfiniBand** (F39) — VMware가 IB를 Ethernet으로 인식

## D. lab 확장 권장 (사이트 운영 결정)

| 영역 | 우선 |
|---|---|
| Dell iDRAC 8 1대 (사고 재현 + 호환성) | P2 |
| HPE iLO 5 구 펌웨어 1대 | P2 |
| Cisco CIMC 4.x 1대 (PowerSubsystem 검증) | P2 |
| Mellanox ConnectX IB 1대 (Linux/Windows/ESXi) | P3 |
| RHEL 10 agent 1대 | P3 |
| Lenovo XCC3 1대 | P2 |

## E. fixture 캡처 우선순위 (다음 세션 작업)

1. **F04 위해 HPE iLO 5 구 펌웨어 BaseNetworkAdapters 응답** (web docs 만으로 부족)
2. **F12 위해 Cisco CIMC PowerSubsystem 응답**
3. **F38 위해 Windows IB Get-PnpDevice 출력**
4. **F10 위해 HPE Gen11 HBM Memory 응답**
5. **F14 위해 Dell iDRAC 10 ServiceRoot**

## 갱신 history

- 2026-05-01: 초안. lab 보유 / 부재 명시. F37~F43 영역 lab 한계 추적.
