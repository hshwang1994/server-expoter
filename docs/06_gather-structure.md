# 06. Gather 구조 설명

> **이 문서는** server-exporter 가 어떤 구조로 정보를 수집하는지 개발자 시야에서 설명합니다.
> "왜 gather 가 여러 파일로 쪼개져 있는지", "fragment 가 정확히 무엇인지" 가 궁금할 때 보세요.
>
> 새 섹션 / 새 채널을 추가하기 전에 본 문서를 한 번 정독하면 후속 PR 시간이 크게 줄어듭니다.

---

## 한 단락 요약

각 gather 파일은 **전체 JSON 을 만들지 않습니다.** 자기 역할의 작은 조각 (fragment) 만 만든 뒤, 공통 정규화 엔진(merge_fragment.yml + build_*.yml) 이 그 조각들을 모아 최종 JSON envelope 을 조립합니다.

이렇게 분리하는 이유:
- 새 섹션 추가가 site.yml 한 줄로 끝납니다.
- 한 gather 의 실패가 다른 gather 의 결과를 오염시키지 않습니다.
- 같은 정규화 엔진이 3 채널을 모두 처리하므로 출력 형식이 자동으로 일관됩니다.

## Fragment 기반 수집 철학

```
raw 수집  (벤더 / OS / API 별 원본 데이터)
   ↓
정규화    (gather 별로 자기 섹션 변환)
   ↓
Fragment 생성     ─┐
  _data_fragment   │
  _sections_*       │  ← 각 gather 가 만들어내는 5종 변수
  _errors_fragment ─┘
   ↓
merge_fragment.yml  (누적 변수에 병합 — 자기 영역만 덧붙임)
   ↓
build_sections / build_status / build_errors / build_meta / build_correlation
   ↓
build_output.yml  (envelope 13 필드 조립)
   ↓
schema_version 주입
   ↓
OUTPUT 태스크 → callback plugin 캡처 → 호출자
```

### 새 수집 항목 추가 방법 (한 줄 정리)

1. 새 `gather_xxx.yml` 작성 → fragment 변수 5종 set_fact → `merge_fragment.yml` 호출
2. `site.yml` 에 `include_tasks: tasks/gather_xxx.yml` 한 줄 추가
3. 끝. (`site.yml` / `build_output.yml` 전체 수정은 필요 없음)

상세 절차와 7단계 체크리스트는 [14_add-new-gather.md](14_add-new-gather.md).

---

## 전체 흐름

```
포털 → Jenkins (target_type: os|esxi|redfish)
     → inventory.sh (ip 만 처리)
     → vault 자동 로딩
     → init_fragments.yml   ← 누적 변수 초기화
     → tasks/ (수집 → 각자 fragment 생성 → merge_fragment)
     → build_sections / build_status / build_errors
     → build_meta / build_correlation
     → build_output → schema_version 주입
     → OUTPUT 태스크 → callback plugin 캡처 → 포털
```

---

## os-gather

```
site.yml Play1: 포트 감지 (SSH 22 / WinRM 5985/5986)
  → 성공: _os_linux 또는 _os_windows 그룹에 등록
  → 실패: build_failed_output.yml 공통 모듈로 failed OUTPUT 생성
          ↓
site.yml Play2 (Linux):
  common/init_fragments.yml     ← 누적 변수 초기화
  adapter_loader (os 채널)      ← adapter 선택
  tasks/linux/preflight.yml     → Python 경로, 명령 존재 확인
  tasks/linux/gather_system.yml → system fragment → merge_fragment
  tasks/linux/gather_cpu.yml    → cpu fragment → merge_fragment
  tasks/linux/gather_memory.yml → memory fragment (dmidecode) → merge_fragment
  tasks/linux/gather_storage.yml → storage fragment (lsblk+mounts) → merge_fragment
  tasks/linux/gather_network.yml → network fragment (gw/dns/speed) → merge_fragment
  tasks/linux/gather_users.yml  → users fragment (getent+lastlog) → merge_fragment
  tasks/normalize/build_output.yml → build_sections/status/errors/output

site.yml Play3 (Windows): 동일 구조, tasks/windows/*
```

---

## esxi-gather

```
site.yml (1 Play):
  common/init_fragments.yml
  tasks/collect_facts.yml      → _e_raw_facts, _e_facts_ok
  tasks/collect_config.yml     → _e_raw_config, _e_config_ok
  tasks/collect_datastores.yml → _e_raw_ds, _e_ds_ok
  tasks/normalize_system.yml   → system/hardware/cpu/memory fragment → merge_fragment
  tasks/normalize_network.yml  → network fragment → merge_fragment
  tasks/normalize_storage.yml  → storage fragment (partial 판정 반영) → merge_fragment
  build_sections / build_status / build_errors / build_output
```

---

## redfish-gather

```
site.yml (1 Play):
  common/init_fragments.yml
  precheck_bundle              → 4단계 진단 (ping→port→protocol→auth)
  tasks/detect_vendor.yml      → _rf_detected_vendor
  adapter_loader (redfish)     → _selected_adapter (벤더별 adapter 자동 선택)
  tasks/load_vault.yml         → vault/redfish/{vendor}.yml
  tasks/collect_standard.yml   → _rf_raw_collect, _rf_vendor
    └ gather_storage()         → Storage 실패 시 SimpleStorage fallback
  tasks/normalize_standard.yml → 전체 표준 fragment → merge_fragment
  _selected_adapter.oem_tasks  → OEM fragment → merge_fragment (adapter 기반 동적 로딩)
  build_sections / build_status / build_errors / build_meta / build_correlation / build_output
```

### Redfish Storage 구조

```
storage
├── controllers[]      ← RAID/HBA 컨트롤러 (id, name, health, drives[])
├── physical_disks[]   ← 물리 디스크 (id, device, model, serial, ...)
├── logical_volumes[]  ← RAID 논리 볼륨 (Redfish only, OS/ESXi는 빈 배열)
├── filesystems[]      ← (Redfish에서는 빈 배열)
└── datastores[]       ← (Redfish에서는 빈 배열)
```

**관계**: `logical_volumes[].controller_id` → `controllers[].id`,
`logical_volumes[].member_drive_ids` → `physical_disks[].id`.

`logical_volumes`는 Redfish `/Systems/{id}/Storage/{id}/Volumes` 엔드포인트에서 수집.
Cisco v1_0_3 스키마는 `RAIDType` 필드가 없어 `VolumeType` → `RAIDType` fallback 매핑 사용.

### Redfish Safe Common 5 필드 (normalize_standard.yml 반영)

| 위치 | 필드 | 타입 |
|------|------|------|
| `hardware` | `health` | string\|null (OK/Warning/Critical) |
| `hardware` | `power_state` | string\|null (On/Off/PoweringOn/PoweringOff) |
| `physical_disks[]` | `serial` | string\|null |
| `physical_disks[]` | `failure_predicted` | boolean\|null |
| `physical_disks[]` | `predicted_life_percent` | integer\|null (0-100) |

**디스크 필터 정책**: CapacityBytes == 0 또는 Name에 "empty" 포함 시 드라이브 skip.
HPE `PredictedMediaLifeLeftPercent` float 값은 int()로 변환.

> **Conditional 필드 (보류)**: hardware.sku, PowerConsumedWatts, PowerCapacityWatts,
> PowerMetrics.*, Proc.MaxSpeedMHz, PSU.Health, NIC.LinkStatus 등은 벤더 간 일관성 미확보로 보류.

### 지원 벤더

dell, hpe, lenovo, supermicro, cisco (5개 벤더)
- Cisco: adapter `redfish_cisco_cimc`, vault `vault/redfish/cisco.yml`

---

## callback_plugins/json_only.py

- `name: OUTPUT` 태스크의 `msg` 만 stdout 으로 캡처
- 나머지 Ansible 출력 전부 억제
- 프로젝트 루트 `callback_plugins/json_only.py` 단일 사본 유지 (`ansible.cfg`의 `callback_plugins = ./callback_plugins`로 참조)

---

## inventory.sh

각 채널 (`os-gather/`, `esxi-gather/`, `redfish-gather/`) 에 같은 동작의 inventory.sh 가 있습니다.

| 동작 | 설명 |
|------|------|
| 우선순위 1 | `INVENTORY_JSON` 환경변수에서 읽음 |
| 우선순위 2 | `.inventory_input.json` 파일에서 읽음 (Jenkinsfile 의 `writeFile` 이 생성) |
| 결과 | Ansible 가 이해할 수 있는 동적 인벤토리 출력 |

> 왜 두 가지 경로가 필요한가?
> Jenkins 의 `ansiblePlaybook` 플러그인이 `environment` 블록의 멀티라인 환경변수를 그대로 전달하지 못하는 경우가 있어서, 파일 fallback 을 함께 둡니다.

다른 약속:
- `inventory_hostname = ip` 로 통일 (호스트명 사전 등록 필요 없음)
- 자격증명 정보는 inventory 에 들어가지 않음 (vault 에서 자동 로딩)

---

## 다음 단계

| 다음 작업 | 문서 |
|---|---|
| Fragment 가 정규화 엔진을 거쳐 envelope 이 되는 흐름 | [07_normalize-flow.md](07_normalize-flow.md) |
| 실패 처리 패턴 (block / rescue / always) | [08_failure-handling.md](08_failure-handling.md) |
| 새 섹션 추가 7단계 체크리스트 | [14_add-new-gather.md](14_add-new-gather.md) |
| Adapter 시스템 (벤더 자동 감지 점수 계산) | [10_adapter-system.md](10_adapter-system.md) |
