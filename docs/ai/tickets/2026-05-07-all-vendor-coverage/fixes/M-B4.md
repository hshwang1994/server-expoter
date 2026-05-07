# M-B4 — Supermicro mock fixture (X9~X14 + AMD/ARM)

> status: [PENDING] | depends: M-B3 | priority: P1 | worker: W1 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. mock fixture 추가." (cycle 진입 ticket DONE 4종 검증 수단 #1)

lab 부재 → mock fixture 로 회귀 회피. Supermicro 7 generation 모두 mock 응답 (ServiceRoot / Chassis / Systems / Storage / Volumes / Drives / Managers / UpdateService / AccountService).

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/supermicro_bmc/`, `supermicro_x9/`, `supermicro_x10/`, `supermicro_x11/`, `supermicro_x12/`, `supermicro_x13/`, `supermicro_x14/`, `supermicro_h12/`, `supermicro_ars/` (디렉터리 9개) |
| 영향 vendor | Supermicro (lab 부재) |
| 함께 바뀔 것 | M-J1 (OEM mapping 검증 입력) + pytest e2e 회귀 |
| 리스크 top 3 | (1) mock 응답 형식 정확성 (web sources 검증) / (2) fixture 디렉터리 비대화 (9개 generation × 9 endpoint = ~81 JSON) / (3) Additive only — 사이트 검증 fixture 영향 0 |
| 진행 확인 | M-B3 model_patterns 확장 후 진입 |

---

## fixture 구조 (각 generation 디렉터리)

```
tests/fixtures/redfish/supermicro_x10/
├── service_root.json          # /redfish/v1/
├── chassis_index.json         # /redfish/v1/Chassis
├── chassis_1.json             # /redfish/v1/Chassis/1
├── chassis_1_power.json       # /redfish/v1/Chassis/1/Power (X10 deprecated path)
├── systems_index.json         # /redfish/v1/Systems
├── systems_1.json             # /redfish/v1/Systems/1
├── systems_1_simple_storage.json  # /redfish/v1/Systems/1/SimpleStorage (X10 사용)
├── managers_index.json        # /redfish/v1/Managers
├── managers_1.json            # /redfish/v1/Managers/1
├── update_service.json        # /redfish/v1/UpdateService
├── update_service_firmware.json   # /redfish/v1/UpdateService/FirmwareInventory
├── account_service.json       # /redfish/v1/AccountService
└── README.md                  # fixture 출처 + web sources URL + lab 부재 명시
```

X12+ (PowerSubsystem 도입) 의 경우 `chassis_1_power_subsystem.json` 추가 (Power deprecated path 와 dual). X11+ (standard storage) 의 경우 `systems_1_storage.json` + `systems_1_storage_volumes.json` + `systems_1_storage_drives.json` 추가.

---

## fixture 작성 원칙 (rule 96 R1-A 의무)

각 fixture JSON 파일 첫 줄에 주석 (또는 README.md 에 일괄):

```json
{
  "_origin": "https://www.supermicro.com/manuals/superserver/IPMI/IPMI_Users_Guide_X10.pdf (확인 2026-05-07)",
  "_lab_status": "부재 — 사용자 명시 2026-05-07 Q2",
  "_note": "web sources 기반 mock — 실 BMC 응답과 차이 있을 수 있음. lab 도입 후 별도 cycle 에서 보정",
  "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
  "@odata.id": "/redfish/v1/",
  "@odata.type": "#ServiceRoot.v1_5_0.ServiceRoot",
  "Id": "RootService",
  "Name": "Root Service",
  "RedfishVersion": "1.6.0",
  ...
}
```

(JSON 표준은 주석 미지원 → `_origin` / `_lab_status` / `_note` underscore prefix key 로. 또는 README.md 에 일괄 명시.)

---

## 권장 fixture 작성 순서

1. **README.md 작성** (모든 디렉터리 공통) — web sources URL + lab 부재 명시 + 파일별 endpoint 매트릭스
2. **service_root.json** — RedfishVersion / Links / OEM 표시
3. **chassis_index.json + chassis_1.json** — Manufacturer / Model 등 vendor 식별 핵심
4. **systems_1.json** — ProcessorSummary / MemorySummary / Manufacturer
5. **storage 영역** — generation 별 분기 (X10 SimpleStorage / X11+ Storage)
6. **power 영역** — generation 별 분기 (X12+ PowerSubsystem)
7. **managers_1.json** — BMC 펌웨어 정보
8. **update_service / firmware / account_service** — 표준 path

---

## 권장 generation 별 우선순위

| 우선순위 | generation | 이유 |
|---|---|---|
| 1 | x14 | 최신 — X12 + 추가 |
| 2 | x12 | PowerSubsystem 도입 + standard storage 분기 |
| 3 | x10 | SimpleStorage + Power deprecated only — legacy 분기 검증 |
| 4 | x11 | standard storage 도입 분기 |
| 5 | x9 | 가장 legacy — 최소 응답 |
| 6 | x13 | x12 와 거의 동일 (PowerSubsystem dual) |
| 7 | bmc | generic fallback |
| 8 | h12 | AMD platform 검증 (X12 와 거의 동일 + Processor Manufacturer="AMD") |
| 9 | ars | ARM platform 검증 (Processor architecture="arm64") |

→ 우선순위 1~5 는 본 ticket 의무. 6~9 는 시간 가용 시 추가 (cycle 종료 시 [SKIP] 가능 — 사유 명시).

---

## 회귀 / 검증

### 정적 검증

- [ ] 각 fixture JSON `python -m json.tool` 파싱 성공 (syntax 오류 0)
- [ ] README.md 모든 디렉터리 존재 + web sources URL 명시

### 동적 검증 — pytest e2e

```bash
# tests/e2e/test_supermicro_envelope.py 신설 (또는 기존 test_envelope_failure_modes.py 패턴 따름)
pytest tests/e2e/test_supermicro_envelope.py -v

# 검증:
# - 각 generation fixture 로 redfish_gather.py 실행 (mock requests)
# - envelope 13 필드 모두 emit
# - vendor=supermicro / generation 정확히 식별
# - status=success (mock 정상 응답 가정)
# - sections 매트릭스 (X10 storage=simple / X12+ power=PowerSubsystem)
```

### Additive only

- [ ] 사이트 검증 4 vendor fixture 영향 0
- [ ] tests/fixtures/redfish/supermicro_*/ 신설만 (기존 fixture 변경 0)

---

## risk

- (MED) mock 응답 형식이 실 BMC 와 다를 가능성 — vendor docs 기반 작성. lab 도입 시 보정 (별도 cycle)
- (LOW) fixture 비대화 — 9 generation × ~10 endpoint = 90+ JSON 파일. cycle 종료 시 우선순위 1~5 만 의무, 6~9 [SKIP] 허용

## 완료 조건

- [ ] tests/fixtures/redfish/supermicro_x10/ + x12/ + x14/ 최소 의무 (3 generation × ~10 endpoint = ~30 JSON)
- [ ] x9 / x11 / x13 / bmc / h12 / ars 가용 시 추가 ([SKIP] 명시 가능)
- [ ] pytest e2e Supermicro 회귀 PASS
- [ ] commit: `test: [M-B4 DONE] Supermicro mock fixture (X10/X12/X14 + 선택) — lab 부재 web sources 기반`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W1 영역 종료. 다음 worker (W2 — Huawei + Inspur) 진입 알림.

## 관련

- M-B1, M-B2, M-B3 (Supermicro 영역)
- M-J1 (OEM mapping 입력)
- rule 96 R1-A (web sources)
- rule 92 R2 (Additive only)
- 정본: `tests/fixtures/redfish/dell_idrac10/` (cycle 2026-05-06 사이트 검증 fixture 패턴)
