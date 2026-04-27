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

## 금지 패턴

- 4단계 순서 일탈 — R1
- 단계별 책임 혼재 (예: ping 단계에서 protocol 검사) — R2
- Vault 1단계 skip — R3
- 일부 실패 시 전체 abort — R4
- 검증을 잘못된 layer에 배치 — R5

## 리뷰 포인트

- [ ] precheck 4단계 호출 순서
- [ ] 각 단계 실패 시 diagnosis.details 기록
- [ ] Redfish는 Vault 2단계
- [ ] graceful degradation 설계
- [ ] 새 검증의 layer 분류 (R5)

## 관련

- rule: `10-gather-core`, `12-adapter-vendor-boundary`
- skill: `debug-precheck-failure`, `classify-precheck-layer`
- agent: `precheck-engineer`
- 정본: `docs/11_precheck-module.md`
