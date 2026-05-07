# Netmask → CIDR Jinja2 namespace fix — 2026-05-07

## 사고 요약

- **위치**:
  - `os-gather/tasks/linux/gather_network.yml:99` (Linux network)
  - `esxi-gather/tasks/normalize_network.yml:67` (ESXi network)
- **사고**: Jinja2 default for-scope 위반 — outer for(octet) 안 `set val = octet|int` + inner for(bit) 안 `set val = val - bit` 가 inner-for 다음 iteration 에 전파 안 됨
- **검출**: cycle 2026-05-07 Phase B `pre_commit_jinja_namespace_check.py` advisory 검출
- **영향**:
  - `/24`, `/16`, `/8`, `/0` 같은 all-FF octet mask: **우연히 정상** (모든 bit 트리거 → 8 bits)
  - `/23`, `/30`, `/22`, `/26` 같은 비표준 mask: **잘못 계산** (비-FF octet 의 모든 bit 트리거 → 8 bits 매번)
- **호출자 영향**: envelope `data.network.interfaces[].addresses[].cidr` 또는 `data.network.interfaces[].prefix` 가 잘못된 값 emit (lab 에서 /24 만 사용해서 표면화 안 됐을 가능성)

## 사고 매트릭스

| Mask | 정답 CIDR | 기존 (broken) | 차이 |
|---|---|---|---|
| 255.255.255.0 | /24 | /24 | 정상 (모든 bit 트리거 우연 일치) |
| 255.255.255.252 | /30 | /32 | -2 |
| 255.255.255.192 | /26 | /32 | -6 |
| 255.255.254.0 | /23 | /24 | -1 |
| 128.0.0.0 | /1 | /8 | -7 |

## Fix

```diff
-{%- set ns = namespace(bits=0) -%}
+{%- set ns = namespace(bits=0, val=0) -%}
 {%- for octet in nm.split('.') -%}
-  {%- set val = octet | int -%}
+  {%- set ns.val = octet | int -%}
   {%- for bit in [128,64,32,16,8,4,2,1] -%}
-    {%- if val >= bit -%}
+    {%- if ns.val >= bit -%}
       {%- set ns.bits = ns.bits + 1 -%}
-      {%- set val = val - bit -%}
+      {%- set ns.val = ns.val - bit -%}
     {%- endif -%}
   {%- endfor -%}
 {%- endfor -%}
```

`val` 을 namespace 에 포함 → inner for 다음 iteration 에 mutation 전파.

## 회귀 차단 (cycle 2026-05-07 신설)

`tests/unit/test_netmask_cidr_jinja_fix.py` (19 PASS):
- `test_fixed_algorithm_correct` × 14 mask: 정답 검증
- `test_broken_algorithm_demonstrates_bug` × 4 mask: 기존 사고 명시 (회귀 차단)
- `test_common_24_works_in_both`: /24 우연 정상 명시 (사고 늦게 발견된 이유)

## Jinja2 namespace hook 결과

- 변경 후: `pre_commit_jinja_namespace_check.py` 의심 0 (gather_network.yml + normalize_network.yml)
- 잔여 의심: `gather_users.yml:77, 212` (별도 evidence — `if` 안 redefinition false-positive)

## 사용자 영향

- `/24` 환경 (lab + 기존 baseline) — 영향 0 (우연 정상)
- 비표준 CIDR (`/23`, `/26`, `/30` 등) 사용 사이트 — envelope `cidr` / `prefix` 정상화
- baseline 회귀: 영향 0 (lab `/24` 만 사용)

## 관련

- rule 22 R7 (Fragment 변수 type / Jinja 안전)
- rule 95 R1 #2 (코드 critical review — set 패턴 회귀)
- 이전 cycle 사고: cycle-015 ESXi vendor 정규화 / cycle-016 Windows runtime swap_total_mb (동일 namespace scoping 회귀 패턴)
- hook: `scripts/ai/hooks/pre_commit_jinja_namespace_check.py` (cycle 2026-05-07 advisory)
- 정본 fix: `os-gather/tasks/linux/gather_network.yml:99` + `esxi-gather/tasks/normalize_network.yml:67`
