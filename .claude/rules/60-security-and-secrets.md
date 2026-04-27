# 보안 및 비밀값 관리

## 적용 대상
- 저장소 전체 (`**`)
- `vault/**` (절대 보호)

## 현재 관찰된 현실

- Ansible Vault로 모든 시크릿 관리 (`vault/{linux,windows,esxi}.yml + vault/redfish/{vendor}.yml`)
- 모든 vault 파일은 ansible-vault encrypt 필수
- 자체 서명 인증서 환경: Redfish HTTPS verify=False
- callback URL 자격증명 path/token 형식만 허용

## 규칙 표기 구조

Default / Forbidden + Why + 재검토 조건.

## 목표 규칙

### 비밀값 관리

- **Default**: 모든 vault 파일은 ansible-vault encrypt. 평문 commit 금지
- **Default (회전)**: vault 회전은 `rotate-vault` skill로만
- **Forbidden**: 코드 / 문서 / 로그에 평문 비밀값 (BMC password, vault password, iDRAC user, redfish basic auth)
- **Forbidden**: vault 파일 직접 편집 (ansible-vault edit/encrypt만)
- **Why**: 공개 저장소/CI 로그 유출 시 즉시 인증 침해 + rotation 필수
- **재검토**: HashiCorp Vault 같은 Secret Manager 도입 시

### log redaction

- **Default**: callback message body / Jenkins console log / ansible -vvv 출력은 `.claude/policy/security-redaction-policy.yaml` 패턴 적용
- **Forbidden**: vault 변수가 평문 log에 누설

### HTTPS 정책

- **Default**: 자체 서명 인증서 환경의 Redfish는 verify=False 허용 (ansible playbook 또는 redfish_gather.py에 명시 주석)
- **Forbidden**: verify 정책 묵시 / 설명 없는 random 변경

### 자격증명 전달

- **Default**: vault에서 ansible 변수로만 (`{{ vault_xxx }}`). environment 변수 / CLI 인자 금지
- **Forbidden**: `--extra-vars "password=..."` (Jenkins console log에 노출)

### 에러 메시지

- **Default**: stacktrace는 callback message에 노출 안 함. errors 필드는 사용자 친화 메시지
- **Forbidden**: `errors: [{traceback: "..."}]`

### 입력 검증 (rule 27 R5와 연동)

- **Default**: callback URL 정규화 (rule 31 R1), inventory_json 형식 검증 (Jenkins Stage 1)
- **Forbidden**: 외부 입력 신뢰

## 금지 패턴

- 평문 비밀값 commit
- vault 직접 편집 (ansible-vault encrypt 우회)
- callback message에 stacktrace
- environment 변수 / CLI에 자격증명 전달
- HTTPS verify 정책 묵시

## 리뷰 포인트

- [ ] 모든 vault 파일이 encrypt 상태
- [ ] 코드/문서에 평문 비밀값 없음
- [ ] callback message redaction
- [ ] verify 정책 명시

## 테스트 포인트

- `pre_commit_policy.py` (vault 파일 / 평문 비밀값 검사)
- `python scripts/ai/hooks/pre_commit_policy.py` (advisory)

## 관련

- agent: `security-reviewer`, `vault-rotator`
- skill: `rotate-vault`, `review-existing-code` (보안 축)
- policy: `.claude/policy/security-redaction-policy.yaml`
- 정본: `docs/03_agent-setup.md` 보안 부분
