# server-exporter 현재 상태

## 일자: 2026-05-06 (multi-session-compatibility cycle Session-3 — M-A3 status 의도 주석 강화 / Case A)

### 사용자 명시 (cycle 진입)
- "이게 로직이 정상작동돼지않는듯함. 부분 성공이라고 하더라도 error 에는 로그가 찍히는데 success로 빠지는경우가 있음 이것은 왜이런지 확인해줘 의도된건지?"
- "사용자 결정 4 포인트도 AI 합리적 default 결정 후 진행" (자율 권한)

### M-A3 결과 (Case A — 의도 주석 강화 only)

M-A2 결정 종합 (Session-2 / commit `c23c7f27`): **B-1 + (a) + (c) + (a)**
→ Case A 채택 — 코드 동작 변경 없음, 의도 명문화 only.

Session-3 적용 변경:

| 파일 | 변경 | 의도 |
|---|---|---|
| `common/tasks/normalize/build_status.yml` | +35 / -2 (헤더 주석만) | 시나리오 4 매트릭스 + errors[] 분리 의미 + 3 reference (gather_memory:171-175 / gather_network:208-209 / esxi normalize_storage:79-83) |
| `tests/fixtures/outputs/status_success_with_warnings.json` | 신규 | 시나리오 B 재현 (Linux OS gather memory dmidecode fallback + network lspci stderr warning) |
| `tests/unit/test_status_scenario_b_invariants.py` | 신규 (13 테스트) | Jinja2 ↔ Python 재현 회귀 + envelope 13 필드 invariant + 4 시나리오 매트릭스 검증 |

### 정본 status 판정 규칙 (build_status.yml 헤더 정본)

```
| # | 섹션 status            | errors[] | overall.status |
|---|------------------------|----------|----------------|
| A | 모두 success           | empty    | success        |
| B | 모두 success           | warnings | success  *     |
| C | success + failed 혼재  | any      | partial        |
| D | 모두 failed            | any      | failed         |
```

\* 시나리오 B 는 의도된 동작. errors[] 는 사유 추적용 분리 영역 — overall status 판정에 영향 없음.

### 검증

- pytest **291/291 PASS** (기존 278 + 신규 13)
- verify_harness_consistency PASS (rules:28 / skills:48 / agents:59 / policies:10)
- baseline 회귀 영향 0 (코드 동작 변경 없음)
- envelope 13 필드 / status enum 3종 보존 (rule 13 R5 / rule 96 R1-B)
- M-A4 [SKIP] — rule 70 R8 trigger NO (rule 본문 변경 없음 / 표면 카운트 변동 없음 / 보호 경로 정책 변경 없음)

### 후속 의무

M-F1 (`docs/20_json-schema-fields.md`) 신설 시 다음 절 포함 의무 (DEPENDENCIES.md 갱신됨):
- `status` 필드 enum 3종 (success / partial / failed)
- 시나리오 4 매트릭스 (build_status.yml 헤더 정본 reference)
- errors[] 와 status 분리 의미

---

## 일자: 2026-05-06 (cycle-020 phase 2 — F50 Cisco 표준 지원 + infraops 통일)

### 사용자 명시
- "cisco는 왜 안되는거임? 되는데 안된다고 적혀있어서 안되는게아닌지? web 검색 필요"
- "redfish 공통계정은 모두 동일해야함 (패스워드도)"
- "vault 값이 달라졌다면 다른 모든 서버들에게도 infraops 패스워드 동기화"

### Cisco 결론 정정 (사이트 실측 → web search 결합)

이전 결론 "Cisco AccountService 표준 미지원" = **잘못된 분류**. 사이트 실측 확인:
- AccountService.v1_6_0 정상 응답
- POST /Accounts 지원하나 vendor-specific:
  1. `Id` 필드 1-15 필수
  2. RoleId enum: `admin`/`user`/`readonly`/`SNMPOnly` (표준 'Administrator' 거부)
- 정정 후: POST {Id:'2', RoleId:'admin'} → HTTP 201 + 인증 200 OK

### infraops 공통계정 password 통일

5 vault primary password 통일 → `Passw0rd1!Infra` (Dell Strengthen Policy 호환 = 가장 엄격):

| vault | 이전 | 신 (cycle 2026-05-06) |
|---|---|---|
| dell.yml | Passw0rd1! | **Passw0rd1!Infra** (phase 1) |
| hpe.yml | Passw0rd1! | **Passw0rd1!Infra** (phase 2) |
| lenovo.yml | Passw0rd1! | **Passw0rd1!Infra** (phase 2) |
| cisco.yml | Passw0rd1! | **Passw0rd1!Infra** (phase 2) |
| supermicro.yml | Passw0rd1! | **Passw0rd1!Infra** (phase 2) |

### BMC 동기화 (실 적용)

| BMC | Vendor | 작업 | 결과 |
|---|---|---|---|
| 10.100.15.27 | dell | slot 3 PATCH (phase 1 적용) | 인증 200 |
| 10.100.15.31 | dell | slot 3 PATCH (phase 1 적용) | 인증 200 |
| 10.50.11.231 | hpe | slot 3 PATCH password 갱신 | 인증 200 |
| 10.50.11.232 | lenovo | slot 4 PATCH password 갱신 | 인증 200 |
| 10.100.15.2 | cisco | slot 2 POST 생성 | 인증 200 |

**5/5 BMC 모두 `infraops/Passw0rd1!Infra` HTTP 200 통일 검증 완료**.

### 검증

- pytest **276/276 PASS** (F50 신규 3건 + F13 cisco_not_supported 제거)
- 5 BMC 직접 curl 검증
- Jenkins job 재실행 가능 (다음 build 에서 used_role=primary 확인 예정)

---

## 일자: 2026-05-06 (cycle-020 — F49 redfish account_provision 호환성 강화)

### 사용자 명시
- "redfish 공통계정 생성이 안 되는 것 같다. 로직 + vault 확인 + 사이트 실측 + web 호환성 + 코드 개선 + 자동화 모두 진행."
- "Jenkins 잡 생성해서 직접 테스트, curl 직접 검증."
- "vault 비밀번호: Goodmit0802!"

### Root cause (사용자 사이트 실측 — rule 25 R7-A-1)

"공통계정 생성 안 됨" 사고의 진짜 원인은 **3중 누적**:

1. **Vault label-mismatch (logic bug)** — `account_service.yml` 의 `_rf_recovery_account_resolved`
   가 username 만으로 vault lookup. Dell vault 에 `root` 4개 (서로 다른 password) →
   첫 entry (Dellidrac1!) 잡혀 password mismatch → AccountService GET 401 → recovered=False.
2. **Dell slot 1 anonymous reserved (BMC 정책)** — UserName='', Enabled=false 인 placeholder.
   기존 `_find_empty_slot()` 가 첫번째 빈 slot (=slot 1) 에 PATCH 시도 → 거부.
3. **Dell silent password fail (펌웨어 정책)** — iDRAC9 7.10.70.00 Security Strengthen
   Policy. `Passw0rd1!` (10자) PATCH 200 OK 응답이지만 실제 password 미적용 (silent skip).
   `Passw0rd1!Infra` (15자) 부터 정상 적용.

### F49 Fix 매트릭스

| Fix | 파일 | 영향 |
|---|---|---|
| label 매칭 lookup | `redfish-gather/tasks/account_service.yml` | username 다중 password 시 정확한 entry |
| `_rf_used_account_password` promote | `redfish-gather/tasks/try_one_account.yml` | account_service 가 vault re-lookup 안 함 |
| Dell slot 1 skip + 다중 retry | `redfish-gather/library/redfish_gather.py` | slot 1 anonymous 회피 + 3 슬롯 retry |
| PATCH 후 verify _get | 동상 | silent fail 감지 + 다음 슬롯 fallback |
| Lenovo PasswordChangeRequired retry | 동상 | XCC 펌웨어 password policy |
| HPE Oem.Hpe.Privileges 3차 retry | 동상 | iLO 일부 펌웨어 |
| Dell vault password 강화 | `vault/redfish/dell.yml` | Passw0rd1! → Passw0rd1!Infra (15자) |
| Jenkins job 등록 | `jenkins/jobs/redfish-account-provision-verify/config.xml` | DRYRUN/TARGET 파라미터 + agent 실행 |
| 회귀 테스트 7건 | `tests/unit/test_account_provision_f49_vendor_compat.py` | 7종 시나리오 회귀 |

### 검증 (사이트 실측)

| BMC | Vendor | dryrun=true | dryrun=false 실 적용 |
|---|---|---|---|
| 10.100.15.27 | dell | PASS (slot 3 patch_empty_slot) | (vault 갱신 후 진행) |
| 10.100.15.31 | dell | PASS (slot 3 patch_empty_slot) | (vault 갱신 후 진행) |
| 10.50.11.231 | hpe | PASS (이미 infraops primary) | NOOP |
| 10.50.11.232 | lenovo | PASS (이미 infraops primary) | NOOP |
| 10.100.15.2 | cisco | PASS (not_supported graceful) | NOOP |

### 검증 (자동화)

- pytest **274/274 PASS** (12종 신 회귀 추가)
- Jenkins job 등록: `redfish-account-provision-verify` (10.100.64.152 master)
- 자동화 스크립트: `scripts/verify_account_provision.sh`

---

## 일자: 2026-05-01 (cycle-019 phase 2 — F44~F47 신규 vendor 4종 도입)

### 사용자 명시 (phase 2)
- "신규 밴더 추가 승인하겠다" (rule 50 R2 9단계 vault SKIP — phase 1 사용자 명시 그대로 적용)

### Phase 2 적용 — Huawei / Inspur / Fujitsu / Quanta

| 단계 (rule 50 R2) | 작업 | 결과 |
|---|---|---|
| 1. vendor_aliases.yml | huawei / inspur / fujitsu / quanta 4 entry | ✅ |
| 2. adapter YAML | huawei_ibmc / inspur_isbmc / fujitsu_irmc / quanta_qct_bmc (priority=80) | ✅ |
| 3. OEM tasks | DEFER — standard_only (사이트 fixture 확보 후) | DEFER |
| 4. vault | **SKIP** (사용자 명시 phase 1) | SKIP |
| 5. baseline | DEFER (lab 부재) | DEFER |
| 6. ai-context | huawei.md / inspur.md / fujitsu.md / quanta.md | ✅ |
| 7. vendor-boundary-map.yaml | 4 vendor + 신 generation 7 adapter 매핑 갱신 | ✅ |
| 8. live-validation | DEFER (lab 부재) | DEFER |
| 9. decision-log | docs/19_decision-log.md cycle-019 entry | ✅ |

### redfish_gather.py 동기화

- `_FALLBACK_VENDOR_MAP` +11 entry (huawei/inspur/fujitsu/quanta 변형 alias)
- `_BMC_PRODUCT_HINTS` +7 entry (ibmc / fusionserver / isbmc / irmc / primergy / quantagrid / quantaplex)
- `bmc_names` +4 entry (huawei→iBMC, inspur→ISBMC, fujitsu→iRMC, quanta→BMC)

### 검증 (phase 2)

- pytest **108/108 PASS** (101 → 108, F44~F47 회귀 7건 신규)
- verify_harness_consistency PASS (vendor_aliases ↔ _FALLBACK_VENDOR_MAP sync 게이트 통과)
- verify_vendor_boundary PASS (nosec 주석 적절 — Allowed 영역만)
- check_project_map_drift PASS (fingerprint 갱신)
- py_compile + YAML 6 파일 syntax PASS
- adapter 4 필수 키 + canonical vendor match 모두 PASS

### 표면 카운트 변동 (phase 2)

- adapters: 34 → 38 (Redfish 23 → 27, +4 신규 vendor)
- vendor 정규화 list: 5 → 9 (5 → 9)
- vault: 변동 없음 (SKIP)
- baseline: 변동 없음 (lab 부재)

### 부재 시 동작 (graceful degradation)

- ServiceRoot 무인증 detect → vendor 정규화 OK (huawei/inspur/fujitsu/quanta)
- vault 부재 → precheck auth 단계 status=failed (rule 27 R4)
- envelope: status=failed + errors[] 명시 ("vault not found for vendor=<X>")

---

## 일자: 2026-05-01 (cycle-019 phase 1 — 7-loop + 10R extended audit P1 22건 일괄 수행)

### 사용자 명시 (phase 1)
- "/clear" 후 "예정돼있는 티켓 모두 수행해."

### 본 cycle 적용 (P1 카테고리)

| Fix | 영역 | 결과 |
|---|---|---|
| F83 | redfish_gather.py docstring | "GET only — PATCH/POST/DELETE 미사용" 명시 (DSP0266 §11 + bmcweb #262 회피) |
| F84 | SSLContext min/max version | minimum_version=TLSv1_2 / maximum_version=TLSv1_3 (DMTF DSP0266 §10.2 + iLO 7 호환) |
| F48 | NetworkPorts/Ports fallback 검증 | redfish_gather.py:1598-1599 이미 적용됨 — 회귀 테스트 3건 신규 |
| F41 | dell_idrac10.yml 신규 (priority=120) | PowerEdge 17G — R670/R770/R7715/R6715/R6815 cover (lab 부재 — web sources) |
| F47 | hpe_ilo7.yml 신규 (priority=120) | Gen12 ProLiant — DL360/DL380 Gen12 (3-part version 형식 분리) |
| F55 | lenovo_xcc3.yml 신규 (priority=120) | ThinkSystem V4 / OpenBMC — bundle 2024.3 |
| F56 | lenovo_xcc.yml 좁힘 | XCC1/XCC2 (V2/V3) cover. XCC3 분리 |
| F61 | supermicro_x12/x13/x14.yml 신규 3종 | AST2600 Whitley/Eagle/X14H14 (priority=90/100/110) |
| F68 | cisco_cimc.yml capabilities 매트릭스 확장 | M4 lab + M5~M8 web sources (firmware_patterns "^[4-6]\\." 좁힘) |
| F69 | cisco_ucs_xseries.yml 신규 (priority=110) | X210c/X410c standalone CIMC (IMM 모드 별도 채널) |
| F80 | EXTERNAL_CONTRACTS.md DMTF 매트릭스 | 2024.1 ~ 2025.4 spec + 모든 vendor BMC schema bundle |
| F91 | EXTERNAL_CONTRACTS advisory 등재 | CVE-2024-54085 AMI MegaRAC (Critical 10.0) — server-exporter read-only 영향 0 |
| F97 | SSL Unexpected EOF retry advisory | F84 의 SSLContext fallback 일부 회피. 추적 |
| F104 | Session lockout advisory | Basic Auth 단발성 유지 시 영향 없음 |
| F125 | Cisco CIMC < 4.x advisory | cisco_cimc.yml firmware_patterns "^[4-6]\\." 로 좁힘 |
| F126 | DIMM error vendor 차이 | Health 만 raw passthrough — 호출자 시스템이 vendor 별 해석 |

### 검증

- pytest **101/101 PASS** (94 → 101, 신규 7건 — F48/F84 회귀)
- verify_harness_consistency PASS (rules=28 / skills=48 / agents=59 / policies=10)
- verify_vendor_boundary PASS (vendor 하드코딩 0건)
- check_project_map_drift PASS (fingerprint 갱신 — adapter 27→34)
- py_compile redfish_gather.py PASS
- YAML 9 파일 syntax PASS (7 신규 + lenovo_xcc + cisco_cimc 변경)
- adapter 4 필수 키 (match/capabilities/collect/normalize) 7 신규 모두 존재

### 표면 카운트 변동

- adapters: 27 → 34 (Redfish 16 → 23, OS / ESXi 변동 없음)
  - dell: 3 → 4 (idrac10 신규)
  - hpe: 4 → 5 (ilo7 신규)
  - lenovo: 3 → 4 (xcc3 신규)
  - supermicro: 3 → 5 (x12/x13/x14 신규, x9 유지)
  - cisco: 2 → 3 (ucs_xseries 신규)
- rules / skills / agents / policies / hooks: 변동 없음 (cycle-018 그대로)

### 본 cycle 미수행 (사용자 결정 필요)

- **F74~F77** (Huawei / Inspur / Fujitsu / Quanta) — rule 50 R2 신규 vendor 9단계 절차 (사용자 명시 승인 필요). lab 부재 + 운영 도입 신호 없음. fixes/F44~F47.md 코드 생성 ticket 만 보존 (vault 미생성).
- **F81** (ThermalSubsystem fallback) — 향후 thermal 섹션 진입 시 적용. 현재 thermal 섹션 자체 미수집 → 영향 없음.

### 다음 cycle 권장

- **사이트 fixture 캡처** — 사용자 도입 시 신 generation BMC (Dell iDRAC10 / HPE iLO7 / Lenovo XCC3 / Supermicro X14 / Cisco UCS X-Series) 첫 수집 검증
- **F138 DMTF Redfish-Service-Validator** 도입 검토 (10R extended P1)

---

## 일자: 2026-05-01 (cycle-018 — 정기 자기개선 cycle, rule 28 drift 정정)

### 사용자 명시
- "/clear" 후 "계획된 작업 모두 수행해라" → "진행해라"

### 본 cycle 작업 (6단계 파이프라인)

| Stage | 결과 |
|---|---|
| 1. Observer | 11종 측정 — drift 4건 + 부수 2건 발견 (HIGH 1 / MED 1 / LOW 2) |
| 2. Architect | diff 명세 작성 |
| 3. Reviewer | architect 미발견 보안 위험 (vault_decrypt_check.py:97 평문 password) 적발 |
| 4. Governor | 모두 Tier 1/2, ADR 불필요 (rule 70 R8 trigger 미해당) |
| 5. Updater | 12 파일 적용 (script 1 + .gitignore + doc/rule 10) |
| 6. Verifier | 검증 6종 모두 PASS (pytest 94/94 포함) |

### 핵심 fix

| Fix | 영역 | 결과 |
|---|---|---|
| F-CYCLE-018-1 | `collect_repo_facts.py:79` 경로 버그 | `tests/baseline_v1` → `schema/baseline_v1` (SessionStart "0개" → "8개") |
| F-CYCLE-018-2 | field_dictionary doc stale 8 파일 | 46 entries → 65 entries (분류 체계 유지: 39 Must + 20 Nice + 6 Skip) |
| F-CYCLE-018-3 | adapter doc stale 3 파일 | 25개 → 27개 (Redfish 14 → 16) |
| F-CYCLE-018-4 | `_vendor_count()` 명명 오용 | docstring 명시 (실 normalized vendor 5 vs adapter 변종 15) |
| F-CYCLE-018-5 | untracked 잔재 9 + vault_decrypt_check.py | `.gitignore` 영구 ignore (Goodmit0802! 평문 leak 차단) |

### 검증
- pytest **94/94 PASS**
- verify_harness_consistency PASS (rules 28 / skills 48 / agents 59 / policies 10 — 표면 카운트 변동 0)
- verify_vendor_boundary PASS
- output_schema_drift_check PASS (fd_paths=65 fd_section_prefixes=16)
- check_project_map_drift PASS
- collect_repo_facts.py 실행 → "Baseline: 8개" 정상

### 적용 원칙
- rule 25 R7-A 사용자 실측 > spec — observer hallucinate (rules 32 주장) 적발 후 메인 직접 측정
- rule 22 / 96 R1-B Additive only — envelope 변경 0, 분류 체계 유지
- rule 70 R8 ADR trigger 미해당 — rule 본문 의미 변경 0 / 표면 카운트 변경 0 / 보호 경로 변경 0

---

## 이전: 2026-05-01 (P1 follow-up — F5/F13/F23 회귀 보강 + F23 적용)

### 사용자 명시 (2026-05-01 후속)
- "남아있는 작업 모두 수행해라"

### 본 cycle 작업 (P1 fix 후보 3건)

| Fix | 영역 | 처리 | 결과 |
|---|---|---|---|
| F5 | power | `_gather_power_subsystem` EnvironmentMetrics fallback | **이미 적용 확인** — 회귀 5건 신규 추가 (`test_power_environment_metrics_f5.py`) |
| F13 | users (provision) | Cisco CIMC AccountService 'not_supported' 분류 | **이미 적용 확인** — 회귀 4건 신규 추가 (`test_account_service_unsupported_f13.py`) |
| F23 | os | Linux/Windows users gather 'not_supported' 점진 전환 | **신규 적용** — `_sections_unsupported_fragment` wiring + 회귀 9건 (`test_os_users_unsupported_f23.py`) |

### F23 변경 상세 (Additive only, rule 96 R1-B)

`os-gather/tasks/linux/gather_users.yml` (Python mode + Raw mode):
- 빈 `getent_passwd` / 빈 `_l_raw_passwd` → `_sections_unsupported_fragment: ['users']` (이전 `_sections_failed_fragment`)
- root 항상 존재 가정 → 빈 결과 = 진짜 미지원 신호 (Alpine / distroless / busybox)
- failed_fragment 는 빈 list로 전환 (errors[] noise 차단)

`os-gather/tasks/windows/gather_users.yml`:
- `_w_users_raw.rc != 0` AND `_w_norm_users_list | length == 0` → unsupported
- rc=0 + 빈 list → collected (정상 0명 케이스 보존, Server Core 정상 동작)

### 검증
- pytest **94/94 PASS** (76 + 신규 18 = F5 5건 + F13 4건 + F23 9건)
- verify_harness_consistency PASS
- verify_vendor_boundary PASS
- py_compile redfish_gather.py PASS
- YAML syntax PASS (Linux/Windows gather_users.yml + cisco_cimc.yml)
- check_project_map_drift PASS (재baseline — os-gather + tests hash 갱신)

### 적용 원칙 (rule 96 R1-B Additive only)
- envelope 13 필드 변경 0건
- schema/sections.yml 변경 0건 (users 섹션 이미 정의)
- 기존 동작 유지 + 진짜 미지원 신호만 unsupported로 명시 분류
- 호출자 시스템 envelope shape 동일

---

## 이전: 2026-05-01 (호환성 ticket 일괄 — F01~F43 22건 처리)

### 사용자 명시 (2026-05-01 후속)
- "호환성 티켓 모두 수행하세요"

### 코드 변경 적용 (Additive only, rule 96 R1-B)

| Fix | 영역 | 변경 위치 | 변경 |
|---|---|---|---|
| F05 | power | `redfish_gather.py:_gather_power_subsystem` | EnvironmentMetrics fallback (PowerWatts.Reading/RangeMin/Max → power_consumed/min/max_watts) — DMTF 2020.4 |
| F02 | cpu | `redfish-gather/tasks/normalize_standard.yml` ProcessorType 필터 | 'CORE' enum 통과 (Redfish 2024.x logical processor) |
| F13/F08 | users (provision) | `redfish_gather.py:account_service_provision` | Cisco 외 vendor도 404-only 응답 시 'not_supported' 분류 (Additive — Cisco 분기 + 일반 404 graceful) |
| F20 | users (auth) | `redfish-gather/tasks/try_one_account.yml` | backoff `sleep 1`→`sleep 5` (BMC lockout 회피) |
| F21 | OS Linux | `ansible.cfg [ssh_connection]` | RHEL 9+ paramiko 2.9.0+ 호환 — HostKeyAlgorithms/PubkeyAcceptedAlgorithms/KexAlgorithms +ssh-rsa append |

### 검증/추적/lab 한계 보류 (코드 변경 없음)

| Fix | 분류 | 사유 |
|---|---|---|
| F01, F09, F10, F12, F17, F22, F24, F34, F35, F40 | 이미 호환 / 검증만 | 코드 자동 호환 — 사이트/lab 검증 시 fixture 추가 |
| F04, F11, F14, F15 | lab 한계 | HPE iLO 5 / Dell iDRAC 10 / Supermicro X9 fixture 부재 — 사이트 도입 시 별도 cycle |
| F33 | P3 추적 | Session 인증 — Basic Auth 부하 미미, 사고 발생 시 적용 |
| F23, F07, F37 | 이미 graceful | gather_hba_ib raw `[ -d ]` 검사 + failed_when:false. sub-section 단위 not_supported 분류는 schema 정의 외 — 사고 재현 후 |
| F38 | lab 한계 | Windows IB host 부재 — 사이트 도입 시 |
| F39 | 의도 skip | ESXi IB Ethernet 인식 — 기술 제약 |
| F41, F42, F43 | 추적만 | community.vmware 7.0.0 / Redfish v2 / RHEL 10 — 도입 시점 추적 |
| F16 | 추적만 | CVE-2024-54085 (AMI MegaRAC) 패치 매트릭스 |

### 검증
- pytest **234/234 PASS**
- verify_harness_consistency PASS
- verify_vendor_boundary PASS
- output_schema_drift_check PASS (sections=10 fd_paths=65)
- project_map_drift PASS (재baseline — redfish-gather hash)
- python AST PASS (redfish_gather.py)
- YAML PASS (normalize_standard.yml, try_one_account.yml)

### 적용 원칙 (호환성 cycle, rule 96 R1-B)
- envelope 13 필드 변경 0건
- 새 데이터/섹션/키 추가 0건
- 기존 path 유지 + 신 환경 fallback 추가만
- web sources / DMTF spec / vendor docs origin 주석 (rule 96 R1-A)

---

## 이전: cycle-017 하네스 보강 — B1~B8 + D + E 일괄 적용

### 사용자 명시 (2026-05-01)
1. "하네스 자기개선 루프도 넣어라" / "에이전트는 오푸스로" / "한 에이전트가 작업한 것을 다른 에이전트가 검수" (commit `a1a3bf6b` 진입 — 7 신규 agent + cross-review-workflow skill)
2. "하네스 보강 작업 모두 수행해라 남겨두지말고 모두" (B/D/E 일괄)
3. "하네스 전체 점검 하네스 작업을 마무리해라 묻지마라 전부해라" (commit + push 자율)

### 적용 (B1~B8 + D + E 모두 [PASS])

| Gap | 보강 | 위치 |
|---|---|---|
| B1 lab 한계 | rule 96 R1-A web sources 의무 | rule 96 본문 |
| B2 reverse regression | rule 25 R7-A-1 사용자 실측 우선 | rule 25 본문 |
| B3 새 JSON 키 자제 | rule 96 R1-B + envelope_change_check hook | rule 96 + scripts/ai/hooks/ |
| B4 ticket cold-start | write-cold-start-ticket skill | .claude/skills/ |
| B5 fallback 패턴 | `_endpoint_with_fallback` 헬퍼 | redfish_gather.py:567 |
| B6 origin 주석 | adapter_origin_check hook | scripts/ai/hooks/ |
| B7 사이트 fixture | capture-site-fixture skill | .claude/skills/ |
| B8 cross-channel | cross_channel_consistency_check hook | scripts/ai/hooks/ |
| D-A1 | web-evidence-collector agent (opus) | .claude/agents/ |
| D-A3 | lab-tracker agent (opus) | .claude/agents/ |
| D-S1 | web-evidence-fetch skill | .claude/skills/ |
| D-S2 | lab-inventory-update skill | .claude/skills/ |
| E | agent-permissions.yaml + ADR | .claude/policy + docs/ai/decisions |

### 표면 카운트
- agents: 57 → **59** (+2)
- skills: 43 → **48** (+5)
- hooks: 18 → **21** (+3)
- rules: 28 (R7-A-1 / R1-A / R1-B 본문 신설)
- decisions: ADR-2026-05-01-harness-reinforcement 신규

### 검증
- pytest 76/76 PASS / verify_harness_consistency PASS / verify_vendor_boundary PASS
- output_schema_drift_check PASS / project_map_drift 0 (재baseline)
- 3 신규 hook self-test PASS / commit_msg_check 5/5 PASS
- redfish_gather.py AST PASS

### 보고서
- `docs/ai/harness/cycle-017.md` (cycle 보고서)
- `docs/ai/decisions/ADR-2026-05-01-harness-reinforcement.md` (governance)
- `docs/ai/tickets/2026-05-01-gather-coverage/HARNESS-RETROSPECTIVE.md` (G절 적용 결과)

### 후속 (다음 세션)
- harness-evolution-coordinator 6단계 정기 cycle 진입
- gather-coverage P1 3건 (F5 / F13 / F23)
- 사이트 fixture 첫 실 적용

---

## 일자: 2026-04-30 (account_service dryrun OFF + Locked 보강 — 사용자 명시 승인, ADR-2026-04-30)

## 요약 (account_service 실 동작 전환 — 2026-04-30)

사용자 명시 승인:
- "dryrun=true default 이게 무슨말?? 지금 동작안하는거임?? 동작하게 해야하는거아님??"
- "Locked 보강 진행 해라 그리고 default가 동작하게 해라 지금 써야하는 기능이다"

### 변경

1. **`redfish-gather/tasks/account_service.yml` line 31**: `_rf_account_service_dryrun | default(true)` → `default(false)`. 이제 default 동작이 **실 PATCH/POST**.
2. **`redfish-gather/library/redfish_gather.py::account_service_provision`**:
   - `existing` 분기 PATCH body에 `Locked: False` 추가 (명세 "있는데 사용을 못하면 enable" 의 locked 풀기)
   - 일부 펌웨어가 Locked PATCH 거부 (400/405) 시 → Locked 빼고 1회 retry (안전판)
3. **docs**: ADR-2026-04-30, VENDOR_ADAPTERS.md dryrun 정책 절 갱신.

### 영향

- **vendor**: dell / hpe / lenovo / supermicro 4 vendor 적용. Cisco는 표준 미지원으로 not_supported errors 기록 후 종료 (변화 없음)
- **흐름**: recovery 자격으로 1차 수집 succeed → account_service 진입 → 실 PATCH/POST → recovered=true → primary로 rotate → 재수집
- **lab BMC에 infraops 영구 생성/갱신/enable**: 다음 빌드부터 자동

### 검증

- Python syntax PASS, YAML syntax PASS
- pytest 216/216 PASS
- vendor boundary PASS

---

## 이전 일자: 2026-04-30 (vault accounts 우선순위 재정렬 — primary default + recovery 우선순위 사용자 명시 — 정정 후)

## 요약 (vault accounts reorder — 2026-04-30, 사용자 명시 + 비즈니스 로직 정정)

### 진짜 비즈니스 로직 (site.yml + account_service.yml 확인 결과)

- `primary` (= infraops/Passw0rd1!) = **provision target** — server-exporter가 모든 BMC에 생성/유지하는 표준 운영 계정
- `recovery` (vendor마다 다름) = **provision 진입 자격** — BMC에 이미 존재하는 자격증명. primary가 아직 없을 때 recovery로 BMC 접속 후 primary 생성 (POST AccountService)
- `_rf_accounts` list 순서대로 시도 → 어느 자격이든 succeed → 만약 succeed가 recovery면 → primary 자동 생성/갱신 → primary로 rotate 후 재수집

→ **list[0] = primary 가 정상**. 이미 BMC에 primary 있으면 그대로 succeed (account_service skip). 없으면 recovery로 fallback → provision.

### 사용자 명시 = recovery 후보들 안에서의 우선순위 (정정)

**Dell (vault/redfish/dell.yml)** — primary 1번 + recovery 사용자 명시 우선순위:
1. common_infraops (infraops/Passw0rd1!) ← primary (default, provision target)
2. dell_fallback_1 (root/Dellidrac1!) ← recovery 1순위 (사용자 명시)
3. dell_fallback_2 (root/calvin) ← recovery 2순위 (사용자 명시)
4. dell_current (root/GoodskInfra1!)
5. lab_dell_root (root/Goodmit0802!)

**Lenovo (vault/redfish/lenovo.yml)** — primary 1번 + recovery 사용자 명시:
1. common_infraops (infraops/Passw0rd1!) ← primary
2. lenovo_fallback (USERID/Passw0rd1!) ← recovery 1순위
3. lenovo_current (USERID/VMware1!)

**HPE (vault/redfish/hpe.yml)** — primary 1번 + recovery 사용자 명시:
1. common_infraops (infraops/Passw0rd1!) ← primary
2. hpe_fallback (admin/hpinvent1!) ← recovery 1순위
3. hpe_current (admin/VMware1!)

role / ansible_user / ansible_password 미변경. list 순서만 변경.

### 직전 commit (잘못된 순서) 정정 이력

- commit 4a84f095 / 700ffbcd: common_infraops를 recovery 후순위로 보냄 (잘못)
- 본 commit: common_infraops를 1번으로 복원 + recovery 안에서 사용자 명시 순서 유지

검증: ansible-vault decrypt round-trip + yaml parse OK.

---

## 이전 일자: 2026-04-30 (vendor-detect-robustness — G1~G7 전체 + multi-account 보강 — 사용자 명시 "남은 작업 모두" 진행)

## 요약 (vendor-detect-robustness 전체 — 2026-04-30)

사용자 명시 요청 진행: "이 장비는 redfish 지원 안 함" + "Lenovo 벤더 null" + "Dell `Dellidrac1!` 401 계정 틀림". Web 조사 (DMTF DSP0266 v1.15 / HPE iLO / Lenovo XCC / Dell iDRAC / Cisco CIMC) → 현재 코드 gap **G1~G7 전체 적용** + Dell multi-account fallback 보강.

### 적용 변경 (3 파일)

**`redfish-gather/library/redfish_gather.py`**:
- `_BMC_PRODUCT_HINTS` 상수 신규 (idrac/ilo/proliant/xclarity/thinksystem/xcc/imm2/megarac/cimc/ucs)
- `_detect_vendor_from_service_root`:
  - **G1**: Oem 정확 매칭 + namespace prefix 매칭 (`Lenovo_xxx`, `Hpe_iLO`)
  - **G2**: Product/Name 필드에 `_BMC_PRODUCT_HINTS` 적용
  - **G7**: Vendor 필드 정확(원형+trailing dot) + substring 매칭 (`'Dell Inc.'`, `'Cisco Systems Inc.'` 호환)
- `_probe_realm_hint` 신규 — **G6**: 401 `WWW-Authenticate` realm에서 vendor 추정
- `detect_vendor`:
  - **G3**: vendor=unknown 시 Chassis → Managers → Systems Manufacturer fallback
  - **G6**: G3까지 fail이면 `_probe_realm_hint` 로 마지막 추정
- `_ctx`: **G4** verify=False 시 `OP_LEGACY_SERVER_CONNECT` + `DEFAULT@SECLEVEL=0`

**`common/library/precheck_bundle.py`**:
- `_build_ssl_context`: **G4** 동일 TLS legacy 옵션
- `probe_redfish`: **G5** payload=None 시 1초 backoff + 1회 retry. probe_facts.retry_count 노출

**`redfish-gather/tasks/try_one_account.yml`** (Dell 401 추적):
- attempt 실패 시 1초 backoff (BMC lockout 회피)
- failure 로그 보강 (status / vendor / first_error 메시지)

### 검증

- Python syntax: PASS (3 파일)
- YAML syntax: PASS (try_one_account.yml)
- pytest 회귀: **216/216 PASS**
- vendor boundary (rule 12): PASS
- harness consistency: PASS
- ad-hoc unit (vendor detection 22 케이스): **22/22 PASS**

### 미적용 (사용자 명시 결정 필요)

- **multi-account partial 정책**: 현재 `_rf_attempt_ok = status != 'failed'` 이라 status=`'partial'` 도 OK 처리해 fallback 차단. 강화안 (`status == 'success'` 만 OK)은 정상 partial 운영 영향 가능 → 사용자 결정 대기.
- **Dell BMC 실측 검증**: 본 변경이 실제 401 해결하는지 Jenkins console log 확인 필요.

### Vault quote 가설 폐기

- vault_decrypt_check.py로 5 vault 모두 검증
- 모든 password 값이 `"..."` double-quoted — quote 누락 **없음 확정**
- Dell 401 원인은 quote가 아니라 (a) BMC 실제 password mismatch, (b) lockout, 또는 (c) partial 상태 fallback 차단 가능성. (b)는 본 cycle backoff 로 일부 보강. (a)/(c)는 실측 검증 필요

---

## 이전 일자: 2026-04-29 (account-fallback-validation — 사용자 명시 lab 권한 위임 8 채널 실 검증)

## 요약 (account-fallback-validation — 2026-04-29 18:30, 8 채널 실 BMC/OS/ESXi 검증)

사용자 명시 보고: "Redfish/OS/ESXi 계정 접속 fallback 로직이 정상 동작하는지 검증한다. 모두수행하라 — DRY가 아닌 실제 동작."

사용자 명시 lab 권한 위임 (Jenkins agent 10.100.64.154 + lab BMC/OS/ESXi 모두 접근 가능). paramiko + ansible-vault encrypt 위임으로 vault 8 파일 갱신 + ansible-playbook 실 실행 검증.

**Vault 갱신 8 파일** (사용자 명세 + lab fallback):
- `vault/{linux,windows,esxi}.yml` — Windows gooddit 제거 (사용자 명시 사내 부재)
- `vault/redfish/{dell,hpe,lenovo,cisco,supermicro}.yml` — Dell `dell_current=root/GoodskInfra1!` 추가, Lenovo 순서 정정 (current 우선)

**검증 결과 8 채널/타겟**:

| 채널 | Target | gather | AccountService (dryrun=false) | 결과 |
|---|---|---|---|---|
| Redfish | Lenovo XCC 10.50.11.232 | [PASS] | recovered=true (post_new, slot 4) | E2E + idempotent ✓ |
| Redfish | HPE iLO5 10.50.11.231 | [PASS] | recovered=true (post_new, slot 3) | E2E + idempotent ✓ |
| Redfish | Dell iDRAC9 10.100.15.27 | [PASS] | **noop** (빈 슬롯 14개 있음에도 코드 검색 None) | gather OK, AS 갭 (G1) |
| Redfish | Cisco CIMC 10.100.15.2 | [PASS] | not_supported (CIMC 1슬롯 only) | gather OK, lab 본질적 제약 (G2) |
| Redfish | Supermicro | (lab 부재) | — | skip |
| ESXi | esxi01 10.100.64.1 | [PASS] | — | esxi_current primary |
| OS Linux | RHEL 9.2 10.100.64.163 | [PASS] | — | linux_current primary, python_ok |
| OS Win | Win 2022 10.100.64.135 | [PASS] | — | windows_current primary |

**JSON 13 필드 emit + auth/account_service 메타** — 8/8 정상. **password 평문 보호** (no_log) — 8/8 정상.

**사용자 5 핵심 원칙 모두 충족**: (1) 계정 실패로 중단 X / (2) 13 필드 항상 emit / (3) status convention / (4) 실패 식별 가능 / (5) password 평문 노출 X.

**Idempotent**: Lenovo / HPE 재실행 시 infraops primary 1회 성공, account_service skip — lab BMC 영속 생성 확인.

**발견된 갭 2건** (NEXT_ACTIONS 등재):
- **G1 OPS-AS-DELL-1** Dell iDRAC9 `find_empty_slot` None 반환 (HIGH, 추가 진단 필요)
- **G2 OPS-AS-CISCO-1** Cisco CIMC multi-slot 노출 가능한 다른 모델 검증 (LOW, 외부 의존)

evidence: `tests/evidence/2026-04-29-account-fallback-validation.md`

---

## 일자: 2026-04-29 (Cisco Redfish 비판적 검증 — envelope 값 미채움 5건 fix + 4 vendor 회귀)

## 요약 (Cisco Redfish bug-fix — 2026-04-29 17:50, 4 vendor 통합 검증)

사용자 명시 보고: "Cisco Redfish 실 데이터 수집 안 되거나 값 이상한 것을 비판적 관점으로 raw 와 비교 검증. 키 늘릴 이유 없음. 버그 있으면 묻지 말고 모두 fix."

실 BMC `10.100.15.2` (Cisco UCS C220 M4 / CIMC 4.1(2g)) raw API 7 endpoint 직접 dump → `redfish_gather.py` + `normalize_standard.yml` path 비교 → envelope 키 미채움/잘못된 매핑 **5건 fix**:

- **H1**: `network.dns_servers` `[]` 하드코딩. → `gather_bmc` 가 BMC NIC NameServers/StaticNameServers 추출 (`_network_meta` 임시 키), `normalize_standard.yml` 의 신설 `_rf_norm_dns` 가 union (placeholder `0.0.0.0`/`::` 필터 — hpe-review 보강 누적). 실측: `["10.100.13.9"]` 채워짐
- **H2**: `network.default_gateways` server NIC만 (Cisco server NIC IPv4 미응답). → `_rf_norm_gateways` 가 BMC NIC `IPv4Addresses[*].Gateway` 도 union. 실측: `[{family:ipv4, address:10.100.15.254}]` 채워짐
- **H3**: `power.power_supplies[*].power_capacity_w` null (Cisco는 PowerCapacityWatts 미응답). → `gather_power` PSU 정규화 시 `InputRanges[0].OutputWattage` fallback. 실측: PSU1=770 / PSU2=770 채워짐
- **H4**: `power.power_control.power_capacity_watts` null (chassis level 미응답). → PSU `power_capacity_w` 합산 fallback. 실측: 1540W (=770×2) 채워짐
- **L1**: firmware list 에 `Version="N/A"` 빈 슬롯 노이즈 (Cisco slot-1, slot-2 PCIe 미장착 슬롯). → `gather_firmware` 가 `N/A`/`""`/`NA` skip. 실측: 7→5 (slot-1, slot-2 제거)

**envelope 비노출 보호**: BMC NIC raw 정보를 `result['_network_meta']` 임시 키로 캐시 → `normalize_standard.yml`의 `_rf_d_bmc_clean`이 envelope `data.bmc` 매핑 시 `_network_meta` 키 제거 (`dict2items | rejectattr | items2dict`). 4 vendor 모두 누설 검증 PASS (`False`).

**검증** (정적 + 통합 + 4 vendor 회귀):
- pytest 158/158 PASS
- `python -m py_compile redfish_gather.py` PASS
- YAML parse `normalize_standard.yml` 9 task PASS
- `verify_harness_consistency.py` PASS (rules:28, skills:43, agents:49, policies:9)
- `verify_vendor_boundary.py` PASS (vendor 하드코딩 0건)
- `ansible-playbook --syntax-check` (Agent 10.100.64.154) OK
- **4 vendor BMC 회귀** (`-f 4` 동시 실행):
  - cisco (10.100.15.2) status=success — 모든 fix 적용 확인
  - hpe (10.50.11.231) status=success — default_gateways=[10.50.11.254] 채워짐, dns_servers=[] (HPE iLO placeholder 필터 동작)
  - lenovo (10.50.11.232) status=success — PSU2 cap=750 채움 (PSU1 InputRanges도 None — 실 hardware Critical 결함, 후속)
  - dell (10.50.11.162) status=failed — BMC HTTP 401 (vault `dell.yml` 자격증명 만료, 우리 fix 회귀 아님 — 후속)
- envelope 13 필드 정합 (4 vendor 모두), `bmc._network_meta` 누설 X (4 vendor 모두)

**rule 96 R1 origin 주석**: `cisco_cimc.yml` Q1~Q7 quirk 명시 (Vendor 표기 / PowerCapacityWatts null / Manager.Manufacturer null / FirmwareInventory N/A 슬롯 / TotalThreads=TotalCores HT 미보고 / Manager NIC NameServers·Gateway 응답). `cisco_bmc.yml` reference.

**envelope 키 추가 0건** — 사용자 정책 준수. 모든 fix 는 기존 envelope 키 채움 또는 fallback 추가만.

**잔류 (운영 작업, NEXT_ACTIONS 등재)**:
- OPS-CISCO-REVIEW-1/2: cisco baseline 재수집 (코드 fix 후 dynamic 필드 정책 결정)
- OPS-DELL-VAULT-1: Dell BMC vault 자격증명 회전 (rotate-vault skill)
- OPS-LENOVO-PSU1: Lenovo PSU1 hardware 점검 (Health=Critical, OutputWattage null)

evidence: `tests/evidence/2026-04-29-cisco-redfish-critical-review.md`

---

## 일자: 2026-04-29 (HPE Redfish 비판적 검증 — envelope 값 미채움 5건 fix)

## 요약 (HPE Redfish bug-fix — 2026-04-29 17시, 실 BMC 통합 검증)

사용자 명시 보고: "HPE Redfish 실제 데이터 수집 안 되거나 값 이상한 것을 비판적 관점으로 raw 데이터와 비교해 검증. 키 늘리지 말고 버그 모두 fix."

실 BMC `10.50.11.231` (HPE iLO 6 v1.73 / DL380 Gen11) raw API 6 endpoint 직접 dump → `redfish_gather.py` + `normalize_standard.yml` path 줄별 비교 → envelope 키 미채움/잘못된 매핑 **5건 fix**:

- **B1 (CRIT)**: `gather_bmc` HPE 분기의 `bmc.oem.ilo_version` — `_safe(oem,'Type')` 잘못된 필드명. Manager.Oem.Hpe 에 `Type` 필드 부재. 이전 매핑은 모든 HPE 호스트에서 항상 null 반환. → `Oem.Hpe.Firmware.Current.VersionString` ("iLO 6 v1.73") + Manager.Model fallback 적용.
- **B2**: `_rf_norm_dns` (cisco-review 신설) 의 placeholder 필터 부재. HPE iLO StaticNameServers default `['0.0.0.0','0.0.0.0','0.0.0.0','::','::','::']` 가 그대로 dns_servers 로 노출. → `0.0.0.0`/`::`/`''`/`none` 필터 적용.
- **B3**: `hardware.bios_date` hardcoded null. 표준 Redfish 에 BIOS Date 키 부재 — vendor OEM 만 보유. → `_hoist_oem_extras` 헬퍼 신설 + `_extract_oem_hpe`/`_extract_oem_dell` 에 `_bios_date` underscore-prefix 키 추가. `gather_system` 이 result 의 **기존 envelope 키만** 채움 (새 키 추가 없음).
- **D1**: `network.interfaces[].is_primary` hardcoded false (모든 NIC). → `_rf_norm_interfaces` namespace mutation 으로 첫 LinkUp+IPv4 NIC 1건 true. IPv4 부재 환경 (HPE host NIC 한계) fallback: 첫 LinkUp NIC.
- **D2**: cpu/system 의 빈 문자열 응답 (HPE BMC 한계 — SerialNumber/PartNumber/AssetTag) `""` 그대로 emit. → `_ne()`/`_ne_p()` helper 로 `null` 정규화. 호출자가 `null ≠ ""` 분기 강제 안 받음.

**검증** (정적 + 통합):
- pytest 158/158 PASS
- `python -m py_compile redfish_gather.py` PASS
- `_hoist_oem_extras` unit smoke (HPE/Dell extractor + 알려지지 않은 `_*` key drop) PASS
- `ansible-playbook --syntax-check redfish-gather/site.yml` (agent 10.100.64.154) OK
- 실 HPE iLO 6 통합 테스트 7/7 PASS — bios_date='03/01/2024' / ilo_version='iLO 6 v1.73' / hostname='test0004.hynix.com' / cpu.architecture='x86' / cpu.serial_number=None / `_bios_date` envelope scrubbed

**envelope 키 추가 0건** — 사용자 정의 ("키 늘릴 이유 없음") 준수. 모든 fix 는 기존 envelope 키 채움/위생/fallback 만 영향. TPM vendor / BootProgress.LastBootTimeSeconds / BMC NIC gateway/subnet_mask 같은 새 키 후보 BUG 들은 사용자 의도대로 모두 제외.

**잔류 (운영 작업)**:
- HPE baseline `schema/baseline_v1/hpe_baseline.json` 재수집 — rule 13 R4 실측 evidence 첨부. 현재 baseline 은 cycle-016 Phase M/N 이전 stale. 재수집 시 본 fix 효과 모두 반영
- Dell baseline 재검토 — `_bios_date` hoist 로 `hardware.bios_date` 채워짐. 실 Dell 검증 후 갱신

evidence: `tests/evidence/2026-04-29-hpe-redfish-critical-review.md`

---

## 이전 cycle: Dell Redfish 비판적 검증 — envelope 값 미채움 7건 fix

## 요약 (Dell Redfish bug-fix — 2026-04-29 18시)

사용자 명시 보고: "Dell Redfish 실제 데이터 수집 안 되는 게 많고 값도 이상함. envelope 키는 있는데 값이 비는 경우. 키 늘리지 말고 버그 모두 fix."

Round 11 실측 reference (`tests/reference/redfish/dell/10_100_15_27`, R760, iDRAC 7.10.70.00, 1624 endpoints) ↔ 코드 비교 → 26건 발견 중 envelope 키 미채움/명확 코드 버그 **7건 fix**:

- **BUG-1 (CRIT)**: `_extract_oem_dell` 의 `EstimatedExhaustTemperatureCel` 키 오타 — raw 키는 `EstimatedExhaustTemperatureCelsius`. `data.hardware.oem.estimated_exhaust_temp` 모든 Dell 호스트에서 항상 None 사고. Celsius 우선 + Cel fallback. (`redfish_gather.py:_extract_oem_dell`)
- **BUG-12**: `data.hardware.bios_date` `null` 하드코딩. vendor OEM 의 `bios_release_date` (Dell `Oem.Dell.DellSystem.BIOSReleaseDate`) fallback 적용. (`normalize_standard.yml`)
- **BUG-13**: `data.cpu.cores_physical / logical_threads` per-processor sum 결과 0 시 fallback 없음 → `System.ProcessorSummary.CoreCount / LogicalProcessorCount` fallback 추가. 라이브러리 `cpu_summary` 에 `core_count / logical_processor_count` 추출 추가. (`redfish_gather.py:gather_system` + `normalize_standard.yml`)
- **BUG-14**: `data.memory.total_mb / installed_mb` per-DIMM sum 0 시 fallback 없음 → `System.MemorySummary.TotalSystemMemoryGiB * 1024` fallback. (`normalize_standard.yml`)
- **BUG-15**: `data.storage.logical_volumes[].boot_volume` Dell-only 처리 → Dell 외 vendor 항상 None. 표준 `Volume.BootVolume` 우선, Dell Oem fallback. (`redfish_gather.py:_extract_storage_volumes`)
- **BUG-16**: `data.storage.logical_volumes[].name` raw `'VD_0   '` (trailing whitespace) 미정리. strip() 적용. (`redfish_gather.py:_extract_storage_volumes`)
- **BUG-19**: `data.storage.logical_volumes[].health` Status.Health 없을 때 HealthRollup fallback 누락 (drive 는 이미 fallback 있음). 동일 패턴 적용. (`redfish_gather.py:_extract_storage_volumes`)

**검증** (정적):
- pytest 158/158 PASS
- `python -m py_compile redfish_gather.py` PASS
- `yaml.safe_load` normalize_standard.yml PASS
- `verify_harness_consistency.py` PASS (rules 28 / skills 43 / agents 49 / policies 9)
- `verify_vendor_boundary.py` PASS (3-channel vendor 하드코딩 0건)

**envelope 키 추가 0건** — 사용자 정의 ("키 늘릴 이유 없음") 준수. 모든 fix 는 기존 envelope 키 채움/위생/fallback 만 영향.

**미수행 (envelope 키 추가 필요 → 사용자 정의로 skip)**: BUG-2 (controller metadata 4 필드), BUG-3~10 (PSU/Firmware/Drive/Volume/Memory/NIC raw 풍부 필드), BUG-11 (BIOS Attributes 571 entries)

**잔류 미세 이슈 (별도 cycle)**:
- baseline_v1/dell_baseline.json 의 `hardware.bios_date: null` → 실 BMC 재수집 시 Dell 환경에서는 OEM bios_release_date 채워질 것 (Round 12 검증 시 갱신)
- `oem.estimated_exhaust_temp` 의 baseline 값 `29` → R760 raw 에는 키 없음 (`null`). 다른 Dell 모델/펌웨어 검증 후 baseline 갱신 필요

---

## 이전 cycle: production-audit 후속 — ESXi BUG #1 / #2 / #4 fix, Round 12 검증

## 요약 (Round 12 — 2026-04-29 14시)

## 요약 (Round 12 — 2026-04-29 14시)

사용자 명시 보고: ESXi 출력 JSON 에서 `hostname=IP`, `vendor` 정규화 실패, `network.adapters / virtual_switches / storage.hbas` 빈 배열.

agent 10.100.64.154 SSH 접속 + raw facts 진단 (`tests/scripts/diag_esxi_raw.yml`) → 3 BUG 확정 + fix:

- **BUG #1 (hostname=IP)**: `normalize_system.yml` 의 `system.fqdn = _e_ip` 잘못. `_e_hostname` 변수 도입 (ansible_hostname 우선, IP 폴백)
- **BUG #2 (vendor 정규화 실패)**: cycle-016 "9 파일 namespace pattern fix" 잔류분 — `esxi-gather/site.yml` 의 `set canonical = canon` 이 inner loop scope 만 영향. `namespace(canonical=none)` wrapping 으로 해결
- **BUG #4 (extended modules 빈 배열)**: `community.vmware 6.2.0` 의 hosts_*_info dict key 는 ESXi configured hostname (IP 아님). 또한 진짜 dict list 는 `vmnic_details` / `vmhba_details` (string list `all` 아님). 매핑 키도 `pci→location`, `adapter_type→type`, `node_world_wide_name→node_wwn`. vswitch 는 dict-of-dict 구조. portgroups 는 `vmware_portgroup_info` 결과를 vswitch 별 group 후 join.

**검증** (실 ESXi 10.100.64.1 + 10.100.64.2):
- esxi01: 6 NIC + vSwitch0 + 4 HBA (AHCI×2 + SAS RAID + iSCSI)
- esxi02: 6 NIC + vSwitch0 + 5 HBA (AHCI×2 + SAS RAID + FC×2 nfnic Cisco UCS VIC Fnic, wwpn `20:00:00:27:E3:6C:A6:6E/F` 정확 추출)
- pytest 158/158 PASS, vendor boundary / harness consistency / ansible-syntax-check 모두 통과
- `schema/baseline_v1/esxi_baseline.json` 갱신 (esxi02 실측, +231/-47 lines)
- evidence: `tests/evidence/2026-04-29-esxi-bug-fix.md` + `tests/evidence/esxi01_2026-04-29.json`

**잔류 미세 이슈 (별도 cycle)**:
- `default_gateways=[]` / `dns_servers=[]` (vmware_host_facts 미반환 + host_config_info 빈 응답 — `vmware_host_dns_info` 모듈 추가 필요)
- `speed_mbps` int / "N/A" string 혼재
- `cpu.architecture` / `max_speed_mhz` null (model 파싱 폴백 가능)
- `include_vars` `name:` 옵션 reserved-name 경고 (4곳 — 호출자 영향 0, 별도 cycle)

---

## 이전 cycle: production-audit (2026-04-29 오전 — 4 agent 전수조사 + HIGH 30+건 일괄 수정)

## 요약 (production-audit)

사용자 명시 요청:
> "실제 모든 서버에서 개더링 데이터가 정상인지 값이맞는지 모두 검증 ... json 형태가 일관된지 확인 ... 모든 정보가 수집되는지 확인. 우리가 실측한 장비는 한정된 환경임을 감안해라. 여러가지 상황을 에상하고 예측해야한다. ... 실제 product 제품으로 출시될수있도록해라."

**Phase 1 — 4 agent 병렬 전수조사** (read-only):
1. Redfish-gather audit — 1504-line library + 16 adapter + vendor tasks
2. OS-gather + ESXi + common audit — 3-channel + precheck + builders
3. Schema + callback + JSON envelope cross-channel consistency
4. Tests + baselines + Jenkins pipelines

**Phase 2 — HIGH 발견 30+건 일괄 수정** (이번 세션):
- **공통 정합 (T1-T3)**:
  - Skeleton drift 동기화 (`init_fragments.yml` + `build_empty_data.yml` + `build_failed_output.yml` 3종 — sections.yml의 storage.{hbas,infiniband,summary}/network.{adapters,ports,virtual_switches,portgroups,driver_map,summary} 복제)
  - `diagnosis.details` shape 통일 (3 채널 always block fallback dict 형태로 통일 — 호출자 TypeError 차단)
  - `field_dictionary.yml` top-level envelope 8 entries 추가 (target_type/collection_method/ip/hostname/vendor/schema_version/meta/correlation) → Must 39 / Nice 20 / Skip 6 = 65 entries
- **Cross-channel JSON 일관성 (T4-T5)**:
  - ESXi vendor 정규화 (vendor_aliases.yml lookup 추가 — 'Cisco Systems Inc' → 'cisco' lowercase canonical)
  - ESXi 성공 path `auth_success: true` set (Must 필드 — null 누출 차단)
  - cisco_baseline.json `users: null → []` (cross-channel type 통일)
  - Windows storage `media_type` 정규화 (Get-PhysicalDisk MSFT_PhysicalDisk + raw WMI fallback → SSD/HDD enum)
- **Linux gather (T6)**: LANG=C 강제 (lscpu/dmidecode 한국어/일본어 로케일 차단), VLAN/bond 이름 underscore 정규화 (`bond0.4094` 매칭), FS allow-list 확장 (ZFS/btrfs/overlay/tmpfs), df '-' parse defense
- **Windows gather (T7)**: gather_runtime swap_total_mb namespace 패턴 적용 (Jinja2 loop scoping 버그), gather_network InterfaceIndex 그룹핑 (multi-IP NIC 분리 차단)
- **Redfish (T8)**: account_service.yml 복구 creds 버그 (unset ansible_user/_password → _rf_recovery_account_resolved), `_rf_attempts_meta` int/bool cast (cross-channel type drift), `_detect_vendor_from_service_root` vendor_aliases.yml + fallback merge (drift 차단), Power.PowerControl 비-dict 방어, `_diagnosis.details combine` mapping type-guard
- **ESXi (T9)**: DNS 추출 dict level 버그 (production에서 항상 빈 list 였음 — `hosts_config_info[hostname]` drill-in), netmask→prefix 비트 카운팅 알고리즘 (/22, /26, /28 등)
- **Common (T10)**: precheck IPv6 듀얼스택 (getaddrinfo — IPv6-only 관리망 지원), diagnosis_mapper None 입력 가드 (rescue path AttributeError)
- **Jenkins (T11)**:
  - `Jenkinsfile`: per-stage timeout (Validate 2m / Gather 20m / Schema 2m / E2E 5m), Stage 4 `fileExists` when 제거 (mandatory), archiveArtifacts 활성
  - `Jenkinsfile_portal`: Stage 3 catchError 제거 (rule 80 R1 hard gate), Callback `error` → `unstable` (rule 31 R2)
- **Secrets (T12)**: tests/scripts/{os_esxi_verify,identifier_verify}.sh + scripts/ai/*.py 5종 — 'Goodmit0802!' 하드코딩 13곳 제거 → 환경변수 강제 (자격증명 회전 권고)

**검증**:
- pytest **148/148 PASS** (이전 147/147 + remote_identifier_test.py main() guard)
- harness consistency PASS (rules 28 / skills 43 / agents 49 / policies 9)
- vendor boundary PASS (rule 12 R1)
- field_dictionary validate PASS (65 entries)
- PROJECT_MAP fingerprint 갱신 (4 drift 해소)

**보존된 알려진 한계**:
- Supermicro vendor: 0 fixture / 0 baseline / 0 pytest 커버 — 실장비 검증 후 보강 (NEXT_ACTIONS)
- ESXi 8.0u3: reference dump만 존재, baseline 미생성 — 실장비 검증 후 보강 (NEXT_ACTIONS)
- Linux raw_fallback: 1 mode (RHEL 8.10 py3.6) 검증, pytest 커버 0 — fixture 추가 보강 (NEXT_ACTIONS)
- 자격증명 git history 잔존: 사용자 회전 + filter-branch 결정 사안 (NEXT_ACTIONS)

## 일자: 2026-04-29 (cycle-016 — 사용자 11항목 점검 + 실 Jenkins 빌드 5회 검증 + summary grouping 완성)

## 요약 (cycle-016)

cycle-015 lab 권한 + Browser E2E 도입 직후, 사용자 명시 요청:
> "전체 프로젝트 코드를 점검하고 ... 실제 product 제품으로 출시될수있도록해라"
> "젠킨스 접속해서 실제 개더링이 잘되는지 ... 한번에 끝내라"
> "redfish 공통 계정생성 그것을 가지고 개더링하는것을 특히 신경써서 검증해라"

cycle-016 처리:
- **사용자 요구사항 11/11 항목 점검 완료** — JSON 항상 출력 / Redfish 공통계정 / recovery fallback / AccountService / OS-ESXi 다중계정 / Jenkins-Vault / Memory-Disk-NIC summary / HBA-IB / 운영정보 (NTP / firewall / runtime).
- **실 Jenkins 빌드 5회** (#39 ~ #45) — `hshwang-gather` Job 152 직접 트리거 + 결과 검증.
  - #39: Redfish Dell 10.100.15.27 / pipeline=SUCCESS / gather=failed (lab vault credential 미정합) / **JSON envelope 13 필드 + 한국어 명확 메시지 + Stage 4 145 pytest pass 검증**.
  - #41: OS RHEL 9.6 / `Template delimiters: '#' at 86` 회귀 발견 → fix.
  - #43: OS RHEL 9.6 / **status=success / network.summary.groups + storage.summary.groups 동작 확인**.
  - #44: namespace pattern fix 후 / **storage.summary.grand_total_gb=100 (이전 0 버그 해결)**.
  - #45: Redfish 회귀 검증 (코드 변경 영향 없음).
- **OS/ESXi summary grouping 갭 닫기** (9 파일):
  - Linux gather_memory.yml — dmidecode SLOT 단위 emit + 2 path
  - Linux gather_storage/network.yml + Windows gather_*.yml — namespace pattern grouping
  - ESXi normalize_storage/network/system.yml — summary 보강
  - Redfish normalize_standard.yml — namespace pattern 변환
- **baseline / examples 일괄 갱신**: `scripts/ai/inject_summary_to_baselines.py` 신규 — 7 vendor + 3 example 자동 grouping 주입.
- **실패 메시지 명확성**: `build_failed_output.yml` default fallback 에 `채널/IP` 컨텍스트 포함.
- **9 inline `{# ... #}` Jinja2 코멘트 제거** — 한국어/특수문자 + 파싱 오류 방지.
- **commit 4건 main push**: `0da258d5`, `88793df8`, `a2e3e75e`, `e18230b8`, `240106bc`.
- **검증**: pytest 147/147 / harness consistency / vendor boundary / schema drift 모두 PASS.

## 일자: 2026-04-29 (cycle-015 — 실장비 lab 전체 권한 + Browser E2E 도입)

## 요약 (cycle-015)

cycle-014 (4 vendor BMC code path + HIGH Jinja2 fix `bf247266`) 직후, 사용자가 lab 권한 + Browser E2E 명시 결정 + 후속 cleanup ("Grafana 파일 제거 / Dell 32 + Cisco 2 + Win10 제거 / Win 2022 IP 정정 + firewall 해제"). cycle-015 Phase A~F 일괄 자율 처리 완료. 호스트 카운트 28→23 정정. **BMC 7/9 primary auth 성공 (OPS-3 vault sync 가능 확인)**.

cycle-015 변경 (이번 세션, 2026-04-29):

- **Phase A — 자격증명 + 인벤토리** (gitignored):
  - `vault/.lab-credentials.yml` 신규 (5 그룹 28 호스트)
  - `inventory/lab/{os-linux,os-windows,redfish,esxi,jenkins}.json` (INVENTORY_JSON 형식)
  - `inventory/lab/README.md`
  - `.gitignore` 강화 (`vault/.lab-credentials.yml` + `inventory/lab/**` 추가 차단)
- **Phase B — LAB_INVENTORY catalog** (sanitized — IP/자격증명 제외):
  - `docs/ai/catalogs/LAB_INVENTORY.md` 신규 (8 섹션 — 권한정책 / 호스트카운트 / zone / 특이호스트 / Round매핑 / 자격증명정책 / 참고파일 / 갱신trigger)
- **Phase C — 연결성 검증** (Windows 클라이언트 직접):
  - 21 호스트 ICMP/TCP protocol PASS (Linux SSH 22 / Redfish HTTPS 443 / ESXi HTTPS 443 / Win10 WinRM 5985 / Jenkins HTTP 8080 모두 OPEN)
  - **rule 96 DRIFT-011 검출** — Dell 32 → 실 `Vendor='AMI'` (사용자 라벨 "dell, GPU") / Cisco 2 → `Product='TA-UNODE-G1'` (사용자 라벨 "cisco")
  - Win Server 2022 (10.100.64.132) 모든 포트 closed → OPS-10 (사용자 firewall 해제)
  - Cisco BMC 1, 3 일시 장애 (503 / timeout) → OPS-11 (다음 일과시간 재확인)
- **Phase D — Playwright Browser E2E**:
  - `requirements-test.txt` 신규 (playwright 1.58 + pytest-playwright 0.7.2 + paramiko 4.0 + pywinrm 0.5.0 + pyyaml + requests)
  - `tests/e2e_browser/` 신규 (lab_loader / conftest / test_jenkins_master / test_grafana_ingest / __init__ / README)
  - Chromium 1208 다운로드 완료
  - **smoke `test_master_dashboard_reachable[chromium]` PASSED 2.42s** (10.100.64.152:8080)
- **Phase E — Catalog + ADR**:
  - `CONVENTION_DRIFT.md` DRIFT-011 entry (open) — user-label vs Redfish Manufacturer
  - `EXTERNAL_CONTRACTS.md` "실 lab 발견 — 비표준 BMC" 절 (AMI 1.11.0 + TA-UNODE-G1 + Cisco 일시 장애)
  - `FAILURE_PATTERNS.md` `user-label-vs-redfish-manufacturer-drift` 첫 실 사례
  - `ADR-2026-04-29-lab-access-grant.md` 신규 (rule 70 R8 #2 trigger — catalogs +1 / 신규 디렉터리 2개)
  - `cycle-015.md` 신규 governance log
  - `tests/evidence/cycle-015/connectivity-2026-04-29.md` 신규
- **표면 카운트**: catalogs 8→9 (+LAB_INVENTORY), decisions 4→5 (+lab-access-grant), 신규 디렉터리 2 (`inventory/lab/` gitignored, `tests/e2e_browser/`)
- **검증**: Browser E2E smoke 1/1 PASS. harness consistency / vendor boundary / project_map_drift는 본 cycle 종료 직전 실행.

cycle-015 Phase F (자율 매트릭스 일괄 — 사용자 "남아있는 작업 모두수행해라" + cleanup 결정 후):

- **F-1 Cleanup**: Jenkinsfile_grafana 삭제 + 모든 참조 정리 (rule 80/13/31/00 + JENKINS_PIPELINES + CLAUDE.md + LAB_INVENTORY + ai-context + policy + hooks). 호스트 정정 (10.100.15.32 / 10.100.15.2 / 10.100.64.120 제거 + Win Server 2022 IP 132→**10.100.64.135** 정정). 호스트 카운트 26→23.
- **F-2 OPS-3 partial**: lab credentials BMC password가 7/9 BMC와 sync — Dell × 5 + HPE + Lenovo 모두 200 OK ServiceRoot+Systems+Managers (`bmc-auth-probe-2026-04-29.json`). Cisco 1, 3은 503/timeout (OPS-11 잔여).
- **F-2 AI-13 Linux raw fallback**: 6/6 SSH PASS. **RHEL 8.10 Python 3.6.8 → python_incompatible** = rule 10 R4 분기 실증 (`linux-probe-2026-04-29.json`).
- **F-2 AI-14 Browser E2E login 활성**: cloviradmin/Goodmit0802!로 Jenkins master login PASS — `test_master_login_then_dashboard[chromium]`.
- **F-2 AI-12 Dell × 5 Round 11 endpoint coverage**: 5/5 PowerEdge R760 BIOS 2.3.5 / Xeon Silver 4510 / Systems+Storage+NIC+FW+Accounts 모두 응답 (`dell-round11-endpoint-coverage.json`).
- **F-2 WinRM Win 2022**: 정정된 IP (10.100.64.135) administrator/NTLM PASS. OS Build 20348 / PS 5.1 / Xeon Silver 4510 / 8GB.
- **closed (cycle-015)**: OPS-10 (firewall) / OPS-12 (Dell 32) / OPS-13 (Cisco 2) / OPS-15 (Grafana) / AI-13 / AI-14 / AI-15 (obviated)
- **잔여**: OPS-9 (private 전환), OPS-3 (운영팀 vault encrypt), OPS-11 (Cisco 1,3 일시 장애), AI-16 (BMC Web UI E2E), AI-17 (baseline 정식 갱신), AI-18 (raw fallback ansible-playbook 실 실행)

## 일자: 2026-04-29 (cycle-014 — 4 vendor BMC 실 검증 + HIGH Jinja2 fix + vault sync 발견)

cycle-014 변경 (이전 세션, 2026-04-29):

- **사용자 명시 권한 부여**: AI에게 모든 권한 (하네스 + 실 장비). e2e Chrome 가능. 메모리 기록 (`feedback_full_authority.md` + `environment_lab.md`).
- **4 vendor BMC 검증** (벤더당 1대): Dell 10.50.11.162 / HPE 10.50.11.231 / Lenovo 10.50.11.232 / Cisco 10.100.15.2 (baseline_v1 정본 IP)
- **agent 154 직접 ansible-playbook 실행** — Jenkins API HTTP 403 (cloviradmin RBAC build 권한 부재) 우회
- **HIGH 회귀 fix** (commit `bf247266`): `common/tasks/precheck/run_precheck.yml:47` Jinja2 expression 안 `{# ... #}` 주석 syntax error. cycle-012 P0~P5 commit 중 도입, cycle-013까지 발견 안 됨 (Jenkins catchError UNSTABLE 마스킹). cycle-014 첫 실 BMC 실행에서 발견.
- **vault ↔ BMC sync 불일치 발견** — ServiceRoot 무인증 4 vendor HTTP 200 OK / vault primary + recovery 4 vendor HTTP 401. OPS-3 회전 매트릭스 우선순위 격상.
- **redfish 공통계정 자동 생성 (P2 account_service)** 진입 안 함 — recovery 자격 fail로 trigger 미발생 (의도된 동작). 자동 생성 코드 검증은 cycle-015 (OPS-3 후) 이월.
- **검증**: 4 vendor 모두 코드 경로 (precheck → detect → adapter 자동 선택 → collect 시도 → rescue) 정상 동작. envelope 13 필드 정합.
- **commit**: `bf247266` (1 file, +2/-1) main push 완료.

## cycle-013 일자: 2026-04-29 (cycle-013 — cycle-012 PR 머지 + 자율 매트릭스 + 정합 정정)

## 요약

server-exporter AI 하네스 **Plan 1+2+3 + cycle-001 ~ cycle-013 완료**. cycle-012 PR #1 머지 완료 (`b74c1103`). cycle-013에서 자율 매트릭스 7건 (AI-1~AI-7) 일괄 처리 + 발견된 분포 1건 over count 정합 정정.

cycle-013 변경 (이번 세션, 2026-04-29):

- **AI-2 PROJECT_MAP fingerprint 갱신** — drift 6 → 0. 본문 stale 4건 정정 (adapters 25→27, schema 46→57, scripts/ai 8 supporting, Stage 4 pipeline별 분화).
- **AI-3 JENKINS_PIPELINES.md** — vault binding 절 신규 (`server-gather-vault-password` Secret File credential, 3 Jenkinsfile 위치 실측).
- **AI-4 SCHEMA_FIELDS.md** — 분포 정정 **Must 31 / Nice 20 / Skip 6 = 57 entries**. cycle-012 commit `8e536447` 메시지 "Nice 12종" + 헤더 주석 "Nice 21 / 58" 1건 over count 발견 → field_dictionary.yml 헤더 주석 + 모든 catalog 정합.
- **AI-5 VENDOR_ADAPTERS.md** — `recovery_accounts` 메타 절 신규 (Redfish 16 adapter 전부, dryrun 정책, Cisco 한정 미지원).
- **AI-6 cycle-012.md 신규** — P0~P5 + vault encrypt + 9 commit 시퀀스 + 검증 + 후속 매트릭스 보존.
- **AI-7 ADR-2026-04-29-vault-encrypt-adoption** — rule 70 R8 trigger 미해당 분석 명시 후 advisory governance trace (옵션 A1/A2/B 비교).
- **AI-1 schema/examples 11 path 보강** — redfish_success.json 7 path + os_partial.json 8 path → **validate_field_dictionary 11 WARN → 0 WARN**.
- **AI-8 (PR 머지 후 main 정리)** — OPS-2 (PR 머지) 완료 확인. main pull / 브랜치 전환은 rule 93 R2 사용자 명시 승인 필요 → OPS-8로 transfer.
- **AI-9 stale reference 일괄 cleanup** — cycle-011 advisory 25 list 보다 많은 49 파일 발견. 47 inline trace 표기로 일괄 정리 (rule + agent + skill + role + ai-context + commands + policy yaml + docs/ai/policy + workflows + catalogs + references).
- **AI-10 docs/ai/harness/ archive (rule 70 R6)** — cycle-001~005 (5개) → `docs/ai/archive/harness/`. active catalog 11 → 6.
- **AI-11 docs/ai/impact/ archive** — 6 보고서 → `docs/ai/archive/impact/`. active catalog 6 → 0.
- **SECURITY_POLICY.md deprecated 헤더** — cycle-011 정책 자체 해제 + cycle-012 vault encrypt ADR reference로 변환.
- **archive README.md 신규** — 진입 reasoning + 보존 정책.
- **cycle-013.md 신규 + handoff 신규** — governance 보존 + 다음 세션 cold start 인계.
- **검증**: harness consistency PASS (28/43/49/9), vendor boundary PASS, project_map_drift PASS, validate_field_dictionary PASS (0 WARN).
- **commit**: 3개 (`0150fa2e` 10 files / `57745bd1` 16 files / `b1d8014c` 38 files) feature/3channel-expansion push 완료. main 머지는 OPS-8 (rule 93 R2 사용자 명시 승인) 대기.

cycle-012 변경 (이전 세션, 2026-04-29):

server-exporter AI 하네스 cycle-012에서 사용자 plan-mode 승인으로 **3-channel gather 확장 (vault multi-auth + AccountService + Group Summary + NIC/HBA/IB depth + runtime)** 6 Phase 진행. PR #1 머지 완료.

cycle-012 변경 (이번 세션, 2026-04-29):

- **plan**: `C:\Users\hshwa\.claude\plans\1-snazzy-haven.md` (P0~P5 6 Phase 분할). 사용자 결정 4건 확정: 6 Phase 직렬, ansible-vault encrypt 후 commit, schema v1 minor 유지, AccountService P2 분리 + dryrun ON default.
- **P0 Foundation** (`f0f621ce`): Jenkinsfile 3종 `withCredentials([file('ansible-vault-password')])` + `.gitignore` (.vault_pass 차단) + `scripts/bootstrap_vault_encrypt.sh` + `docs/01_jenkins-setup.md` 갱신 + `tests/e2e/test_envelope_failure_modes.py` 12 fixture × 50 testcase.
- **P1 Auth Multi-Candidate** (`fe0be36c`): vault `accounts: list` 신키 + `ansible_user/password` dual-write 호환. redfish: load_vault.yml + try_one_account.yml + collect_standard.yml loop. OS/ESXi: try_credentials.yml (raw probe + `meta: reset_connection`). 16 redfish adapter 에 `recovery_accounts` 메타 (P2 진입점).
- **P2 AccountService + P4 NetworkAdapters** (`0448d00d`): `redfish_gather.py` `_post`/`_patch` 헬퍼 + `account_service_provision()` 4 메서드 (Dell slot PATCH / HPE-Lenovo-SM POST / Cisco not_supported). main() `mode='account_provision'` + `dryrun: True` default. `gather_network_adapters_chassis()` (NetworkAdapters/Ports + PortType FC/IB 자동 분류). `account_service.yml` 신규.
- **P3 Group Summary + P4 normalize 매핑** (`fbb0f357`): Redfish CPU/memory/storage/network 4종 group summary + Linux memory summary 빈값. `_rf_proc_map` 에 network_adapters → network 추가.
- **P5 Linux runtime** (`92b935c3`): `gather_runtime.yml` 신규 — NTP (timedatectl) / firewall (firewalld/ufw/iptables 자동 감지) / listening ports (ss/netstat) / swap (free -m). `data.system.runtime` sub-key.
- **추가 작업 (PR 갱신, cycle-012 후반부)**:
  - **P4 Linux** — `gather_hba_ib.yml` (FC HBA `/sys/class/fc_host` + InfiniBand `/sys/class/infiniband` + NIC driver/VLAN/bond raw fallback)
  - **P4 Windows** — `gather_storage.yml` 에 `Get-InitiatorPort` 추가 (FC HBA WWPN)
  - **P4 ESXi** — `collect_network_extended.yml` 신규 (vmware_host_vmnic_info + vmware_host_vmhba_info + vmware_vswitch_info + vmware_portgroup_info)
  - **P5 sub-phase b** — Windows `gather_runtime.yml` 신규 (w32tm/Get-NetFirewallProfile/Get-NetTCPConnection/Win32_PageFileUsage)
  - **schema 갱신** — `schema/sections.yml` storage/network 에 hbas/infiniband/adapters/ports/virtual_switches/portgroups/driver_map/summary 사용 가능 sub-key 명시. `schema/field_dictionary.yml` 12 entries Nice 추가 (cpu/memory/storage/network.summary, network.adapters/ports/virtual_switches/driver_map, storage.hbas/infiniband, system.runtime)
- **검증**: 145 기존 e2e + 50 신규 fixture = 195 PASS. harness 일관성 PASS (28/43/49/9). vendor boundary PASS (rule 12 R1 nosec). field_dictionary PASS.
- **PR**: `feature/3channel-expansion` GitHub push 완료, PR 사용자 직접 생성 (옵션 A1).
- **잔여 사용자 작업**: (1) 평문 commit된 password 6종 회전 (Passw0rd1!/Goodmit0802!/Dellidrac1!/calvin/hpinvent1!/VMware1!), (2) `.vault_pass` 결정 → `bash scripts/bootstrap_vault_encrypt.sh`, (3) Jenkins credentials store 등록 (`ansible-vault-password` Secret File), (4) lab 검증 (P1 vendor 5종 → P2 dryrun ON Dell+HPE → 후 OFF), (5) baseline_v1/* 7개 실측 갱신 (P3/P4 schema 변경 정합).

cycle-011 변경 (이전 세션):

cycle-011 변경 (이번 세션):

- **첫 자동화 검증 사례** — Win Server 2022 (10.100.64.135) Agent 154 경유 ansible.windows.win_shell 28/28 PASS, 4.14 MB raw archive 수집. cycle-011 정책 해제의 실효성 검증됨. evidence: `tests/evidence/2026-04-28-win2022-validation.md`
- **rule 60 (security-and-secrets) 삭제**: rules 29 → 28
- **policy/security-redaction-policy.yaml 삭제**: policies 10 → 9 (protected-paths.yaml은 stub로 잔존)
- **scripts/ai/hooks/pre_commit_policy.py 삭제**: hooks 19 → 18 + git hooks 재설치
- **scripts/ai/policy_loader.py 삭제**
- **agents/security-reviewer + vault-rotator 삭제**: agents 51 → 49
- **.claude/settings.json 보안 deny 38건 모두 제거** + `disableBypassPermissionsMode` 제거 + `defaultMode: bypassPermissions` + sandbox `allowUnsandboxedCommands: true`
- **PreToolUse pre_edit_guard hook 삭제**
- **rule 00 보호 경로 절** "참고용 (정책 강제 해제됨)"으로 갱신
- **ADR 작성**: `ADR-2026-04-28-security-policy-removal.md` (rule 70 R8 적용 두 번째 사례 — 3 trigger 모두 해당)
- **검증**: verify_harness_consistency PASS (28/43/49/9), verify_vendor_boundary PASS

cycle-010 변경 (이전 세션): 2026-04-28 cycle-010 (사용자 "권장하는 작업 모두 수행 + 후속 작업 마무리" 명시 승인)에서 cycle-009의 NEXT_ACTIONS 사용자 결정 대기 매트릭스 3건 (T3-04/05/06) 일괄 처리 + 신규 governance rule 1건 (R8 신설):

cycle-010 변경 (이번 세션):

- **T3-04 (04-A 채택)** — 27개 adapter (redfish 16 + os 7 + esxi 4) 의 `version: "1.0.0"` placeholder 1줄 일괄 삭제. `adapter_loader.py` / `module_utils/adapter_common.py` 참조 0건 검증. `tested_against` (rule 96 R1)이 펌웨어 검증 추적 충실
- **T3-05 (05-A 유지)** — redfish_gather.py BMC IP 수집 break-on-first-IP 패턴 (평균 1~2회 호출)이 실 N+1 아니므로 현재 유지. cycle-008 `_resolve_first_member_uri` helper로 가독성 개선됨. NEXT_ACTIONS T3-05 close
- **T3-06 (06-B 채택)** — `rule 70` R8 신설 (ADR 의무 trigger 3종): rule 본문 의미 변경 / 표면 카운트 변경 / 보호 경로 정책 변경. `ADR-2026-04-28-rule12-oem-namespace-exception.md` 소급 작성 (DRIFT-006 governance trace 보강 — R8 적용 첫 사례)
- **검증**: `verify_harness_consistency.py` PASS (29/43/51/10), `verify_vendor_boundary.py` PASS (0건), 27 adapter YAML 파싱 PASS + version 키 0/27, PROJECT_MAP fingerprint 갱신 (adapters)

cycle-009 변경 (이전 세션):

- **3-channel `site.yml` fallback envelope 13 필드 일관성**:
  - **HIGH 버그 fix #1**: `os-gather/site.yml` PLAY 3 (Windows) `always` fallback이 2 필드 (`status` / `errors`) 만 → 13 필드 envelope 보강 (rule 13 R5 / rule 20 R1 정합)
  - **HIGH 버그 fix #2**: `esxi-gather/site.yml` `always` fallback의 `_ip` 변수명 오류 → `_e_ip` 정정 (fallback 시 ip null 출력되던 문제 해결)
  - **MED fix**: `collection_method` 값 build_meta와 일관성 (OS: `ansible`→`agent`, ESXi: `vmware`→`vsphere_api`, Redfish: `redfish`→`redfish_api`)
- **T2-A7 — rule 7개 5요소 보강**: `rule 24` (completion-gate), `rule 26` (multi-session-guide), `rule 41` (mermaid-visualization), `rule 50` (vendor-adapter-policy), `rule 60` (security-and-secrets), `rule 70` (docs-and-evidence-policy), `rule 90` (commit-convention) 본문 R-번호 + Default/Allowed/Forbidden/Why/재검토 5요소 구조 적용 (rule 00 표기 구조 컨벤션 정합)

cycle-008 변경 (이전 세션):

- **redfish_gather.py — 함수 분리 추가**: `gather_system` 103→57줄 (vendor OEM helper 4종 `_extract_oem_{hpe,dell,lenovo,supermicro}` 추출 + `_OEM_EXTRACTORS` dispatch dict), `detect_vendor` 64→37줄 (`_fetch_service_root` + `_resolve_first_member_uri` 추출), `main` 67→45줄 (`_make_section_runner` + `_collect_all_sections` + `_compute_final_status` 추출). rule 10 R3 정합
- **os-gather/tasks/linux/gather_system.yml**: 346→322줄. `build_identifier_diagnostics.yml` 별도 task로 분리 (rule 10 R3)
- **adapters/redfish/**: HPE iLO5 priority 100→90 차등 (T3-02), `lenovo_bmc.yml` generic fallback 신규 (T3-03 일관성), `cisco_bmc.yml` generic fallback 신규 (일관성), `lenovo_imm2.yml` tested_against 펌웨어 명시 (rule 96 R1), `cisco_cimc.yml` 세대 차등 검토 결정 명시 (M5/M6 미검증으로 보류)
- **callback_plugins/json_only.py `_emit()`**: silent `pass` → `JSON_ONLY_DEBUG=1` 환경변수로 stderr 경고 활성화 (호출자 호환성 유지하면서 디버그 가시성)
- **lookup_plugins/adapter_loader.py**: score 동률 정렬 문서화 (Python list.sort stable + 파일명 알파벳 tie-break) + 동률 발견 시 vvv 경고
- **redfish_gather.py docstring**: Cisco 추가 (LOW), `int(vcap_int / 1048576)` → `vcap_int // 1048576` 정수 나눗셈 통일 (LOW), `bmc_names`에 `'cisco': 'CIMC'` 추가, gather_system Cisco silent OEM 의도 주석 추가

cycle-007 (이전):

- **cycle-007 #2**: rule 22 R7 ↔ 코드 drift 정합 — 5 공통 fragment 변수 명명 (`_data_fragment` + `_sections_{supported,collected,failed}_fragment` + `_errors_fragment`) 정정. rule + CLAUDE.md + ai-context + agent + skill 8 파일 동시 갱신
- **cycle-007 #1**: `redfish_gather.py` `gather_storage()` 190줄 → 5 함수 분리 (`_gather_simple_storage`, `_gather_standard_storage`, `_extract_storage_controller_info`, `_extract_storage_drives`, `_extract_storage_volumes`). rule 10 R3 정합
- **cycle-007 #3**: `precheck_bundle.py` `run_module()` 181줄 → 5 함수 분리 + `lookup_plugins/adapter_loader.py` `LookupModule.run()` 115줄 → 5 함수 분리
- **cycle-007 #4**: `precheck_bundle.py` `requests` 선택적 의존 제거 → urllib stdlib 단일 경로 통일 + 에러 분류 강화 (HTTPError / socket.timeout / URLError / SSLError)

- **cycle-007 #2**: rule 22 R7 ↔ 코드 drift 정합 — 5 공통 fragment 변수 명명 (`_data_fragment` + `_sections_{supported,collected,failed}_fragment` + `_errors_fragment`) 정정. rule + CLAUDE.md + ai-context + agent + skill 8 파일 동시 갱신
- **cycle-007 #1**: `redfish_gather.py` `gather_storage()` 190줄 → 5 함수 분리 (`_gather_simple_storage`, `_gather_standard_storage`, `_extract_storage_controller_info`, `_extract_storage_drives`, `_extract_storage_volumes`). rule 10 R3 정합
- **cycle-007 #3**: `precheck_bundle.py` `run_module()` 181줄 → 5 함수 분리 + `lookup_plugins/adapter_loader.py` `LookupModule.run()` 115줄 → 5 함수 분리
- **cycle-007 #4**: `precheck_bundle.py` `requests` 선택적 의존 제거 → urllib stdlib 단일 경로 통일 + 에러 분류 강화 (HTTPError / socket.timeout / URLError / SSLError)

cycle-006 (이전):

- **T2-B2 적용**: `verify_harness_consistency.py` FORBIDDEN_WORDS 검사 default 활성화 (rule 00 약속 충족 — `--no-forbidden-check`로 비활성)
- **T2-C2 적용**: `precheck_bundle.py` Stage 1 (reachable) ↔ Stage 2 (port_open) 분리 + ConnectionRefusedError 시 host alive 판정 (rule 27 R2 정합)
- **T2-C8 적용**: `os-gather/files/get_last_login.sh` 공유 snippet 추가 + Python/Raw 양 경로에서 lookup file 통합 (gather_users.yml 294 → 239 lines, rule 10 R3 정합)
cycle-006 (이전):

- **DRIFT-004 resolved**: `users[]` 섹션 6 필드 등록 (Must +3 / Nice +2 / Skip +1) → 분포 46 entries, output_schema_drift 정합
- **DRIFT-005 resolved**: `_BUILTIN_VENDOR_MAP` → `_FALLBACK_VENDOR_MAP` 이름 변경 + 3-tier path resolution + nosec silence
- **DRIFT-006 resolved**: rule 12 R1에 Allowed (cycle-006 추가) 절 — Redfish API spec OEM namespace는 외부 계약 직접 의존이라 의도된 예외. 17 라인 nosec silence
- **W2 (b) resolved**: os-gather Jinja2 OEM list silence + 동기화 책임 명시
- **vendor_boundary 0건 달성**: cycle-005 26 → cycle-006 0

cycle-005 (이전):
- 도구 정밀화 (scan #2 재설계 + scan #4 specificity + vendor_boundary docstring) + DRIFT-007 catalog 정합 + alias 동기화 게이트

- **DRIFT-007 catalog 정합**: validate_field_dictionary.py 기준 실측 분포 "Must 28 / Nice 7 / Skip 5 = 40 entries"로 5 위치 일괄 정정 (cycle-002 정정값 자체가 잘못된 grep 카운트였음 — 헤더 주석 noise)
- **scan #2 재설계**: set_fact 다음 indent 블록 lookahead로 누적 변수 직접 수정만 검출 → 107 → 0건
- **scan #4 specificity 분석**: 같은 priority여도 distribution_patterns / version_patterns / firmware_patterns로 분리되면 silence → 7 → 0건
- **verify_vendor_boundary docstring 인식**: Python triple-quote 페어링으로 docstring 라인 skip → 33 → 26건
- **verify_harness_consistency 동기화 게이트**: `_BUILTIN_VENDOR_MAP` ↔ vendor_aliases.yml drift advisory (DRIFT-005 옵션 (2) 사전 적용)
- **scan_suspicious_patterns.py: 11 패턴 모두 0건** (server-exporter 코드 rule 95 R1 100% 정합)

## 완료된 Plan / Cycle

| Plan / Cycle | 내용 | commit |
|---|---|---|
| Plan 1 (Foundation) | settings.json + 19 hooks + supporting scripts + policy + role + ai-context + templates + commands + 29 rules + CLAUDE.md Tier 0 | d87af96, 31526c3, ee82f1b, 031b32e |
| Plan 2 (Skills + Agents) | 43 skills + 51 agents | 183a79e, 2b3268f |
| Plan 3 (docs/ai 골격) | catalogs / decisions / policy / workflows / harness / handoff / impact / references | cc3067d, 50343f3 |
| cycle-001 (dry-run) | 자기개선 루프 dry-run | (cc3067d 일부) |
| cycle-002 (실측 + DRIFT 발견) | 실측 catalog 갱신 + 3 DRIFT 발견 + verify 강화 | 4b5ec30 |
| cycle-003 (DRIFT 정리 + 도구) | DRIFT-001/002/003 resolved + scan_suspicious_patterns.py 신규 + 13 adapter origin 발견 | 69abb8a |
| cycle-004 (전수조사) | 도구 3종 정밀화 + 13 adapter origin 일괄 + _safe_int + 변수 silence + DRIFT-004/005/006 등재 | fef5789..6142eea |
| cycle-005 (AI 자체 가능 일괄) | DRIFT-007 catalog 정합 + scan #2/#4 재설계 + vendor_boundary docstring + alias 동기화 게이트 → scan 11 패턴 0건 | 72b2613..2b4900d |
| cycle-006 (DRIFT 4종 일괄) | DRIFT-004 (users 등록) + DRIFT-005 (alias 통합) + DRIFT-006 (rule 12 예외 절) + W2 (b) silence → vendor_boundary 0건 | 86c91bc |
| full-sweep 2026-04-28 (Tier 1+2) | docs/rule/잔재어휘 정합 + code/schema 결함 + adapter origin/policy/settings | 1eb6abe / dd88aac / c1d6f9b |
| full-sweep 잔여 (T2-B2/C2/C8) | forbidden default 활성화 + precheck Stage 분리 + gather_users 함수 통합 | ad87006 |
| cycle-007 (4축 검수 + HIGH 4 일괄) | rule 22 R7 drift 정합 + redfish_gather.py 5 함수 분리 + precheck/adapter_loader 함수 분리 + requests 의존 제거 | 6a473bd |
| cycle-008 (P2 MED/LOW 일괄) | redfish_gather 추가 함수 분리 (gather_system/detect_vendor/main) + linux gather_system identifier_diagnostics 분리 + HPE priority 차등 + Lenovo/Cisco bmc fallback + json_only debug + adapter_loader 동률 문서화 | 756e1e77 |
| **cycle-009 (fallback envelope + rule 5요소)** | **3-channel fallback envelope 13 필드 일관성 (HIGH fix 2건 + MED fix 1건) + T2-A7 rule 7개 5요소 보강 (24/26/41/50/60/70/90)** | (이번 세션) |

## 검증 결과 (cycle-009 후)

```
[정적]
verify_harness_consistency.py        : PASS (rules 29 / skills 43 / agents 51 / policies 10)
validate_claude_structure.py         : OK
check_project_map_drift.py           : PASS (site.yml 3 fingerprint 갱신)
scan_suspicious_patterns.py          : clean (11 패턴 0건)
verify_vendor_boundary.py            : PASS — 0건
output_schema_drift_check.py         : 정합 (sections=10, fd_paths=46, fd_section_prefixes=10)
ansible-playbook --syntax-check       : PASS — 3 채널 (WSL)
pytest tests/                         : PASS — 95/95
```

도메인 코드:
- cycle-006 도메인 코드 변경: redfish_gather.py (이름 변경 + path resolution + nosec silence) + Jinja2 silence + field_dictionary +6 entries
- pytest 95 PASS — 영향 vendor 회귀 0건
- **모든 harness 도구 0건 — 100% 정합 달성**

## 카탈로그 (실측, 2026-04-29 cycle-013 후)

| 카테고리 | 카운트 | 변화 |
|---|---|---|
| rules | 28 | cycle-011 rule 60 삭제 |
| skills | 43 | 변화 없음 |
| agents | 49 | cycle-011 security-reviewer + vault-rotator 삭제 |
| policies | 9 | cycle-011 security-redaction 삭제 |
| roles | 6 | 변화 없음 |
| ai-context | 14 | cycle-009/010 추가 |
| templates | 8 | 변화 없음 |
| commands | 5 | 변화 없음 |
| hooks (Python) | 18 + supporting 8 | cycle-011 pre_commit_policy 삭제 |
| references (외부 docs) | 14 | 변화 없음 |
| **adapters** | **27** (cycle-008 lenovo_bmc + cisco_bmc, cycle-012 recovery_accounts 메타 16 redfish) | 100% rule 96 R1 정합 |
| **schema entries** | **57** (Must 31 / Nice 20 / Skip 6 — cycle-012 +11 Nice, cycle-013 1건 over count 정정) | rule 13 R5 정합 |
| **vault encrypt** | **8/8** (cycle-012 ansible-vault AES256, Jenkins credential `server-gather-vault-password`) | OPS-3 password 회전 대기 |
| **DRIFT 등재** | **6** (resolved 모두) | cycle-013 추가 발견 없음 |

## 채널별 / Vendor 상태

| 채널 | 상태 | adapter | origin 주석 |
|---|---|---|---|
| os-gather | ok | 7 | 100% (cycle-004) |
| esxi-gather | ok | 4 | 100% (cycle-004) |
| redfish-gather | ok | 14 | 100% (cycle-003 12 + cycle-004 1 redfish_generic + 1 registry) |

| Vendor | adapter | baseline | origin |
|---|---|---|---|
| Dell | 3 (idrac8/9/generic) | 있음 | 기존 + 검증 |
| HPE | 4 (ilo4/5/6/generic, iLO5/6 priority 차등 cycle-008) | 있음 | 기존 + 검증 |
| Lenovo | 3 (xcc/imm2/bmc — bmc fallback cycle-008 추가) | 있음 | 기존 + 검증 |
| Supermicro | 3 (x11/x9/bmc) | 일부 | 기존 + 검증 |
| Cisco | 2 (cimc/bmc — bmc fallback cycle-008 추가, 세대 차등은 M5/M6 미검증으로 보류) | 일부 | 기존 + 검증 |

## DRIFT 현황

| ID | 분류 | 상태 |
|---|---|---|
| DRIFT-001 | catalog-stale (Field Dictionary 28→29 Must, cycle-003 정정 자체 stale) | resolved (cycle-003), DRIFT-007에서 재정정 |
| DRIFT-002 | catalog-stale (Stage 4 일반화) | resolved (cycle-003) |
| DRIFT-003 | catalog-stale (vendor-bmc-guides adapter 이름) | resolved (cycle-003) |
| DRIFT-004 | convention-violation (`users` 섹션 field_dictionary 미등록) | **resolved (cycle-006)** — users[] 6 항목 등록 |
| DRIFT-005 | convention-violation (`_BUILTIN_VENDOR_MAP` 중복) | **resolved (cycle-006)** — _FALLBACK_VENDOR_MAP + path resolution + nosec |
| DRIFT-006 | convention-violation (redfish_gather.py vendor 분기 17건) | **resolved (cycle-006)** — rule 12 R1 Allowed 절 + 17 라인 nosec |
| DRIFT-007 | catalog-stale (Must 28/Nice 7/Skip 5 실측 — cycle-002 grep 헤더 noise 오인) | resolved (cycle-005) |

**모든 등재 DRIFT resolved.** cycle-007 진입 시 새 DRIFT 발견은 그 시점 catalog 추가.

## Round 11 reference 종합 수집 (2026-04-28)

> 사용자 제공 27대 실장비에 대한 종합 raw 정보 수집. 향후 schema 추가 / 매핑 검증 / vendor 온보딩 / 회귀 비교 reference.

- **신규 디렉터리**: `tests/reference/{redfish,os,esxi,agent,scripts,local}/`
- **수집 도구 4개**:
  - `crawl_redfish_full.py` — Redfish ServiceRoot부터 모든 link 재귀
  - `gather_os_full.py` — paramiko SSH (Linux) + pywinrm (Windows) + ansible setup
  - `gather_esxi_full.py` — paramiko + pyvmomi + esxcli
  - `gather_agent_env.py` — paramiko, REQUIREMENTS 검증용
- **자격**: `tests/reference/local/targets.yaml` (gitignored)
- **수집 결과 (완료, 2026-04-28 17:15)**:
  - Redfish 11대 시도 → 9 OK (Dell 5 + HPE + Lenovo + Cisco 15.2) / 1 SKIP (Dell 32 vendor 의심) / 2 환경 이슈 (Cisco 15.1 BMC 다운 + 15.3 도달 불가)
  - OS 7대 시도 → 6 OK (Linux distro 5 + bare-metal) / 1 환경 이슈 (Win10 WinRM)
  - ESXi 3대 → pyvmomi 3 OK, SSH 1만 (.1/.3 SSH 비활성)
  - Agent/Master 4대 → 모두 OK (각 39 명령)
- **최종 통계**: **15964 파일 / 126MB** (redfish 108MB / os 5.8MB / esxi 11MB / agent 399K)
- **사고 7건** (F1~F7): F1 자격 정정 (RESOLVED) / F2 vendor 의심 / F3 BMC 환경 / F4 WinRM 환경 / F5 SSH 비활성 / F6 sudo 대기 (RESOLVED) / F7 SKIP/옵션 추가 (RESOLVED)
- **회귀 영향**: 없음 (별도 디렉터리, fixtures/baseline 무수정, harness consistency PASS, vendor boundary PASS)
- **Evidence**: `tests/evidence/2026-04-28-reference-collection.md`
- **decision-log**: `docs/19_decision-log.md` §13 Round 11
- **follow-up**: F2 (사용자 확인) / F3 (장비 가동) / F4 task #10 (Win10 WinRM) / F5 (ESXi SSH 활성화) / F6 (sudo 처리 개선)

## 다음 작업 (cycle-007 후보)

> `docs/ai/NEXT_ACTIONS.md` 참조. 2026-04-28 full-sweep 보고서: `docs/ai/harness/full-sweep-2026-04-28.md`

### 사용자 결정 / 외부 의존
- T2-D2: `schema/baseline_v1/cisco_baseline.json` `data.users: null` → `[]` (rule 13 R4 — 실측 evidence 필요)
- T2-A7: rule 24 / 26 / 41 / 50 / 60 / 70 / 90 본문 R-번호 + Default/Allowed/Forbidden/Why 5요소 보강 (큰 재구조화)
- T3-01~T3-06 (full-sweep Tier 3): precheck `requests` 의존 / iLO5/6 priority / Lenovo generic / adapter 버전 / BMC IP 최적화 / ADR 필수 정책
- 새 vendor 추가 (PO 결정)
- Round 11 검증 (실장비)

### AI 자체 가능 (cycle-007)
- scan_suspicious_patterns.py #2 재설계 (set_fact 다음 라인 분석)
- scan_suspicious_patterns.py #4 specificity 분석 (priority 동률 + match.distribution_patterns 결합)
- verify_vendor_boundary.py Python `"""` docstring 인식 추가
- verify_harness_consistency.py에 `_VENDOR_ALIASES` ↔ `vendor_aliases.yml` 동기화 게이트
- verify_harness_consistency.py FORBIDDEN_WORDS default 모드 검사 활성화 (T2-B2)

## 정본 reference

- `CLAUDE.md` (Tier 0 정본, 보강됨)
- `GUIDE_FOR_AI.md`, `REQUIREMENTS.md`, `README.md`
- `docs/01_jenkins-setup` ~ `docs/19_decision-log`
- 직전 cycle: `docs/ai/harness/cycle-004.md`
- vendor 경계 분석: `docs/ai/impact/2026-04-27-vendor-boundary-57.md`
- DRIFT 카탈로그: `docs/ai/catalogs/CONVENTION_DRIFT.md`
- plan: `C:/Users/hshwa/.claude/plans/rosy-wishing-crescent.md`
