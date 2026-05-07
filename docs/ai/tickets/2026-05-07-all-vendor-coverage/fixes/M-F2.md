# M-F2 — Quanta mock fixture (S/D/T/J series)

> status: [PENDING] | depends: M-F1 | priority: P1 | worker: W3 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. mock fixture 추가."

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/quanta_qct/` (1 디렉터리 — Quanta OEM 약함으로 1 generation 의무) |
| 영향 vendor | Quanta QCT (lab 부재) |
| 함께 바뀔 것 | M-J1 OEM mapping + pytest e2e |
| 리스크 top 3 | (1) ODM 모델 응답 다양 / (2) Oem.Quanta_Computer_Inc vs Oem.QCT mock / (3) S/D/T/J series 차이 |
| 진행 확인 | M-F1 OEM tasks 후 진입 |

---

## fixture 구조

```
tests/fixtures/redfish/quanta_qct/
├── service_root.json
├── chassis_index.json
├── chassis_1.json                   # Manufacturer: "Quanta", Model: "S5B-MB" 등
├── chassis_1_power.json             # Power deprecated (Quanta 표준)
├── systems_index.json
├── systems_1.json                   # ProcessorSummary + Oem.Quanta_Computer_Inc
├── systems_1_storage.json
├── managers_index.json
├── managers_1.json
├── update_service.json
├── update_service_firmware.json
├── account_service.json
└── README.md                        # web sources URL + lab 부재 + ODM 가능성 명시
```

→ ODM 모델 (Microsoft Olympus 등) 은 별도 mock 가능 — 시간 가용 시.

---

## 회귀 / 검증

- [ ] 각 fixture JSON 파싱 성공
- [ ] README.md + web sources URL + ODM 모델 변형 가능성 명시
- [ ] pytest e2e Quanta 회귀 PASS — vendor=quanta 식별 / Oem.Quanta_Computer_Inc / Oem.QCT fallback

## risk

- (MED) ODM 모델 응답 형식 customer-specific — 사이트 도입 시 보정
- (LOW) S/D/T/J series 별 응답 차이 — 시간 가용 시 별도 mock

## 완료 조건

- [ ] tests/fixtures/redfish/quanta_qct/ 의무 (1 generation × ~10 endpoint = ~10 JSON)
- [ ] (선택) quanta_qct_olympus/ 추가 (ODM 변형)
- [ ] pytest e2e Quanta PASS
- [ ] commit: `test: [M-F2 DONE] Quanta mock fixture (S series + Oem.Quanta_Computer_Inc)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W3 → M-G1 (Superdome OEM 보강).

## 관련

- M-F1, M-J1, rule 96 R1-A
