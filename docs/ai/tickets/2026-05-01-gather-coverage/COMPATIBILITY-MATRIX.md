# 호환성 매트릭스 (Compatibility Fallback)

> 사용자 명시 (2026-05-01): "redfish 모델/버전에 따라 api경로/데이터 다를 수 있기 때문에" 다양한 환경 대비.
> **새 데이터 수집이 아니다 — 같은 정보를 다른 path/schema 에서 가져올 수 있게 fallback.**

> 사용자 명시: "lab 장비는 테스트해볼 수 있지만 한계가 있다. 그래서 web 검색하라고 한 것."
> → web 검색이 lab fixture 대체 역할. 검색에서 호환성 정보 충분히 모이면 fallback 코드 적용 가능.

## 이미 적용된 호환성 fallback (cycle 2026-04-30 / 2026-05-01)

### A. URL/path 변종
| # | 구 path | 신 path | 코드 위치 | 상태 |
|---|---|---|---|---|
| A1 | `/Storage` | `/SimpleStorage` (구 BMC) | gather_storage:1417 | ✓ |
| A2 | `/Power` | `/PowerSubsystem` (DMTF 2020.4+) | gather_power + _gather_power_subsystem | ✓ cycle 2026-05-01 |

### B. ServiceRoot 필드 위치 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| B1 | `Vendor` 필드 부재 (Redfish<1.6) | detect_vendor G3 fallback Chassis/Managers/System Manufacturer | ✓ cycle 2026-04-30 |
| B2 | ServiceRoot 빈 응답 | WWW-Authenticate realm fallback | ✓ G6 |

### C. OEM namespace 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| C1 | `Oem.Hpe` (iLO 5+) vs `Oem.Hp` (iLO 4) | `_extract_oem_hpe()` 둘 다 시도 | ✓ |
| C2 | `Oem.Dell.DellSystem` BIOSReleaseDate | `_hoist_oem_extras` _bios_date 끌어올림 | ✓ |
| C3 | `Oem.Lenovo.Chassis` (chassis 위치) | `_extract_oem_lenovo` chassis_data 인자 | ✓ |

### D. Status / Health 필드 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| D1 | `Status.Health` vs `Status.HealthRollup` (HPE) | gather_system MemorySummary fallback | ✓ |
| D2 | `IndicatorLED` (deprecated Gen11) vs `LocationIndicatorActive` | gather_system fallback | ✓ |

### E. 빈 응답 / 형식 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| E1 | `HostName` 빈 문자열 (HPE) → None | gather_system 정규화 | ✓ |
| E2 | `PartNumber` trailing whitespace (Cisco) → strip | _ne() / _ne_p() | ✓ |
| E3 | Memory `Manufacturer` raw JEDEC ID (Cisco) | `_normalize_jedec()` | ✓ B90 |
| E4 | `link_status` enum 다양 (Dell linkup / HPE NoLink / Cisco Connected) | `_normalize_link_status()` | ✓ B13 |
| E5 | `0.0.0.0` / `::` placeholder (HPE NameServers) | `_rf_norm_dns` filter | ✓ |
| E6 | `PowerControl` 비-dict (Cisco edge) | isinstance(dict) guard | ✓ |
| E7 | `TrustedModules` 비-list / 빈 list | isinstance(list) guard | ✓ |

### F. ProcessorType / 데이터 분리
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| F-prc | GPU/Accelerator가 Processor 컬렉션에 (Dell R760 Tesla T4) | normalize_standard.yml ProcessorType filter | ✓ B01 |

### G. 컬렉션 응답 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| G1 | `Members` 에 Name/Version 없음 (Dell/HPE/SM) | gather_firmware 개별 URI 조회 | ✓ |
| G2 | `Previous-` prefix (Dell 비활성 펌웨어) | gather_firmware skip | ✓ Q-14 |
| G3 | `N/A`/`""` Version (Cisco 빈 슬롯) | gather_firmware skip | ✓ B43 |
| G4 | `Pending` ID (Lenovo 적용 대기) | pending=true 메타 | ✓ |
| G5 | 빈 placeholder NetworkAdapter (Lenovo XCC SR650 V2) | port_count=0 + mfr/model 빈 → skip | ✓ |
| G6 | NIC root mac 누락 (HPE) → NetworkPorts fold-in | adapter level fold-in | ✓ B93 |

### H. PSU power_capacity 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| H1 | `PowerCapacityWatts` null (Cisco) → InputRanges[0].OutputWattage | gather_power fallback | ✓ |
| H2 | chassis level capacity null → PSU 합산 | 합산 fallback | ✓ |
| H3 | per-DIMM CapacityMiB 0 → MemorySummary.TotalSystemMemoryGiB * 1024 | gather_memory fallback | ✓ BUG-14 |
| H4 | per-processor TotalThreads 0 → System.ProcessorSummary.LogicalProcessorCount | gather_processors fallback | ✓ BUG-13 |

### I. HTTP 응답 status 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| I1 | 401 / 403 (인증 필요) → Redfish 살아있음 | probe_redfish 분류 | ✓ |
| I2 | 405 / 406 (method/Accept 협상) → Redfish 살아있음 | probe_redfish 분류 | ✓ cycle 2026-04-30 |
| I3 | 503 (BMC 일시 과부하) → 1회 retry + supported | probe_redfish | ✓ G5 |
| I4 | 404 (endpoint 부재 = 미지원) → 'not_supported' 분류 | _make_section_runner | ✓ cycle 2026-05-01 |

### J. HTTP 헤더 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| J1 | `Accept` 부재 시 일부 BMC 406 거부 | http_get 명시 | ✓ cycle 2026-04-30 |
| J2 | OData-Version / User-Agent 추가 시 일부 BMC reject | hotfix Accept만 유지 | ✓ |

### K. TLS / cipher 변종
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| K1 | OpenSSL 3.x legacy renegotiation (구 BMC) | OP_LEGACY_SERVER_CONNECT | ✓ |
| K2 | weak cipher (구 BMC HPE iLO4 / Lenovo IMM2) | SECLEVEL=0 | ✓ |
| K3 | self-signed cert | verify=False | ✓ |
| K4 | URLError/timeout/SSLError | 1회 retry payload=None | ✓ G5 |

### L. IPv4/IPv6 placeholder
| # | 변종 | 코드 위치 | 상태 |
|---|---|---|---|
| L1 | IPv4 0.0.0.0 / 빈 문자열 | filter | ✓ |
| L2 | IPv6 `::` placeholder | filter | ✓ |
| L3 | server NIC IPv4 부재 → BMC NIC fallback (Cisco) | gateways union | ✓ |

## 추가 호환성 fix 후보 (web 검색 R5 — 사용자 의도 부합)

### F33 — Session 인증 (X-Auth-Token) 도입 검토
- **현재**: Basic Auth만 — 매 요청 username/password 검증 → BMC 부하
- **호환성**: 5 vendor 모두 X-Auth-Token 지원 (HPE/Lenovo/Supermicro/Dell/Cisco)
- **변경 (Additive)**: session 생성 후 token 사용. failed 시 Basic Auth fallback
- **우선**: P3 (성능 영역, 단발성 gather라 영향 작음)
- **lab 한계**: 5 vendor 모두 web 문서 명시 — fixture 없이 적용 가능

### F34 — Drive Protocol OEM enum 자동 통과 (검증만)
- **현재**: `_safe(drv, 'Protocol')` raw read — 모든 enum (NVMe-oF / SAS-4 등) 자동 통과
- **변경 없음**: 이미 호환. 등재만
- **우선**: P3

### F35 — Manager URI 위치 변종 (검증만)
- **현재**: ServiceRoot.Managers collection 의 첫 member URI 사용 (`detect_vendor`)
- **호환**: HPE `/Managers/1` / OpenBMC `/bmc` / Superdome `/Managers/RMC` / Cisco `/Managers/CIMC` 모두 자동
- **변경 없음**: 이미 호환. 등재만
- **우선**: P3

### F36 — HPE OEM fallback sensor (thermal 영역, F6 묶음)
- **새 섹션 영역** — F6 진행 시 통합

## 종합 결론

**호환성 fallback 은 이미 대부분 적용됨** (35건 / cycle 2026-04-30 + 2026-05-01 + 이전 cycle 누적).

남은 진짜 호환성 fix 후보:
- F02 / F04 / F05 / F09 / F10 / F12 / F13 / F14 / F15 / F17 / F20 / F21 / F22 / F24
- F33 / F34 (검증) / F35 (검증) / F36 (F6 묶음)

**호환성 영역에서 추가 검색 효용 적음** — 이미 14 카테고리 (A~L) 다양한 변종 처리 완료.

신규 데이터 수집 (F03/F06/F19/F26/F28/F29/F30/F32/F31) 은 **사용자 의도와 어긋남** — 별도 영역으로 분리. 현재 cycle scope 외.

## 갱신 history

- 2026-05-01: 호환성 매트릭스 작성. 35건 적용된 호환성 분류. F33~F36 신규 후보. 신규 데이터 수집과 분리.
