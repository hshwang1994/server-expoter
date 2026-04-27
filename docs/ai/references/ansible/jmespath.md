# JMESPath — JSON 쿼리 언어 (Ansible json_query 필터)

> Source: https://jmespath.org/specification.html
> Fetched: 2026-04-27
> 사용 위치 (server-exporter): `filter_plugins/`, `lookup_plugins/`, gather/normalize playbook의 `json_query` 필터

## 개요

JMESPath는 JSON 쿼리 언어. Ansible `json_query` 필터(community.general)가 사용. server-exporter Redfish 응답에서 깊이 중첩된 데이터 추출에 핵심.

## 기본 표현식

### Key 접근

```jmespath
foo            # 단일 key
foo.bar.baz    # 중첩 (좌→우)
"with space"   # 공백/특수문자는 quoted
```

### Array

```jmespath
myarray[0]     # 첫 요소
myarray[-1]    # 마지막 요소
myarray[0:3]   # slice (Python 스타일)
myarray[::-1]  # 역순
```

### 와일드카드

```jmespath
people[*].name              # array의 각 요소에서 name 추출
servers.*.status            # object의 모든 값에서 status
results[]                   # nested array flatten
```

### 필터

```jmespath
servers[?status == `'active'`]
devices[?temperature > `75`]
servers[?status == `'online'` && cpu_usage > `80`]
```

### 파이프

```jmespath
servers[*].data | [0]       # projection 종료 + 전체 결과에 [0]
```

### Multi-Select (재구조화)

```jmespath
[name, age, city]                                          # array
{name: name, status: state, health: Status.Health}         # object (rename)
```

## 주요 함수

### String / Array / Numeric

- `length(@)`, `contains(haystack, needle)`, `starts_with(s, p)`, `ends_with(s, p)`
- `sort(@)`, `sort_by(arr, &expr)`, `min_by`, `max_by`
- `reverse(@)`, `map(&expr, arr)`
- `keys(obj)`, `values(obj)`, `merge(o1, o2)`
- `not_null(e1, e2, ...)`, `to_string`, `to_number`, `to_array`

## server-exporter Redfish 패턴

### Member URI 추출

```jmespath
Members[*]."@odata.id"
```

### Health 필터

```jmespath
Members[?Status.Health == `'OK'`]
```

### 재구조화 + 필터

```jmespath
Members[*].{name: Name, state: State, health: Status.Health}
Members[?Status.Health != `'OK'`].{path: "@odata.id", health: Status.Health}
```

### 카운트 / 요약

```jmespath
{total: length(Members[*]), healthy: length(Members[?Status.Health == `'OK'`])}
```

### Drives 평탄화

```jmespath
Members[*].Drives | flatten(@) | sort_by(@, &CapacityBytes)
```

## Ansible 사용 예시

```yaml
- name: Storage controller list 추출
  set_fact:
    _data_fragment:
      storage:
        controllers: "{{ redfish_response.json | json_query('Members[*].\"@odata.id\"') }}"

- name: Health 문제 디스크만
  set_fact:
    _failed_drives: "{{ drives_response.json | json_query('Members[?Status.Health != `OK`].{name: Name, health: Status.Health}') }}"
```

## 주의 사항

- 백틱(`` ` ``) 안의 string은 JSON literal (single quote 사용 — `` `'OK'` ``)
- 결과 type 보존 (string / number / array / object / null)
- 잘못된 필드 접근은 에러 아닌 `null` 반환

## 적용 위치 (server-exporter)

- `filter_plugins/diagnosis_mapper.py` (간접 사용)
- gather playbook의 `json_query` 필터 (Redfish 응답 파싱)
- `redfish-gather/library/redfish_gather.py`는 stdlib만 사용 → JMESPath 미사용 (Python dict 직접 navigation)

## 적용 rule

- rule 10 R2 (stdlib 우선) — 라이브러리 모듈은 jmespath 사용 OK
- rule 30 (integration-redfish-vmware-os) — 외부 응답 파싱
