# cycle-015 — 실장비 lab 권한 확장 + 연결성 검증 (2026-04-29)

> cycle-015 (4 vendor BMC code path 검증)에 이어 사용자가 lab 전체 (28 호스트) 권한 부여 + Browser E2E 도입 결정.
> 본 evidence는 cycle-015 (lab access grant) 첫 연결성 검증.
> 환경: Windows 클라이언트 (직접) → lab zones (10.100.64.0/24, 10.100.15.0/24, 10.50.11.0/24)

## 1. ICMP 도달성 (21/21 PASS)

모든 21개 sampled 호스트 ping 응답.

| 그룹 | 카운트 | Ping |
|---|---|---|
| Jenkins master | 2 | [PASS] 2/2 |
| Jenkins agent | 2 | [PASS] 2/2 |
| Linux VM + baremetal | 6 | [PASS] 6/6 |
| Windows VM | 2 | [PASS] 2/2 |
| BMC (Dell × 6 sample 2 + HPE + Lenovo + Cisco × 1) | 5 | [PASS] 5/5 |
| ESXi | 3 | [PASS] 3/3 |

## 2. TCP Protocol 포트

| 호스트 | 포트 | Proto | 결과 |
|---|---|---|---|
| jenkins-master-152 | 8080 | HTTP | [OK] OPEN |
| jenkins-agent-154 | 22 | SSH | [OK] OPEN |
| rhel810 (Py 3.6) | 22 | SSH | [OK] OPEN |
| ubuntu2404 | 22 | SSH | [OK] OPEN |
| win10-120 | 5985 | WinRM-HTTP | [OK] OPEN |
| win10-120 | 5986 | WinRM-HTTPS | [FAIL] CLOSED |
| win2022-132 | 5985/5986/3389/135/445/22 | All | [FAIL] ALL CLOSED |
| dell-bmc-27 | 443 | HTTPS | [OK] OPEN |
| dell-bmc-32-gpu | 443 | HTTPS | [OK] OPEN |
| hpe-bmc | 443 | HTTPS | [OK] OPEN |
| lenovo-bmc | 443 | HTTPS | [OK] OPEN |
| cisco-bmc-1 | 443 | HTTPS | [OK] OPEN |
| esxi-1 | 443 | HTTPS | [OK] OPEN |

## 3. Redfish ServiceRoot 무인증 응답 (rule 27 R3 1단계 검증)

### Dell BMC 6대 전수

| BMC IP | Product | Vendor | RedfishVer | 검증 |
|---|---|---|---|---|
| 10.100.15.27 | Integrated Dell Remote Access Controller | Dell | 1.20.1 | [OK] iDRAC 9 (5+ generation) |
| 10.100.15.28 | Integrated Dell Remote Access Controller | Dell | 1.20.1 | [OK] iDRAC 9 |
| 10.100.15.31 | Integrated Dell Remote Access Controller | Dell | 1.20.1 | [OK] iDRAC 9 |
| **10.100.15.32** | **AMI Redfish Server** | **AMI** | **1.11.0** | **[FAIL] rule 96 DRIFT — Dell 아님** |
| 10.100.15.33 | Integrated Dell Remote Access Controller | Dell | 1.20.1 | [OK] iDRAC 9 (OS=10.100.64.96 매칭) |
| 10.100.15.34 | Integrated Dell Remote Access Controller | Dell | 1.20.1 | [OK] iDRAC 9 |

### Cisco BMC 3대

| BMC IP | Product | RedfishVer | 검증 |
|---|---|---|---|
| 10.100.15.1 | (503 Service Unavailable) | — | [HOLD] 일시 장애 또는 무인증 차단 |
| **10.100.15.2** | **TA-UNODE-G1** | 1.2.0 | **[WARN] 표준 Cisco UCS Product 아님 — 후속 식별** |
| 10.100.15.3 | (timeout 5s) | — | [HOLD] 일시 장애 또는 응답 지연 |

### HPE / Lenovo

| BMC IP | Product | RedfishVer | 검증 |
|---|---|---|---|
| 10.50.11.231 | ProLiant DL380 Gen11 | 1.20.0 | [OK] Gen11 = iLO6 |
| 10.50.11.232 | (empty Product) | 1.15.0 | [OK] Lenovo XCC (Product 빈 값은 일부 펌웨어 정상) |

## 4. WinRM 응답

- Win10 (10.100.64.120) http://5985/wsman → 401 Unauthorized = WinRM 정상 응답 [OK]
- Win Server 2022 (10.100.64.132) → 모든 포트 닫힘. **호스트 firewall / 서비스 down 추정** [FAIL]

## 5. 발견 (rule 96 외부 계약 drift)

### 5.1. DRIFT — Dell 32 (GPU 호스트)

- **사용자 라벨**: "dell, GPU 카드 설치"
- **Redfish 응답**: `Vendor='AMI', Product='AMI Redfish Server', RedfishVersion=1.11.0`
- **AMI MegaRAC = Supermicro / Asrock / whitebox 가능성**
- **현재 adapter 매칭 결과**: `redfish_generic.yml` 또는 `supermicro_bmc.yml` 후보 (Dell adapter 매칭 안 됨)
- **후속 조사**:
  - 호스트 물리 라벨 확인 (사용자 lab 직접)
  - `deep_probe_redfish.py`로 Manufacturer / Model 상세 추출
  - inventory/lab/redfish.json 의 `_vendor: dell` → 실제 vendor로 수정
  - `docs/ai/catalogs/EXTERNAL_CONTRACTS.md` entry 추가

### 5.2. DRIFT — Cisco BMC 2

- **사용자 라벨**: "cisco"
- **Redfish 응답**: `Product='TA-UNODE-G1', RedfishVersion=1.2.0`
- **표준 CIMC 응답 형식 아님** — Cisco UCS C-시리즈는 보통 `Product='UCS C220 M5'` 형식
- **TA-UNODE 검색 필요** — Cisco TelePresence / Tetration / 다른 제품 시리즈 가능
- **후속 조사**: 동일 절차

### 5.3. Win Server 2022 firewall

- 모든 포트 closed → 호스트 firewall 또는 WinRM 미설치
- **자율 처리 한계** — 사용자가 host 콘솔 진입 후 `Enable-PSRemoting -Force` 실행 필요
- 또는 vCenter / RDP로 접근 후 firewall rule 추가

## 6. 도구 가용성 (Windows 클라이언트)

| 도구 | 상태 | 용도 |
|---|---|---|
| Python 3.11.9 | [OK] | Redfish stdlib 호출 / probe_redfish.py |
| ssh.exe (OpenSSH) | [OK] | Linux SSH 접근 |
| ansible | [FAIL] | 미설치 — Jenkins agent (10.100.64.154)에서 실행 필요 |
| playwright | [FAIL] | Phase D에서 pip install 예정 |
| pywinrm | [FAIL] | WinRM 자동화는 ansible agent 또는 별도 install |
| sshpass / plink | [FAIL] | password SSH는 paramiko 또는 ssh.exe + key 권장 |

## 7. Phase C 결론

**자율 진행 가능 영역** (Windows 직접):
- BMC Redfish probe (Dell × 5 정상 + AMI 1대 별도 + HPE + Lenovo)
- ESXi HTTPS 확인 (3대)
- Linux SSH (Python paramiko 설치 후) — 6대
- Win10 WinRM (pywinrm 설치 후) — 1대
- Jenkins master Web UI (Playwright 설치 후) — Browser E2E

**자율 진행 한계** (사용자 조정 필요):
- Win Server 2022 firewall 해제
- Cisco BMC 1, 3 일시 장애 또는 무인증 차단 확인
- Dell 32 (실제 AMI) vendor 라벨 정정

**검증된 핵심 사실**:
- 21개 호스트 ICMP / TCP 도달성 [OK]
- Redfish 무인증 ServiceRoot 응답 형식 정상 (rule 27 R3 1단계 통과)
- 호스트 12/14 본 수집 진행 가능

## 8. 후속 작업 (NEXT_ACTIONS.md 등재 예정)

- [ ] Phase D — Playwright 설치 + Jenkins UI E2E
- [ ] DRIFT-005 신규 entry — Dell 32 / Cisco 2 vendor 라벨 vs 실 Manufacturer
- [ ] EXTERNAL_CONTRACTS.md — AMI Redfish 1.11.0 / TA-UNODE-G1 미지원 vendor entry
- [ ] FAILURE_PATTERNS.md — `user-label-vs-redfish-manufacturer-drift` 패턴 등재
- [ ] Win Server 2022 firewall 사용자 조치
- [ ] Cisco BMC 1, 3 가용성 재확인 (다음 일과시간)
