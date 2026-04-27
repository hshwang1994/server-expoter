---
name: plan-feature-change
description: 기능 변경 / 추가 / 리팩토링의 구현 계획 수립. API (callback / Jenkinsfile) 설계 + 채널 영향 + 테스트. 사용자가 "구현 계획 세워줘", "어떻게 만들지" 등 요청 시. - 복잡한 기능 추가 / 변경 전 / task-impact-preview 후 HIGH 리스크
---

# plan-feature-change

## 목적

server-exporter 기능 변경 구현 계획. clovirone API (Spring REST) 대신 server-exporter는 callback 호출 + Jenkinsfile + 3-channel + adapter.

## 계획 항목

1. **요구 의도 3 가지**: 사용자 flow / 핵심 결정 / 기존 시스템 제약
2. **변경 영역 list** (실측):
   - 채널: os / esxi / redfish
   - vendor: agnostic / specific
   - schema: sections.yml / field_dictionary / baseline
   - vault / Jenkinsfile
3. **변경 sub-task 분할**:
   - SUB-1 / SUB-2 / ... 순서 + 의존성
4. **테스트 전략**:
   - 단위 (pytest)
   - 통합 (ansible-playbook syntax-check)
   - 회귀 (영향 vendor baseline)
   - 실장비 (Round 검증 필요 여부)
5. **회귀 영역** (rule 91 R7 자동 포함):
   - 공통 fragment 영역
   - adapter 추가/수정
   - Jenkinsfile cron
   - 출력 schema
   - vault
6. **위험 / 완화**:
   - HIGH 위험 → write-impact-brief + 사용자 승인
7. **머지 전략** (rule 93 R5 — squash 기본)

## 출력

```markdown
## 구현 계획 — <기능명>

### 의도 3 가지
- (a) 호출자 flow: ...
- (b) 핵심 결정: ...
- (c) 기존 제약: ...

### SUB 분할
- SUB-1: <범위> — depends: 없음
- SUB-2: <범위> — depends: SUB-1
- ...

### 테스트
- 단위: pytest tests/X
- 회귀: dell + hpe baseline (영향 vendor)
- 실장비: SUB-N 후 Round 검증

### 회귀 영역 (자동 포함)
- ✓ 공통 fragment (common/tasks/normalize/)
- ✓ Jenkinsfile (Stage 4 시간 영향)

### 머지: feature/<name> → main, squash
```

## 적용 rule / 관련

- rule 91 (task-impact-gate), rule 92 (dependency-and-regression-gate)
- skill: `task-impact-preview`, `prepare-regression-check`, `vendor-change-impact`, `compare-feature-options`
- agent: `product-planner`, `change-impact-analyst`
