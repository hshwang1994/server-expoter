# Cisco TA-UNODE-G1 모델 분석 (Round 11)

> 일자: 2026-04-28
> 데이터 출처: `tests/reference/redfish/cisco/10_100_15_2/`
> 분석 목적: 새로 발견한 모델 (TA-UNODE-G1)이 기존 cisco_cimc adapter로 정상 매치되고 모든 섹션이 수집 가능한지 검증

## 모델 식별

| 항목 | 실측 값 |
|---|---|
| **ServiceRoot.Product** | TA-UNODE-G1 |
| **ServiceRoot.Vendor** | Cisco Systems Inc. |
| **System.Manufacturer** | Cisco Systems Inc |
| **System.Model** | TA-UNODE-G1 |
| **System.URI** | /redfish/v1/Systems/FCH2116V1V0 (Serial as ID) |
| **Manager URI** | /redfish/v1/Managers/CIMC |
| **Manager.Model** | TA-UNODE-G1 |
| **CIMC FirmwareVersion** | 4.1(2g) |
| **BIOS** | **C220M4.4.1.2c.0.0202211901** (UCS C220 M4 시리즈 펌웨어 식별 가능) |
| **CPU** | Intel Xeon E5-2699 v4 (Broadwell-EP) × 2 |
| **Memory** | 1024 GB |
| **Redfish 버전** | 1.2.0 (구 spec — Cisco BMC가 표준 부분 지원) |

**해석**: "TA-UNODE-G1"은 BIOS 식별자에서 **UCS C220 M4 하드웨어 위에 커스텀 펌웨어 brand로 식별됨**. Cisco가 UCS C220 M4를 OEM/ODM 형태로 다른 라벨로 출하한 변형으로 보임.

## adapter 매칭 결과

`adapters/redfish/cisco_cimc.yml` 기준:

```yaml
match:
  vendor: ["Cisco", "Cisco Systems Inc", "Cisco Systems Inc.", "Cisco Systems", "cisco"]
priority: 100
```

- **vendor 매칭**: "Cisco Systems Inc"가 list에 포함 → **MATCH**
- **firmware_patterns**: 없음 (모든 firmware OK)
- **model_patterns**: 없음 (모든 model OK)
- **점수**: priority(100) × 1000 + specificity(낮음) = **약 100000**
- **fallback redfish_generic**: priority(0) × 1000 = 0
- **결과**: cisco_cimc 선택 — **정상**

## 섹션 capability 매트릭스

cisco_cimc adapter capabilities 선언 vs 실측:

| Section | adapter 선언 | 실측 데이터 | 매칭 |
|---|---|---|---|
| system | ✓ | Manufacturer/Model/Serial/BIOS/UUID/HostName 모두 | OK |
| hardware | ✓ | Memory/Processors/PCIeDevices 링크 | OK |
| bmc | ✓ | Manager TA-UNODE-G1 FW 4.1(2g) | OK |
| cpu | ✓ | Processors collection (2 socket, Xeon E5-2699 v4) | OK |
| memory | ✓ | Memory collection + MemorySummary 1024 GB | OK |
| storage | ✓ | Storage + SimpleStorage 양쪽 노출 | OK |
| network | ✓ | EthernetInterfaces + NetworkInterfaces | OK |
| firmware | ✓ | UpdateService.FirmwareInventory: 7 components | OK |
| power | ✓ | PowerControl ×1 + PowerSupplies ×2 | OK |
| **users** | **MISSING** | AccountService.Accounts: 1 member 존재 | **갭** |

## 발견 — users 섹션 capabilities 미명시

`cisco_cimc.yml` capabilities.sections_supported에 **users 섹션 없음** (cycle-006 DRIFT-004에서 추가된 섹션).

**영향**:
- adapter capabilities는 가용성 선언만 (실 수집은 collect/normalize task가 담당)
- 실 수집 task가 users 섹션을 vendor-agnostic으로 처리하면 영향 없음
- adapter 기반 sections_supported 검사가 있다면 users 누락 가능

**권장**: cisco_cimc.yml + 다른 vendor adapter 4종에 users 섹션 추가 (별도 PR — 모든 vendor 일괄 처리).

## 미해결 (사용자 측)

- **10.100.15.1** HTTP 503 — CIMC 서비스 다운 (BMC 재기동 필요)
- **10.100.15.3** connect timeout — BMC 도달 불가 (전원/케이블/firmware 점검 필요)

위 2대도 회수되면 모델 일관성 추가 검증 가능.

## 결론

- **cisco_cimc adapter로 TA-UNODE-G1 정상 매치 + 9개 섹션 모두 수집 가능**
- `adapters/redfish/cisco_cimc.yml`의 metadata `Tested against (실측 2026-04-28)`에 본 정보 반영 완료
- 단일 차이: users 섹션 capabilities 누락 (별도 PR)

## 관련

- rule: 12 R3 (vendor 추가 3단계), 12 R4 (adapter 4 필수 필드), 96 R1 (origin 주석)
- skill: `score-adapter-match`, `add-new-vendor`
- 정본: `adapters/redfish/cisco_cimc.yml` (metadata 갱신 완료)
- 데이터: `tests/reference/redfish/cisco/10_100_15_2/`
