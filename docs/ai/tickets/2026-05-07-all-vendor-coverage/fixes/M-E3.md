# M-E3 — Fujitsu mock fixture (PRIMERGY / PRIMEQUEST)

> status: [PENDING] | depends: M-E2 | priority: P1 | worker: W3 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. mock fixture 추가."

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/fujitsu_irmc_s4/`, `fujitsu_irmc_s5/`, `fujitsu_irmc_s6/`, `fujitsu_primequest/` (4 디렉터리) |
| 영향 vendor | Fujitsu iRMC (lab 부재) |
| 함께 바뀔 것 | M-J1 OEM mapping + pytest e2e |
| 리스크 top 3 | (1) iRMC S2 mock 가용성 (Redfish 미지원) / (2) Oem.ts_fujitsu vs Oem.Fujitsu mock 분기 / (3) PRIMEQUEST 응답 web sources 약함 |
| 진행 확인 | M-E2 OEM tasks 후 진입 |

---

## fixture 구조

```
tests/fixtures/redfish/fujitsu_irmc_s5/   # 대표 generation
├── service_root.json
├── chassis_index.json
├── chassis_1.json                      # Manufacturer: "Fujitsu", Model: "PRIMERGY RX2540 M5"
├── chassis_1_power.json
├── systems_index.json
├── systems_1.json                      # ProcessorSummary + Oem.ts_fujitsu 영역
├── systems_1_storage.json              # standard storage
├── managers_index.json
├── managers_1.json                     # iRMC 펌웨어 정보
├── update_service.json
├── update_service_firmware.json
├── account_service.json
└── README.md                           # web sources URL + lab 부재 명시

tests/fixtures/redfish/fujitsu_irmc_s6/   # 최신 generation (PowerSubsystem 도입)
└── ... (S5 + chassis_1_power_subsystem.json)

tests/fixtures/redfish/fujitsu_primequest/ # mission-critical
└── ... (PRIMEQUEST-specific Oem.ts_fujitsu.PartitionInfo)
```

---

## 우선순위

| 우선 | generation | 모델 | 이유 |
|---|---|---|---|
| 1 | iRMC S5 | PRIMERGY RX2540 M5 | 대표 generation |
| 2 | iRMC S6 | PRIMERGY 신모델 | PowerSubsystem 도입 검증 |
| 3 | PRIMEQUEST | 3800B | mission-critical 분기 |
| 4 | iRMC S4 | PRIMERGY (legacy) | OEM 약함 분기 |
| 5 | iRMC S2 | (Redfish 미지원) | service_root.json + protocol fail 시뮬 |

→ 1~2 의무. 3~5 시간 가용 시.

---

## 회귀 / 검증

- [ ] 각 fixture JSON 파싱 성공
- [ ] README.md + web sources URL
- [ ] pytest e2e Fujitsu 회귀 PASS — vendor=fujitsu / generation 식별 / Oem.ts_fujitsu 추출

## risk

- (MED) iRMC S2 Redfish 미지원 mock — graceful degradation 시뮬
- (LOW) PRIMEQUEST Oem.ts_fujitsu.PartitionInfo 응답 형식 web sources 약함

## 완료 조건

- [ ] tests/fixtures/redfish/fujitsu_irmc_s5/ + s6/ 의무
- [ ] (선택) primequest / s4 / s2 추가
- [ ] pytest e2e Fujitsu PASS
- [ ] commit: `test: [M-E3 DONE] Fujitsu mock fixture (iRMC S5/S6 + PRIMEQUEST 선택)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W3 → M-F1 (Quanta OEM).

## 관련

- M-E1, M-E2 (Fujitsu 영역)
- M-J1 / rule 96 R1-A
