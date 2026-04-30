# Coverage — OS Storage Deep Dive (Linux) — 추가 검토

## 컨텍스트

Linux storage gather 의 deep 도구 호환성. 우리 코드 (`os-gather/tasks/linux/gather_storage.yml`) 가 이미 처리하는지 확인.

## 표준 도구 (R1)

### NVMe 관리
- **`nvme list`** — NVMe SSD 목록 (id-ctrl / smart-log / fw-log)
- **`nvme id-ctrl -H /dev/nvme0`** — controller info
- **`nvme smart-log /dev/nvme0`** — health / wear leveling

### LVM (Logical Volume Manager)
- **`pvs`** — Physical Volume 목록
- **`vgs`** — Volume Group 목록
- **`lvs`** — Logical Volume 목록
- **`lvdisplay`** / **`vgdisplay`** / **`pvdisplay`** — verbose

### MD RAID (Software RAID)
- **`mdadm --detail /dev/md0`** — array detail
- **`cat /proc/mdstat`** — software RAID 상태

### 파일시스템
- **`lsblk -J`** — block device tree (JSON)
- **`df -h`** — mount point 사용량
- **`blkid`** — UUID / FSTYPE
- **`findmnt -J`** — mount tree (JSON)

### Multipath
- **`multipath -ll`** — multipath device 목록

## 우리 코드 점검 (스캔 결과 추가 필요)

### 현재 우리 gather 도구 사용
(grep 결과 첨부 — `os-gather/tasks/linux/gather_storage.yml` 분석)
- lsblk / df / blkid 사용 ✓ (확인 필요)
- nvme-cli / lvs / pvs / vgs / mdadm 사용 여부 — **확인 필요**

### 검토 필요 항목
1. NVMe SSD 가 `lsblk` 로만 잡히면 wear-level / smart 정보 누락
2. LVM 환경에서 logical volume / physical volume / volume group 정보 누락 가능
3. Software RAID (mdadm) 환경에서 RAID 상태 / member disk 누락

## fix 후보

### F32 — Linux storage deep 도구 통합 (P2)
- **현재 위치**: `os-gather/tasks/linux/gather_storage.yml` (현재 lsblk 위주)
- **변경 (Additive)**: 추가 도구 호출 — graceful (도구 부재 시 skip)
  - `nvme list` (nvme-cli 설치 시) — NVMe wear level 등 추가 메타
  - `lvs` / `vgs` / `pvs` (lvm2 설치 시) — LVM 정보
  - `cat /proc/mdstat` — Software RAID
  - `multipath -ll` (multipath-tools 설치 시)
- **회귀**: minimal Alpine / 도구 부재 시 graceful (기존 동작 유지)
- **schema 영향**: `data.storage.physical_disks[*]` 에 추가 필드 (smart_data / wear_level / raid_member)
- **우선**: P2 — 사고 재현 또는 사용자 요구 시

## Cold-start

1. 우리 코드 `gather_storage.yml` 분석 (현재 도구 사용 명확화)
2. 미수집 영역 식별
3. 추가 task 작성 (graceful)
4. lab fixture (LVM / mdadm / NVMe)
5. schema field_dictionary 갱신 (사용자 명시 승인)

## Sources

- [nvme-cli GitHub](https://github.com/linux-nvme/nvme-cli)
- [RHEL 9 Managing Storage Devices](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html-single/managing_storage_devices/index)
- [LVM cheatsheet](http://www.datadisk.co.uk/html_docs/redhat/rh_lvm.htm)

## 갱신 history

- 2026-05-01: 신규 영역 ticket / F32 P2
