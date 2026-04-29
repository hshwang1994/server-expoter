# pyvmomi — Python SDK for vSphere

> Source: https://github.com/vmware/pyvmomi
> Fetched: 2026-04-27
> Version (server-exporter 검증 기준): pyvmomi 9.0.0

server-exporter Agent에서 community.vmware의 backend로 사용. 직접 호출은 거의 안 함 — Ansible 모듈이 wrapper.

## 핵심 개념

### Connection

```python
from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim

# 자체 서명 환경 (일반)
si = SmartConnectNoSSL(host="esxi.host", user="root", pwd="...", port=443)

# 정식 인증서
si = SmartConnect(host="vcenter.host", user="...@vsphere.local", pwd="...", port=443)

# 사용 후
Disconnect(si)
```

### 핵심 Managed Objects

| Object | 용도 |
|---|---|
| `vim.HostSystem` | ESXi host (hardware / config / capability) |
| `vim.VirtualMachine` | VM |
| `vim.Datastore` | 데이터스토어 |
| `vim.ClusterComputeResource` | 클러스터 |
| `vim.Network` | 네트워크 |

### 인벤토리 탐색

```python
content = si.RetrieveContent()
for dc in content.rootFolder.childEntity:
    if isinstance(dc, vim.Datacenter):
        for cluster in dc.hostFolder.childEntity:
            for host in cluster.host:  # vim.HostSystem
                # host.summary.hardware.cpuModel
                # host.summary.hardware.memorySize
                # host.summary.hardware.numCpuPkgs
                # host.summary.hardware.vendor / .model
                # host.config.network.pnic
                # host.config.storageDevice
                pass
```

### Hardware fact 추출 패턴

`vim.HostSystem` 주요 필드:
- `summary.hardware.{vendor, model, cpuModel, cpuMhz, numCpuCores, numCpuPkgs, numCpuThreads, memorySize}`
- `summary.config.product.{name, fullName, version, build, osType}`
- `config.network.pnic` — physical NIC list
- `config.network.vnic` — VMkernel
- `config.storageDevice.{scsiLun, scsiTopology}` — 디스크
- `config.fileSystemVolume.mountInfo` — datastore

## 버전 호환성

pyvmomi 버전 = `X.Y.Z.U.P`:
- X.Y = vSphere major (6.0 / 7.0 / 8.0)
- 4 버전 backward compatible (예: pyvmomi 8.0.0은 5.x ~ 8.0)

server-exporter는 pyvmomi 9.0.0 → ESXi 6.0 ~ 9.x 호환.

## SSL 처리

- **default**: SSL cert validation enabled
- **자체 서명**: `SmartConnectNoSSL` 사용 (or `ssl.create_default_context()` 커스텀)
- **production**: 정식 cert 권장

server-exporter Agent는 자체 서명 일반 → `SmartConnectNoSSL`.

## Python 호환성

- pyvmomi 9.0.0+ → Python 3.9+
- server-exporter Agent: Python 3.12.3 ✓

## 설치

```bash
pip install pyvmomi==9.0.0
```

server-exporter는 venv (`/opt/ansible-env/`)에서 관리.

## 적용 위치

- community.vmware 모듈이 backend로 자동 사용 → Ansible playbook에서 직접 import 안 함
- 단 일부 커스텀 검증 (deep_probe_esxi.py 같은 향후 도구)에서는 직접 사용 가능

## 정본 reference

- `.claude/ai-context/vmware/...` — esxi adapters
- `.claude/ai-context/external/integration.md` — vSphere API
- `docs/ai/references/vmware/community-vmware-modules.md` — Ansible 모듈

## 적용 rule

- rule 30 (integration-redfish-vmware-os) — vSphere 통합
- (cycle-011: rule 60 해제 — vault/esxi.yml은 cycle-012 encrypt 운영 권장 / validate_certs 정책은 운영자 결정)
