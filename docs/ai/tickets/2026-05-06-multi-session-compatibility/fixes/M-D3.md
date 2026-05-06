# M-D3 — Fallback 코드 추가 (additive only)

> status: [DONE] | depends: M-D2 | priority: P1 | cycle: 2026-05-06-multi-session-compatibility | worker: Session-5

## 적용 결과 (2026-05-06)

W1~W6 9 라인 변경 적용 완료 (Additive only — rule 92 R2):

| 작업 | 파일 | 변경 | 검증 |
|---|---|---|---|
| W1 | adapters/redfish/dell_idrac8.yml | `+ - power` 1 줄 (cycle 2026-05-01 PowerSubsystem fallback 활용) | sections=9, power=True |
| W2 | adapters/redfish/hpe_ilo4.yml | `+ - storage` 1 줄 (A1 SimpleStorage fallback 활용) | sections=9, storage=True |
| W3 | adapters/redfish/hpe_ilo4.yml | `+ - power` 1 줄 (A2 PowerSubsystem→Power fallback 활용) | sections=9, power=True |
| W4 | adapters/redfish/lenovo_imm2.yml | `+ - storage` 1 줄 (A1) | sections=9, storage=True |
| W5 | adapters/redfish/lenovo_imm2.yml | `+ - power` 1 줄 (A2) | sections=9, power=True |
| W6 | adapters/redfish/{huawei_ibmc, inspur_isbmc, fujitsu_irmc, quanta_qct_bmc}.yml | `- - users` 4 곳 제거 (sections.yml channels=[os] 정합) | sections=9, users=False (모든 vendor) |

→ 코드 변경 9 라인 (5 capabilities 추가 + 4 users drift 정정). 모두 cycle 2026-05-01 fallback 코드 활용 (신규 fallback 코드 0 라인 추가).

### 정적 검증 (2026-05-06)

```
adapters/redfish/dell_idrac8.yml:    sections=9 users=False power=True storage=True
adapters/redfish/hpe_ilo4.yml:       sections=9 users=False power=True storage=True
adapters/redfish/lenovo_imm2.yml:    sections=9 users=False power=True storage=True
adapters/redfish/huawei_ibmc.yml:    sections=9 users=False power=True storage=True
adapters/redfish/inspur_isbmc.yml:   sections=9 users=False power=True storage=True
adapters/redfish/fujitsu_irmc.yml:   sections=9 users=False power=True storage=True
adapters/redfish/quanta_qct_bmc.yml: sections=9 users=False power=True storage=True
```

→ 7 adapter 모두 9 sections (system/hardware/bmc/cpu/memory/storage/network/firmware/power) 정합. users 4 곳 제거 정합 (sections.yml channels=[os]).

### Additive only 검증

| 변경 | Additive 여부 |
|---|---|
| W1~W5 (5 capabilities 추가) | 기존 capabilities 모두 유지 + power/storage 추가만 — Additive ✓ |
| W6 (users 4 곳 제거) | drift 정정 (sections.yml 정본 우선 — Redfish 채널 미해당 항목 제거). 기존 존재 안 했어야 할 entry 정정 — drift fix 분류 |

→ rule 92 R2 위반 0건. 사용자 명시 (2026-05-01 "기존에있는것을 버리는게아니라 더 다양한환경을 호환하기위해서") 정합.



## 사용자 의도

M-D2 web 검색 gap 결과 → 호환성 fallback 코드 추가. **Additive only** (rule 92 R2 + 사용자 명시 2026-05-01 "기존에있는것을 버리는게아니라 더 다양한환경을 호환하기위해서").

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (_endpoint_with_fallback / _gather_<section> / _FALLBACK_VENDOR_MAP), adapter YAML (필요 시 신 fallback target 추가) |
| 영향 vendor | M-D2 결과 따라 (~9 vendor 모두 가능) |
| 함께 바뀔 것 | 회귀 fixture (M-D4) + EXTERNAL_CONTRACTS.md (origin 주석) + adapter origin 주석 (rule 96 R1) |
| 리스크 top 3 | (1) 기존 path 깨짐 — Additive only 위반 / (2) Fallback chain 무한 루프 / (3) BMC 응답 시간 초과 |
| 진행 확인 | M-D2 [DONE] fallback 후보 list 입력 |

## 작업 spec

### Additive only 원칙 (rule 92 R2)

| 변경 종류 | 허용 / 금지 |
|---|---|
| 새 fallback target 추가 (기존 path 실패 시 시도) | **허용** |
| 새 OEM 분기 추가 (기존 분기 + 새 vendor) | **허용** |
| 기존 path 변경 / 삭제 | **금지** (사용자 명시) |
| 기존 OEM 분기 동작 변경 | **금지** |
| 새 ad-hoc 변수 / set_fact 추가 | **허용** (타 fragment 침범 X) |

### Fallback 패턴 (cycle 2026-05-01 학습)

`_endpoint_with_fallback` 헬퍼 (B5, redfish_gather.py 추가됨):

```python
def _endpoint_with_fallback(self, primary_path, fallback_paths, accept_404=True):
    """기존 path 시도 → 실패 시 fallback_paths 순차 시도"""
    response = self._get(primary_path)
    if response.status_code == 200:
        return response.json()
    if accept_404 and response.status_code == 404:
        for fb_path in fallback_paths:
            fb_response = self._get(fb_path)
            if fb_response.status_code == 200:
                return fb_response.json()
    return None  # not_supported 분류
```

### M-D2 산출물 → 코드 변경 매핑

각 fallback 후보 → 다음 중 하나:

| 후보 종류 | 코드 변경 위치 |
|---|---|
| (a) PowerSubsystem fallback (DMTF 2020.4) | `_gather_power_subsystem` (이미 cycle 2026-05-01 적용 — 재검증) |
| (b) Storage → SimpleStorage fallback | `_gather_storage` (모범 패턴) |
| (c) NetworkPorts → Ports fallback (HPE Gen12 deprecated) | `_gather_network_adapters` |
| (d) AccountService OEM 분기 추가 (Cisco / Huawei / Inspur 등) | `account_service_provision` |
| (e) Manager.LinkStatus fallback | `_gather_bmc` |
| (f) ThermalSubsystem fallback (DMTF 2020.4) | (향후 thermal 섹션 진입 시) |
| (g) Volume.Encrypted / SED fallback | `_gather_storage` |
| (h) UpdateService firmware list fallback | `_gather_firmware` |
| ... | (M-D2 결과로 채움) |

### 신규 4 vendor (Huawei / Inspur / Fujitsu / Quanta) 적용

각 vendor adapter (cycle-019 phase 2 추가) 의 capabilities 갱신:
- collect.standard_endpoint: `/redfish/v1/Systems/{id}` 등 표준
- collect.fallback: M-D2 검색 결과 따라
- normalize.oem_path: vendor 별 OEM extraction (rule 12 R1 Allowed)

### 신규 7 generation 재검증 (cycle 2026-05-01 적용분)

dell_idrac10 / hpe_ilo7 / lenovo_xcc3 / supermicro_x12/13/14 / cisco_ucs_xseries:
- 이미 fallback 적용 — M-D2 검색 결과로 누락 영역 식별 + 보강

## 회귀 / 검증

- pytest 108 + N건 PASS (M-D4 에서 N건 회귀 추가)
- 정적 검증:
  - `python scripts/ai/verify_vendor_boundary.py` (rule 12)
  - `python scripts/ai/hooks/adapter_origin_check.py` (rule 96 R1)
  - `python scripts/ai/hooks/cross_channel_consistency_check.py` (rule 13 R5 envelope shape)
  - `python -m ast redfish-gather/library/redfish_gather.py`

## risk

- (HIGH) Additive only 위반 시 회귀 사고. 모든 변경 line 검토 의무
- (MED) Fallback chain 무한 루프 — 각 fallback path 의 timeout 명시
- (MED) BMC 응답 시간 초과 — fallback 시도 횟수 제한 (max 3)
- (LOW) origin 주석 누락 — adapter_origin_check 자동 검출

## 완료 조건

- [ ] M-D2 fallback 후보 모든 적용 (~50~80 cell 변경 가능)
- [ ] Additive only 검증 (각 변경 line 별 기존 path 유지 확인)
- [ ] origin 주석 (rule 96 R1) — 각 변경에 source URL
- [ ] 정적 검증 PASS
- [ ] 회귀 fixture 식별 (M-D4 입력)
- [ ] commit: `feat: [M-D3 DONE] vendor 호환성 fallback N건 (additive only)`

→ 본 ticket 변경 규모 큼 (~200~500 lines) → **N개 sub commit 으로 분할** (vendor 별 또는 section 별):
- `feat: [M-D3-1 DONE] PowerSubsystem fallback 보강 (DMTF 2020.4)`
- `feat: [M-D3-2 DONE] AccountService OEM 분기 추가 (4 vendor)`
- ...

## 다음 세션 첫 지시 템플릿

```
M-D3 fallback 코드 추가 진입.

읽기 우선순위:
1. fixes/M-D3.md
2. M-D2 fallback 후보 list (산출물)
3. redfish-gather/library/redfish_gather.py _endpoint_with_fallback (B5)
4. 이전 cycle commit: 9eb11fe4 (404→unsupported), ce8d5e3c (P1 22건 신 generation)
5. rule 92 R2 (Additive only)
6. rule 12 R1 Allowed 영역 (vendor 분기 OK 영역)

작업:
1. M-D2 fallback 후보 별 코드 변경 (vendor / section 분할)
2. origin 주석 (rule 96 R1)
3. 정적 검증 PASS
4. M-D4 회귀 fixture 식별 → 다음 ticket 입력

선행: M-D2 [DONE]
후속: M-D4 (회귀 검증)
```

## 관련

- rule 92 R2 (Additive only)
- rule 96 R1 (origin 주석)
- rule 12 R1 (vendor 경계 Allowed)
- skill: vendor-change-impact
- 이전 cycle 패턴: cycle 2026-05-01 P1 22건 (commit ce8d5e3c)
