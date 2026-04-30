# Coverage — InfiniBand 호환성 (4 채널)

> 사용자 명시 (2026-05-01): "InfiniBand 도 redfish/os/esxi 에서 개더링 돼야 한다 (기술적으로 안 되면 skip). lab 장비에 InfiniBand 없음 → web 검색 필수."
>
> **호환성 영역 only — 새 데이터 수집 아님**. 같은 정보 (IB 카드 / port / link state) 를 어느 채널에서든 수집 가능하게 fallback.

## R6 Web 검색 결과

### 1. Redfish — InfiniBand

- **NetworkAdapter PortType enum**: `InfiniBand` 표준 정의됨
- **NetworkDeviceFunction NetType**: `InfiniBand` 표준
- **vendor**: NVIDIA (Mellanox), HPE, Lenovo 등 — ConnectX-4+ VPI 카드는 IB/Ethernet 둘 다 지원, default IB

#### 우리 코드 현재 동작
- `redfish-gather/tasks/normalize_standard.yml:299-339` `_rf_summary_network`
- PortType (`fibre`/`infin`/`ether`) 기반 분류
- `data.storage.infiniband[]` 에 IB-only port 분리 emit ✓

→ **이미 호환** (cycle 2026-04-29 lenovo-critical-review). PortType=InfiniBand 자동 통과.

### 2. OS Linux — InfiniBand

#### 표준 도구
- `ibstat` — port state / GUID / firmware (rdma-core 패키지)
- `ibv_devices` / `ibv_devinfo` — devices 목록 (libibverbs)
- `/sys/class/infiniband/<device>/ports/<port>/state` — sysfs
- `lspci -nn | grep -i infiniband` — PCI 식별
- `mlxconfig -d /dev/mst/...` — Mellanox 설정 (mft 패키지)
- `mst status` — Mellanox status

#### 우리 코드 현재 동작
`os-gather/tasks/linux/gather_hba_ib.yml`:
- lspci 기반 IB 카드 식별
- `data.storage.infiniband[]` 에 분리 emit
- raw fallback 분기 있음

→ 부분 호환. 다만:
- **`ibstat` / `ibv_devinfo` 미사용** — 더 자세한 정보 (link layer / GUID / firmware)는 누락 가능
- **`/sys/class/infiniband/` sysfs 직접 read 미사용**

### 3. OS Windows — InfiniBand

#### 표준 도구 (PowerShell)
- `Get-NetAdapter` (`-IncludeHidden` 옵션) — 모든 NIC (IB IPoIB 포함)
- `Get-NetOffloadGlobalSetting` — NetworkDirect (RDMA) 활성 여부
- `Get-SmbServerNetworkInterface` — IB RDMA / IPoIB capability
- `Get-PnpDevice -Class Net` Vendor ID `VEN_15B3` (Mellanox)
- Mellanox WinOF 드라이버 — IPoIB / IBAL / ND / NDKPI 포함

#### 우리 코드 현재 동작
`os-gather/tasks/windows/gather_network.yml`:
- `Win32_NetworkAdapter` 사용 — IPoIB 인터페이스 normal NIC 처럼 emit
- IB 별도 분류 없음

`os-gather/tasks/linux/gather_hba_ib.yml` 만 IB 분리 — **Windows 채널은 IB 분리 미지원**.

→ 호환성 부족. Windows IB 환경에서 IB 카드가 Ethernet NIC 처럼 emit (data.network.interfaces 에 통합) — IB 분류 없음.

### 4. VMware ESXi — InfiniBand

#### ESXi IB 인식
- ESXi 가 **IB 를 Ethernet adapter 로 노출** (VPI mode default Ethernet)
- 진짜 IB 모드 (RDMA over IB) 는 별도 driver 설치 필요 (Mellanox OFED)
- esxcli `system module parameters set -m nmlx5_core ...` — IB/Eth 모드 설정
- vSphere 8 InfiniBand config white paper 있음 (VMware 공식)

#### 우리 코드 현재 동작
`esxi-gather/tasks/normalize_network.yml`:
- vmnic / vSwitch / portgroup 정규화
- IB 가 Ethernet adapter 로 노출되면 normal NIC 처럼 emit
- 별도 IB 분류 없음

→ **ESXi 채널은 IB 분리 사실상 미지원** (vendor 의도 — ESXi가 IB를 Ethernet으로 인식). 기술적 제약. **skip 가능 영역** (사용자 명시 "기술적으로 안 되면 skip").

## InfiniBand 호환성 fix 후보

### F37 — Linux IB 도구 부재 graceful (검증만)
- **현재**: `gather_hba_ib.yml` 가 lspci 부재 시 graceful (failed_when:false)
- **변경 (Additive)**: cycle 2026-05-01 인프라 활용 — lspci 부재 시 `_sections_unsupported_fragment: ['hba_ib']` 분류 (F07 묶음)
- **호환성**: 도구 부재 환경 (Alpine container) graceful
- **우선**: P3 (F07/F23 묶음)

### F38 — Windows IB NIC 분류 fallback (Additive)
- **현재**: Windows gather가 IB 카드를 Ethernet NIC 와 분리 안 함
- **변경 (Additive)**: `Get-PnpDevice -Class Net` 으로 vendor ID `VEN_15B3` (Mellanox) 또는 driver 명 (ibal / mlx5) 검출 → `data.storage.infiniband[]` 분리 emit
  ```powershell
  Get-PnpDevice -Class Net | Where-Object {
      $_.HardwareID -match 'VEN_15B3' -or $_.Service -match '^(mlx|ibal)'
  }
  ```
- **호환성**: Windows IB 환경 (드물지만 HPC) 에서 IB 카드 식별. IB 없으면 빈 list (graceful)
- **lab 한계**: Windows IB lab 없음 → web 검색 의존 (Mellanox WinOF / Microsoft Get-NetAdapter docs)
- **우선**: P3 (실 운영 시 호환성)

### F39 — ESXi IB skip (의도된 미지원)
- **현재**: ESXi 가 IB 를 Ethernet 으로 노출 — 우리 esxi-gather 가 이미 EthernetInterface 처리
- **변경**: 없음 — **기술적 제약으로 skip** (사용자 명시 허용)
- **명시**: docs / ticket 에 "ESXi IB 분리 미지원 (vendor 의도 — ESXi가 IB를 Ethernet adapter로 인식)" 추적
- **우선**: P4 (기술 제약)

### F40 — Redfish NetworkAdapter ConnectX VPI mode 호환 (검증만)
- **현재**: PortType raw read — Ethernet / FibreChannel / InfiniBand 자동 분류
- **호환**: ConnectX VPI 카드의 IB ↔ Ethernet 모드 전환 시 PortType 응답 변동 → 우리 코드 자동 처리
- **변경 없음**: 검증만
- **우선**: P3

## 채널별 호환성 매트릭스

| 채널 | IB 식별 | data 위치 | 상태 |
|---|---|---|---|
| Redfish | PortType=InfiniBand 자동 | `data.storage.infiniband[]` | ✓ 호환 |
| OS Linux | lspci 기반 (raw fallback) | `data.storage.infiniband[]` | ✓ 부분 호환 (ibstat 미사용) |
| OS Windows | 미수집 | (Ethernet 통합 emit) | ✗ Fix 후보 F38 |
| ESXi | 미수집 (vendor 의도 — Ethernet) | (Ethernet 통합 emit) | △ 기술 제약 — skip |

## 우리 코드 위치 (현재)

- Redfish: `redfish_gather.py:1481` `gather_network_adapters_chassis` + `normalize_standard.yml:299-339`
- Linux: `os-gather/tasks/linux/gather_hba_ib.yml`
- Windows: 미수집 (`os-gather/tasks/windows/gather_network.yml` Ethernet 통합)
- ESXi: 미수집 (`esxi-gather/tasks/normalize_network.yml` Ethernet 통합)

## Sources

- [NVIDIA InfiniBand interface (Mellanox)](https://docs.nvidia.com/networking/display/mlnxosv3103002/infiniband+interface)
- [NVIDIA InfiniBand OS Distributors](https://network.nvidia.com/products/adapter-ibvpi-sw/infiniband-osv-support/)
- [InfiniBand Wikipedia](https://en.wikipedia.org/wiki/InfiniBand)
- [Linux InfiniBand ArchWiki](https://wiki.archlinux.org/title/InfiniBand)
- [Red Hat IB testing](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/networking_guide/sec-testing_early_infiniband_rdma_operation)
- [Mellanox Cheatsheet (Merox)](https://docs.merox.dev/operations/cheatsheet/Infiniband/mellanox_infiniband/)
- [Mellanox WinOF Installation Guide](https://content.mellanox.com/WinOF/Mellanox_WinOF_Installation_Guide_1_10.pdf)
- [Microsoft Get-NetAdapter docs](https://learn.microsoft.com/en-us/powershell/module/netadapter/get-netadapter)
- [VMware InfiniBand vSphere 8 white paper](https://www.vmware.com/docs/infiniband-config-vsphere8-perf)
- [vmexplorer ESXi 6.5 Mellanox HCAs](https://vmexplorer.com/2018/06/08/home-lab-gen-iv-part-v-installing-mellanox-hcas-with-esxi-6-5/)
- [ESXi 7.0 Mellanox ConnectX-2 patch](https://vdan.cz/vmware/esxi-7-0-and-mellanox-connectx-2-support-fix/)

## 갱신 history

- 2026-05-01: R6 InfiniBand 4 채널 검색 + F37/F38/F39/F40 호환성 fix 후보
