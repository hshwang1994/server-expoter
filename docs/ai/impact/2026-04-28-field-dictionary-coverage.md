# field_dictionary 46 entries × vendor 매핑 정합 (Round 11)

> 일자: 2026-04-28
> rule: 13 R1 (3종 동반 갱신), 13 R2 (Must 모든 vendor)
> 데이터 출처: `tests/reference/redfish/<vendor>/<ip>/`
> 분석 목적: schema/field_dictionary.yml 46 entries가 4 vendor 실 endpoint에서 추출 가능한지 매트릭스 검증

## field_dictionary.yml 분포 (실측 2026-04-28)

| 분류 | 개수 |
|---|---|
| Must | 31 |
| Nice | 9 |
| Skip | 6 |
| **합계** | **46** |

CLAUDE.md / rule 13 / SCHEMA_FIELDS.md 명시 분포와 정합.

## Section별 필드 분포

| Section | Total | Must | Nice | Skip |
|---|---|---|---|---|
| storage | **17** | 12 | 3 | 2 |
| users | 6 | 3 | 2 | 1 |
| hardware | 4 | 3 | 1 | 0 |
| memory | 3 | 3 | 0 | 0 |
| cpu | 2 | 1 | 0 | 1 |
| firmware[] | 2 | 1 | 0 | 1 |
| network | 2 | 1 | 1 | 0 |
| system | 2 | 1 | 0 | 1 |
| diagnosis | 2 | 1 | 1 | 0 |
| bmc | 1 | 1 | 0 | 0 |
| correlation | 1 | 1 | 0 | 0 |
| meta | 1 | 0 | 1 | 0 |
| power | 1 | 1 | 0 | 0 |
| sections | 1 | 1 | 0 | 0 |
| status | 1 | 1 | 0 | 0 |

> envelope-level 5종 (status / sections / meta / correlation / diagnosis)는 build_*.yml에서 생성 — 모든 vendor 공통.

## 데이터 섹션 vendor × section 매트릭스

| Section | Dell R760 | HPE DL380 Gen11 | Lenovo SR650 V2 | Cisco TA-UNODE-G1 |
|---|---|---|---|---|
| system   | OK | OK | OK | OK |
| hardware | OK | OK | OK | OK |
| bmc      | OK | OK | OK | OK |
| cpu      | OK | OK | OK | OK |
| memory   | OK | OK | OK | OK |
| storage  | OK | OK | OK | OK |
| network  | OK | OK | OK | OK |
| firmware | OK | OK | OK | OK |
| power    | OK | OK | OK | OK |
| users    | OK | OK | OK | OK |

**모든 9 데이터 섹션 + users가 4 vendor에서 모두 endpoint 노출 OK** (rule 13 R2 — Must 필드 모든 vendor 보장 가능).

## 판정 기준 (heuristic)

각 section에 대해 redfish endpoint 존재 여부:

| Section | 검사 endpoint pattern |
|---|---|
| system | `/redfish/v1/Systems/*` |
| hardware | `/redfish/v1/Chassis/*` |
| bmc | `/redfish/v1/Managers/*` |
| cpu | `/redfish/v1/Systems/*/Processors*` |
| memory | `/redfish/v1/Systems/*/Memory*` |
| storage | `/redfish/v1/Systems/*/Storage*` 또는 `SimpleStorage*` |
| network | `/redfish/v1/Systems/*/EthernetInterfaces*` 또는 `NetworkInterfaces*` |
| firmware | `/redfish/v1/UpdateService/FirmwareInventory` |
| users | `/redfish/v1/AccountService/Accounts` |
| power | `/redfish/v1/Chassis/*/Power*` |

> 이 검사는 endpoint 존재성만 확인. 필드별 정밀 매핑 (예: `system.serial` ↔ `SerialNumber`)은 normalize task가 처리 — 별도 회귀 권장.

## 결론

- **46 entries / Must 31 / Nice 9 / Skip 6 — 분포 정합** (cycle-006 / DRIFT-004 resolved 후 측정값 일치)
- **모든 데이터 section이 4 vendor에서 endpoint 노출** — rule 13 R2 (Must 모든 vendor) 충족 가능 환경
- **잔여 검증**: 각 Must 필드의 raw → normalize 매핑 정합은 회귀 테스트 (`pytest tests/`)에서 검증 (Jenkins Stage 4)

## 후속

- (E2) **필드별 raw 매핑 검증**: tests/reference/redfish/* raw 데이터로 normalize_*.yml 시뮬레이션 → field_dictionary와 1:1 매핑 정합 확인 (별도 작업)
- (E3) **OS 채널 매핑 매트릭스**: Linux 6개 distro × users / system 등 OS-side 섹션 매핑 매트릭스 (별도 작업)

## 관련

- rule: 13 (output-schema-fields), 21 (output-baseline-fixtures), 70 (docs-and-evidence-policy)
- 정본: `schema/field_dictionary.yml`, `schema/sections.yml`
- 데이터: `tests/reference/redfish/`
- evidence: `tests/evidence/2026-04-28-reference-collection.md`
