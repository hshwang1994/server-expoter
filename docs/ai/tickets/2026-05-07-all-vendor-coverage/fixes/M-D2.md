# M-D2 — Inspur mock fixture (NF/NP/SA series)

> status: [PENDING] | depends: M-D1 | priority: P1 | worker: W2 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. mock fixture 추가."

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/inspur_isbmc/` (1 디렉터리 — Inspur OEM 약함으로 1 generation 만 의무) |
| 영향 vendor | Inspur ISBMC (lab 부재) |
| 함께 바뀔 것 | M-J1 OEM mapping 검증 + pytest e2e |
| 리스크 top 3 | (1) Inspur 응답 형식 web sources 약함 / (2) Oem.Inspur vs Oem.Inspur_System 분기 mock / (3) NF/NP/SA series 차이 |
| 진행 확인 | M-D1 OEM tasks 후 진입 |

---

## fixture 구조

```
tests/fixtures/redfish/inspur_isbmc/
├── service_root.json
├── chassis_index.json
├── chassis_1.json                   # Manufacturer: "Inspur", Model: "NF5280M5"
├── chassis_1_power.json             # Power deprecated path
├── systems_index.json
├── systems_1.json                   # ProcessorSummary + Oem.Inspur (또는 Oem.Inspur_System) 영역
├── systems_1_storage.json           # standard storage path
├── managers_index.json
├── managers_1.json                  # ISBMC 펌웨어 정보
├── update_service.json
├── update_service_firmware.json
├── account_service.json
└── README.md                        # fixture 출처 + lab 부재 명시
```

→ Inspur 는 OEM 약함 — 1 generation mock 만 의무. NP / SA series 추가 mock 은 시간 가용 시.

---

## fixture 작성 원칙

- README.md 에 web sources URL + lab 부재 명시
- chassis_1.json + systems_1.json 에 `Oem.Inspur.SystemInfo` 추가 (M-D1 OEM tasks 검증 입력)
- 일부 fixture 는 `Oem.Inspur_System` (underscore) 변형 — fallback 분기 검증

---

## 회귀 / 검증

### 정적 검증

- [ ] 각 fixture JSON 파싱 성공
- [ ] README.md 존재 + web sources URL

### 동적 검증 (pytest e2e)

```bash
pytest tests/e2e/test_inspur_envelope.py -v

# 검증:
# - mock fixture 로 redfish_gather.py 실행
# - envelope 13 필드 모두 emit
# - vendor=inspur 식별
# - sections 매트릭스 (storage=standard / power=Power legacy)
# - Oem.Inspur 영역 → _data_fragment.bmc.oem_inspur 추출
# - Oem.Inspur_System fallback 분기 검증 (별도 fixture variant)
```

### Additive only

- [ ] tests/fixtures/redfish/inspur_*/ 신설만

---

## risk

- (MED) Inspur 응답 형식 web sources 가용성 낮음 — 가장 표준 가까운 응답 가정. 사이트 도입 시 보정
- (LOW) NP/SA series 별도 mock 누락 — 시간 가용 시 추가

## 완료 조건

- [ ] tests/fixtures/redfish/inspur_isbmc/ 의무 (1 generation × ~10 endpoint = ~10 JSON)
- [ ] (선택) inspur_isbmc_v2/ 추가 (Oem.Inspur_System variant)
- [ ] pytest e2e Inspur 회귀 PASS
- [ ] commit: `test: [M-D2 DONE] Inspur mock fixture (NF series + Oem.Inspur fallback)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W2 영역 종료. 다음 worker (W3 — Fujitsu + Quanta + Superdome) 진입 알림.

## 관련

- M-D1 (Inspur OEM tasks)
- M-J1 (OEM mapping 입력)
- rule 96 R1-A (web sources)
