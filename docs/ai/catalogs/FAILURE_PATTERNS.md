# FAILURE_PATTERNS — server-exporter

> 발견된 실패 / 오탐 / 반복 실수 기록 (append-only, rule 70 트리거).
> 새 사례 발견 시 즉시 추가. 카테고리: scope-miss / ai-hallucination / external-contract-drift / vendor-boundary-violation / fragment-violation / vault-leak / convention-drift

## 형식

```
## YYYY-MM-DD — <한 줄 요약>

- 카테고리: scope-miss / ai-hallucination / ...
- 발견 위치: <파일 또는 commit>
- 증상: <관측>
- 원인: <분석>
- 영향: <범위>
- 수정: <commit / PR>
- 재발 방지: <rule / skill / hook 변경>
- 관련 rule: rule N
```

---

## 2026-04-29 — production-audit-bundle (4 agent 전수조사로 일괄 발굴)

- 카테고리: scope-miss + cross-channel-drift + jinja2-loop-scoping
- 발견 위치: 4 agent audit 결과 (Redfish + OS-ESXi-common + Schema + Tests)
- 증상 (대표 6건):
  1. **Skeleton drift** — `init_fragments.yml` + `build_empty_data.yml` + `build_failed_output.yml` 3종이 sections.yml과 sync 안 됨 (storage.{hbas,infiniband,summary} / network.{adapters,...} 누락) — rescue path가 success path와 다른 envelope shape 출력
  2. **ESXi vendor 미정규화** — esxi_baseline.json `vendor: "Cisco Systems Inc"` (Redfish는 'cisco' lowercase canonical) — 호출자 라우팅 불가
  3. **diagnosis.details 형변환** — 성공 path는 dict, fallback은 list of strings — 호출자 파싱 시 TypeError
  4. **Windows runtime swap_total_mb 합계 버그** — Jinja2 loop scoping (cycle-016 namespace fix가 memory/storage만 적용, runtime 누락) → 마지막 pagefile 크기만 emit
  5. **ESXi DNS 항상 빈 list** — `vmware_host_config_info`의 `hosts_config_info[hostname]` 구조를 top-level iterate (production에서 DNS 정보 0건)
  6. **account_service.yml 복구 creds 미설정** — `ansible_user`/`ansible_password` Ansible connection var 사용했지만 set_fact 안 됨, 빈 string으로 401
- 원인: 점진적 cycle 누적 + cross-channel 일관성 검증 hook 부재 + Jinja2 scoping 패턴 유사 코드 일괄 적용 누락
- 영향: 모든 5 vendor + 모든 OS + ESXi (cross-channel JSON 호환성)
- 수정: 본 production-audit cycle 일괄 fix (Edit tool 직접 적용 / pytest 148/148 PASS / verify_* 4종 PASS)
- 재발 방지:
  - JSON envelope cross-channel consistency hook 추가 검토 (rule 13 R5 자동 검증)
  - cycle 종료 시 4 agent audit 패턴 정기화 (rule 28 R1 추가 측정 대상 검토)
  - Jinja2 loop scoping linter 검토
- 관련 rule: rule 13 R5 / rule 22 R1 / rule 80 R1

---

## 2026-04-29 — user-label-vs-redfish-manufacturer-drift (cycle-015)

- 카테고리: external-contract-drift
- 발견 위치: `inventory/lab/redfish.json` ↔ 실 Redfish ServiceRoot 응답 (rule 27 R3 1단계)
- 증상: 사용자가 BMC IP에 vendor 라벨 부여 ("dell" / "cisco") 했으나 무인증 ServiceRoot 응답이 다른 Manufacturer로 회신 (`AMI` / `TA-UNODE-G1`)
- 원인:
  1. 사용자가 호스트 라벨을 OS / 사용 환경 기준으로 부여 (e.g. "이 머신에 Dell 서버 OS 깔려있음")하지만 실제 BMC는 별도 OEM
  2. Whitebox / GPU 호스트는 보드 OEM과 BMC OEM이 다른 케이스 잦음
  3. Cisco TelePresence / Tetration 같은 비-UCS 제품도 Cisco 그룹으로 통칭
- 영향:
  - rule 27 R3 1단계가 자동 검출 → graceful degradation 가능 (회귀 영향 0)
  - 단, 사용자 라벨에 의존한 inventory 작업 / vault 매핑은 잘못된 vendor 사용 위험
- 수정: 본 cycle 시점 inventory/lab/redfish.json은 `_vendor` 메타 보존 + DRIFT-011 entry로 추적. 실측 deep_probe 후 라벨 정정.
- 재발 방지:
  - **rule 27 R3 1단계 (무인증 ServiceRoot detect) 의무 — 이미 채택**
  - rule 96 R4 — drift 발견 시 3 곳 기록 의무 (이미 채택)
  - **신규 권장**: 새 BMC inventory 등록 시 사용자 라벨 + Redfish 실 응답 1회 확인 의무 (skill `add-new-vendor` 본문에 추가 권장 — 후속)
- 관련 rule: rule 27 R3 (Vault 2단계 — 1단계가 본 drift 검출), rule 96 R1 (외부계약 origin), rule 50 R1 (vendor 정규화)
- 관련 evidence: `tests/evidence/cycle-015/connectivity-2026-04-29.md` 5절

## 2026-04-30 — http-200-only-protocol-classification (5 commits)

- 카테고리: external-contract-drift
- 발견 위치: `common/library/precheck_bundle.py` (probe_redfish/probe_esxi/probe_os) + `redfish_gather.py` (storage controller / network adapters) + `esxi-gather/tasks/collect_runtime.yml` (firewall_state)
- 증상: 호출자에게 "Redfish 미지원" / "vSphere endpoint 미응답" / "WinRM 미응답" / "controller 정보 부재" 보고가 발생하지만 실제 BMC/ESXi/Windows 는 정상 응답 중. 인증 강화 펌웨어 (HPE iLO5/6 일부, Lenovo XCC 일부) 가 ServiceRoot 무인증 시 401 던지는 케이스가 가장 흔함.
- 원인: HTTP 200 응답만 "프로토콜 살아있음"으로 분류, 401/403/503 등 의미 있는 응답을 모두 fail 로 분류. probe_esxi 는 이미 status_code 화이트리스트 패턴 갖고 있었으나 401/403/503 누락. probe_os WinRM 도 403/503 누락.
- 영향: 인증 강화 BMC + 다중 host vCenter + IIS 재시작 중 Windows 환경에서 false negative — 호출자가 "장비 자체 미지원" 으로 잘못 판단.
- 수정 (2026-04-30 push):
  - `c23d185f` probe_redfish 401/403/503 → protocol_supported (회귀 테스트 8건)
  - `31178f8c` probe_esxi/probe_os 401/403/503 + timeout_protocol 6→15s (회귀 13건)
  - `a60e42b5` redfish storage controller 401/403/503 silent fail 정정 (errors 누적 + status_code 메타, 회귀 7건)
  - `6ea2c292` ESXi firewall_state 빈 list ≠ disabled (보안 라벨 반대 보고 차단)
  - `9d5c957b` ESXi collect_runtime hostname 명시 lookup (multi-host 임의 host 참조 차단)
- 재발 방지:
  - 새 probe / endpoint 추가 시 status_code 화이트리스트 명시 의무 (별도 rule 검토 후속)
  - rule 96 R4 정합 — origin 주석에 "status_code 응답별 의미" 매트릭스 기록 권장 (`EXTERNAL_CONTRACTS.md` 매트릭스 참조)
- 관련 rule: rule 27 R5 (precheck layer), rule 96 R1 / R4 (외부계약), rule 95 R1 #11 (외부계약 drift)
- 관련 evidence: `tests/unit/test_precheck_probe_*.py` (3 파일 21 케이스), `tests/unit/test_redfish_storage_controller.py` (7 케이스)

---

## 2026-04-30 — errors-string-iteration (char 분해 회귀)

- 카테고리: jinja2-string-coerce + fragment-violation
- 발견 위치: `os-gather/tasks/linux/gather_system.yml:344-352` (root cause) + `common/tasks/normalize/merge_fragment.yml` (수신측 char iter)
- 증상: 호출자 envelope `errors[]` 가 단일 character 들로 분해된 5개 entry 보고 — `[{"section":"unknown","message":"["}, {"...":"]"}, {"...":"\n"}, {"...":"}"}, {"...":"}"}]`. 사용자가 의미 있는 메시지 받지 못함.
- 원인 (3 layer):
  1. **ROOT**: `_errors_fragment: >- ... }} }}` — `>-` folded scalar 끝에 잉여 `}}` 두 글자. Jinja list 결과가 string 으로 coerce 되며 `\n}}` 가 concat → `_errors_fragment` 가 list 가 아닌 string `"[]\n}}"` 로 들어감.
  2. **수신측 char iter**: `merge_fragment.yml` 의 `for e in (_errors_fragment | default([]))` 가 string 입력에 대해 character 단위 iterate (Jinja2 표준).
  3. **방어 부재**: `_errors_fragment` 가 list 가 아닌 경우의 가드 없음.
- 영향: 모든 OS gather Linux Python path. 호출자 시스템 파싱 오류 가능. 보안 영향 없음 (정보 손실만).
- 수정 (2026-04-30 push):
  - `88de692d` (root cause + 방어 layer 2겹) — gather_system.yml 잉여 `}}` 제거 + merge_fragment/build_errors 에 string/dict/None/int 입력 list 강제 wrap, char iter 차단, whitespace char skip. 회귀 테스트 10건.
  - `cfc24eee` (전수 스캔 후속) — 같은 패턴이 windows/gather_system + redfish/normalize_standard 의 `_errors_fragment` 에도 잠재 위험으로 존재 → 단일 ternary 로 단순화.
- 재발 방지:
  - **신규 패턴 식별**: fragment 변수에 `>-` block scalar + 다중 `{{}}` 분기 + plain text 혼재 = string-coerce 위험. 단일 expression 또는 별도 set_fact 분리 권장.
  - rule 22 R8 (fragment 타입) — list of dicts 강제 명시. 본 cycle entry 추가 검토.
  - 회귀 테스트 패턴: jinja2 라이브러리로 fragment Jinja 직접 evaluate (Ansible 환경 없이 단위 테스트 가능).
- 관련 rule: rule 22 R7/R8 (fragment 명명/타입), rule 23 R8 (ASCII 태그 — 다이어그램 정렬도 같은 폰트 폭 이슈)
- 관련 evidence: `tests/unit/test_errors_normalize.py` 10 케이스 (사용자 보고 케이스 정확 재현 + 차단 검증)

---

## 향후 가능 패턴 (Plan 1+2 도입 시점 예측)

참고 — clovirone에서 학습한 일반 패턴은 rule 95 R1 (의심 패턴 11종)에 흡수됨.

### 향후 가능 패턴

1. **Fragment 침범** (rule 22): gather가 다른 섹션의 fragment 변수 set_fact
2. **Vendor 하드코딩** (rule 12): common 코드에 "Dell" 등 직접 분기
3. **외부 계약 drift** (rule 96): 펌웨어 업그레이드로 Redfish path 변경 → adapter origin 주석 stale
4. **Vault 누설** (운영 권장 — cycle-011: rule 60 해제, cycle-012 vault encrypt 채택): Jenkins console log에 BMC password 노출
5. **Schema 3종 일부만 갱신** (rule 13): sections.yml만 수정하고 field_dictionary / baseline 미갱신
6. **adapter score 동률** (rule 95 R1 #4): 의도와 다른 adapter 선택
7. **Linux raw fallback 미고려** (rule 10 R4): Python 3.6 환경에서 setup 모듈 가정
8. **callback URL 후행 슬래시** (이미 commit 4ccc1d7로 fix): 입력 URL 정규화 누락
9. **Jenkinsfile cron 사용자 승인 누락** (rule 80): AI 임의 cron 변경
10. **incoming-merge 위반 무시** (rule 97): 자동 검사 보고서를 후속 PR으로 정리 안 함

## 2026-04-30 — Lenovo XCC2/XCC3 namespace prefix Oem 키로 vendor=null

- 카테고리: external-contract-drift
- 발견 위치: `redfish-gather/library/redfish_gather.py::_detect_vendor_from_service_root`
- 증상: Lenovo 장비인데 ServiceRoot vendor 감지 결과 `null`. envelope의 `vendor: null` 출력. 동적 vault 로딩 실패로 인증 단계 우회 가능성.
- 원인: 일부 Lenovo XCC2/XCC3 펌웨어가 Oem 키를 단순 `"Lenovo"`가 아닌 `"Lenovo_xxx"` namespace prefix 형식으로 반환. 기존 코드는 정확 매칭만 시도 (`if k in vm`).
- 영향: Lenovo 일부 펌웨어 전체. vendor=null → adapter 매칭 generic fallback → 일부 OEM 섹션 누락.
- 수정: cycle 2026-04-30 — `_detect_vendor_from_service_root`에 namespace prefix 매칭 1-B 단계 추가 (`k.startswith(alias + '_') or k.startswith(alias + '.')`)

## 2026-04-30 — 구 BMC TLS handshake 실패로 "Redfish 미지원" 오판정

- 카테고리: external-contract-drift
- 발견 위치: `common/library/precheck_bundle.py::_build_ssl_context`, `redfish-gather/library/redfish_gather.py::_ctx`
- 증상: curl `-k` 로는 ServiceRoot 정상 응답 받는데, server-exporter precheck Stage 3에서 "이 장비는 Redfish를 지원하지 않습니다" 메시지.
- 원인: Python 3.12 + OpenSSL 3.x default SSL context는 legacy renegotiation 차단 + weak cipher 차단. 구 BMC (HPE iLO4, Lenovo IMM2, 일부 iDRAC7/8 펌웨어)와 handshake 실패 → URLError → http_get payload=None → probe_redfish가 status_code 분기 못 타서 fail.
- 영향: 구 BMC 펌웨어 환경 전체. precheck Stage 3 false negative → 본 수집 진입 차단.
- 수정: cycle 2026-04-30 — verify=False 시 `OP_LEGACY_SERVER_CONNECT` + `DEFAULT@SECLEVEL=0` 적용 (curl `-k` 동등 관용성, BMC self-signed 망 한정)

## 2026-04-30 — BMC 제품명 시그니처 부족으로 vendor=null

- 카테고리: external-contract-drift
- 발견 위치: `redfish-gather/library/redfish_gather.py::_detect_vendor_from_service_root`
- 증상: ServiceRoot Vendor 필드 부재 + Oem 부재 펌웨어에서 Product에 "XClarity Controller" / "iDRAC9" / "AMI MegaRAC" 등 BMC 제품명만 있을 때 vendor=null.
- 원인: 기존 코드는 `'ilo' in product` / `'proliant' in product` 만 추가 매칭 (HPE만). Dell iDRAC / Lenovo XClarity / Supermicro MegaRAC / Cisco CIMC 시그니처 부재.
- 영향: ServiceRoot v1.0~1.4 펌웨어 + Oem 부재 BMC.
- 수정: cycle 2026-04-30 — `_BMC_PRODUCT_HINTS` 상수 도입 (idrac/ilo/proliant/xclarity/thinksystem/xcc/imm2/megarac/cimc/ucs). Product + Name 필드 둘 다 매칭.

## 2026-04-30 — ServiceRoot v1.0~1.4 펌웨어 vendor=unknown (G3 fix)

- 카테고리: external-contract-drift
- 발견 위치: `redfish-gather/library/redfish_gather.py::detect_vendor`
- 증상: ServiceRoot Vendor/Product 표준 필드 부재 + Oem 부재 BMC 펌웨어에서 vendor=unknown.
- 원인: Vendor는 ServiceRoot v1.5.0+, Product는 v1.3.0+ 표준 필드. 구 펌웨어 (구 iDRAC7/8, iLO 4, IMM2)는 두 필드 모두 부재. ServiceRoot 5단계 매칭 모두 fail.
- 영향: 구 BMC 펌웨어 환경. vendor=unknown → adapter 매칭 generic fallback.
- 수정: cycle 2026-04-30 — `detect_vendor`에 Chassis → Managers → Systems Manufacturer fallback 순회 추가. 표준 Manufacturer 필드는 v1.0+ 모든 BMC 표준.

## 2026-04-30 — probe_redfish transient URLError로 false negative (G5 fix)

- 카테고리: external-contract-drift
- 발견 위치: `common/library/precheck_bundle.py::probe_redfish`
- 증상: BMC 부팅 직후 / 일시 부하 시 1회 fail로 "Redfish 미지원" 오판정.
- 원인: payload=None (URLError/timeout/SSLError) 시 retry 부재 — 1회 fail 즉시 status 결정.
- 영향: BMC 재시작 / 운영 부하 transient 환경.
- 수정: cycle 2026-04-30 — payload=None 시 1초 backoff 후 1회 retry. probe_facts에 retry_count 노출.

## 2026-04-30 — ServiceRoot 본문 비어도 401 realm으로 vendor 식별 가능 (G6 fix)

- 카테고리: external-contract-drift
- 발견 위치: `redfish-gather/library/redfish_gather.py::_probe_realm_hint` (신규)
- 증상: 일부 보안 강화 BMC 펌웨어가 무인증 ServiceRoot에 401 + 본문 비어 반환. ServiceRoot 5단계 + G3 Chassis fallback 모두 인증 필요해 fail.
- 원인: 401 응답의 `WWW-Authenticate: Basic realm="iDRAC"` / `realm="iLO"` / `realm="XClarity Controller"` 헤더 미활용.
- 영향: 보안 강화 펌웨어 환경. vendor=unknown → vault 동적 로딩 차단 가능.
- 수정: cycle 2026-04-30 — `_probe_realm_hint` 신규. 401/403 응답의 realm에서 vendor_aliases + `_BMC_PRODUCT_HINTS` 매칭. detect_vendor 의 마지막 fallback로 통합.

## 2026-04-30 — Vendor 필드 'Dell Inc.' trailing dot 케이스 (G7 fix)

- 카테고리: external-contract-drift
- 발견 위치: `redfish-gather/library/redfish_gather.py::_detect_vendor_from_service_root` step 2
- 증상: ServiceRoot `Vendor: "Dell Inc."` 응답에서 vendor=null. (Product 매칭이 보통 회복하지만 Vendor 단독 케이스 fail)
- 원인: 기존 코드 `v.lower().strip().rstrip('.')` 로 `'dell inc'` 만들고 정확 매칭만. vm에 `'dell inc'` 키 없음 (`'dell inc.'` 만 있음).
- 영향: Vendor 필드만 채우고 Product/Oem 비어 있는 펌웨어.
- 수정: cycle 2026-04-30 — 정확 매칭은 원형 + trailing dot 제거 두 형식 모두 시도. 추가로 substring 매칭으로 보강.

## 2026-04-30 — Redfish multi-account fallback BMC lockout 회피 + 디버그 로그 보강

- 카테고리: external-contract-drift
- 발견 위치: `redfish-gather/tasks/try_one_account.yml`
- 증상: 5 accounts 순회 시 일부 BMC (iDRAC, iLO 일부 펌웨어)가 연속 fail에 source IP 일시 차단. 결과적으로 정답 자격증명도 401 받음. 디버깅 시 어느 단계에서 fail인지 message 부족.
- 원인: attempt 사이 backoff 부재 + failure log가 label/role 만 표시 (status/error 미포함).
- 영향: BMC lockout 환경 + 디버깅 시간 증가.
- 수정 (부분): cycle 2026-04-30 — 실패 시 1초 backoff + status/vendor/first_error 로그 보강.
- 미적용 (사용자 결정 대기): primary `partial` 결과를 fallback 시도 차단으로 처리하는 정책 변경 (`_rf_attempt_ok = status == 'success'` 강화).
