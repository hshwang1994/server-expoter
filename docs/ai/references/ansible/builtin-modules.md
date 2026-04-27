# Ansible Builtin Modules — 핵심 reference

> Source: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html
> Fetched: 2026-04-27 (server-exporter Plan 2 reference 수집)
> Collection version (server-exporter 검증 기준): ansible-core 2.20.5

server-exporter는 Linux/Windows OS gather에서 ansible.builtin 모듈 사용. 핵심:

## Facts Gathering

| Module | 용도 | 핵심 파라미터 |
|---|---|---|
| `setup` | 원격 호스트 facts (hostname / OS / hardware / network) | `filter`, `gather_subset`, `gather_timeout` |
| `gather_facts` | 다중 호스트 fact 병렬 수집 | `parallel`, `timeout` |
| `getent` | unix getent (passwd / group / hosts) | `database`, `key`, `service` |

server-exporter Linux gather는 `setup` + `getent`로 OS info / users 수집.

## Command Execution

| Module | 용도 | 비고 |
|---|---|---|
| `command` | 셸 처리 없이 명령 직접 실행 (executable + args) | `cmd`, `creates`, `removes`, `chdir` |
| `shell` | 셸 처리 (pipe, redirect 가능) | `cmd`, `executable` |
| `raw` | 가장 low-level. **Python 없는 호스트도 동작** | `command`, `timeout` |

**server-exporter Linux 2-tier 핵심**: `_l_python_mode == "python_*missing/incompatible/raw_forced"` 일 때 `raw` 모듈만으로 6 섹션 수집 (Python 3.6 이하 호스트 대응).

## File / I/O

| Module | 용도 |
|---|---|
| `copy` / `template` / `file` | 파일 배포 / Jinja2 템플릿 / 권한 |
| `lineinfile` / `blockinfile` / `replace` | 텍스트 in-place 편집 |
| `stat` / `find` | 파일 메타 / 검색 |
| `slurp` / `fetch` / `get_url` | 원격 → 로컬 회수 / 다운로드 |

## Variables / Control Flow

| Module / Keyword | 용도 |
|---|---|
| `set_fact` | host fact 설정 (Fragment 변수 생성에 사용 — rule 22) |
| `register` | task 결과 캡처 |
| `include_vars` | 외부 yml에서 변수 로드 (Vault 2단계 로딩에 사용) |
| `debug` / `assert` / `fail` | 진단 / 단언 / 실패 |
| `block` / `rescue` / `always` | 실패 처리 (rule 30 외부 시스템) |
| `include_tasks` / `import_tasks` | 동적 / 정적 include (rule 11 R3) |
| `include_role` / `import_role` | role 호출 |
| `pause` / `wait_for` | 동기화 |

**server-exporter 패턴**:
```yaml
- include_tasks: "{{ playbook_dir }}/common/tasks/normalize/merge_fragment.yml"  # 동적
```
- 동적: vendor가 precheck 후 결정되므로 `include_tasks`
- 정적: 모든 host 공통 init은 `import_tasks` 가능

## Networking

| Module | 용도 |
|---|---|
| `uri` | HTTP/HTTPS REST 요청 (Redfish gather에서 일부 사용) |
| `get_url` | 파일 다운로드 |

## Service / Package

| Module | 용도 |
|---|---|
| `service` / `systemd_service` | 서비스 관리 (수집에서는 거의 사용 안 함) |
| `package` / `apt` / `dnf` / `pip` | 패키지 관리 (수집에서는 거의 사용 안 함) |

## Best Practices for server-exporter

1. **Fragment 변수 생성은 `set_fact`만**: 한 번에 set_fact로 fragment dict 전체 정의
2. **raw fallback 호환**: Linux gather는 setup 의존하지 말고 `getent passwd` + raw shell로 대체 경로 준비
3. **Jinja2 정합성**: post_edit_jinja_check.py가 `{{ }}` / `{% %}` 짝 검증
4. **Vault 변수**: `include_vars: { file: "vault/redfish/{{ vendor }}.yml", name: _rf_vault }` 후 `{{ _rf_vault.username }}` 참조

## 적용 rule

- rule 10 (gather-core) — 모듈 선택 가이드
- rule 11 (gather-output-boundary) — include_tasks vs import_tasks
- rule 22 (fragment-philosophy) — set_fact 패턴
- rule 27 (precheck-guard-first) — 4단계 진단
