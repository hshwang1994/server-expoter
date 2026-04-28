# Vendor / Adapter 정책

## 규칙 표기 구조

본 rule의 각 항목은 **Default / Allowed / Forbidden + Why + 재검토 조건** 3단 구조.

## 적용 대상

- 저장소 전체 (`**`) — 벤더 추가/변경 시
- `adapters/`, `redfish-gather/tasks/vendors/`, `vault/redfish/`
- `common/vars/vendor_aliases.yml`

## 현재 관찰된 현실

- 5 vendor (Dell / HPE / Lenovo / Supermicro / Cisco) + generic fallback
- 단일 main 브랜치 운영. branch는 `main` + `feature/*` + `fix/*` + `vendor/*` (벤더 추가 시) + `docs/*` + `harness/*`
- vendor별 plugin 모듈 없음 — adapter YAML + OEM tasks + vault만
- 27 adapter (Redfish 16 + OS 7 + ESXi 4 — cycle-008 기준)

## 목표 규칙

### R1. Vendor 정규화 정본

- **Default**: vendor 정규화 정본은 `common/vars/vendor_aliases.yml`. 모든 alias 매핑은 이 파일에 등록
  | 벤더 | aliases (Manufacturer) | normalized | BMC |
  |---|---|---|---|
  | Dell | "Dell Inc.", "Dell EMC", "Dell" | dell | iDRAC8/9 |
  | HPE | "HPE", "Hewlett Packard Enterprise", "Hewlett-Packard", "HP" | hpe | iLO5/6 |
  | Lenovo | "Lenovo", "IBM" | lenovo | XCC |
  | Supermicro | "Supermicro", "Super Micro Computer", "SMCI" | supermicro | AMI MegaRAC |
  | Cisco | "Cisco Systems", "Cisco" | cisco | CIMC |
- **Allowed**: `_FALLBACK_VENDOR_MAP` (redfish_gather.py)는 vendor_aliases.yml 로드 실패 시 fallback. 두 위치 동기화 의무 (rule 22 R5와 같은 정신)
- **Forbidden**: vendor 분기 코드에서 alias 직접 비교 (`if manufacturer == "Dell Inc."`)
- **Why**: alias 변형이 펌웨어/모델별로 다양 (mark dot 누락 등). 정규화 정본 1곳에서 관리해야 신뢰
- **재검토**: BMC 표준 manufacturer 표기 합의 시

### R2. 새 vendor 추가 9단계

- **Default**: 새 vendor 추가는 정확히 9단계
  1. `common/vars/vendor_aliases.yml` 매핑 추가
  2. `adapters/{redfish,os,esxi}/{vendor}_*.yml` adapter 생성 (priority/specificity/match/capabilities/collect/normalize)
  3. (선택) `redfish-gather/tasks/vendors/{vendor}/` OEM tasks
  4. `vault/redfish/{vendor}.yml` 생성 (ansible-vault encrypt)
  5. `tests/baseline_v1/{vendor}_baseline.json` 추가 (실장비 검증 후)
  6. `.claude/ai-context/vendors/{vendor}.md` 추가
  7. `.claude/policy/vendor-boundary-map.yaml` 갱신
  8. `docs/13_redfish-live-validation.md` Round 갱신
  9. `docs/19_decision-log.md` 추가
- **Allowed**: site.yml 수정 불필요 (adapter_loader가 동적 감지)
- **Forbidden**:
  - 9단계 일부 skip
  - site.yml에 vendor 분기 추가
  - vendor_aliases.yml 누락 후 adapter만 추가
  - adapter 없이 OEM tasks만 추가
- **Why**: 단계 일부 skip 시 vendor 감지/매칭/회귀 중 하나가 깨짐. 일관 경로로만 추가해야 안정
- **재검토**: vendor 추가 자동화 도구 도입 시

### R3. Adapter 점수 일관성

- **Default**: adapter 점수 계산
  ```
  score = priority × 1000 + specificity × 10 + match_score
  ```
  같은 vendor 내:
  - generic fallback = 0~10 (예: `lenovo_bmc.yml` priority=10)
  - 기본 vendor (모델 무관) = 50
  - 세대별 (예: `dell_idrac9.yml`) = 80~100
  - 모델별 = 100 + match.model_patterns의 specificity
- **Allowed**: 같은 vendor 내 priority 동률은 specificity / match_score로 tie-break
- **Forbidden**:
  - priority 역전 (세대별 < generic)
  - 같은 vendor의 다른 generation이 동일 priority + 동일 specificity (선택 결과 불확정)
- **Why**: adapter_loader가 점수순 정렬 후 최고 점수 선택. 일관성 깨지면 어떤 adapter가 선택될지 예측 불가
- **재검토**: 점수 계산식 자체 변경 시

### R4. Branch 정책 (단순 운영)

- **Default**: branch 패턴
  | 브랜치 패턴 | 용도 |
  |---|---|
  | `main` | 운영 기준선 |
  | `feature/<name>` | 기능 추가 |
  | `fix/<name>` | 버그 수정 |
  | `vendor/<name>` | 새 벤더 추가 (예: `vendor/huawei`) |
  | `docs/<name>` | 문서 작업 |
  | `harness/<name>` | 하네스 변경 |
- **Allowed**: 사용자 명시 승인 후 main 직접 push
- **Forbidden**:
  - main 직접 commit (사용자 명시 승인 외)
  - force push (rule 93 R1)
  - `git push --all`
- **Why**: 단일 main 보호 + 변경 추적 가능
- **재검토**: develop / release branch 운영 모델 도입 시

### R5. Vendor 경계 (rule 12 연동)

- **Default**: 본 rule은 정책 수준. 코드 검증은 rule 12 (adapter-vendor-boundary)
  - common/, 3-channel 코드에 vendor 이름 하드코딩 금지
  - adapter YAML / OEM tasks 안에서만 vendor 분기
- **Allowed**: rule 12 R1 Allowed 영역 (Redfish API spec OEM namespace 등)
- **Forbidden**: rule 12 R1 위반
- **Why**: vendor 추가 시 모든 코드 위치 수정 부담을 0으로 만드는 게 본 정책의 핵심
- **재검토**: rule 12 R1 자체 변경 시

### R6. Generic fallback 의무

- **Default**: 모든 채널에 generic fallback adapter 1개 (priority=0~10)
- **Allowed**: vendor별 generic fallback (예: `lenovo_bmc.yml` priority=10) 추가
- **Forbidden**: 채널에 fallback 부재 (매치 안 되는 vendor에 대한 graceful degradation 불가)
- **Why**: 새 vendor / 알려지지 않은 펌웨어에 대해 최소한의 수집 시도 + 명확한 status="failed"
- **재검토**: 모든 vendor가 명시 adapter 보유 정책 도입 시

## 금지 패턴

- vendor_aliases 누락 후 adapter만 추가 — R2
- adapter 없이 OEM tasks만 추가 — R2
- main 직접 push (force) — R4
- common/ + 3-channel에 vendor 하드코딩 — R5 (rule 12 R1)
- 채널에 generic fallback 부재 — R6

## 리뷰 포인트

- [ ] 새 vendor 추가 시 9단계 모두
- [ ] adapter 점수 일관성 (priority 역전 없음)
- [ ] branch 패턴 준수
- [ ] generic fallback 존재
- [ ] vendor_aliases.yml ↔ _FALLBACK_VENDOR_MAP 동기화

## 테스트 포인트

- `python scripts/ai/verify_vendor_boundary.py` (rule 12 검증)
- `python scripts/ai/verify_harness_consistency.py` (alias 동기화)
- 새 vendor: `score-adapter-match` skill로 점수 디버깅

## 관련

- rule: `12-adapter-vendor-boundary`, `60-security-and-secrets`, `93-branch-merge-gate`
- skill: `add-new-vendor`, `vendor-change-impact`, `score-adapter-match`
- agent: `vendor-onboarding-worker`, `vendor-boundary-guardian`
- policy: `.claude/policy/vendor-boundary-map.yaml`
- 정본: `docs/14_add-new-gather.md`, `docs/13_redfish-live-validation.md`
