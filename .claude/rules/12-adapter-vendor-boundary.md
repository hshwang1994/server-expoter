# Adapter / Vendor 경계 보호

## 적용 대상
- `adapters/{redfish,os,esxi}/**`
- `redfish-gather/tasks/vendors/**`
- `common/`, `os-gather/`, `esxi-gather/`, `redfish-gather/` (vendor 하드코딩 금지 영역)
- `common/vars/vendor_aliases.yml`

## 현재 관찰된 현실

- 25개 adapter YAML (Redfish 14 + OS 7 + ESXi 4)
- 5 vendor (Dell / HPE / Lenovo / Supermicro / Cisco) + generic fallback
- adapter_loader (lookup plugin)이 동적 점수 계산으로 선택
- vendor-specific OEM tasks는 `redfish-gather/tasks/vendors/{vendor}/`

## 목표 규칙

### R1. Vendor 이름 하드코딩 금지

- **Default**: `common/`, `os-gather/`, `esxi-gather/`, `redfish-gather/` (단 `tasks/vendors/` 제외) 코드에 vendor 이름 하드코딩 금지
- **Allowed**: `redfish-gather/tasks/vendors/{vendor}/` 안, `adapters/{channel}/{vendor}_*.yml` 안, `common/vars/vendor_aliases.yml`
- **Forbidden**: `if vendor == "Dell"` 같은 분기 코드, `Dell` / `HPE` / `Lenovo` / `Supermicro` / `Cisco` 문자열 비교
- **Why**: gather 코드는 vendor-agnostic. 분기는 adapter score + lookup으로 동적 처리. vendor 이름 하드코딩하면 새 vendor 추가 시 코드 수정 부담
- **재검토**: 6개월 vendor 추가 0건 시 일부 완화 가능

`scripts/ai/verify_vendor_boundary.py`가 자동 검출.

### R2. Adapter 점수 일관성

- **Default**: 같은 vendor 내 adapter는 priority 역전 금지
  - generic vendor adapter (예: dell_idrac.yml) priority = 10
  - 세대별 (예: dell_idrac8.yml) priority = 50
  - 최신 (예: dell_idrac9.yml) priority = 100
- **Forbidden**: 세대별 adapter가 generic보다 priority 낮음 (generic이 매번 선택됨)
- **Why**: 점수 계산 일관성 + 디버깅 용이성

### R3. Vendor 추가 3단계

- **Default**: 새 vendor 추가는 정확히 3단계:
  1. `common/vars/vendor_aliases.yml`에 alias 매핑
  2. `adapters/{redfish,os,esxi}/{vendor}_*.yml` adapter 생성
  3. (선택) `redfish-gather/tasks/vendors/{vendor}/` OEM tasks
- **Forbidden**: site.yml 수정 (adapter_loader가 동적 감지)
- **Why**: site.yml을 vendor마다 수정하면 vendor 수만큼 site.yml이 비대해짐

### R4. Adapter YAML 필수 필드

- **Default**: adapter는 `match` / `capabilities` / `collect` / `normalize` 4개 키 필수
- **Allowed**: `metadata` 키로 vendor / firmware / tested_against / oem_path 등 origin 주석 (rule 96 R1)
- **Forbidden**: 4개 키 누락 (adapter_loader 파싱 실패)

### R5. Generic fallback

- **Default**: 모든 채널에 generic adapter 1개 (`{channel}/redfish_generic.yml` 등) priority = 0 (fallback)
- **Why**: 매치 안 되는 vendor에 대해서도 graceful degradation

## 금지 패턴

- gather 코드에 vendor 이름 하드코딩 — R1 (verify_vendor_boundary.py 자동 검출)
- adapter priority 역전 — R2
- 새 vendor 추가하면서 site.yml 수정 — R3
- adapter 4개 필수 필드 누락 — R4
- generic fallback 부재 — R5

## 리뷰 포인트

- [ ] verify_vendor_boundary.py 통과 (vendor 하드코딩 0건)
- [ ] 새 adapter priority가 같은 vendor 다른 generation과 일관성
- [ ] vendor 추가 시 정확히 3단계만
- [ ] adapter YAML 4개 필수 필드 모두 존재
- [ ] origin 주석 (rule 96 R1) 존재

## 테스트 포인트

- `python scripts/ai/verify_vendor_boundary.py` (exit 0)
- `score-adapter-match` skill로 점수 디버깅
- 새 vendor: deep_probe_redfish.py로 프로파일링 후 baseline 검증

## 관련

- rule: `10-gather-core`, `22-fragment-philosophy`, `96-external-contract-integrity`
- skill: `add-new-vendor`, `score-adapter-match`, `verify-adapter-boundary`, `vendor-change-impact`
- agent: `adapter-author`, `vendor-onboarding-worker`, `adapter-boundary-reviewer`, `vendor-boundary-guardian`
- policy: `.claude/policy/vendor-boundary-map.yaml`
- 정본: `docs/10_adapter-system.md`, `docs/14_add-new-gather.md`
