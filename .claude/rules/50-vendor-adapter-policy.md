# Vendor / Adapter 정책

## 적용 대상
- 저장소 전체 (`**`) — 벤더 추가/변경 시
- `adapters/`, `redfish-gather/tasks/vendors/`, `vault/redfish/`

## 현재 관찰된 현실

- 5 vendor (Dell / HPE / Lenovo / Supermicro / Cisco) + generic fallback
- 단일 main 브랜치 운영. branch는 `main` + `feature/*` + `fix/*` + `vendor/*` (벤더 추가 시) + `docs/*` + `harness/*`
- vendor별 plugin 모듈 없음 — adapter YAML + OEM tasks + vault만

## 목표 규칙

### R1. Vendor 식별

| 벤더 | aliases (Manufacturer) | normalized | BMC |
|---|---|---|---|
| Dell | "Dell Inc.", "Dell EMC", "Dell" | dell | iDRAC8/9 |
| HPE | "HPE", "Hewlett Packard Enterprise", "Hewlett-Packard", "HP" | hpe | iLO5/6 |
| Lenovo | "Lenovo", "IBM" | lenovo | XCC |
| Supermicro | "Supermicro", "Super Micro Computer", "SMCI" | supermicro | AMI MegaRAC |
| Cisco | "Cisco Systems", "Cisco" | cisco | CIMC |

정규화 정본: `common/vars/vendor_aliases.yml`.

### R2. 새 vendor 추가 절차 (rule 12 R3 + 본 rule)

3단계:
1. `common/vars/vendor_aliases.yml` 매핑 추가
2. `adapters/{redfish,os,esxi}/{vendor}_*.yml` adapter 생성 (priority/specificity/match/capabilities/collect/normalize)
3. (선택) `redfish-gather/tasks/vendors/{vendor}/` OEM tasks
4. `vault/redfish/{vendor}.yml` 생성 (ansible-vault encrypt)
5. `tests/baseline_v1/{vendor}_baseline.json` 추가 (실장비 검증 후)
6. `.claude/ai-context/vendors/{vendor}.md` 추가
7. `.claude/policy/vendor-boundary-map.yaml` 갱신
8. `docs/13_redfish-live-validation.md` Round 갱신
9. `docs/19_decision-log.md` 추가

site.yml은 수정 불필요 (adapter_loader 동적 감지).

### R3. Adapter 점수 계산 일관성

```
score = priority × 1000 + specificity × 10 + match_score
```

같은 vendor 내:
- generic = 0~10
- 기본 = 50
- 세대별 = 80~100
- 모델별 = 100 + match.model_patterns의 specificity

### R4. Branch 정책 (단순 운영)

| 브랜치 패턴 | 용도 |
|---|---|
| `main` | 운영 기준선 |
| `feature/<name>` | 기능 추가 |
| `fix/<name>` | 버그 수정 |
| `vendor/<name>` | 새 벤더 추가 (예: `vendor/huawei`) |
| `docs/<name>` | 문서 작업 |
| `harness/<name>` | 하네스 변경 |

force push / direct push to main 금지 (rule 93).

### R5. Vendor 경계 (rule 12 연동)

본 rule은 정책 수준. 코드 검증은 rule 12 (adapter-vendor-boundary).

## 금지 패턴

- vendor_aliases 누락 후 adapter만 추가 — R2
- adapter 없이 OEM tasks만 추가 — R2
- main 직접 push (force) — R4
- common/ + 3-channel에 vendor 하드코딩 — R5 (rule 12 R1)

## 리뷰 포인트

- [ ] 새 vendor 추가 시 9단계 모두
- [ ] adapter 점수 일관성
- [ ] branch 패턴 준수

## 관련

- rule: `12-adapter-vendor-boundary`, `60-security-and-secrets`, `93-branch-merge-gate`
- skill: `add-new-vendor`, `vendor-change-impact`
- agent: `vendor-onboarding-worker`, `vendor-boundary-guardian`
- policy: `.claude/policy/vendor-boundary-map.yaml`
- 정본: `docs/14_add-new-gather.md`, `docs/13_redfish-live-validation.md`
