# Gather Convention — server-exporter

> 3-channel gather (os/esxi/redfish) 작업 컨벤션.
> 정본: `GUIDE_FOR_AI.md` (Fragment 철학 / 새 gather 템플릿 / 변수 네이밍).

## 0. 정본 reference

본 문서는 인덱스. 본문은 정본 참조 (rule 70 중복 보존 금지):

- `GUIDE_FOR_AI.md` — Fragment 철학, 변수 네이밍, 실패 처리 패턴
- `docs/06_gather-structure.md` — 3-channel 구조
- `docs/07_normalize-flow.md` — Fragment 정규화 흐름
- `docs/08_failure-handling.md` — block/rescue/always 실패 처리
- `docs/11_precheck-module.md` — 4단계 진단

## 1. Fragment 철학 (rule 22)

각 gather는 **자기 fragment만** 만든다:
- `_data_fragment` — 섹션별 raw 데이터 (예: `cpu`, `memory`)
- `_sections_<name>_supported_fragment` — 지원 섹션 list
- `_errors_fragment` — 수집 오류

`merge_fragment.yml`이 누적 병합 → 공통 builder가 최종 JSON 조립.

**Forbidden**: 다른 gather의 fragment 변수를 set_fact로 수정.

```yaml
# WRONG — 다른 섹션의 fragment 수정
- set_fact:
    _sections_memory_collected_fragment: [...]

# CORRECT — 자신의 fragment만
- set_fact:
    _data_fragment:
      cpu: {...}
    _sections_cpu_collected_fragment: ['cpu']
```

## 2. 명명 규칙

| 패턴 | 위치 | 용도 |
|---|---|---|
| `gather_<section>.yml` | `os-gather/tasks/{linux,windows}/`, `esxi-gather/tasks/`, `redfish-gather/tasks/` | raw 수집 |
| `normalize_<section>.yml` | `esxi-gather/tasks/` 등 | 채널-specific 정규화 |
| `build_<artifact>.yml` | `common/tasks/normalize/` | 공통 builder (sections / status / errors / meta / correlation / output) |
| `precheck_*.yml` | gather entry | 본 수집 전 4단계 진단 |
| `_<scope>_<name>_fragment` | set_fact 변수 | fragment 변수 prefix `_` |

## 3. 새 gather 추가 (template)

`GUIDE_FOR_AI.md` "새 gather 템플릿" 섹션 그대로 따른다. 핵심:

1. `gather_<section>.yml` 또는 `collect_<section>.yml` 작성 (raw 수집)
2. Fragment 변수 set_fact (`_data_fragment`, `_sections_<name>_supported_fragment`, `_errors_fragment`)
3. `normalize_<section>.yml` 또는 `common/tasks/normalize/build_<section>.yml` 작성
4. `merge_fragment.yml` 호출 확인
5. `common/vars/supported_sections.yml` 업데이트
6. `schema/sections.yml` + `schema/fields/*.yml` 추가
7. Baseline JSON 예시 추가 + 문서 갱신

## 4. Linux 2-tier (Python 감지 + Raw Fallback)

`os-gather/preflight.yml`이 `_l_python_mode` 자동 설정:

| 모드 | 조건 | 수집 방식 |
|---|---|---|
| `python_ok` | Python 3.9+ | 기존 Python 경로 (setup/shell/command/getent) |
| `python_missing` / `python_incompatible` | 미설치 또는 3.8↓ | raw-only |
| `raw_forced` | `SE_FORCE_LINUX_RAW_FALLBACK=true` | raw-only (개발/검증) |

raw 경로 원칙:
- remote는 `raw` 모듈만, controller-side `set_fact`/Jinja2 파싱 허용
- 6 섹션 모두 수집 가능, JSON 스키마 호환 100%
- `diagnosis.details`에 `gather_mode` + `python_version` 추가
- SELinux: `getenforce` → `enabled`/`disabled` 정규화 (Round 2 수정)
- Memory raw 경로는 dmidecode 기반 → `physical_installed` (Python 경로의 `os_visible`보다 정밀)

## 5. Vault 2단계 로딩 (Redfish 특화)

```yaml
# 1단계: 무인증으로 ServiceRoot detect
- redfish_gather:
    ip: "{{ target_ip }}"
    # 계정 없음 (ServiceRoot 무인증)
  register: _rf_probe

# 2단계: vendor에 맞는 vault 로드
- include_vars:
    file: "vault/redfish/{{ _rf_detected_vendor }}.yml"
    name: _rf_vault

# 3단계: 인증으로 재수집
- redfish_gather:
    ip: "{{ target_ip }}"
    username: "{{ _rf_vault.username }}"
    password: "{{ _rf_vault.password }}"
```

## 6. Adapter 점수

```
score = priority × 1000 + specificity × 10 + match_score
```

priority:
- generic = 0
- 기본 vendor = 10
- 세대별 = 50~100
- 구체적 모델 = match.model_patterns + 높은 specificity

## 7. 4단계 Precheck (precheck_bundle.py)

```
ping → port → protocol → auth
```

각 단계 실패 시 `diagnosis.details`에 어디서 막혔는지 기록 + graceful degradation.

## 8. 자주 호출하는 Skill / Agent

- `task-impact-preview` — 코드 변경 전 영향
- `validate-fragment-philosophy` — 다른 gather fragment 침범 검증
- `score-adapter-match` — 점수 디버깅
- `add-new-vendor` — 벤더 추가 3단계
- `probe-redfish-vendor` — 새 펌웨어 프로파일링
- agent: `gather-refactor-worker`, `fragment-engineer`, `adapter-author`, `vendor-onboarding-worker`, `precheck-engineer`
