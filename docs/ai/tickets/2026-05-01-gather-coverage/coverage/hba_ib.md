# Coverage — hba_ib 영역 (HBA + InfiniBand)

## 채널

- **OS Linux only** — `os-gather/tasks/linux/gather_hba_ib.yml`
- Redfish: NetworkAdapter PortType=FibreChannel/InfiniBand 으로 수집 (network_adapters 영역에서 분류)
- OS Windows / ESXi 미수집

## 도구 (R1)

### Linux
- `lspci -nn | egrep -i "fibre|hba"` (FC HBA 식별)
- `lsmod | grep ib_` (InfiniBand kernel module)
- `mlxconfig -d /dev/mst/...` (Mellanox 설정)
- `mstconfig query` (Mellanox)
- `cat /sys/class/fc_host/host*/port_name` (WWPN — FC)
- `cat /sys/class/infiniband/mlx*/node_guid` (GUID — IB)
- `ibstat` (IB 상태)

### Windows / ESXi
- 미수집 — host OS native API 다름

## 분류 (R1)

### FC HBA
- `WWPN` (port name), `WWNN` (node name)
- 일반적으로 16자 hex (8 octet)
- vendor: Emulex / QLogic (Marvell) / Brocade

### InfiniBand
- `GUID` (Global Unique IDentifier)
- vendor: NVIDIA Mellanox / Cornelis (Omni-Path)
- IPoIB (IP over IB) 가능

## Vendor 호환성 (R2)

| OS / 환경 | lspci | dmidecode | mlxconfig | sysfs |
|---|---|---|---|---|
| RHEL 8/9 | OK | OK | OK (Mellanox 설치 시) | OK |
| Ubuntu 22.04/24.04 | OK | OK | OK (별도 설치) | OK |
| Rocky 9 | OK | OK | OK | OK |
| RHEL 7 (구) | OK | OK | 부분 | OK |
| SLES | OK | OK | OK | OK |
| Alpine container | **lspci 부재 가능** | 부재 가능 | 미설치 | OK |
| busybox / minimal embedded | 매우 제한 | 미설치 | — | 부분 |

## 알려진 사고 (R3)

### HB1 — F7: lspci 부재 환경
- **증상**: minimal Alpine / busybox / 일부 임베디드 Linux 에서 lspci 명령 부재
- **현재 코드 영향**: graceful (failed_when:false). 빈 결과 반환 → sections.storage.hbas=[]
- **우선**: P3 — 'not_supported' 분류로 명시 가능 (F23 OS 점진 전환의 일부)

### HB2 — Mellanox mlxconfig 미설치
- **증상**: mlxconfig 패키지 미설치 (RHEL minimal install)
- **현재 코드 영향**: graceful — sysfs로 fallback

### HB3 — RHEL 9 InfiniBand persistent naming
- **증상**: RHEL 9 가 InfiniBand device 이름 변경 가능 (mlx4_ib0 → ib0)
- **fix**: udev rule (`/etc/udev/rules.d/70-persistent-ipoib.rules`)
- **현재 코드 영향**: 우리는 device 이름 가져옴 — 정규화 안 함. 호출자가 처리

### HB4 — Redfish vs Linux gather 매칭
- **증상**: Redfish가 PortType=FibreChannel 응답 + Linux에서 같은 host의 lspci로 HBA 응답 — 둘이 같은 device일 수 있음
- **현재 코드**: 두 채널 별도 수집 — 호출자가 매칭

## fix 후보 (hba_ib 영역)

### F7 — lspci 부재 환경 'not_supported' 분류 (Additive)
- **현재 위치**: `os-gather/tasks/linux/gather_hba_ib.yml` (graceful 빈 list)
- **변경 (Additive)**: lspci 명령 실패 (rc!=0) 또는 부재 시 `_sections_unsupported_fragment: ['hba_ib']` set. 명령 정상 + 빈 결과 시 기존 동작 (success + 빈 list)
- **회귀**: lab Linux (lspci 정상) — 동작 유지 / Alpine container — unsupported 분류
- **우선**: P3 (F23의 일부 — OS 점진 전환)

## 우리 코드 위치

- task: `os-gather/tasks/linux/gather_hba_ib.yml`
- raw fallback: 같은 파일 안 — `_l_python_mode != 'python_ok'` 분기
- normalize: data.storage.hbas / data.storage.infiniband (storage 섹션 안 sub-key)

## Sources

- [How to check FC HBA in Linux (Open Tech Guides)](https://www.opentechguides.com/how-to/article/linux/18/fc-hba-linux.html)
- [Configuring InfiniBand RHEL 8](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/configuring_infiniband_and_rdma_networks/index)
- [Mellanox mlxconfig RHEL](https://access.redhat.com/articles/3082811)

## 갱신 history

- 2026-05-01: R1+R2+R3 / HB1~HB4 / F7 P3
