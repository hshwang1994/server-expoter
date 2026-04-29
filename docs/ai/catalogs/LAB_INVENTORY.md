# LAB_INVENTORY — 실장비 lab 토폴로지

> 정본: `inventory/lab/*.json` (gitignored — 실 IP) + `vault/.lab-credentials.yml` (gitignored — 자격증명).
> 본 catalog는 sanitized 메타. 작성: 2026-04-29 cycle-015.

## 1. 권한 정책

사용자 명시 결정 (2026-04-29 채팅):
> "이 프로젝트는 ai에게 모든 권한을 준다 ... 실장비 권한도 하네스에게 주겠다 어짜피 테스트서버이다"

→ AI는 본 lab 모든 호스트에 자율 접속 가능 (cycle-011 보안 정책 해제 확장).

관련 ADR:
- `ADR-2026-04-28-security-policy-removal.md` — 보안 정책 자체 해제
- `ADR-2026-04-29-lab-access-grant.md` — 실장비 접근 권한 확장 (cycle-015, 본 작업)

## 2. 호스트 카운트 (총 28대)

| 그룹 | 카운트 | 채널 | 검증 가치 |
|---|---|---|---|
| Jenkins master | 2 | (관리) | 파이프라인 트리거 / Web UI E2E |
| Jenkins agent (Ansible) | 2 | (관리) | 본 수집 실행 환경 (Python 3.12 / ansible-core 2.20) |
| Linux VM | 5 | os-gather | RHEL 8.10 / 9.2 / 9.6 / Rocky 9.6 / Ubuntu 24.04 |
| Linux baremetal | 1 | os-gather | OS↔BMC correlation 검증용 (Dell BMC와 매칭) |
| Windows VM | 2 | os-gather | Win10 + Win Server 2022 |
| Dell BMC (iDRAC) | 6 | redfish-gather | 1대는 GPU 설치, 1대는 baremetal OS 매칭 |
| HPE BMC (iLO) | 1 | redfish-gather | — |
| Lenovo BMC (XCC) | 1 | redfish-gather | — |
| Cisco BMC (CIMC) | 3 | redfish-gather | UCS 시리즈 검증 |
| ESXi host | 3 | esxi-gather | community.vmware 6.2.0 검증 |

## 3. 네트워크 zone

| Zone | CIDR | 용도 |
|---|---|---|
| Service / OS | 10.100.64.0/24 | Jenkins master/agent + OS gather VM + ESXi |
| Dell + Cisco BMC | 10.100.15.0/24 | iDRAC + CIMC |
| HPE + Lenovo BMC | 10.50.11.0/24 | iLO + XCC |

→ Jenkins agent (10.100.64.0/24)에서 모든 zone 도달 가능 (production routing).

## 4. 특이 호스트 (검증 우선순위)

| 호스트 그룹 | 특이사항 | 검증 가치 |
|---|---|---|
| Linux RHEL 8.10 | Python 3.6 환경 | rule 10 R4 (raw fallback) 실증 |
| Linux baremetal | Dell BMC와 같은 머신 | OS data ↔ BMC data correlation envelope 검증 |
| Dell BMC (GPU 설치) | NVIDIA GPU 카드 | Redfish PCIeDevices / Storage 섹션 GPU 필드 검증 |
| Win Server 2022 | administrator account | WinRM 5985 / domain-less |
| Cisco BMC × 3 | UCS 시리즈 | 동일 vendor 다수 — adapter score tie-break 검증 |

## 5. 검증 라운드 매핑

| Round | 영역 | 우선순위 | 비고 |
|---|---|---|---|
| Round 11 (예정) | Dell × 6 baseline 갱신 | HIGH | GPU 호스트 + correlation 호스트 우선 |
| Round 12 (예정) | HPE / Lenovo 단일 호스트 | MED | 1대씩이라 fallback 검증 한계 |
| Round 13 (예정) | Cisco × 3 baseline | MED | 신규 vendor (cycle-008 도입) |
| Round 14 (예정) | Linux raw fallback | HIGH | RHEL 8.10 (Py 3.6) 1대로 rule 10 R4 실증 |
| Round 15 (예정) | Win 2-tier | MED | Win10 + Server 2022 |
| Round 16 (예정) | ESXi 회귀 | LOW | 3대로 community.vmware 안정성 |
| Browser E2E (예정) | Jenkins UI / Grafana | LOW | Playwright |

## 6. 자격증명 정책

- **현재** (2026-04-29 ~ private 전환 전): `vault/.lab-credentials.yml` 평문 로컬 + gitignored
- **private 전환 후 옵션**:
  - (A) ansible-vault encrypt → 기존 `vault/redfish/{vendor}.yml` 등으로 흡수
  - (B) gitignored 평문 영구 유지 (lab 운영 단순)
- **결정 시기**: 사용자가 repo private 전환 시점에 (NEXT_ACTIONS 추적)

## 7. 참고 파일

- `inventory/lab/os-linux.json` — 6 호스트 (`service_ip`)
- `inventory/lab/os-windows.json` — 2 호스트 (`service_ip`)
- `inventory/lab/redfish.json` — 11 호스트 (`bmc_ip`)
- `inventory/lab/esxi.json` — 3 호스트 (`service_ip`)
- `inventory/lab/jenkins.json` — 4 호스트 (`service_ip`, 참고)
- `vault/.lab-credentials.yml` — 자격증명 그룹 5종

## 8. 갱신 trigger

다음 시 본 catalog 갱신:
- 새 호스트 추가/제거
- vendor 추가
- Round 검증 완료 후 row 5 (검증 라운드 매핑) 진행률 갱신
- repo visibility 전환 후 row 6 (자격증명 정책) 결정 기록
