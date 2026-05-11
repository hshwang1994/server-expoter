# Cisco CIMC 3.x (UCS C-series M5) fixture — M-H4 (cycle 2026-05-07)

> Lab 부재 — web sources only (rule 96 R1-A). Priority 1 fixture.

## 출처

- Sources: `https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/api/3_0/b_Cisco_IMC_REST_API_guide_301/m_redfish_api_examples.html`
- Generation: CIMC 3.x (UCS C-series M5 — Skylake-SP) 2017-2020

## 시뮬레이션 시나리오

- ServiceRoot.RedfishVersion: "1.6.0" (DSP0268 v1.6+)
- Manufacturer: "Cisco Systems Inc."
- Standard storage path
- Power deprecated only (PowerSubsystem 미도입 시기)
- OEM strategy: standard_only (Cisco OEM tasks 디렉터리 미생성)

## 매칭 검증

- `cisco_cimc.yml` (priority=100) 매칭 — firmware_patterns "^[4-6]\\." / "CIMC.*[4-6]"
- 본 fixture 의 펌웨어 "3.0(4j)" 는 `^[4-6]\\.` 에 미매치 → `cisco_bmc.yml` (priority=10) fallback
- model_patterns "C220 M5" / "UCSC-C220 M5" 매칭

## 주의

CIMC 3.x 는 firmware_patterns 의 "^[4-6]\\." 정의에 따라 advisory:
- Cisco web sources (rule 96 R1-A) 에 의하면 CIMC 3.x 는 Redfish 1.0-1.6 부분 지원
- cisco_cimc.yml 의 cover 범위는 4.x ~ 6.x. CIMC 3.x 는 cisco_bmc.yml fallback (생산 환경 동작 확인 필요)
