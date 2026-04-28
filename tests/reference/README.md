# tests/reference/ — 실장비 종합 참조 데이터

> **목적**: 실장비에서 도달 가능한 모든 raw 정보를 수집해 향후 schema 추가 / 매핑 검증 / 새 vendor 온보딩 / 회귀 비교의 reference 자산으로 보존.
>
> 본 디렉터리는 **참조용**이지 회귀 input이 아니다. 회귀 input은 `tests/fixtures/` + `schema/baseline_v1/`.

생성: 2026-04-28 (Round 11 reference collection)

---

## 디렉터리 구조

```
tests/reference/
├── README.md                  ← 이 파일
├── INDEX.md                   ← 전체 카탈로그 (수집 일자 / 장비 list / endpoint 수 / 디스크 사용)
├── redfish/
│   └── <vendor>/<ip>/
│       ├── _manifest.json     ← endpoint list / 상태 / timing
│       ├── _summary.txt       ← 사람이 읽는 요약
│       └── <path-derived>.json ← 각 endpoint의 raw 응답 (수천 개 가능)
├── os/
│   └── <distro>/<ip>/
│       ├── _manifest.json
│       ├── _summary.txt
│       ├── ansible_setup.json ← ansible setup 모듈 facts
│       └── cmd_<name>.txt     ← 각 shell 명령 출력 (~80개)
├── esxi/
│   └── <ip>/
│       ├── _manifest.json
│       ├── pyvmomi_host_dump.json ← pyvmomi 객체 dump
│       └── esxcli_<name>.txt  ← esxcli / vim-cmd / SSH 명령 출력 (~40개)
├── agent/
│   ├── agent/<ip>/             ← Jenkins agent 환경 (ansible / python / collection / 도구)
│   └── jenkins_master/<ip>/    ← Jenkins master 환경
├── scripts/                    ← 수집 스크립트 (재실행 가능)
│   ├── crawl_redfish_full.py
│   ├── gather_os_full.py
│   ├── gather_esxi_full.py
│   └── gather_agent_env.py
└── local/                      ← 자격 (gitignored)
    ├── targets.yaml.sample
    └── targets.yaml            ← .gitignore 등록 — 절대 commit 금지
```

## 보안

| 항목 | 위치 | commit |
|---|---|---|
| 수집 자격 (BMC user/pass, OS user/pass) | `local/targets.yaml` | **NO** (.gitignore) |
| Sample 자격 파일 | `local/targets.yaml.sample` | YES (빈 password) |
| Raw 수집 데이터 | `redfish/`, `os/`, `esxi/`, `agent/` | YES (단 OS의 sshd_config / sudoers 등 민감 파일은 사용자 검토 후 commit 결정) |
| 수집 로그 | `local/crawl_*.log` | NO |

`.gitignore`에 등록된 패턴:
```
tests/reference/local/*
!tests/reference/local/.gitkeep
tests/reference/.cache/
tests/reference/**/.crawl_inflight/
```

## 사용 시나리오

1. **새 vendor 온보딩**: `redfish/<vendor>/` 디렉터리에서 그 vendor의 endpoint 구조 파악 → adapter YAML metadata (`tested_against`, `oem_path`) 채움
2. **새 schema 필드 후보 검토**: `redfish/<vendor>/<ip>/_summary.txt`에서 OEM endpoint list 확인 → 어느 vendor에 어떤 데이터가 있는지 비교
3. **OS 매핑 검증**: `os/<distro>/<ip>/cmd_*.txt`로 raw 명령 출력과 ansible setup facts 비교 → field_dictionary 갱신 검증
4. **회귀 비교**: 펌웨어 / OS 업그레이드 후 동일 명령 다시 수집 → diff
5. **장애 분석 사전 자료**: 정상 동작 시점의 endpoint 응답을 확보해두고 장애 시점과 비교

## 재수집

수집 자격 (`local/targets.yaml`)을 채운 후 (sample 참조):

```bash
# Redfish (Windows에서 직접 실행 가능)
python tests/reference/scripts/crawl_redfish_full.py --skip-existing

# OS (WSL 권장 — paramiko + ansible CLI 필요)
wsl python3 tests/reference/scripts/gather_os_full.py --skip-existing

# ESXi (WSL — paramiko + pyvmomi 필요)
wsl python3 tests/reference/scripts/gather_esxi_full.py --skip-existing

# Agent / Master 환경
wsl python3 tests/reference/scripts/gather_agent_env.py --skip-existing
```

옵션:
- `--target <name>`: 특정 장비 1대만
- `--vendor <name>`: vendor 전수 (Redfish 만)
- `--skip-existing`: 기존 파일 그대로 두고 누락분만
- `--max-depth N`: Redfish 재귀 깊이 제한

## 수집 후 정리

수집 완료 → 사용자 검토 → 다음 결정:
1. raw 디렉터리 자체를 commit (디스크 비용 vs 가치)
2. 일부 vendor / 일부 카테고리만 commit (예: BMC raw는 commit, OS sudoers 같은 민감 파일은 제외)
3. `local/targets.yaml` 삭제 (자격 평문 제거)

## 관련

- rule 13 (output-schema-fields), 21 (output-baseline-fixtures), 96 (external-contract-integrity)
- skill: `add-new-vendor`, `update-vendor-baseline`, `probe-redfish-vendor`, `update-output-schema-evidence`
- 정본: `tests/fixtures/` (회귀 input) / `schema/baseline_v1/` (회귀 기준선)
- evidence: `tests/evidence/2026-04-28-reference-collection.md`
