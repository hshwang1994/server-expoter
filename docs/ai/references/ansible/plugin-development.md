# Ansible Plugin Development — 핵심 reference

> Source: https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html
> Fetched: 2026-04-27
> 사용 위치 (server-exporter): `callback_plugins/json_only.py`, `lookup_plugins/adapter_loader.py`, `filter_plugins/diagnosis_mapper.py`, `filter_plugins/field_mapper.py`, `module_utils/adapter_common.py`

## 플러그인 종류 (server-exporter 사용)

| 종류 | 위치 | server-exporter 인스턴스 |
|---|---|---|
| Callback | `callback_plugins/` | `json_only.py` (stdout — OUTPUT 태스크만 JSON) |
| Lookup | `lookup_plugins/` | `adapter_loader.py` (adapter 동적 선택) |
| Filter | `filter_plugins/` | `diagnosis_mapper.py`, `field_mapper.py` |
| Module utils | `module_utils/` | `adapter_common.py` (점수 / vendor 정규화) |

## 공통 요구사항

- Python으로 작성
- 에러는 `AnsibleError` raise
- 반환 string은 unicode (`to_text` 사용)
- `DOCUMENTATION` 변수로 옵션 정의

## Callback Plugin (json_only.py 패턴)

`CallbackBase` 상속, `v2_*` 메서드 override.

### 핵심 속성

```python
from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_NAME = 'json_only'        # 폴더 이름과 일치
    CALLBACK_TYPE = 'stdout'           # stdout 전용 callback
    CALLBACK_NEEDS_ENABLED = False     # 자동 활성 (ansible.cfg stdout_callback)
```

### 핵심 v2_* 메서드

| 메서드 | 호출 시점 |
|---|---|
| `v2_playbook_on_start(self, playbook)` | playbook 시작 |
| `v2_playbook_on_task_start(self, task, is_conditional)` | task 시작 |
| `v2_runner_on_ok(self, result)` | task 성공 |
| `v2_runner_on_failed(self, result, ignore_errors=False)` | 실패 |
| `v2_runner_on_skipped(self, result)` | skip |
| `v2_playbook_on_stats(self, stats)` | playbook 종료 (요약) |

### server-exporter json_only.py 핵심

- 일반 task 출력 무시
- task name이 "OUTPUT"으로 시작하는 경우만 JSON 직렬화 (rule 20 R3)
- stdout으로 envelope JSON 1개 출력 → 호출자가 파싱

## Lookup Plugin (adapter_loader.py 패턴)

`LookupBase` 상속, `run()` 메서드.

```python
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        ret = []
        for term in terms:
            ret.append(...)  # 처리 결과
        return ret
```

### server-exporter adapter_loader.py 핵심

- `terms = [channel]` (예: `'redfish'`)
- `kwargs = {'manufacturer': 'Dell', 'model': '...', 'firmware': '...'}`
- adapters/{channel}/*.yml 스캔
- match 평가 → 점수 계산 (rule 12 R2)
- 정렬 → 최고 점수 adapter 반환 (또는 generic fallback)

### Ansible 호출

```yaml
- set_fact:
    _selected_adapter: "{{ lookup('adapter_loader', 'redfish',
                                  manufacturer=_rf_manufacturer,
                                  model=_rf_model,
                                  firmware=_rf_firmware) }}"
```

## Filter Plugin (diagnosis_mapper.py 패턴)

```python
class FilterModule:
    def filters(self):
        return {
            'diagnosis_status': self.diagnosis_status,
            'normalize_vendor': self.normalize_vendor,
        }

    def diagnosis_status(self, precheck_result):
        # ping/port/protocol/auth → success/partial/failed
        return {...}
```

### Ansible 호출

```yaml
- set_fact:
    _diagnosis: "{{ _precheck_result | diagnosis_status }}"
```

## Module Utils (adapter_common.py 패턴)

플러그인 간 공유 로직. `import` 가능한 일반 Python.

```python
# module_utils/adapter_common.py
def calculate_score(adapter, context):
    priority = adapter.get('priority', 0)
    specificity = ...
    match_score = ...
    return priority * 1000 + specificity * 10 + match_score

def normalize_vendor(manufacturer, aliases):
    return aliases.get(manufacturer.lower().strip(), 'generic')
```

```python
# lookup_plugins/adapter_loader.py
import sys
sys.path.insert(0, os.path.dirname(__file__) + '/../module_utils')
from adapter_common import calculate_score, normalize_vendor
```

## 옵션 정의

```python
DOCUMENTATION = '''
    name: my_plugin
    options:
      verbose:
        type: bool
        default: false
        env:
          - name: SERVER_EXPORTER_VERBOSE
        ini:
          - section: defaults
            key: verbose
'''
```

`self.get_option('verbose')` 또는 `self.set_options()`.

## 에러 처리

```python
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.common.text.converters import to_native

try:
    ...
except Exception as e:
    raise AnsibleError(f"adapter_loader 실패: {to_native(e)}")
```

## server-exporter Best Practices

1. **callback은 stdout 전용**: `CALLBACK_TYPE = 'stdout'` (json_only.py)
2. **lookup은 list 반환**: `run()`이 단일 dict 반환해도 list로 wrap
3. **filter는 등록 dict**: `filters()`가 `{name: func}` 반환
4. **module_utils는 stateless**: 클래스 인스턴스 변수 금지 (Ansible 멀티프로세스)
5. **에러는 AnsibleError**: `to_native` 안전 변환

## 적용 rule

- rule 10 (gather-core) — 플러그인 위치 / 책임 분리
- rule 11 (gather-output-boundary) — callback이 envelope 결정
- rule 20 (output-json-callback) — json_only.py 보호
