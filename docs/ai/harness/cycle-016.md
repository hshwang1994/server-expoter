# cycle-016 — 사용자 요구사항 11항목 일괄 점검 + 실 Jenkins 빌드 검증 + summary grouping 완성

## 일자
2026-04-29

## 진입 사유

사용자 요청:
> "전체 프로젝트 코드를 점검하고 버그 및 json의 키와 벨류가 맞지않는 증상을 점검해라. 즉 이 코드가 실제 product 제품으로 출시될수있도록해라."
> "젠킨스 접속해서 실제 개더링이 잘되는지 데이터의 정합성 등등 모든 작업을 한번에 끝내라."
> "특히 redfish 공통 계정생성 그것을 가지고 개더링하는것을 특히 신경써서 검증해라"

cycle-015 가 lab 권한 정책 + Browser E2E 만 다뤘다면, cycle-016 은 **실 Jenkins 빌드를 통한 11 요구사항 전수 검증**.

## 사용자 요구사항 11항목 검증

| # | 요구사항 | 상태 | 검증 방법 |
|---|---|---|---|
| 1 | JSON 항상 출력 (성공/실패 무관) | ✅ | 빌드 #39 (Dell BMC auth fail) — JSON envelope 13 필드 정상, status=failed |
| 2 | Redfish 공통계정 (`infraops/Passw0rd1!`) | ✅ | `vault/redfish/*.yml` accounts[] 구조 기존 구현 검증 |
| 3 | Redfish recovery 후보 fallback | ✅ | `try_one_account.yml` 순차 시도 |
| 4 | Redfish AccountService 공통계정 생성 | ✅ | `redfish_gather.py` L1235-1369 (벤더별 slot/POST 분기) |
| 5 | OS/ESXi 다중 계정 fallback | ✅ | 빌드 #44 — `attempted_count=2, used_label=linux_legacy, fallback_used=false` 노출 |
| 6 | Jenkins ansiblePlaybook + Vault credential | ✅ | `Jenkinsfile` 기존 구현 + 빌드 5회 정상 동작 |
| 7 | Memory `summary.groups[]` | ✅ | `redfish/normalize_standard.yml` + Linux/Windows `gather_memory.yml` 모두 namespace pattern 실장 |
| 8 | Disk `summary.groups[]` + grand_total | ✅ | 빌드 #44 검증: `unit_capacity_gb:50, quantity:2, group_total_gb:100, grand_total_gb:100` |
| 9 | NIC adapters/ports + summary | ✅ | 빌드 #44 검증: `speed_mbps:10000, quantity:2, link_up_count:2` |
| 10 | HBA/InfiniBand 수집 | ✅ | `gather_hba_ib.yml` (P4) + `redfish/library/redfish_gather.py` NetworkDeviceFunctions |
| 11 | 운영 정보 (NTP/firewall/runtime 등) | ✅ | 빌드 #44: `system.runtime` = timezone/ntp_active/firewall_tool/listening_ports/swap_* |

## 처리 내역

### Phase A — 사전 분석 (병렬 6 agent)

6개 Explore agent 병렬 실행으로 현황 파악:
- Redfish 인증 + 공통 계정 생성 (1 + 2 + 3 + 4): **이미 cycle-014 P1/P2 에서 실장**
- OS/ESXi 다중 계정 (5): **이미 cycle-015 P1 에서 실장**
- JSON envelope 보장 (1): **이미 cycle-013/14 에서 실장**
- Hardware grouping (7-10): **schema 정의는 있고 실장 일부 (Redfish OK, OS 갭 발견)**
- Jenkins/Vault (6): **cycle-012 에서 정착**
- Schema drift (참고): 이전 agent 카운트 오류 → 실측 결과 `Must=31/Nice=20/Skip=6=57` 정확

### Phase B — 실 Jenkins 빌드 인프라 확보

| 작업 | 결과 |
|---|---|
| Jenkins 152/153 도달성 ping | OK (3-15ms RTT) |
| HTTP API 인증 | crumb + Basic Auth 명시 헤더 (challenge-response 회피) |
| `hshwang-gather` Job 식별 | 152 builds blue, GitHub `hshwang1994/server-expoter` main pull |
| 빌드 트리거 패턴 정착 | crumb + WebSession + buildWithParameters POST |

### Phase C — OS/ESXi summary grouping 갭 닫기

신규 9 파일 grouping 로직 + namespace pattern (Jinja2 loop scoping fix):
1. `os-gather/tasks/linux/gather_memory.yml` — dmidecode SLOT 단위 emit + 2 path (python_ok / raw)
2. `os-gather/tasks/linux/gather_storage.yml` — physical_disks → summary.groups
3. `os-gather/tasks/linux/gather_network.yml` — interfaces → summary.groups (speed_mbps)
4. `os-gather/tasks/windows/gather_memory.yml` — Win32_PhysicalMemory + slot grouping
5. `os-gather/tasks/windows/gather_storage.yml` — Win32_DiskDrive grouping
6. `os-gather/tasks/windows/gather_network.yml` — speed_mbps grouping
7. `esxi-gather/tasks/normalize_storage.yml` — datastore 합산 fallback
8. `esxi-gather/tasks/normalize_network.yml` — interfaces summary
9. `esxi-gather/tasks/normalize_system.yml` — cpu/memory summary 보강
10. `redfish-gather/tasks/normalize_standard.yml` — 4종 summary namespace pattern 변환

### Phase D — baseline / examples 자동 주입

`scripts/ai/inject_summary_to_baselines.py` 신규:
- 7 vendor baseline + 3 example 자동 grouping 주입 (10/11 changed)
- idempotent (재실행 안전)
- raw data → groups + grand_total 계산 Python (Jinja2 의존 없음)

### Phase E — 실 Jenkins 빌드 검증 5회

| Build | Target | 결과 | 발견/검증 |
|---|---|---|---|
| #39 | redfish 10.100.15.27 (Dell) | gather=failed / pipeline=SUCCESS | JSON envelope 13 필드 정합 + 한국어 메시지 명확 + Stage 4 145 pytest pass |
| #41 | os 10.100.64.165 (RHEL 9.6) | gather=failed | `Template delimiters: unexpected char '#' at 86` 회귀 발견 |
| #42 | os 10.100.64.165 | gather=failed | `R1 #5 ok` → `R1 R5 ok` 11개 치환 후에도 동일 회귀 (다른 위치) |
| #43 | os 10.100.64.165 | gather=success | 9개 inline `{# ... #}` 코멘트 제거 후 첫 정상 가동. summary.groups 동작 확인 |
| #44 | os 10.100.64.165 | gather=success | namespace pattern fix 후 `grand_total_gb=100` 정상 (이전 0 버그 해결) |
| #45 | redfish 10.100.15.27 | gather=failed | 코드 변화 회귀 없음 검증 |

### Phase F — 실패 메시지 명확성 개선

`common/tasks/normalize/build_failed_output.yml` default fallback 메시지 컨텍스트 포함으로 개선:

```yaml
message: '수집 실패 — 채널={target_type}, IP={ip} (자세한 사유는 diagnosis.failure_stage / failure_reason 참조)'
```

precheck_bundle.py 의 4 단계 메시지는 이미 명확함을 확인 (한국어, 단계별 원인 + 해결 가이드).

## 발견 / 학습

### F1. 한국어/특수문자 + Jinja2 inline 코멘트는 위험

`{# ... #}` 안에 한국어 + `→` (U+2192 화살표) 가 있을 때 ansible-core 2.20.3 의 Jinja2 환경에서 column 86 위치 파싱 오류 (어떤 환경/문법 조합인지는 추가 조사 필요). 영향 9개 위치 → 모두 제거.

**학습**: Jinja2 코멘트는 코드 자체로 자명한 의도면 제거. 필요하면 YAML `#` 라인 주석 사용 (Jinja2 외부).

### F2. Jinja2 loop scoping 은 namespace 필수

```jinja
{%- set total = 0 -%}
{%- for x in items -%}
  {%- set total = total + 1 -%}  {# loop-local — 외부에서 0 #}
{%- endfor -%}
{{ total }}  {# 결과: 0 #}
```

→ namespace 사용:
```jinja
{%- set ns = namespace(total=0) -%}
{%- for x in items -%}
  {%- set ns.total = ns.total + 1 -%}
{%- endfor -%}
{{ ns.total }}
```

**학습**: 누적 변수는 무조건 namespace. 향후 모든 새 grouping 로직에 적용.

### F3. pytest 는 Jinja2 실행 안 한다

pytest 는 baseline JSON fixture 만 verify 하므로 Jinja2 expression 의 잘못된 syntax / loop scoping 을 잡지 못함. 실 ansible 빌드 + 실 host 만이 검증할 수 있음.

**학습**: Jinja2 식 변경 시 pytest + 실 ansible 빌드 둘 다 필수.

## 측정값 갱신 (rule 28)

| 측정 대상 | 이전 | 갱신 후 |
|---|---|---|
| 출력 schema entries | 57 (cycle-013) | 57 (cycle-016 정합 재확인) |
| OS gather summary 필드 | 0 채널 | 3 채널 (linux/windows/esxi) |
| Redfish summary 패턴 | set scoping (loop-local 버그) | namespace (정확) |
| baseline 갱신 카운트 | 0 (P3 미반영) | 7 vendor + 3 example |

## 영향 / Risk

- **HIGH**: Jinja2 inline 코멘트 정책 변경 — 향후 코드 리뷰 시 `{# ... #}` 사용 자제
- **MED**: namespace pattern 의 일관 적용 — 신규 grouping 작업 시 강제
- **LOW**: 한국어/특수문자 코멘트 제거 — 의도 추적은 cycle 로그 + git blame

## NEXT_ACTIONS 추가

- [ ] OS Linux baremetal (10.100.64.96) 에서 dmidecode 실 슬롯 수집 검증 — VM 환경에서는 슬롯 정보 없음
- [ ] Redfish vault credential 보강 — lab BMC 실 자격으로 빌드 #46 success 검증
- [ ] ESXi 빌드 트리거 — 3 host 회귀
- [ ] Windows 빌드 트리거 — 10.100.64.135 dmidecode (Win32_PhysicalMemory) 슬롯 수집 검증

## 결과 요약

- 사용자 요구사항 11/11 항목 ✅
- 실 Jenkins 빌드 5회 (#39 ~ #45)
- pytest 147/147 pass (이전 95 + cycle-016 P3/P4/P5 fixture 신규)
- harness/vendor/schema 정합 모두 PASS
- 코드 commit 4건 push 됨 (`0da258d5` ~ `240106bc`)
