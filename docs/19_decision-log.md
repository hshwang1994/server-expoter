# 의사결정 로그

> **이 문서는** server-exporter 가 지금 모습이 된 "이유" 를 누적 기록한 결정 이력이다.
> 누군가 "왜 이렇게 만들었는지" 또는 "전에 다른 방식으로 한 적 있는지" 가 궁금할 때 가장 먼저 검색하는 곳이다.
>
> 검증 라운드(Round) 결과, 사용자 의심 분석, 정책 변경 같은 큰 결정은 모두 이 문서에 시간순으로 추가된다.
> 코드만 읽고는 알 수 없는 맥락(왜 이 fallback 이 있는지 등)이 여기 있다.

> 최종 갱신: 2026-05-07

## 2026-05-07 — schema/output_examples/ 신설 + baseline_v1 annotated 정리 (실 장비 개더링)

### 컨텍스트

사용자 (hshwang1994) 명시 (2026-05-07):

> "실제 개더링할수있는 장비를 대상으로 개더링하고 그 값을 대상으로 json출력 예시를 업데이트해라. 만약 schema/baseline_v1이 json출력예시 디렉터리가 아니라면 별도로 디렉터리를 만들고 schema/baseline_v1에 생성한 파일은 지워라. 만약 의도가맞다면 업데이트만 해라. 그리고 한글로 할때 모든 json 키값에대한 설명을 주석으로 달아라."

직전 cycle 2026-05-06 b65e162e 가 baseline_v1 안에 한글 주석본 8개 (`*_annotated.jsonc`) 를 추가했으나, baseline_v1 정본 의도 (회귀 기준선 — Jenkins Stage 4 pytest 입력) 와 충돌. 사용자가 위치 부적합 지적.

### 결정

**A. baseline_v1 != 출력 예시 → 신규 디렉터리** `schema/output_examples/` 신설.

**B. 자격증명** — vault 사용 + 평문 노출 OK (사용자 명시 "기존 볼트를 사용하고, 그것이 평문에 담겨도된다").

**C. 실행 위치** — Jenkins 에이전트 10.100.64.155 SSH 접속 후 직접 ansible-playbook 실행. 결과 rsync 회수.

**D. 디렉터리 분류**:

| 디렉터리 | 정본 의도 | 누가 사용 |
|---|---|---|
| `schema/baseline_v1/` | **회귀 기준선** (Jenkins Stage 4 pytest 입력) | 자동화 회귀 |
| `schema/output_examples/` (신설) | **호출자 / 운영자 reference** — 한글 주석 + 실 응답 | 사람 |
| `schema/examples/` | 시나리오 별 예시 (success/partial/failed/not_supported) | 호출자 (시나리오 설명) |

### 산출물

- 신설: `schema/output_examples/{README.md, 10 jsonc 파일}`
- 삭제: `schema/baseline_v1/*_annotated.jsonc` 8개 (사용자 명시)
- 보존: baseline_v1 *_baseline.json 8개 / examples *.json 4개 / sections.yml / field_dictionary.yml

### 검증

- pytest 335/335 PASS / verify_harness PASS / verify_vendor_boundary PASS
- envelope 13 필드 / sections 10 / field_dictionary 65 — 변경 없음 (rule 13 R5 / rule 96 R1-B Additive only)
- 호출자 시스템 파싱 변경 0

### Evidence

- `tests/evidence/2026-05-07-real-gather.md` (실행 절차 + 발견 사항 + 호출자 영향)

### 후속

- 펌웨어 / 환경 변경 시 본 디렉터리 재 캡처 — `update-vendor-baseline` skill 또는 직접 갱신
- 6개월 갱신 0건 시 stale 가능 — `EXTERNAL_CONTRACTS.md` 동기화 권장

---

## 2026-05-06 (cycle 2026-05-06-multi-session-compatibility) — status 의도 결정 (Case A 채택)

### 컨텍스트

사용자 (hshwang1994) 의심 영역 (cycle 진입 시점 명시):

> "스키마 검증 들어가자. 모든 값에 대한 스키마 검증해주되 특히 자세히 봐야할것은 개더링상태가 success failed partial 이렇게 3개로 나눠져있는것으로 보이는데, 이게 로직이 정상작동돼지않는듯함. 부분 성공이라고 하더라도 error 에는 로그가 찍히는데 success로 빠지는경우가 있음 이것은 왜이런지 확인해줘 의도된건지?"

→ M-A1 [DONE] (commit `ba003b2f`) 분석 결과: 시나리오 B (섹션 success + errors warning → overall=success) 는 **명백한 의도된 동작**. 코드 주석 3 위치가 명시:
- `os-gather/tasks/linux/gather_memory.yml:171-172` (dmidecode fallback 사유 추적)
- `os-gather/tasks/linux/gather_network.yml:208` (lspci stderr 권한 부족 추적)
- `esxi-gather/tasks/normalize_storage.yml:79-80` (NFS/vSAN/vVOL cap 미수집 추적)

build_status.yml 판정 로직 (정본 인라인 Jinja2): **errors[] 는 보지 않는다 / 섹션 status 만 본다**. errors[] 는 사유 추적용 분리 영역.

### 결정 (4 포인트)

AI 자율 진행 권한 적용 (cycle 진입 시 사용자 명시 — "사용자 결정 4 포인트도 AI 합리적 default 결정 후 진행"):

| 결정 | 선택 | 근거 |
|---|---|---|
| (1) 시나리오 B 처리 | **B-1 (현재 동작 유지)** | M-A1 분석 — 의도된 설계 + Additive only cycle + rule 96 R1-B (envelope shape 보존) |
| (2) errors[] severity | **(a) 유지** | rule 22 R7/R8 + rule 13 R5 + 3채널 27+ 위치 영향 → 별도 cycle 영역 |
| (3) status_rules.yml | **(c) 유지** | DEAD CODE 명시 주석 "삭제 금지 / 향후 reserved" + rule 70 R5 보존 판정 YES |
| (4) status enum | **(a) 3 enum 유지** | rule 13 R5 envelope 13 필드 정본 + rule 96 R1-B (호환성 외 schema 확장 별도 cycle) |

→ **Case A 채택** — 의도된 동작 명시 only (Additive 주석/문서 강화).

### 영향

- 코드 동작 변경: **0건**
- envelope 13 필드: **변경 0** (rule 13 R5 / 96 R1-B 보존)
- status enum: **3종 유지** (success / partial / failed)
- 9 vendor baseline 회귀: **영향 0**
- 호출자 시스템 파싱: **영향 0**
- ADR (rule 70 R8 trigger): **NO** — rule 본문 변경 없음, 표면 카운트 변동 없음 → M-A4 SKIP 가능

### M-A3 작업 (다음 세션)

1. `common/tasks/normalize/build_status.yml` 헤더 주석 강화 — 시나리오 B 의도 명시 + errors[] 분리 의미 명문화 + 코드 주석 3 reference
2. `status_rules.yml` 변경 0 (DEAD CODE 명시 주석 reference 확인만)
3. mock fixture 1건 신규 — 시나리오 B 재현 (`status_success_with_warnings.json`)
4. pytest 회귀 + verify_harness_consistency PASS 확인
5. M-F1 (docs/20_json-schema-fields.md 신설 시) status 판정 규칙 절 포함 의무 — DEPENDENCIES 갱신

### 대안 비교 (Considered)

- **Case B (B-2 + ?)**: errors non-empty → overall=partial. 거절 이유: 모든 vendor baseline 회귀 fail (success → partial 전환), 호출자 partial 대응 로직 추가 필요, rule 96 R1-B 호환성 외 영역
- **Case C (B-3 + (b) + (b))**: 4 enum + severity 도입. 거절 이유: envelope schema 변경 (rule 13 R5 + 92 R5 사용자 명시 승인 필요), 3채널 27+ 위치 영향, 본 cycle Additive only 영역 외 — 별도 cycle 사용자 명시 승인 후 진행 영역

### rule / 정본 참조

- rule 13 R5 (envelope 13 필드 — status 필드 정본 보존)
- rule 22 R7/R8 (Fragment 5 변수 / 타입 정본 — 변경 안 함)
- rule 70 R5 (문서 보존 판정 — status_rules.yml 유지)
- rule 70 R8 (ADR trigger — Case A 는 NO → M-A4 SKIP)
- rule 92 R2 (Additive only)
- rule 92 R5 (schema 변경 사용자 명시 — Case C 거절 이유)
- rule 96 R1-B (호환성 cycle 외 envelope shape 변경 자제)
- ticket: `docs/ai/tickets/2026-05-06-multi-session-compatibility/fixes/M-A1.md`, `M-A2.md`, `M-A3.md`

---

## 2026-05-01 (cycle-019) — 신규 vendor 4종 도입 (Huawei / Inspur / Fujitsu / Quanta)

### 컨텍스트
사용자 (hshwang1994) 명시:
1. 2026-05-01 1차: "신규 장비 도입할 의향이 있다 다만 테스트할 lab 장비가 없다. 일단 vault는 만들지 말고 코드 생성에 대한 티켓은 만들어라"
2. 2026-05-01 2차 (본 cycle): "신규 밴더 추가 승인하겠다"

cycle-019 본 cycle 에서 7-loop + 10R extended audit P1 22건 적용 후, 사용자 명시 승인으로 신규 vendor 4종 진행.

### 결정
4 vendor adapter 코드 영역 진행. **vault 단계 SKIP** (lab 부재 — 사용자 명시 1차).

### 적용 범위 (rule 50 R2 9단계 매핑)

| 단계 | 작업 | 상태 |
|---|---|---|
| 1. vendor_aliases.yml 매핑 | 4 vendor alias 추가 | ✅ |
| 2. adapter YAML 생성 | huawei_ibmc / inspur_isbmc / fujitsu_irmc / quanta_qct_bmc | ✅ |
| 3. (선택) OEM tasks | 부재 (standard_only — 사이트 fixture 확보 후 보강) | DEFER |
| 4. vault 생성 | vault/redfish/{vendor}.yml | **SKIP (사용자 명시)** |
| 5. baseline | schema/baseline_v1/{vendor}_baseline.json | DEFER (lab 부재) |
| 6. ai-context | .claude/ai-context/vendors/{vendor}.md 4종 | ✅ |
| 7. vendor-boundary-map.yaml | huawei/inspur/fujitsu/quanta 추가 | ✅ |
| 8. live-validation | docs/13_redfish-live-validation.md Round 갱신 | DEFER (lab 부재) |
| 9. decision-log | 본 entry | ✅ |

### redfish_gather.py 동기화

`_FALLBACK_VENDOR_MAP` + `_BMC_PRODUCT_HINTS` + `bmc_names` dict 모두 4 vendor 추가 (rule 12 R1 nosec 주석 보존).

- `_FALLBACK_VENDOR_MAP`: 11 신 entry (huawei/inspur/fujitsu/quanta 변형 alias)
- `_BMC_PRODUCT_HINTS`: 7 신 entry (ibmc/fusionserver/isbmc/irmc/primergy/quantagrid/quantaplex)
- `bmc_names`: 4 신 entry (huawei→iBMC, inspur→ISBMC, fujitsu→iRMC, quanta→BMC)

### 영향
- adapter 표면: 34 → 38 (Redfish 23 → 27)
- vendor 정규화 list: 5 → 9
- vault 신규: 0 (사용자 명시 SKIP)
- baseline 신규: 0 (lab 부재)
- 운영 가능 시점: lab 또는 사이트 장비 도입 + vault 생성 시

### 부재 시 동작 (graceful degradation)

- ServiceRoot 무인증 detect → vendor=huawei/inspur/fujitsu/quanta 정규화 OK
- vault 부재 → precheck auth 단계에서 status=failed (rule 27 R4 graceful)
- 호출자 envelope: status=failed + errors[] = ["vault not found for vendor=<huawei|inspur|fujitsu|quanta>"]

### 사이트 도입 시 절차

1. `vault/redfish/{vendor}.yml` 생성 (ansible-vault encrypt + username/password)
2. `tests/redfish-probe/probe_redfish.py --vendor {vendor}` 실행
3. `schema/baseline_v1/{vendor}_baseline.json` 생성
4. `tests/evidence/<날짜>-{vendor}.md` Round 검증 기록
5. `docs/13_redfish-live-validation.md` Round 갱신
6. `capture-site-fixture` skill 으로 사이트 fixture 캡처

### rule / 정본 참조

- rule 50 R2 (vendor 추가 9단계, vault SKIP 사용자 명시 적용)
- rule 96 R1-A (lab 부재 — web sources 4종 1개 이상 — 4 ticket 모두 충족)
- rule 12 R1 (vendor 경계 — _FALLBACK_VENDOR_MAP 등 nosec 보존)
- rule 92 R5 (사용자 명시 승인 — 본 entry 가 승인 trace)
- ticket: `docs/ai/tickets/2026-05-01-gather-coverage/fixes/F44~F47.md`

---

## Round 12 (2026-04-29) — ESXi 채널 hostname / vendor / extended modules fix

### 배경
사용자 보고: ESXi 출력 JSON 에서 `hostname=IP`, `vendor` 정규화 실패, `network.adapters / virtual_switches / storage.hbas` 빈 배열.

### 진단
agent 10.100.64.154 SSH + 진단 playbook (`tests/scripts/diag_esxi_raw.yml`) 으로 raw facts 캡처.

| BUG | 원인 |
|---|---|
| #1 hostname=IP | `normalize_system.yml` 의 `system.fqdn = _e_ip` (ansible_hostname 미사용) |
| #2 vendor 정규화 | Jinja2 loop scoping — cycle-016 namespace fix 잔류분 |
| #4 extended 빈 | `community.vmware 6.2.0` hosts_*_info dict key 는 hostname (IP 아님). dict list 는 `vmnic_details`/`vmhba_details` (`all` 은 string list). 매핑 키 정정: pci→location, adapter_type→type, node_wwn 등. vswitch 는 dict-of-dict |

### Fix
- `esxi-gather/site.yml` (+11 lines) — `_e_hostname` 변수 + namespace pattern
- `esxi-gather/tasks/normalize_system.yml` (+3 lines)
- `esxi-gather/tasks/collect_network_extended.yml` (+30 lines)
- `schema/baseline_v1/esxi_baseline.json` (+231 / -47, esxi02 실측 갱신)

### 검증
- 실 호스트 esxi01 + esxi02 (10.100.64.1 / .2) 본 site.yml 실행 — NIC/vSwitch/HBA 모두 정상 채워짐
- pytest 158/158 PASS, vendor boundary / harness consistency / ansible-syntax-check 통과
- evidence: `tests/evidence/2026-04-29-esxi-bug-fix.md`

### 잔류 (별도 cycle)
- `default_gateways=[]` / `dns_servers=[]` — vmware_host_facts 미반환 / host_config_info 빈 응답 (vmware_host_dns_info 모듈 추가 필요)
- `speed_mbps` int / "N/A" string 혼재
- `cpu.architecture` / `max_speed_mhz` null (model 파싱 폴백 가능)
- `include_vars` `name:` reserved-name 경고 (호출자 영향 0)

---



## 1. 코드 점검 1차/2차 결과 요약

### 1차 점검 (이전 세션)
- 전체 프로젝트 구조 분석
- 보안 이슈 (no_log 누락) 식별
- 기본 코드 품질 이슈 도출

### 2차 점검 (4 배치 완료)
- **Batch 1 (P0)**: power section 추가, hostname fallback 개선, int coercion regex 수정, vault 경고
- **Batch 2 (P1)**: OUTPUT default 방어, 에러 메시지 개선, no_log 정리
- **Batch 3 (P2)**: bare except → specific exceptions, no_log 제거, hostname None-safety
- **Batch 4 (P3)**: CALLBACK_NEEDS_WHITELIST → CALLBACK_NEEDS_ENABLED

총 19개 파일, ~50개 변경사항 — 모두 검증 완료.

## 2. Redfish Endpoint 선택 근거

### 코드가 호출하는 14개 엔드포인트

| # | 엔드포인트 | 선택 근거 |
|---|-----------|----------|
| 1 | Service Root | DMTF 필수. 벤더 감지 + 컬렉션 URI 확보 |
| 2 | Systems 컬렉션 | system_uri 동적 취득 |
| 3 | Systems/{id} | 서버 기본 정보 (model, serial, CPU/메모리 요약) |
| 4 | Managers/{id} | BMC 정보 (firmware version) |
| 5 | Processors 컬렉션 | CPU 상세 (모델, 코어, 스레드) |
| 6 | Processors/{pid} | 개별 CPU 정보 |
| 7 | Memory 컬렉션 | DIMM 목록 |
| 8 | Memory/{mid} | 개별 DIMM 정보 |
| 9 | Storage 컬렉션 | 스토리지 컨트롤러/드라이브 |
| 10 | Storage/{sid} | 컨트롤러 상세 + 드라이브 링크 |
| 11 | SimpleStorage (fallback) | Storage 미지원 구형 BMC 호환 |
| 12 | EthernetInterfaces 컬렉션 + 개별 | 호스트 NIC 정보 |
| 13 | FirmwareInventory 컬렉션 + 개별 | 전체 펌웨어 목록 |
| 14 | Chassis/{id}/Power | PSU 정보 |

### 미포함 엔드포인트와 제외 근거

| 엔드포인트 | 제외 근거 |
|-----------|----------|
| Chassis/{id}/Thermal | 온도/팬 정보 — 판정 시점에 normalize 스키마 미정의. 향후 추가 고려 |
| Managers/{id}/EthernetInterfaces | BMC NIC — system 레벨로 충분 |
| Bios | BIOS 설정 — BiosVersion은 System에서 이미 취득 |
| LogServices | 이벤트 로그 — 수집 범위 초과 |
| NetworkInterfaces | NIC 상세 — EthernetInterfaces로 충분 |

## 3. Adapter 설계 근거

### 왜 adapter 시스템을 사용하는가
1. **벤더별 normalize 차이**: 같은 Redfish 표준이라도 필드 존재 여부가 다름
2. **세대별 차이**: 같은 벤더라도 BMC 세대에 따라 스키마 다름 (예: HPE iLO5 vs iLO6)
3. **확장성**: 새 벤더/세대 추가 시 adapter YAML만 추가하면 됨
4. **테스트 용이**: adapter 단위로 fixture 테스트 가능

### Adapter 선택 알고리즘
- `adapter_loader.py`가 `adapters/redfish/` 디렉토리 스캔
- `match` 조건 (vendor, model_pattern 등) 비교
- 복수 매칭 시 `priority` + `specificity` 점수로 정렬
- 최고 점수 adapter 반환

## 4. Normalize 정책 근거

### null 허용 정책
실장비 검증 결과, 벤더마다 누락 필드가 다름:
- HPE: IndicatorLED, SpeedMbps, LinkStatus, ProcessorSummary.Status.Health
- Lenovo: Manager.Status.Health
- Dell: Drive.Status.Health

→ **정책**: 코드가 추출하는 모든 필드는 `_safe()` 함수로 None 반환 허용.
normalize에서 `| default(none)` 처리.

### 빈 문자열 처리
- HPE HostName = "" (빈 문자열) → normalize에서 `or _out_ip` fallback 필요
- build_output.yml에서 처리 (2차 점검에서 수정 완료)

### Storage Controllers fallback
- 판정 시점: `StorageControllers` 인라인 배열만 처리
- HPE Gen11: `Controllers` 서브링크 사용 → **fallback 추가 필요** (P0-1에서 구현 완료, 8절 참조)

## 5. 실장비 검증으로 확정된 사항

| 항목 | 결정 | 근거 |
|------|------|------|
| vendor 감지 기준 | System.Manufacturer | 3사 모두 동작 확인 |
| URI 패턴 | 동적 (Members[0]) | 벤더마다 다른 ID 패턴 |
| Storage fallback | Storage 우선, SimpleStorage fallback | Lenovo/HPE는 SimpleStorage 404 |
| Basic Auth | 유지 | 3사 모두 동작 |
| Thermal 수집 | 보류 | endpoint 존재하나 normalize 스키마 미정의 |
| default_gateways | Redfish 불가 | OS 레벨 정보 — os-gather에서 수집 |

## 6. 실장비 검증으로 추정에 머무는 사항

| 항목 | 추정 내용 | 불확실 요인 |
|------|----------|------------|
| 다른 세대 URI 패턴 | 동일할 것으로 추정 | Gen10, R640 등 미검증 |
| Supermicro 호환 | 코드에 Supermicro 분기 있으나 미검증 | 장비 부재 |
| Session Auth | 동작할 것으로 추정 | Basic만 테스트 |
| HPE iLO5 차이 | iLO6과 유사할 것으로 추정 | Oem.Hpe vs Oem.Hp fallback 미검증 |
| 다중 System member | Members[0]만 사용 | 블레이드 서버 등 미검증 |

## 7. OEM 필드 보강 판정 (B2, Round 14)

> 판정일: 2026-03-25

### 결론

**판정 시점의 수집 범위에서는 Standard Redfish로 대응 가능하다.** OEM placeholder는 향후 운영 요구 발생 시 확장한다.

수집 범위(firmware inventory + PSU health/state/metrics) 기준으로, 아래 근거 표의 모든 영역에서 standard endpoint만으로 필요 데이터를 확보할 수 있었다. OEM 추가 가치가 낮다고 판단한 근거는 아래 표 참조.

### 근거

| 영역 | Standard 수집 현황 | OEM 추가 가치 |
|------|-------------------|---------------|
| Firmware | FirmwareInventory 28+ 항목 (BIOS, BMC, RAID, NIC, PSU FW) | OEM-specific metadata (낮음) |
| Power | PSU health/state/metrics + power_control consumed watts | PSU redundancy N+1, line voltage (낮음) |
| 기타 | — | Thermal throttle history, license/warranty (범위 외) |

### OEM Framework 상태

- 4개 벤더(Dell/HPE/Lenovo/Supermicro) adapter YAML에 `oem_tasks` 경로 정의 완료
- `collect_oem.yml` / `normalize_oem.yml` placeholder 파일 존재
- **운영 요구 발생 시 placeholder만 채우면 즉시 확장 가능**

### 향후 확장 트리거

OEM 구현을 재검토해야 하는 상황:
1. 포털에서 PSU redundancy status(N+1) 표시 요구 발생
2. 벤더별 OEM-specific health code 해석 요구
3. Thermal 섹션 스키마 정의 및 수집 요구
4. 특정 벤더에서 standard endpoint로 수집 불가능한 필드 발견

## 8. 리팩토링 이력 (실장비 검증 기반, 2026-03-18)

### 완료 (P0/P1)

| 항목 | 파일 | 내용 |
|------|------|------|
| P0-1 | `redfish_gather.py` | HPE Storage Controllers fallback (Controllers 서브링크 드릴다운) |
| P0-2 | `redfish_gather.py` | gather_power() ServiceRoot 중복 호출 제거 (chassis_uri 직접 전달) |
| P0-3 | `hpe_ilo6.yml` | HPE iLO 6 전용 adapter 신규 생성 |
| P1-3 | `redfish_gather.py` | 벤더별 null 필드 경고 로깅 |
| P1-4 | `redfish_gather.py` | HostName 빈 문자열 → None 변환 |
| P1-7 | `redfish_gather.py` | MemorySummary Health → HealthRollup fallback |
| P1-7-2 | `redfish_gather.py` | IndicatorLED → LocationIndicatorActive fallback |

### 보류 (P1-P2)

| 항목 | 사유 |
|------|------|
| 단위 변환 헬퍼 통일 | 검증 시점에 코드 동작 확인됨, 우선순위 낮음 |
| Thermal 수집 추가 | normalize 스키마 미정의, 향후 요구 시 구현 |
| Supermicro/다중 System member/Session Auth/iLO5 차이 | 실장비 미보유로 검증 불가, 장비 확보 시 재검토 |

## 9. Linux Raw Fallback Round 2 검증 (2026-04-15)

### 배경

Round 1에서 Linux 2-Tier Gather (Python 감지 + Raw Fallback) 기본 구현을 완료했다. Round 2에서는 5대 서버에 대해 31개 필드 전수 비교 검증을 수행했다.

### SELinux 정규화 버그 수정

`gather_system.yml`의 raw 경로에서 `getenforce` 출력값(`Enforcing`/`Permissive`/`Disabled`)을 Ansible 컨벤션(`enabled`/`disabled`)으로 정규화하지 않는 버그를 발견하고 수정했다.

- **수정 전**: `getenforce` 출력 그대로 반환 (예: `Enforcing`)
- **수정 후**: `Enforcing`/`Permissive` → `enabled`, `Disabled` → `disabled`로 정규화

### 5대 서버 필드 전수 비교 결과

| 서버 | OS | Python | 감지 모드 | 결과 | 비고 |
|------|-----|--------|----------|------|------|
| RHEL 8.10 | RHEL 8.10 | 3.6.8 | `python_incompatible` (자동) | 31/31 MATCH | auto fallback과 forced raw 간 완전 일치 |
| RHEL 9.2 | RHEL 9.2 | 3.9+ | `python_ok` | memory 차이만 | raw 경로가 더 정밀 (아래 분석 참조) |
| RHEL 9.6 | RHEL 9.6 | 3.9+ | `python_ok` | memory 차이만 | 동일 |
| Rocky 9.6 | Rocky 9.6 | 3.9+ | `python_ok` | memory 차이만 | 동일 |
| Ubuntu 24.04 | Ubuntu 24.04 | 3.9+ | `python_ok` | selinux 1건 차이 | 허용 범위 (아래 분석 참조) |

### Memory 차이 분석 (버그 아님)

RHEL 9.x / Rocky 9.6에서 Python 경로와 raw 경로 간 memory 값 차이가 발생한다. 이는 **버그가 아니라 raw 경로가 더 정확**한 결과이다.

| 경로 | 수집 방식 | 값 (예시) | 의미 |
|------|----------|----------|------|
| Python 경로 | `ansible_memtotal_mb` (OS 보고) | 7680 MB | 커널 예약 후 OS 가시 메모리 (`os_visible`) |
| Raw 경로 | `dmidecode --type 17` (하드웨어 직접) | 8192 MB | 물리 장착 메모리 (`physical_installed`) |

→ raw 경로의 dmidecode 기반 수집이 실제 물리 메모리를 반환하므로 하드웨어 인벤토리 용도에 더 적합하다.

### Ubuntu SELinux 차이 (허용)

Ubuntu 24.04에서 `selinux` 필드 차이 1건 발생:
- Python 경로: `disabled` (Ansible이 SELinux 미설치를 disabled로 보고)
- Raw 경로: `null` (`getenforce` 명령 미설치)

→ Ubuntu는 SELinux를 기본 탑재하지 않으므로 `null` 반환이 의미적으로 정확하다. 허용 범위로 판정.

### 결론

5대 서버, 31개 필드 전수 검증 완료. Raw fallback은 Python 경로와 동등하거나 더 정밀한 결과를 제공한다. 프로덕션 적용 가능.

## 10. Network 심층 검증 (Round 3, 2026-04-15)

### 배경

Round 2 이후 Network 섹션에 대해 심층 검증을 수행했다. 가상 인터페이스 skip 패턴 확장, 다중 default route 동작 확인, primary 판단 규칙 명확화가 주요 내용이다.

### skip 패턴 확장

기존 skip 패턴(`lo`, `docker*`, `br-*`, `veth*`, `virbr*`, `vir*`)에 아래 패턴을 추가했다:

| 추가 패턴 | 대상 | 추가 근거 |
|----------|------|----------|
| `cni*` | Kubernetes CNI 인터페이스 | K8s 노드에서 불필요한 가상 인터페이스 수집 방지 |
| `flannel*` | Flannel CNI overlay | 동일 |
| `cali*` | Calico CNI | 동일 |
| `tunl*` | tunnel 인터페이스 | IPIP 터널 등 가상 인터페이스 제외 |
| `dummy*` | dummy 인터페이스 | 테스트/라우팅 용도 가상 인터페이스 제외 |
| `kube-*` | Kubernetes internal | kube-proxy 등 내부 인터페이스 제외 |

**주의**: `br0`, `bond0`, `team0`, `eth0.100`(VLAN) 등 실 네트워크 인터페이스는 skip 대상이 아니다.

### 5대 서버 다중 default route 동작 확인

5대 서버(RHEL 8.10, RHEL 9.2, RHEL 9.6, Rocky 9.6, Ubuntu 24.04)에서 다중 default route가 존재하는 경우 metric 기준 정렬 후 첫 번째만 사용하는 동작을 확인했다. Python 경로(`ansible_default_ipv4`)와 raw 경로(`ip route show default | head -1`) 모두 동일한 결과를 반환한다.

### primary 판단 규칙 명확화

| 결정 | 내용 |
|------|------|
| primary 정의 | IPv4 default route가 걸린 인터페이스 = primary |
| bond master | default route가 bond master에 걸리면 bond master가 primary |
| bridge | default route가 bridge에 걸리면 bridge가 primary |
| slave/port | IP가 없으므로 primary 불가 |
| 다중 default route | lowest metric wins (첫 번째만 사용) |

### 결론

Network 수집 정책을 GUIDE_FOR_AI.md에 문서화 완료. skip 패턴 확장으로 Kubernetes/tunnel/dummy 가상 인터페이스를 추가 제외하고, primary 판단 규칙과 다중 default route 처리를 명확화했다.

## 11. Network 복잡 토폴로지 실증 (Round 4, 2026-04-15)

### 배경

Round 3에서 skip 패턴을 확장하고 primary 판단 규칙을 명확화했다. Round 4에서는 Ubuntu 24.04에 복잡 네트워크 토폴로지를 실제 구성하여 수집 정확성을 실증했다.

### 실증 환경

Ubuntu 24.04 (10.100.64.167)에 아래 토폴로지를 구성:

| 인터페이스 | 유형 | 역할 |
|-----------|------|------|
| ens192 | 물리 NIC | primary (default route dev) |
| ens224 | 물리 NIC | 보조 NIC |
| br0 | bridge | dummy0를 slave로 포함 |
| ens192.100 | VLAN | ens192 위 VLAN 서브인터페이스 |
| dummy0 | dummy (bridge slave) | br0의 port (slave) |
| cni0 | container NIC | Kubernetes CNI |
| flannel.1 | container NIC | Flannel overlay |
| docker0_test | container NIC | Docker 테스트 bridge |
| policy routing | table 100 | `ip rule` + `ip route table 100` |

### 발견된 문제

skip 패턴(`dummy*`)이 배포 시점에 반영되지 않아 cni0, flannel.1은 skip되지 않았다 (배포 이슈). 이와 별개로, **dummy0가 bridge port(slave)임에도 수집되는 문제**를 발견했다. dummy0는 br0의 하위 포트이므로 독립 인터페이스로 수집하면 안 된다.

### 수정 내용

raw path에 bridge slave / bond slave 자동 필터를 추가했다:

- `/sys/class/net/$dev/master`가 존재하는지 확인 (slave 여부)
- slave이면서 자신이 bridge master(`/sys/class/net/$dev/bridge/` 존재)도 아니고 bond master(`/sys/class/net/$dev/bonding/` 존재)도 아닌 경우 → skip
- bridge master나 bond master는 slave이더라도 수집 (중첩 구성 대응)

### 수집 결과 비교

| 구분 | 수집된 인터페이스 | 개수 |
|------|-----------------|------|
| 수정 전 | ens192, ens224, br0, ens192.100, dummy0, cni0, flannel.1 | 7개 |
| 수정 후 | ens192, ens224, br0, ens192.100 | 4개 |

### 인터페이스별 검증

| 인터페이스 | primary | speed | IP 수집 | 판정 |
|-----------|---------|-------|--------|------|
| ens192 | true (default route dev) | 10000 | O | 정확 |
| ens224 | false | 10000 | O | 정확 |
| br0 | false | null (가상) | O | 정확 |
| ens192.100 | false | 10000 (부모 상속) | O | 정확 |
| dummy0 | — | — | — | skip (bridge slave) = 정확 |
| cni0 | — | — | — | skip (가상 NIC) = 정확 |
| flannel.1 | — | — | — | skip (가상 NIC) = 정확 |
| docker0_test | — | — | — | skip (가상 NIC) = 정확 |

### 결론

복잡 토폴로지(bridge + VLAN + container NIC + policy routing)에서 수집 정확성을 실증했다. bridge slave/bond slave 자동 필터 추가로 불필요한 하위 포트 수집이 제거되었다. 4개 인터페이스만 정확히 수집되며, primary 판단도 정확하다.

## 12. Network 운영 해석 기준 확정 + bond 실증 (Round 5, 2026-04-15)

### 배경

Round 4까지 skip 패턴, primary 판단, bridge slave 필터를 검증했다. Round 5에서는 5대 서버 명령어 존재성 매트릭스 실측과 bond 토폴로지 실증을 수행하여 운영 해석 기준을 확정했다.

### 명령어 존재성 매트릭스 실측

15개 명령 x 5대 서버(RHEL 8.10, RHEL 9.2, RHEL 9.6, Rocky 9.6, Ubuntu 24.04)에 대해 명령어 존재 여부를 실측했다.

핵심 발견:
- RHEL 9는 `resolvectl` 미설치 (systemd-resolved 패키지 미포함)
- Ubuntu는 `nmcli` 미설치 (NetworkManager 미사용)
- `ip`, `getent`, `/sys/class/net`, `/proc/*`, `/etc/os-release`는 모든 배포판에서 보장

→ 배포판 무관 소스(`ip`, sysfs, `/proc`, `/etc`) 사용 전략의 정당성을 실측으로 확인했다.

### bond 실증

Ubuntu 24.04에 bond 토폴로지를 구성하여 수집 정확성을 실증했다:

| 구성 | 내용 |
|------|------|
| bond0 | active-backup 모드, 2개 dummy slave |
| bond0.200 | VLAN-on-bond (bond0 위 VLAN 서브인터페이스) |
| br_test | bridge (테스트용) |

검증 결과:

| 항목 | 결과 |
|------|------|
| bond master 수집 | ✅ bond0 수집됨 |
| slave 제외 | ✅ dummy slave 제외됨 (master sysfs 감지) |
| VLAN-on-bond 수집 | ✅ bond0.200 수집됨 |
| bridge port 제외 | ✅ bridge 하위 port 제외됨 |

### source 우선순위 체계 확정

```
kernel sysfs > POSIX 명령 > /proc > /etc
```

- kernel sysfs (`/sys/class/net/*`): MAC, MTU, speed, operstate, master, bridge/bonding 판정
- POSIX 명령 (`ip`): IPv4 주소, default gateway, primary 판정
- `/proc`: cpuinfo, meminfo
- `/etc`: resolv.conf (DNS), os-release (system)

### 운영 해석 정책 확정

| 항목 | 해석 |
|------|------|
| `is_primary` | IPv4 main table default route device (운영 대표 IP와 동일하지 않을 수 있음) |
| `speed=null` | kernel 미보고 (bond/bridge master, 가상 NIC) |
| `dns 127.0.0.53` | stub resolver (systemd-resolved, 실제 upstream DNS가 아님) |
| policy routing / IPv6 / VRF | 미지원 |

### 결론

명령어 매트릭스 실측으로 배포판 무관 설계를 검증하고, bond 실증으로 bond master/slave/VLAN-on-bond 수집 정확성을 확인했다. source 우선순위와 운영 해석 정책을 확정하여 GUIDE_FOR_AI.md에 반영했다.

---

## 13. Reference 종합 수집 (Round 11, 2026-04-28)

### 배경

새 vendor 추가 / schema 필드 보강 / OS 매핑 검증 / 회귀 비교 시 매번 실장비에 직접 접속하는 비용을 줄이고, 향후 재현/비교 가능한 raw 자산을 확보할 필요가 있었다. 사용자가 Jenkins master 2대 / agent 2대 / OS VM 6대 + bare-metal 1대 / Windows VM 1대 / BMC 11대 / ESXi 3대를 테스트 자격과 함께 제공했다.

### 결정

`tests/reference/` 디렉터리에 종합 reference 데이터를 보존한다. 회귀 input (`tests/fixtures/`) 및 회귀 기준선 (`tests/baseline_v1/`)과는 별개 디렉터리로 분리하여 회귀 입력 변경 위험을 피한다.

수집 도구 4개를 작성:
- `crawl_redfish_full.py` — Redfish ServiceRoot부터 모든 link 재귀 follow (Python stdlib + PyYAML)
- `gather_os_full.py` — paramiko SSH (Linux) + pywinrm (Windows) + ansible setup
- `gather_esxi_full.py` — paramiko SSH (esxcli/vim-cmd) + pyvmomi (vSphere API)
- `gather_agent_env.py` — paramiko SSH 기반 환경 dump (REQUIREMENTS.md 검증)

### 자격 처리

자격 평문 commit 방지를 위해 `tests/reference/local/targets.yaml`을 `.gitignore`에 등록. `targets.yaml.sample`만 commit. 수집 완료 후 `targets.yaml` 삭제 권장.

### 1차 수집 결과 (2026-04-28)

| 채널 | 시도 | 성공 | 실패 |
|---|---|---|---|
| Redfish | 11 | (진행 중) | 3 (Cisco 1/3 도달 불가, Dell 32 vendor 의심) |
| OS | 7 | 6 (Linux) | 1 (Win10 WinRM) |
| ESXi | 3 | 3 (pyvmomi), 1 (SSH) | 0 (전체) / 2 (SSH만) |
| Agent/Master | 4 | 4 | 0 |

세부는 `tests/evidence/2026-04-28-reference-collection.md` 참조.

### 발견 사항

- **F1**: Dell BMC 사용자는 user=admin이 아닌 user=root (사용자 채팅 정정)
- **F2**: 10.100.15.32가 "dell" label인데 ServiceRoot=AMI Redfish Server. 실 vendor / 자격 사용자 확인 필요 (rule 96 R2 — 외부 계약 디버깅 시 질의 우선)
- **F3**: Cisco 10.100.15.1 HTTP 503 / 15.3 timeout. 장비 가동 상태 확인 필요
- **F4**: Win10 WinRM 5986 미활성 + 5985 Basic 미허용 + WSL Python 3.12 ntlm-auth 라이브러리의 OpenSSL 3.0 MD4 미지원
- **F5**: ESXi 10.100.64.1 / .3 SSH 비활성 (vSphere 기본 상태). 활성화 후 esxcli 53종 추가 수집 가능
- **F6**: gather_agent_env.py의 sudo 명령 처리 개선 필요 (Master 153에서 ~120초 대기 발생)

### 누적 통계 (BMC 진행 중 시점 기준)

- 파일 수: 4420 (BMC 완료 시 ~10000 예상)
- 디스크 사용: 43MB (BMC 완료 시 ~150-200MB 예상)

### 활용

1. **새 vendor 온보딩**: 그 vendor의 redfish endpoint list로 OEM path 파악 + adapter metadata `tested_against` 갱신 근거
2. **schema 필드 추가**: cross-vendor OEM 데이터 비교
3. **OS 매핑 검증**: cmd_dmidecode_*.txt ↔ ansible_setup ↔ field_dictionary 정합 (rule 13 R1)
4. **REQUIREMENTS.md 검증**: agent 디렉터리의 ansible/python/collection 버전 ↔ 문서 명시
5. **회귀 비교**: 펌웨어 / OS 업그레이드 후 동일 명령 재수집 → diff

### 보존 정책 (rule 70)

- 본 디렉터리는 commit 대상 (raw raw 자료 가치 큼). 단:
  - `tests/reference/local/`은 .gitignore (자격)
  - 민감 파일 (sshd_config / sudoers)은 commit 전 사용자 검토
- 차후 수집 사이클마다 `tests/reference/INDEX.md` 갱신 + 본 decision-log에 Round 추가

### 후속 작업

- F2/F3/F4/F5/F6 follow-up (`tests/evidence/2026-04-28-reference-collection.md` 표 참조)
- 본 reference 자료 기반의 schema 추가 / adapter metadata 보강은 별도 PR

### rule / 정본 참조

- rule 13 (output-schema-fields), 21 (output-baseline-fixtures), 70 (docs-and-evidence-policy), 96 (external-contract-integrity)
- 정본: `tests/reference/README.md`, `tests/reference/INDEX.md`, `tests/evidence/2026-04-28-reference-collection.md`

---

## 다음에 읽을 문서

| 다음 작업 | 문서 |
|---|---|
| 검증 라운드 결과 누적 | [13_redfish-live-validation.md](13_redfish-live-validation.md) |
| Adapter 시스템 (점수 / 새 벤더 추가) | [10_adapter-system.md](10_adapter-system.md) |
| envelope 13 필드 의미 사전 | [20_json-schema-fields.md](20_json-schema-fields.md) |

## 본 문서를 보는 법

- 시간 역순으로 누적됩니다 (최신 결정이 위쪽).
- 각 결정은 "사용자 의심 / 분석 / 결정 / 영향 / 회귀" 5절 구조를 따릅니다.
- 결정의 "왜" 가 본문이고, "무엇을 했는지" 는 git log / commit 메시지로 보완됩니다.
