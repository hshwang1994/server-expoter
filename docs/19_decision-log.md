# 의사결정 로그

> 최종 갱신: 2026-04-15

## 1. 코드 점검 1차/2차 결과 요약

### 1차 점검 (이전 세션)
- 전체 프로젝트 구조 분석
- 보안 이슈 (no_log 누락) 식별
- 기본 코드 품질 이슈 도출

### 2차 점검 (4 배치 완료)
- **Batch 1 (P0)**: power section 추가, hostname fallback 개선, int coercion regex 수정, vault 경고
- **Batch 2 (P1)**: OUTPUT default 방어, 에러 메시지 개선, no_log 정리
- **Batch 3 (P2)**: bare except → specific exceptions, no_log 제거, hostname None-safety
- **Batch 4 (P3)**: CALLBACK_NEEDS_WHITELIST → CALLBACK_NEEDS_ENABLED

총 19개 파일, ~50개 변경사항 — 모두 검증 완료.

## 2. Redfish Endpoint 선택 근거

### 코드가 호출하는 14개 엔드포인트

| # | 엔드포인트 | 선택 근거 |
|---|-----------|----------|
| 1 | Service Root | DMTF 필수. 벤더 감지 + 컬렉션 URI 확보 |
| 2 | Systems 컬렉션 | system_uri 동적 취득 |
| 3 | Systems/{id} | 서버 기본 정보 (model, serial, CPU/메모리 요약) |
| 4 | Managers/{id} | BMC 정보 (firmware version) |
| 5 | Processors 컬렉션 | CPU 상세 (모델, 코어, 스레드) |
| 6 | Processors/{pid} | 개별 CPU 정보 |
| 7 | Memory 컬렉션 | DIMM 목록 |
| 8 | Memory/{mid} | 개별 DIMM 정보 |
| 9 | Storage 컬렉션 | 스토리지 컨트롤러/드라이브 |
| 10 | Storage/{sid} | 컨트롤러 상세 + 드라이브 링크 |
| 11 | SimpleStorage (fallback) | Storage 미지원 구형 BMC 호환 |
| 12 | EthernetInterfaces 컬렉션 + 개별 | 호스트 NIC 정보 |
| 13 | FirmwareInventory 컬렉션 + 개별 | 전체 펌웨어 목록 |
| 14 | Chassis/{id}/Power | PSU 정보 |

### 미포함 엔드포인트와 제외 근거

| 엔드포인트 | 제외 근거 |
|-----------|----------|
| Chassis/{id}/Thermal | 온도/팬 정보 — 판정 시점에 normalize 스키마 미정의. 향후 추가 고려 |
| Managers/{id}/EthernetInterfaces | BMC NIC — system 레벨로 충분 |
| Bios | BIOS 설정 — BiosVersion은 System에서 이미 취득 |
| LogServices | 이벤트 로그 — 수집 범위 초과 |
| NetworkInterfaces | NIC 상세 — EthernetInterfaces로 충분 |

## 3. Adapter 설계 근거

### 왜 adapter 시스템을 사용하는가
1. **벤더별 normalize 차이**: 같은 Redfish 표준이라도 필드 존재 여부가 다름
2. **세대별 차이**: 같은 벤더라도 BMC 세대에 따라 스키마 다름 (예: HPE iLO5 vs iLO6)
3. **확장성**: 새 벤더/세대 추가 시 adapter YAML만 추가하면 됨
4. **테스트 용이**: adapter 단위로 fixture 테스트 가능

### Adapter 선택 알고리즘
- `adapter_loader.py`가 `adapters/redfish/` 디렉토리 스캔
- `match` 조건 (vendor, model_pattern 등) 비교
- 복수 매칭 시 `priority` + `specificity` 점수로 정렬
- 최고 점수 adapter 반환

## 4. Normalize 정책 근거

### null 허용 정책
실장비 검증 결과, 벤더마다 누락 필드가 다름:
- HPE: IndicatorLED, SpeedMbps, LinkStatus, ProcessorSummary.Status.Health
- Lenovo: Manager.Status.Health
- Dell: Drive.Status.Health

→ **정책**: 코드가 추출하는 모든 필드는 `_safe()` 함수로 None 반환 허용.
normalize에서 `| default(none)` 처리.

### 빈 문자열 처리
- HPE HostName = "" (빈 문자열) → normalize에서 `or _out_ip` fallback 필요
- build_output.yml에서 처리 (2차 점검에서 수정 완료)

### Storage Controllers fallback
- 판정 시점: `StorageControllers` 인라인 배열만 처리
- HPE Gen11: `Controllers` 서브링크 사용 → **fallback 추가 필요** (P0-1에서 구현 완료, 8절 참조)

## 5. 실장비 검증으로 확정된 사항

| 항목 | 결정 | 근거 |
|------|------|------|
| vendor 감지 기준 | System.Manufacturer | 3사 모두 동작 확인 |
| URI 패턴 | 동적 (Members[0]) | 벤더마다 다른 ID 패턴 |
| Storage fallback | Storage 우선, SimpleStorage fallback | Lenovo/HPE는 SimpleStorage 404 |
| Basic Auth | 유지 | 3사 모두 동작 |
| Thermal 수집 | 보류 | endpoint 존재하나 normalize 스키마 미정의 |
| default_gateways | Redfish 불가 | OS 레벨 정보 — os-gather에서 수집 |

## 6. 실장비 검증으로 추정에 머무는 사항

| 항목 | 추정 내용 | 불확실 요인 |
|------|----------|------------|
| 다른 세대 URI 패턴 | 동일할 것으로 추정 | Gen10, R640 등 미검증 |
| Supermicro 호환 | 코드에 Supermicro 분기 있으나 미검증 | 장비 부재 |
| Session Auth | 동작할 것으로 추정 | Basic만 테스트 |
| HPE iLO5 차이 | iLO6과 유사할 것으로 추정 | Oem.Hpe vs Oem.Hp fallback 미검증 |
| 다중 System member | Members[0]만 사용 | 블레이드 서버 등 미검증 |

## 7. OEM 필드 보강 판정 (B2, Round 14)

> 판정일: 2026-03-25

### 결론

**판정 시점의 수집 범위에서는 Standard Redfish로 대응 가능하다.** OEM placeholder는 향후 운영 요구 발생 시 확장한다.

수집 범위(firmware inventory + PSU health/state/metrics) 기준으로, 아래 근거 표의 모든 영역에서 standard endpoint만으로 필요 데이터를 확보할 수 있었다. OEM 추가 가치가 낮다고 판단한 근거는 아래 표 참조.

### 근거

| 영역 | Standard 수집 현황 | OEM 추가 가치 |
|------|-------------------|---------------|
| Firmware | FirmwareInventory 28+ 항목 (BIOS, BMC, RAID, NIC, PSU FW) | OEM-specific metadata (낮음) |
| Power | PSU health/state/metrics + power_control consumed watts | PSU redundancy N+1, line voltage (낮음) |
| 기타 | — | Thermal throttle history, license/warranty (범위 외) |

### OEM Framework 상태

- 4개 벤더(Dell/HPE/Lenovo/Supermicro) adapter YAML에 `oem_tasks` 경로 정의 완료
- `collect_oem.yml` / `normalize_oem.yml` placeholder 파일 존재
- **운영 요구 발생 시 placeholder만 채우면 즉시 확장 가능**

### 향후 확장 트리거

OEM 구현을 재검토해야 하는 상황:
1. 포털에서 PSU redundancy status(N+1) 표시 요구 발생
2. 벤더별 OEM-specific health code 해석 요구
3. Thermal 섹션 스키마 정의 및 수집 요구
4. 특정 벤더에서 standard endpoint로 수집 불가능한 필드 발견

## 8. 리팩토링 이력 (실장비 검증 기반, 2026-03-18)

### 완료 (P0/P1)

| 항목 | 파일 | 내용 |
|------|------|------|
| P0-1 | `redfish_gather.py` | HPE Storage Controllers fallback (Controllers 서브링크 드릴다운) |
| P0-2 | `redfish_gather.py` | gather_power() ServiceRoot 중복 호출 제거 (chassis_uri 직접 전달) |
| P0-3 | `hpe_ilo6.yml` | HPE iLO 6 전용 adapter 신규 생성 |
| P1-3 | `redfish_gather.py` | 벤더별 null 필드 경고 로깅 |
| P1-4 | `redfish_gather.py` | HostName 빈 문자열 → None 변환 |
| P1-7 | `redfish_gather.py` | MemorySummary Health → HealthRollup fallback |
| P1-7-2 | `redfish_gather.py` | IndicatorLED → LocationIndicatorActive fallback |

### 보류 (P1-P2)

| 항목 | 사유 |
|------|------|
| 단위 변환 헬퍼 통일 | 검증 시점에 코드 동작 확인됨, 우선순위 낮음 |
| Thermal 수집 추가 | normalize 스키마 미정의, 향후 요구 시 구현 |
| Supermicro/다중 System member/Session Auth/iLO5 차이 | 실장비 미보유로 검증 불가, 장비 확보 시 재검토 |

## 9. Linux Raw Fallback Round 2 검증 (2026-04-15)

### 배경

Round 1에서 Linux 2-Tier Gather (Python 감지 + Raw Fallback) 기본 구현을 완료했다. Round 2에서는 5대 서버에 대해 31개 필드 전수 비교 검증을 수행했다.

### SELinux 정규화 버그 수정

`gather_system.yml`의 raw 경로에서 `getenforce` 출력값(`Enforcing`/`Permissive`/`Disabled`)을 Ansible 컨벤션(`enabled`/`disabled`)으로 정규화하지 않는 버그를 발견하고 수정했다.

- **수정 전**: `getenforce` 출력 그대로 반환 (예: `Enforcing`)
- **수정 후**: `Enforcing`/`Permissive` → `enabled`, `Disabled` → `disabled`로 정규화

### 5대 서버 필드 전수 비교 결과

| 서버 | OS | Python | 감지 모드 | 결과 | 비고 |
|------|-----|--------|----------|------|------|
| RHEL 8.10 | RHEL 8.10 | 3.6.8 | `python_incompatible` (자동) | 31/31 MATCH | auto fallback과 forced raw 간 완전 일치 |
| RHEL 9.2 | RHEL 9.2 | 3.9+ | `python_ok` | memory 차이만 | raw 경로가 더 정밀 (아래 분석 참조) |
| RHEL 9.6 | RHEL 9.6 | 3.9+ | `python_ok` | memory 차이만 | 동일 |
| Rocky 9.6 | Rocky 9.6 | 3.9+ | `python_ok` | memory 차이만 | 동일 |
| Ubuntu 24.04 | Ubuntu 24.04 | 3.9+ | `python_ok` | selinux 1건 차이 | 허용 범위 (아래 분석 참조) |

### Memory 차이 분석 (버그 아님)

RHEL 9.x / Rocky 9.6에서 Python 경로와 raw 경로 간 memory 값 차이가 발생한다. 이는 **버그가 아니라 raw 경로가 더 정확**한 결과이다.

| 경로 | 수집 방식 | 값 (예시) | 의미 |
|------|----------|----------|------|
| Python 경로 | `ansible_memtotal_mb` (OS 보고) | 7680 MB | 커널 예약 후 OS 가시 메모리 (`os_visible`) |
| Raw 경로 | `dmidecode --type 17` (하드웨어 직접) | 8192 MB | 물리 장착 메모리 (`physical_installed`) |

→ raw 경로의 dmidecode 기반 수집이 실제 물리 메모리를 반환하므로 하드웨어 인벤토리 용도에 더 적합하다.

### Ubuntu SELinux 차이 (허용)

Ubuntu 24.04에서 `selinux` 필드 차이 1건 발생:
- Python 경로: `disabled` (Ansible이 SELinux 미설치를 disabled로 보고)
- Raw 경로: `null` (`getenforce` 명령 미설치)

→ Ubuntu는 SELinux를 기본 탑재하지 않으므로 `null` 반환이 의미적으로 정확하다. 허용 범위로 판정.

### 결론

5대 서버, 31개 필드 전수 검증 완료. Raw fallback은 Python 경로와 동등하거나 더 정밀한 결과를 제공한다. 프로덕션 적용 가능.

## 10. Network 심층 검증 (Round 3, 2026-04-15)

### 배경

Round 2 이후 Network 섹션에 대해 심층 검증을 수행했다. 가상 인터페이스 skip 패턴 확장, 다중 default route 동작 확인, primary 판단 규칙 명확화가 주요 내용이다.

### skip 패턴 확장

기존 skip 패턴(`lo`, `docker*`, `br-*`, `veth*`, `virbr*`, `vir*`)에 아래 패턴을 추가했다:

| 추가 패턴 | 대상 | 추가 근거 |
|----------|------|----------|
| `cni*` | Kubernetes CNI 인터페이스 | K8s 노드에서 불필요한 가상 인터페이스 수집 방지 |
| `flannel*` | Flannel CNI overlay | 동일 |
| `cali*` | Calico CNI | 동일 |
| `tunl*` | tunnel 인터페이스 | IPIP 터널 등 가상 인터페이스 제외 |
| `dummy*` | dummy 인터페이스 | 테스트/라우팅 용도 가상 인터페이스 제외 |
| `kube-*` | Kubernetes internal | kube-proxy 등 내부 인터페이스 제외 |

**주의**: `br0`, `bond0`, `team0`, `eth0.100`(VLAN) 등 실 네트워크 인터페이스는 skip 대상이 아니다.

### 5대 서버 다중 default route 동작 확인

5대 서버(RHEL 8.10, RHEL 9.2, RHEL 9.6, Rocky 9.6, Ubuntu 24.04)에서 다중 default route가 존재하는 경우 metric 기준 정렬 후 첫 번째만 사용하는 동작을 확인했다. Python 경로(`ansible_default_ipv4`)와 raw 경로(`ip route show default | head -1`) 모두 동일한 결과를 반환한다.

### primary 판단 규칙 명확화

| 결정 | 내용 |
|------|------|
| primary 정의 | IPv4 default route가 걸린 인터페이스 = primary |
| bond master | default route가 bond master에 걸리면 bond master가 primary |
| bridge | default route가 bridge에 걸리면 bridge가 primary |
| slave/port | IP가 없으므로 primary 불가 |
| 다중 default route | lowest metric wins (첫 번째만 사용) |

### 결론

Network 수집 정책을 GUIDE_FOR_AI.md에 문서화 완료. skip 패턴 확장으로 Kubernetes/tunnel/dummy 가상 인터페이스를 추가 제외하고, primary 판단 규칙과 다중 default route 처리를 명확화했다.
