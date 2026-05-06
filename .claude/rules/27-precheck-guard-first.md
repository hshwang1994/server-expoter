# Precheck Guard First

> 본 수집 전에 4단계 진단 통과 보장. 각 단계 실패 시 graceful degradation.

## 적용 대상

- `common/library/precheck_bundle.py`
- `os-gather/`, `esxi-gather/`, `redfish-gather/` 의 entry tasks (precheck 호출)
- `classify-precheck-layer` skill 호출

## 현재 관찰된 현실

- 4단계: ping → port → protocol → auth
- 각 단계 실패 시 `diagnosis.details`에 어디서 막혔는지 기록
- precheck 결과로 graceful degradation 또는 abort 결정
- Vault 2단계 로딩 (Redfish): 1단계 무인증 detect → vendor 결정 → 2단계 vault 로드

## 목표 규칙

### R1. 4단계 진단 순서 보장

- **Default**: 본 수집 전 반드시 ping → port → protocol → auth 순서로 진단
- **Forbidden**: 일부 단계 skip 후 본 수집 진입
- **Why**: ping 실패 시 port 시도 의미 없음. protocol 실패 시 auth 시도 의미 없음. 무의미한 timeout 누적 → 빌드 시간 증가

### R2. 단계별 책임 분리

| 단계 | 책임 |
|---|---|
| ping | ICMP 또는 TCP SYN으로 host 도달 가능성 |
| port | target_type별 port 응답 (SSH=22, WinRM=5986, vSphere=443, Redfish=443) |
| protocol | TCP 응답 + 첫 응답 형식 (HTTPS handshake / SSH banner / Redfish JSON) |
| auth | 자격증명으로 인증 성공 |

각 단계가 어디서 실패했는지 `diagnosis.details`에 명시.

### R3. Vault 2단계 로딩 (Redfish 특화)

- **Default**: Redfish는 단계별 처리:
  1. ServiceRoot (`/redfish/v1/`) 무인증 GET → vendor manufacturer 추출
  2. vendor 결정 후 `vault/redfish/{vendor}.yml` 동적 로드
  3. 인증으로 본 수집 재개
- **Forbidden**: 1단계 없이 vendor 가정으로 인증 vault 사용 (잘못된 vendor면 인증 실패)
- **Why**: 새 vendor / 알려지지 않은 펌웨어에 대해 robustness 확보

### R4. Graceful degradation

- **Default**: precheck 일부 단계 실패 시 가능한 데이터만 수집:
  - ping ok / port ok / protocol fail → status: "failed", errors: ["protocol unsupported"]
  - ping ok / port ok / protocol ok / auth fail → status: "failed", errors: ["auth failed"]
  - 일부 endpoint만 실패 → status: "partial", data: { 가능한 섹션만 }
- **Forbidden**: 일부 실패 시 전체 abort (호출자가 원하는 정보를 못 받음)

### R5. Validation Layer 분류 (classify-precheck-layer skill)

새 검증을 추가할 때 어디서 차단할지 결정:

| 검증 종류 | 위치 |
|---|---|
| 입력 형식 (JSON 파싱 / IP 형식) | Jenkins Stage 1 (Validate) |
| 호스트 도달성 | precheck 1-2 (ping/port) |
| 프로토콜 응답 | precheck 3 (protocol) |
| 자격증명 | precheck 4 (auth) |
| 데이터 형식 (envelope schema) | Jenkins Stage 3 (Validate Schema) |
| 비즈니스 규칙 (vendor-specific) | adapter YAML capabilities |

각 검증이 적절한 layer에서 차단 — 늦은 차단은 시간 낭비, 이른 차단은 graceful degradation 무력화.

### R6. Vault 자동 반영 단서 3개 (cycle 2026-05-06-post M-C 학습 형식화)

vault/redfish/{vendor}.yml 변경 시 다음 ansible 실행에서 자동 반영 보장. 의심 시 다음 3 단서 검증:

- **단서 1: include_vars cacheable 옵션 부재**
  - **Default**: `redfish-gather/tasks/load_vault.yml` 의 `include_vars` 호출에 `cacheable: yes` 옵션 **금지**
  - **검증 명령**: `grep -rn 'cacheable' redfish-gather/tasks/load_vault.yml` 0 결과
  - **Why**: `cacheable: yes` 시 fact_cache (Redis) 에 host facts 로 저장 → 다음 run 에서도 stale vault 사용 위험
- **단서 2: set_fact host facts 미등록**
  - **Default**: `_rf_accounts` / `_rf_vault_data` 변수는 task scope 만. host facts (`ansible_facts.*`) 또는 `cacheable: yes` 등록 **금지**
  - **검증 명령**: `grep -rn 'cacheable' redfish-gather/tasks/load_vault.yml common/tasks/normalize/` 0 결과
  - **Why**: host facts 등록 시 fact_cache 영향 — vault 변경 후에도 다음 run 에서 stale 가능
- **단서 3: ansible-vault decrypt 캐시 부재**
  - **Default**: `ansible.cfg` 또는 환경변수에 vault decrypt 결과 캐시 옵션 부재 (Ansible default — decrypt 매 run 수행)
  - **검증 명령**: `grep -rn 'vault_password_file\|vault_identity\|VAULT_PASSWORD_FILE' ansible.cfg` — vault password file 만 있어야 함 (decrypt 캐시 옵션 없음)
  - **Why**: Ansible 은 vault decrypt 결과 캐시 안 함 (default) — vault password file 만 있고 decrypt 결과 캐시 옵션 없으면 매 run 새로 decrypt
- **Forbidden**:
  - `cacheable: yes` 옵션 추가 (vault 자동 반영 무효화)
  - host facts 영역에 `_rf_accounts` / `_rf_vault_data` 등록
  - vault decrypt 캐시 옵션 도입 (사용자 명시 승인 외)
- **Why**: M-C 학습 (cycle 2026-05-06) — 사용자 의심 "vault 변경이 자동 반영되는지" 발생 → 3 단서 (cacheable 0건 / fact_caching 0건 / vault decrypt 캐시 0건) 검증 후 자동 반영 보장 확인. 향후 의심 재발 시 본 R6 lookup 로 1턴에 검증
- **재검토**: vault 자동 반영 자동 검증 hook 도입 시 advisory → blocking 격상

## 금지 패턴

- 4단계 순서 일탈 — R1
- 단계별 책임 혼재 (예: ping 단계에서 protocol 검사) — R2
- Vault 1단계 skip — R3
- 일부 실패 시 전체 abort — R4
- 검증을 잘못된 layer에 배치 — R5
- vault include_vars cacheable / host facts 등록 / decrypt 캐시 도입 — R6

## 리뷰 포인트

- [ ] precheck 4단계 호출 순서
- [ ] 각 단계 실패 시 diagnosis.details 기록
- [ ] Redfish는 Vault 2단계
- [ ] graceful degradation 설계
- [ ] 새 검증의 layer 분류 (R5)
- [ ] vault 자동 반영 3 단서 (cacheable 0 / fact_caching 0 / decrypt 캐시 0) — R6

## 관련

- rule: `10-gather-core`, `12-adapter-vendor-boundary`
- skill: `debug-precheck-failure`, `classify-precheck-layer`, `rotate-vault`
- agent: `precheck-engineer`
- 정본: `docs/11_precheck-module.md`, `docs/21_vault-operations.md`
