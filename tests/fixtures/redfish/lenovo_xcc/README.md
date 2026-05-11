# Lenovo XCC (XCC1 + XCC2) fixture — M-H3 (cycle 2026-05-07)

> Round 11 lab 검증 (XCC1 V2 — `tests/fixtures/redfish/lenovo/`).
> 본 fixture 는 XCC2 (ThinkSystem V3) 변형 시뮬 — web sources only.

## 출처

- Sources: `https://pubs.lenovo.com/xcc/` / `https://lenovopress.lenovo.com/lp1604-lenovo-xclarity-controller-xcc`
- Generation: XCC2 (ThinkSystem V3) 2020-2024

## 시뮬레이션 시나리오

- ServiceRoot.RedfishVersion: "1.17.0" (DSP0268 v1.10+, XCC2 시기)
- XCC version: "TAOT 3.10" (XCC2 V3 모델 펌웨어 prefix)
- Standard storage path
- Power deprecated only (PowerSubsystem 미도입 시기 또는 dual)
- Oem.Lenovo namespace

## HTTP 헤더 정책 (rule 25 R7-A-1)

- cycle 2026-04-30 사이트 사고 — Accept + OData-Version + User-Agent reject
- "Accept만" hotfix 적용 (redfish_gather.py _get())
- XCC1 / XCC2 모두 보수적 정책

## 매칭 검증

- `lenovo_xcc.yml` (priority=100) 매칭 — firmware_patterns "XCC" / "TAOT*"
- model_patterns "ThinkSystem.*V3" 매칭
- XCC3 (priority=120) 패턴 (firmware "XCC3" / "ThinkSystem.*V4") 매치 안 됨
