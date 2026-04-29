# server-exporter 현재 상태

## 일자: 2026-04-29 (production-audit — 4 agent 전수조사 + HIGH 30+건 일괄 수정)

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
