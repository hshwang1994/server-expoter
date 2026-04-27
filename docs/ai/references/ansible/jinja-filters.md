# Ansible Jinja2 Filters — 핵심 reference

> Source: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_filters.html
> Fetched: 2026-04-27
> 사용 위치 (server-exporter): 모든 Ansible playbook (build_*.yml, normalize_*.yml, gather_*.yml)

## 핵심 filter 카테고리

### 1. 변수 / 기본값

| Filter | 용도 | 예시 |
|---|---|---|
| `default(value)` | 기본값 fallback | `{{ x | default(omit) }}` |
| `default(value, true)` | 빈 string도 fallback | — |
| `mandatory` | 정의 안 됐으면 에러 | `{{ x | mandatory }}` |
| `ternary(true_val, false_val, omit_val)` | 3항 조건 | `{{ enabled | ternary('on', 'off', omit) }}` |
| `type_debug` | 타입 디버깅 | `{{ x | type_debug }}` |

server-exporter 빈번 사용: `default(omit)` (Ansible vars 누락 방어, rule 95 R1 #1)

### 2. dict / list 변환

| Filter | 용도 |
|---|---|
| `dict2items` / `items2dict` | dict ↔ list of {key, value} |
| `combine(dict_b, recursive=True)` | dict 재귀 병합 |
| `union` / `intersect` / `difference` / `symmetric_difference` | 집합 연산 |
| `zip` / `zip_longest` | 두 list 병합 |
| `flatten` (`levels=N`) | nested list 평탄화 |

server-exporter `merge_fragment.yml`은 `combine(recursive=True)` 패턴 사용.

### 3. JSON / YAML

| Filter | 용도 |
|---|---|
| `to_json` / `to_nice_json` (indent=2) | dict → JSON string |
| `from_json` | JSON string → dict |
| `to_yaml` / `to_nice_yaml` | dict → YAML |
| `from_yaml` | YAML → dict |
| `community.general.json_query('expr')` | JMESPath (별도 reference) |

callback_plugins/json_only.py는 `to_json` 사용 (rule 20 envelope 6 필드).

### 4. 정규식

| Filter | 용도 |
|---|---|
| `regex_search('pattern')` | 첫 매치 |
| `regex_findall('pattern')` | 모든 매치 list |
| `regex_replace('pattern', 'repl')` | 치환 |

dead code 패턴 (rule 95 R1 #3) 회피.

### 5. 파일 경로

| Filter | 용도 |
|---|---|
| `basename` / `dirname` | 파일명 / 디렉터리 |
| `expanduser` | `~` 해석 |
| `splitext` | (name, ext) tuple |
| `win_basename` / `win_dirname` | Windows 변환 |

### 6. URL / Encoding

| Filter | 용도 |
|---|---|
| `urlsplit('hostname')` | URL 파싱 |
| `quote` | shell escape |
| `b64encode` / `b64decode(encoding='utf-8')` | Base64 |
| `hash('sha256')` / `hash('md5')` | 해시 |
| `password_hash('sha512')` | 비밀번호 해시 |

callback URL 무결성 (rule 31): `url | urlsplit('hostname')` 활용 가능.

### 7. 네트워크 (ansible.utils.ipaddr)

| Filter | 용도 |
|---|---|
| `ipaddr` | IP 형식 검증 |
| `ipv4` / `ipv6` | 버전별 |
| `ipaddr('address')` / `ipaddr('network')` / `ipaddr('netmask')` / `ipaddr('prefix')` | 변환 |
| `ipaddr('host/prefix')` | CIDR 분해 |

server-exporter inventory_json의 IP 형식 검증 (Jenkins Stage 1).

### 8. 수학 / 통계

| Filter | 용도 |
|---|---|
| `min` / `max` | 최소 / 최대 |
| `pow(2)` | 거듭제곱 |
| `log(base=10)` | 로그 |
| `random(seed='...')` | 시드 기반 random |

### 9. Datetime

| Filter | 용도 |
|---|---|
| `to_datetime('%Y-%m-%d')` | string → datetime |
| `strftime('%Y-%m-%d')` | datetime → string |
| `strftime('%H:%M:%S', utc=True)` | UTC |

## server-exporter 빈번 사용 패턴

### Fragment 변수 안전 default

```yaml
- set_fact:
    _data_fragment:
      cpu: "{{ cpu_data | default({}) }}"
      memory: "{{ memory_data | default({}) }}"
```

### combine recursive (build_*.yml)

```yaml
- set_fact:
    _collected_data: "{{ _collected_data | default({}) | combine(_data_fragment, recursive=True) }}"
```

### json_query (Redfish 응답)

```yaml
- set_fact:
    _drives: "{{ rf_response.json | json_query('Members[*].\"@odata.id\"') }}"
```

### Date stamp (evidence)

```yaml
- set_fact:
    _evidence_path: "tests/evidence/{{ '%Y-%m-%d' | strftime }}-{{ vendor }}-{{ firmware }}.md"
```

## Best Practices for server-exporter

1. **`default(omit)` 빈번 사용**: Ansible vars 누락 방어 (rule 95 R1 #1)
2. **`combine(recursive=True)`**: fragment 병합에 사용 (단 누적 변수만, gather에서 직접 사용 금지 — rule 22)
3. **`json_query`**: Redfish 응답 파싱 (filter_plugins / lookup_plugins / playbook 모두 가능)
4. **`hash`**: fingerprint 계산 (project-map fingerprint와 정합)

## 적용 rule

- rule 10 (gather-core)
- rule 22 (fragment-philosophy)
- rule 95 R1 (의심 패턴)
