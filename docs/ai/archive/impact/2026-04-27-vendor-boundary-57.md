# Vendor 경계 57건 분석 보고서 — 2026-04-27 (cycle-004)

> cycle-004 W2. `verify_vendor_boundary.py` 인코딩 fix (W1) 후 처음으로 본 출력 결과 분석.
> 사용자 결정 대기 중 (자동 패치 금지).

## 요약

`verify_vendor_boundary.py` 첫 정상 실행 결과 **총 57건** 검출. 분류:

| 분류 | 카운트 | 평가 |
|---|---|---|
| (a) `common/vars/vendor_aliases.yml` (rule 12 R1 명시 허용) | 24 | **False positive** — 도구 EXCLUDE에 추가됨 (이번 cycle T1) |
| (b) `os-gather/tasks/{linux,windows}/gather_system.yml` Jinja2 OEM list | 2 | **검토 필요 — 경계 위반 의심** |
| (c) `redfish-gather/library/redfish_gather.py` docstring / 주석 | 7 | False positive (Python multiline docstring 인식 미지원) |
| (d) `redfish-gather/library/redfish_gather.py` `_VENDOR_ALIASES` dict | 7 | **디자인 결정 — 동기화 책임 필요** |
| (e) `redfish-gather/library/redfish_gather.py` vendor 분기 코드 | 17 | **검토 필요 — 라이브러리 안 vendor 분기 정합성** |

분류 (a) 제외 후 **남은 33건은 별도 cycle 결정 후보**. 자동 패치 없이 본 보고서 + 사용자 결정 대기.

---

## (a) vendor_aliases.yml — 24건, False positive

위치: `common/vars/vendor_aliases.yml` (lines 18~50, vendor 5종 alias 매핑)

```yaml
dell:
  - "Dell"
  - "Dell Inc."
  ...
hpe:
  - "HPE"
  - "Hewlett Packard Enterprise"
  ...
```

**평가**: rule 12 R1 Allowed 영역 (vendor alias 정규화 메타). 도구가 이 파일을 검사 대상에 포함한 게 문제.

**조치**: cycle-004 W1에서 `verify_vendor_boundary.py`의 `EXCLUDE_PATTERNS`에 `common/vars/vendor_aliases\.yml$` 추가 — false positive 24건 제거 완료.

---

## (b) os-gather/tasks/{linux,windows}/gather_system.yml Jinja2 OEM list — 2건, **경계 위반 의심**

### linux/gather_system.yml:189

```jinja2
{%- set oem_vendors = ['Dell Inc.', 'HPE', 'Hewlett Packard Enterprise', 'Hewlett-Packard', 'HP', 'Lenovo', 'Supermicro', 'Super Micro Computer'] -%}
```

### windows/gather_system.yml:70

```jinja2
{%- set oem_mfrs  = ['Dell Inc.', 'HPE', 'Hewlett Packard Enterprise', 'Lenovo', 'Supermicro'] -%}
```

**평가**: rule 12 R1 위반 가능성. 두 위치 모두 OEM vendor list가 inline 하드코딩. 변경 시 vendor_aliases.yml 변경과 동시 갱신 의무 발생 → drift 위험.

**옵션**:
- (1) **vendor_aliases.yml 참조로 전환** — `_oem_known | flatten | unique` 등으로 alias map에서 추출. 대규모 변경 아님 (Jinja2 단일 라인). 권장.
- (2) **현 상태 유지 + 동기화 주석** — 변경 빈도 낮음 + 기능 정상. 두 위치에 "common/vars/vendor_aliases.yml과 동기화 필수" 주석. 차선.
- (3) **현 상태 유지** — 무시. 비권장 (drift 잠재).

**리스크**:
- 옵션 (1): 영향 vendor (Dell/HPE/Lenovo/Supermicro) baseline 회귀 의무. Linux/Windows OS gather가 inventory hwinfo 정상 동작 확인.
- 옵션 (2): drift는 줄어들지만 잠재 위험 남음.

---

## (c) redfish_gather.py docstring / 주석 — 7건, False positive

위치: `redfish-gather/library/redfish_gather.py:8-11, 21, 194, 747`

```python
"""
Redfish 표준 + OEM 보정으로 hardware info 수집.

Endpoint 매핑:
  HPE iLO 5/6  : Systems/1               / Managers/1   (Oem.Hpe / Oem.Hp fallback)
  Dell iDRAC 9 : Systems/System.Embedded.1 / Managers/iDRAC.Embedded.1  (Oem.Dell)
  ...
"""

short_description: Gather hardware info via Redfish API (Dell/HPE/Lenovo/Supermicro/Cisco)
```

**평가**: Python multiline docstring 안의 vendor 이름 reference. 코드 분기 아님. 도구가 `#`/`//`만 comment로 인식하고 `"""..."""`는 인식 못 함 → false positive.

**조치**:
- (선택) cycle-004 T1-D 도구 정밀화에 추가: Python `"""` triple-quote 블록 안 라인은 skip.
- 또는 명시 `# nosec vendor-boundary` 주석. 비권장 (의도치 않은 silence).

이번 cycle은 보고서까지만. 다음 cycle 또는 별도 P2 작업으로.

---

## (d) redfish_gather.py `_VENDOR_ALIASES` dict — 7건, **디자인 결정**

위치: `redfish-gather/library/redfish_gather.py:103-109`

```python
_VENDOR_ALIASES = {
    'dell': 'dell', 'dell inc.': 'dell',
    'hpe': 'hpe', 'hewlett packard enterprise': 'hpe', 'hp enterprise': 'hpe', 'hp': 'hpe',
    'lenovo': 'lenovo',
    'supermicro': 'supermicro', 'super micro computer, inc.': 'supermicro',
    'super micro computer': 'supermicro',
    'cisco': 'cisco', 'cisco systems inc': 'cisco', 'cisco systems inc.': 'cisco',
    'cisco systems': 'cisco',
}
```

**평가**: `common/vars/vendor_aliases.yml`과 **중복**. Python module은 Ansible runtime context (lookup_plugins) 외에서도 호출 가능 (직접 invoke / pytest)이라 자체 alias dict 보유 — 디자인 의도.

**문제**: 두 source of truth → drift 위험 (vendor_aliases.yml에 alias 추가했는데 redfish_gather.py에 빠지면 redfish 검출 누락).

**옵션**:
- (1) **YAML import** — module load 시 `common/vars/vendor_aliases.yml` 파싱하여 dict 구성. rule 10 R2 stdlib 우선 (`yaml`은 ansible 자체 의존이라 OK). pytest에서도 동작 가능. 권장.
- (2) **동기화 주석 + CI 게이트** — `_VENDOR_ALIASES` 위에 "common/vars/vendor_aliases.yml과 동기화 필수" 주석 + verify_harness_consistency.py에 동기화 검증 추가. 차선.
- (3) **현 상태 유지** — 변경 빈도 낮음 + 영향 적음.

**리스크**:
- (1): 모든 vendor baseline 회귀 의무. Ansible 외부 invoke (pytest) 동작 확인.
- (2): drift는 잠재.
- (3): 신규 vendor 추가 시 두 곳 갱신 필요 (rule 50 R2 9단계에 추가).

---

## (e) redfish_gather.py vendor 분기 코드 — 17건, **검토 필요**

위치: `redfish-gather/library/redfish_gather.py:221-222, 353-394, 415, 446-450, 705-706`

대표:
```python
def _detect_from_product(p: str) -> str | None:
    p = p.lower()
    if 'idrac' in p: return 'dell'
    if 'ilo' in p or 'proliant' in p: return 'hpe'
    if 'xcc' in p or 'thinksystem' in p: return 'lenovo'
    ...

# OEM 추출
if vendor == 'hpe':
    oem = _safe(data, 'Oem', 'Hpe') or _safe(data, 'Oem', 'Hp') or {}
elif vendor == 'dell':
    oem = _safe(data, 'Oem', 'Dell', 'DellSystem') or {}
elif vendor == 'lenovo':
    oem = _safe(data, 'Oem', 'Lenovo') or {}
elif vendor == 'supermicro':
    oem = _safe(data, 'Oem', 'Supermicro') or {}

bmc_names = {'dell': 'iDRAC', 'hpe': 'iLO', 'lenovo': 'XCC', 'supermicro': 'BMC', 'cisco': 'CIMC'}

# Volume boot 추출
'boot_volume': _safe(vdata, 'Oem', 'Dell', 'DellVolume', 'BootVolumeSource')
              if _safe(vdata, 'Oem', 'Dell') else None,
```

**평가**: rule 12 R1상 vendor 분기는 `redfish-gather/tasks/vendors/{vendor}/` 또는 adapter YAML capabilities에만. 그러나 `redfish_gather.py`는 Python 모듈로, OEM 추출 로직이 Redfish API path에 직접 의존 (Oem.Hpe / Oem.Dell / Oem.Lenovo). adapter YAML로 위임하려면:

- adapter YAML의 `capabilities`에 `oem_path` 또는 `oem_extractor` 정의
- Python 모듈은 adapter dict를 받아 generic하게 OEM 추출

**옵션**:
- (1) **현 상태 유지 + adapter YAML metadata에 OEM 매핑 추가** — origin 주석 (rule 96 R1 — T2-A 작업 일환)에서 `oem_path: /redfish/v1/Systems/1/Oem/Hpe` 명시. 라이브러리 분기는 `_VENDOR_ALIASES` 처럼 동기화 주석. **권장 (현실적)**.
- (2) **라이브러리 vendor-agnostic 리팩토링** — `oem_extractor: {dell: 'Oem.Dell.DellSystem', hpe: 'Oem.Hpe', ...}` 같은 매핑을 adapter capabilities에서 받음. 큰 리팩토링 + 모든 vendor baseline 회귀 의무. 별도 cycle.
- (3) **rule 12 R1 예외 명시** — rule 12 R1에 "redfish-gather/library/redfish_gather.py는 OEM 추출 로직 안 vendor 분기 허용" 명시. 차선.

**리스크**:
- (1): 변경 없음, 단 다음 cycle adapter origin 주석에 OEM 매핑 추가 의무.
- (2): 영향 vendor 전부 회귀 (Dell/HPE/Lenovo/Supermicro/Cisco) + Round 11 권장.
- (3): rule 의도 약화.

---

## 사용자 결정 대기 (다음 cycle 후보)

| 항목 | 옵션 | 권장 |
|---|---|---|
| (b) os-gather Jinja2 OEM list | (1) vendor_aliases 참조 / (2) 동기화 주석 / (3) 무시 | (1) — 별도 cycle |
| (c) redfish_gather docstring | 도구 정밀화 (Python `"""` 인식) | T1 (다음 cycle 도구 보강) |
| (d) `_VENDOR_ALIASES` dict 중복 | (1) YAML import / (2) 동기화 주석 + CI / (3) 무시 | (2) — 본 cycle 가능, (1) 별도 cycle |
| (e) vendor 분기 17건 | (1) adapter origin에 OEM 매핑 / (2) 리팩토링 / (3) rule 예외 | (1) — T2-A 일환으로 진행 |

본 cycle (cycle-004)에서는:
- 도구 정밀화 (vendor_aliases EXCLUDE 추가) — **완료**
- 보고서 작성 — **본 문서**
- (b)/(d)/(e) 자동 패치 **없음** (사용자 결정 대기)
- (e) 일부는 T2-A adapter origin 주석에서 OEM 매핑 명시로 자연스럽게 정합 강화

## 적용 rule

- rule 12 R1 (adapter / vendor 경계)
- rule 50 R2 (새 vendor 추가 9단계 — `_VENDOR_ALIASES` 동기화 추가 후보)
- rule 96 R1 (origin 주석 — OEM 매핑 명시)
- rule 25 R7 (실측 검증 — 본 보고서가 실측)

## 결정 요청

본 보고서 검토 후 다음 cycle 또는 다음 PR에서 결정:

1. (b) Jinja2 OEM list 정리 (옵션 1/2/3)
2. (c) 도구 Python docstring 인식 추가 — T1 다음 cycle
3. (d) `_VENDOR_ALIASES` 통합 (옵션 1/2)
4. (e) vendor 분기 17건 처리 (옵션 1/2/3)
