# M-G2 — Superdome Flex mock fixture (Gen 1/2 + 280)

> status: [PENDING] | depends: M-G1 | priority: P1 | worker: W3 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. mock fixture 추가."

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/hpe_superdome_flex/`, `hpe_superdome_280/` (2 디렉터리) |
| 영향 vendor | HPE Superdome Flex (lab 부재) |
| 함께 바뀔 것 | M-J1 OEM mapping + pytest e2e |
| 리스크 top 3 | (1) Superdome 응답 web sources 약함 (mission-critical 하드웨어) / (2) Partition / FlexNode 영역 정확성 / (3) iLO 시리즈 mock 영향 0 (Additive) |
| 진행 확인 | M-G1 OEM 보강 후 진입 |

---

## fixture 구조

```
tests/fixtures/redfish/hpe_superdome_flex/   # Gen 1/2 통합
├── service_root.json
├── chassis_index.json
├── chassis_1.json                          # Manufacturer: "HPE", Model: "Superdome Flex"
├── chassis_1_power.json
├── systems_index.json
├── systems_1.json                          # ProcessorSummary + Oem.Hpe.PartitionInfo
├── systems_1_storage.json
├── managers_index.json
├── managers_1.json                         # iLO 펌웨어 + Oem.Hpe.GlobalConfiguration
├── update_service.json
├── update_service_firmware.json
├── account_service.json
└── README.md                               # web sources URL + lab 부재 명시

tests/fixtures/redfish/hpe_superdome_280/    # 280 series
└── ... (chassis_1.json model="Superdome Flex 280")
```

---

## fixture 작성 원칙

- README.md 에 web sources URL + lab 부재 + Gen 1/2/280 변형 가능성 명시
- chassis_1.json + systems_1.json + managers_1.json 안에 다음 OEM 영역 추가:
  - `Oem.Hpe.PartitionInfo` (systems_1.json)
  - `Oem.Hpe.FlexNodeInfo` (chassis_1.json)
  - `Oem.Hpe.GlobalConfiguration` (systems_1.json + managers_1.json)
- 일반 iLO 시리즈 OEM (`Oem.Hpe.SmartStorage`) 와 분리 — Superdome 은 SmartStorage 영역 없음 (storage-less node)

---

## 회귀 / 검증

- [ ] 각 fixture JSON 파싱 성공
- [ ] README.md + web sources URL
- [ ] pytest e2e Superdome 회귀 PASS — vendor=hpe / model=Superdome Flex / Partition / FlexNode / Global 추출
- [ ] iLO 시리즈 fixture (사이트 검증 iLO7) 영향 0 (Additive)

## risk

- (MED) Gen 1 (2018-2020) vs Gen 2 (2020-2022) vs 280 (2022+) 응답 차이 — 본 ticket 은 generic mock
- (LOW) Storage-less node mock — Storage 영역 없음 또는 빈 응답

## 완료 조건

- [ ] tests/fixtures/redfish/hpe_superdome_flex/ 의무 (1 generation × ~10 endpoint = ~10 JSON)
- [ ] (선택) hpe_superdome_280/ 추가
- [ ] pytest e2e Superdome PASS
- [ ] commit: `test: [M-G2 DONE] Superdome Flex mock fixture (Gen 1/2 + 280 선택)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W3 영역 종료. 다음 worker (W4 — 기존 4 vendor 미검증 + gather sections) 진입 알림.

## 관련

- M-G1, adapters/redfish/hpe_superdome_flex.yml
- rule 96 R1-A
