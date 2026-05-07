# M-C3 — Huawei mock fixture (FusionServer Pro / Atlas)

> status: [PENDING] | depends: M-C2 | priority: P1 | worker: W2 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "lab 한계는 web sources로 보완. mock fixture 추가." (cycle 진입 ticket DONE 4종 검증 #1)

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `tests/fixtures/redfish/huawei_ibmc_v2/`, `huawei_ibmc_v3/`, `huawei_ibmc_v4/`, `huawei_atlas/` (디렉터리 4개) |
| 영향 vendor | Huawei iBMC (lab 부재) |
| 함께 바뀔 것 | M-J1 OEM mapping 검증 입력 + pytest e2e |
| 리스크 top 3 | (1) iBMC 응답 형식 정확성 (web sources 기반) / (2) Atlas vs FusionServer Pro 분기 / (3) iBMC 1.x mock 가용성 (응답 약함) |
| 진행 확인 | M-C2 OEM tasks 후 진입 |

---

## fixture 구조

```
tests/fixtures/redfish/huawei_ibmc_v2/   # iBMC 2.x (FusionServer Pro RH 시리즈)
├── service_root.json
├── chassis_index.json
├── chassis_1.json                      # Manufacturer: "Huawei", Model: "RH2288 V5"
├── chassis_1_power.json                # Power deprecated path (iBMC 2.x)
├── systems_index.json
├── systems_1.json                      # ProcessorSummary / Oem.Huawei.SystemInfo
├── systems_1_storage.json              # standard storage path
├── managers_index.json
├── managers_1.json                     # iBMC 펌웨어 정보
├── update_service.json
├── update_service_firmware.json
├── account_service.json
└── README.md                           # fixture 출처 + lab 부재 명시

tests/fixtures/redfish/huawei_ibmc_v4/   # iBMC 4.x (FusionServer Pro 신모델)
├── ... (위 동일 + chassis_1_power_subsystem.json — PowerSubsystem 도입)

tests/fixtures/redfish/huawei_atlas/     # Atlas 800 (AI training)
├── ... (위 동일 + Atlas-specific Oem.Huawei.AIComputeInfo)
```

iBMC 1.x mock 은 Redfish 응답 매우 약함 — service_root.json + chassis_1.json 만 (graceful degradation 시뮬).

---

## fixture 작성 우선순위

| 우선순위 | generation | 모델 | 이유 |
|---|---|---|---|
| 1 | iBMC 2.x | RH2288 V5 (FusionServer Pro 일반) | 대표 generation — OEM 영역 존재 |
| 2 | iBMC 4.x | (최신 FusionServer Pro) | PowerSubsystem 도입 검증 |
| 3 | Atlas | Atlas 800 | AI 서버 분기 검증 |
| 4 | iBMC 1.x | (legacy 모델) | graceful degradation (Redfish 약함) — 시간 가용 시 |

---

## 권장 작성 순서

1. **README.md** (4 디렉터리 공통) — web sources URL + lab 부재 명시 + Huawei iBMC Redfish API guide URL
2. **service_root.json + chassis_1.json + systems_1.json** — vendor 식별 핵심
3. **storage / power 영역** — generation 별 분기
4. **Oem.Huawei 영역 추가** (chassis_1.json + systems_1.json 안에 Oem.Huawei.* sub-namespace)
5. **managers_1.json + update_service / firmware / account_service** — 표준 path

---

## 회귀 / 검증

### 정적 검증

- [ ] 각 fixture JSON `python -m json.tool` 파싱 성공
- [ ] README.md 모든 디렉터리 + web sources URL

### 동적 검증 (pytest e2e)

```bash
pytest tests/e2e/test_huawei_envelope.py -v

# 검증:
# - 각 fixture 로 redfish_gather.py 실행 (mock requests)
# - envelope 13 필드 모두 emit
# - vendor=huawei / generation=ibmc 식별
# - sections 매트릭스 (iBMC 2.x storage=standard / iBMC 4.x power=PowerSubsystem)
# - Oem.Huawei.SystemInfo 추출 → _data_fragment.bmc.oem_huawei.system_health
```

### Additive only

- [ ] tests/fixtures/redfish/huawei_*/ 신설만 (기존 fixture 변경 0)

---

## risk

- (MED) iBMC 1.x mock 가용성 약함 — Redfish 미지원 BMC 도 있음. service_root.json + chassis_1.json 만 mock + protocol fail 시뮬
- (LOW) Atlas AI 서버 응답은 web sources 약함 — FusionServer Pro 와 동일 가정 + AI-specific OEM 추가

## 완료 조건

- [ ] tests/fixtures/redfish/huawei_ibmc_v2/ + huawei_ibmc_v4/ 의무 (2 generation × ~10 endpoint = ~20 JSON)
- [ ] huawei_atlas/ + huawei_ibmc_v1/ 가용 시 추가 ([SKIP] 명시 가능)
- [ ] pytest e2e Huawei 회귀 PASS
- [ ] commit: `test: [M-C3 DONE] Huawei mock fixture (iBMC 2.x / 4.x + Atlas) — lab 부재 web sources`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W2 → M-D1 (Inspur OEM tasks).

## 관련

- M-C1, M-C2 (Huawei 영역)
- M-J1 (OEM mapping 입력)
- rule 96 R1-A (web sources)
- 정본: `tests/fixtures/redfish/dell_idrac10/` (cycle 2026-05-06 패턴)
