# 보안 및 비밀값 관리

## 규칙 표기 구조

본 rule의 각 항목은 **Default / Allowed / Forbidden + Why + 재검토 조건** 3단 구조.

## 적용 대상

- 저장소 전체 (`**`)
- `vault/**` (절대 보호 — protected-paths.yaml)
- `callback_plugins/`, `Jenkinsfile*`, `redfish-gather/library/`

## 현재 관찰된 현실

- Ansible Vault로 모든 시크릿 관리 (`vault/{linux,windows,esxi}.yml + vault/redfish/{vendor}.yml`)
- 모든 vault 파일은 ansible-vault encrypt 필수
- 자체 서명 인증서 환경: Redfish HTTPS verify=False
- callback URL 자격증명 path/token 형식만 허용
- `pre_commit_policy.py`가 평문 비밀값 advisory 검사

## 목표 규칙

### R1. Vault 파일 encrypt 의무

- **Default**: `vault/**` 모든 파일은 ansible-vault encrypt 상태로 commit
- **Allowed**: encrypt 후 ansible-vault edit/encrypt만 사용
- **Forbidden**:
  - 평문 vault 파일 commit
  - 코드 / 문서 / 로그에 평문 비밀값 (BMC password, vault password, iDRAC user, redfish basic auth)
  - vault 파일 직접 편집 (텍스트 에디터로)
- **Why**: 공개 저장소 / Jenkins console log 유출 시 즉시 인증 침해 + 모든 vault rotation 필요
- **재검토**: HashiCorp Vault 같은 외부 Secret Manager 도입 시

### R2. Vault 회전 절차

- **Default**: vault 회전은 `rotate-vault` skill로만
- **Allowed**: 사용자 명시 승인 후 ansible-vault rekey 직접 실행
- **Forbidden**: 회전 없이 의심 vault 계속 사용 (예: 노출 사고 후)
- **Why**: 회전 절차 표준화 → 누락 / 동기화 실패 방지
- **재검토**: 자동 vault 회전 도구 도입 시

### R3. Log redaction

- **Default**: callback message body / Jenkins console log / ansible -vvv 출력은 `.claude/policy/security-redaction-policy.yaml` 패턴 적용 (password / token / secret 변수명 매칭)
- **Allowed**: 디버그 시 `JSON_ONLY_DEBUG=1` 환경변수로 일부 메타 노출 (값은 redact)
- **Forbidden**: vault 변수가 평문 log에 누설
- **Why**: Jenkins console log는 RBAC로 보호되지만, log forwarding 시 외부 노출 가능
- **재검토**: 자동 redaction hook 도입 시

### R4. HTTPS verify 정책 명시

- **Default**: 자체 서명 인증서 환경의 Redfish는 verify=False 허용. 단 코드에 명시 주석 필수 (예: `verify_ssl: false  # BMC 자체서명 인증서 사용. 운영 보안 정책에 따라 변경 검토`)
- **Allowed**: 인증서 chain이 검증 가능한 환경에서 verify=True 적용
- **Forbidden**:
  - verify 정책 묵시 (default 사용)
  - 설명 없는 random 변경
- **Why**: verify=False는 MITM에 취약하지만 BMC 환경에서 불가피. 명시 주석으로 의도된 결정임을 표기
- **재검토**: BMC 인증서 자동 발급 도구 도입 시

### R5. 자격증명 전달 (vault → ansible 변수 only)

- **Default**: vault에서 ansible 변수로만 (`{{ vault_xxx }}`)
- **Forbidden**:
  - environment 변수에 자격증명 (process list 노출 위험)
  - CLI `--extra-vars "password=..."` (Jenkins console log 노출)
  - 코드 hardcode
- **Why**: Jenkins console log + ps/proc filesystem 노출. environment 변수도 process tree로 leak
- **재검토**: 자격증명 broker 도입 시

### R6. 에러 메시지에 stacktrace 비노출

- **Default**: callback message body의 errors 필드는 사용자 친화 메시지 (예: "BMC 인증 실패: 사용자명 또는 비밀번호를 확인하세요")
- **Allowed**: stacktrace는 stderr 또는 Jenkins log에만 (호출자 응답에 비노출)
- **Forbidden**:
  - `errors: [{traceback: "..."}]` (호출자 응답 envelope)
  - file path / line number / variable value 노출
- **Why**: 호출자 시스템이 message를 그대로 사용자에게 표시할 수 있음. stacktrace 노출 시 내부 구조 유출
- **재검토**: 구조화된 에러 코드 도입 시

### R7. 입력 검증

- **Default**:
  - callback URL 정규화 (rule 31 R1 — strip + rstrip /)
  - inventory_json 형식 검증 (Jenkins Stage 1)
  - target_type / loc 화이트리스트 검증
- **Forbidden**: 외부 입력 신뢰 (raw concatenation 등)
- **Why**: rule 27 R5 layer 분류 정신. 입력 검증은 가장 이른 layer에서
- **재검토**: 입력 schema validator 도입 시

### R8. 보안 스캔 의무

- **Default**: PR 머지 전 다음 검사 통과
  - `pre_commit_policy.py` advisory 검토
  - vault 파일 encrypt 상태 확인
  - 평문 비밀값 grep
- **Allowed**: advisory 위반 후 사용자 승인 시 진행
- **Forbidden**: vault 평문 commit / 평문 비밀값 commit
- **Why**: 사후 발견 시 rotation + git history rewrite 비용
- **재검토**: 자동 보안 스캔 hook 도입 시

## 금지 패턴

- 평문 비밀값 commit — R1
- vault 직접 편집 — R1
- 회전 절차 우회 — R2
- log에 vault 변수 누설 — R3
- HTTPS verify 정책 묵시 — R4
- environment 변수 / CLI에 자격증명 — R5
- callback errors에 stacktrace — R6
- 외부 입력 raw 신뢰 — R7

## 리뷰 포인트

- [ ] 모든 vault 파일이 encrypt 상태
- [ ] 코드/문서에 평문 비밀값 없음
- [ ] callback message redaction
- [ ] verify 정책 명시 (주석)
- [ ] errors에 stacktrace 비노출
- [ ] 입력 검증 layer 적절

## 테스트 포인트

- `pre_commit_policy.py` advisory 통과
- `python scripts/ai/hooks/pre_commit_policy.py`

## 관련

- agent: `security-reviewer`, `vault-rotator`
- skill: `rotate-vault`, `review-existing-code` (보안 축)
- policy: `.claude/policy/security-redaction-policy.yaml`
- rule: `27-precheck-guard-first` R5, `31-integration-callback`
- 정본: `docs/03_agent-setup.md` 보안 부분
