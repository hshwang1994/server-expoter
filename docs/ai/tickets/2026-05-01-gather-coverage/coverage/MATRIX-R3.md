# Coverage Round 3 — 알려진 사고 / 함정 / 호환성 issue

> GitHub issue / DMTF Validator / 벤더 release notes / 사용자 보고 사례. cycle 2026-05-01.

## R3 발견 — Redfish

### F16 — CVE-2024-54085 (AMI MegaRAC BMC Auth Bypass)
- **영향**: ASUS / Dell / Gigabyte / HPE / Lanner / Lenovo / NVIDIA / Tyan
- **CVSS 10**, X-Server-Addr / Host header 기반 인증 우회
- **우리 영향**: read-only gather라 직접 risk 작음. 단 패치 펌웨어 vs 미패치 응답 차이 가능 — 사이트 BMC 펌웨어 버전 추적 (P3)
- 패치: AMI 2025-03-11. HPE / Lenovo 패치 출시
- Source: [Greenbone CVE-2024-54085 분석](https://www.greenbone.net/en/blog/ami-bmc-flaw-remote-takeover-and-dos-of-server-infrastructure/)

### F17 — Schema 버전 mismatch (DMTF Validator known issue)
- **증상**: Service가 v1.0.0 schema 응답하는데 client가 신 schema (v1.0.5) 가정 → false validation failure
- **우리 영향**: redfish_gather.py가 schema 버전 명시 없이 필드 read. 일부 필드 부재 시 `_safe()` 가 None 반환 → 안전. 하지만 **신규 enum 값** (예: cpu ProcessorType=Accelerator)은 우리 가정 위반 가능
- 권장: errata schema (v1.X.Y 의 latest patch) 기준 검증
- Source: [DMTF Redfish-Service-Validator issue #68](https://github.com/DMTF/Redfish-Service-Validator/issues/68)

### F18 — vendor 비표준 응답 (Cisco / Gigabyte / Advantech)
- **Gigabyte BMC**: 펌웨어 따라 `Missing Redfish Data` (Cray docs known issue) — 펌웨어 업그레이드 필요
- **Advantech BMC**: `/redfish/v1/TaskService/Tasks/0` 404 — TaskService 변종
- **Cisco CIMC**: vendor별 implementation 다름 — bb-Ricardo/check_redfish 등 monitoring tool 도 vendor 분기 필요 (우리 adapter 시스템과 같은 정신)
- **우리 영향**: 우리 5 vendor (Dell/HPE/Lenovo/Supermicro/Cisco) 외라 직접 영향 미미. 단 Cisco CIMC 응답 변종은 cycle 2026-04-29 cisco-critical-review 에서 일부 처리

### F19 — TaskService / EventService 등 보조 service 미수집
- **우리 영향**: 우리는 9 섹션 (system/bmc/...) 만 수집. TaskService / EventService / SessionService 등 미수집 — 영향 없음. 향후 firmware update 자동화 도입 시 검토

### F20 — vendor lockout policy 차이
- **Dell iDRAC**: 5회 fail시 source IP lockout (default 5분)
- **HPE iLO**: 3회 fail (펌웨어별)
- **Lenovo XCC**: 5회 fail / 사용자 설정 가능
- **우리 영향**: cycle 2026-04-30 try_one_account.yml backoff 1초 — 너무 짧을 수 있음. NEXT_ACTIONS 등재됨

## R3 발견 — OS 채널 (Linux + Windows)

### F21 — paramiko 2.9.0+ + RHEL 9 ssh-rsa 거부
- **증상**: "no matching host key type found. Their offer: ssh-rsa"
- **원인**: paramiko 2.9.0+ default = rsa-sha2-512/256 우선. RHEL 9 SSH server (구 펌웨어) 가 ssh-rsa 만 응답 시 fail
- **fix 옵션**:
  - Ansible: `use_rsa_sha2_algorithms=false` (paramiko_ssh 옵션)
  - SSH config: `KexAlgorithms=+diffie-hellman-group14-sha1` + `RequiredRSASize`
  - server side: 구 Linux SSH server upgrade
- **우리 코드 영향**: ansible.cfg `[ssh_connection] ssh_args` 에 legacy 옵션 추가 검토 (P2 — 사고 재현 후)
- Source: [Red Hat solution 7056072](https://access.redhat.com/solutions/7056072), [Ansible #76737](https://github.com/ansible/ansible/issues/76737)

### F22 — WinRM NTLM 신 encryption 미지원
- **증상**: NTLM 은 구 encryption 만. TLS 1.3 만 활성화된 환경에서 fail 가능
- **fix**:
  - Kerberos auth (도메인 환경)
  - Basic / NTLM over HTTPS (TLS 1.2 호환 펌웨어)
  - Python 3.8+ + urllib3 2.0.7+ (TLS 1.3 cert 인증)
- **우리 코드**: ansible.cfg `[winrm] transport = ntlm` — Windows Server 2012/2016 호환 OK. Windows 11 TLS 1.3-only 환경 시 follow-up 필요 (P3)

### F23 — getent / lspci / dmidecode 부재 환경
- **증상**: minimal Alpine container, 일부 임베디드 Linux 에서 명령 부재
- **우리 코드**: graceful fail (failed_when:false) — 빈 결과 반환. 'not_supported' 분류 안 됨 → cycle 2026-05-01 인프라로 점진 전환 가능 (P1)

## R3 발견 — ESXi 채널

### F24 — pyvmomi thumbprint deprecated
- **증상**: pyvmomi `connect()` thumbprint 인자 deprecated → `serverPemCert` 사용 권장
- **우리 코드**: 현재 verify=False 가정. 향후 보안 강화 시 인증서 검증 도입 검토 (P3)
- Source: [pyvmomi GitHub connect.py](https://github.com/vmware/pyvmomi/blob/master/pyVim/connect.py)

### F25 — vSphere 7 → 8 upgrade path 제한
- **증상**: 7.0 U3w → 8.0 U3g 권장. 다른 path는 미지원
- **우리 영향**: 운영 측 cycle. 우리 코드는 양립.

## R3 종합 fix 후보 (R1+R2+R3)

| # | 영역 | 발견 | 우선 | 출처 |
|---|---|---|---|---|
| F1 | system | SystemType=DPU 신규 enum | P3 | R1 DMTF |
| F2 | cpu | ProcessorType 'Accelerator'/'Core' 신규 | P2 | R1 DMTF |
| F3 | network | IPv6 미수집 | P3 | R1 DMTF |
| F4 | network_adapters | HPE iLO 5 BaseNetworkAdapters fallback 미구현 | P2 | R1+R2 |
| F5 | power | EnvironmentMetrics 미수집 (PowerControl null) | P1 | R1 |
| F6 | thermal | 섹션 자체 미수집 | P2 | R1 |
| F7 | hba_ib | lspci 부재 환경 graceful 검증 | P3 | R1 |
| F8 | users | Cisco CIMC AccountService 제한 | P2 | R1+R2 |
| F9 | system | HPE Gen10/Gen10+/Gen11 BIOS Oem 위치 변경 | P3 | R2 |
| F10 | memory | HPE Gen11 HBM memory 모듈 enum | P2 | R2 |
| F11 | network_adapters | F4와 동일 (병합) | — | — |
| F12 | power | Cisco CIMC PowerSubsystem 지원 검증 | P2 | R2 |
| F13 | users | Cisco CIMC AccountService 'not_supported' 분류 적용 | P1 | R2 |
| F14 | system | Dell iDRAC 10 호환성 사전 검증 | P3 | R2 |
| F15 | system | Supermicro X9 adapter 정확성 | P3 | R2 |
| F16 | bmc | CVE-2024-54085 패치/미패치 응답 차이 추적 | P3 | R3 |
| F17 | (전체) | Schema 버전 mismatch — errata schema 검증 | P2 | R3 |
| F18 | (전체) | 우리 5 vendor 외 비표준 응답 (직접 영향 미미) | P3 | R3 |
| F19 | (전체) | TaskService 등 보조 service 미수집 (현재 영향 없음) | P3 | R3 |
| F20 | users | BMC vendor lockout policy 차이 — backoff 1초 너무 짧음 | P2 | R3 |
| F21 | OS Linux | paramiko 2.9.0+ + RHEL 9 ssh-rsa 거부 | P2 | R3 |
| F22 | OS Windows | WinRM NTLM TLS 1.3 호환성 | P3 | R3 |
| F23 | OS | getent/lspci 부재 환경 'not_supported' 분류 점진 전환 | P1 | R3 |
| F24 | ESXi | pyvmomi thumbprint deprecated | P3 | R3 |
| F25 | ESXi | vSphere 7→8 upgrade path 제한 (운영 측) | — | R3 |

## P0 작업 — 즉시 fix 후보 없음

cycle 2026-05-01 에서 P0 (사용자 직접 사고) 모두 처리됨.

## P1 작업 — 다음 cycle 권장

| 작업 | 영역 | 이유 |
|---|---|---|
| F5 EnvironmentMetrics fallback | power | PowerSubsystem fallback 시 PowerControl null — system-level metric 손실 |
| F13 Cisco CIMC AccountService 'not_supported' | users | cycle 2026-05-01 인프라 활용. 현재 envelope에서 partial로 잘못 분류 가능 |
| F23 OS gather 'not_supported' 점진 전환 | os | hba_ib / users / Windows 미지원 케이스 분류 |

## P2 작업 — 후속 cycle (사고 재현 또는 lab 검증 후)

| 작업 | 영역 | 검증 |
|---|---|---|
| F2 ProcessorType 'Accelerator' 통과 | cpu | lab CPU+GPU mixed system fixture |
| F4 HPE iLO 5 BaseNetworkAdapters fallback | network_adapters | 구 펌웨어 실 BMC 검증 |
| F6 thermal 섹션 신규 도입 | thermal | schema/sections.yml 변경 — 사용자 결정 |
| F8 Cisco CIMC AccountService 제한 처리 | users | F13과 묶음 |
| F10 HBM memory enum 처리 | memory | HPE Gen11 + GPU 시스템 검증 |
| F12 Cisco PowerSubsystem 검증 | power | Cisco CIMC 4.x lab 검증 |
| F17 Schema 버전 errata 사용 | (전체) | 우리 코드는 _safe() 안전 — 우선순위 낮음 |
| F20 backoff 1초 → 5초 | users | BMC lockout 회피 |
| F21 SSH legacy ssh-rsa 호환 | os Linux | RHEL 9 agent + 구 Linux server 사고 재현 후 |

## P3 작업 — 선제 변경 자제 (rule 92 R2)

F1 / F3 / F9 / F14 / F15 / F16 / F18 / F19 / F22 / F24 — 현재 사고 재현 없음. NEXT_ACTIONS 등재만.

## R3 추가 검색 항목 (없음 — cycle 종료 조건)

- 5 vendor BMC 호환성 — R2에서 충분
- DMTF schema 변천 — R1에서 충분
- 사고/함정 — R3에서 충분
- OS/ESXi — R3에서 충분
- **추가 검색 항목 0건 — 사용자 명시 종료 조건 도달 (3 round 모두 완료)**

## Sources (R3)

- [Greenbone CVE-2024-54085 분석](https://www.greenbone.net/en/blog/ami-bmc-flaw-remote-takeover-and-dos-of-server-infrastructure/)
- [DMTF Redfish-Service-Validator issue #68](https://github.com/DMTF/Redfish-Service-Validator/issues/68)
- [Gigabyte BMC Missing Redfish Data (Cray)](https://cray-hpe.github.io/docs-csm/en-15/troubleshooting/known_issues/gigabyte_bmc_missing_redfish_data/)
- [Cisco CIMC support GitHub](https://github.com/bb-Ricardo/check_redfish/issues/12)
- [Red Hat ssh-rsa solution 7056072](https://access.redhat.com/solutions/7056072)
- [Ansible paramiko #76737](https://github.com/ansible/ansible/issues/76737)
- [Ansible WinRM docs](https://docs.ansible.com/projects/ansible/latest/os_guide/windows_winrm.html)
- [pyvmomi connect.py](https://github.com/vmware/pyvmomi/blob/master/pyVim/connect.py)
- [VMware ESXi 8 build numbers](https://knowledge.broadcom.com/external/article/316595/build-numbers-and-versions-of-vmware-esx.html)

## 갱신 history

- 2026-05-01: R3 사고/함정 검색 + OS/ESXi 추가 (10건 신규 fix 후보 F16~F25). 종료 조건 도달.
