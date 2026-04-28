# ADR-2026-04-28 — rule 12 R1 OEM namespace 예외 (소급 ADR)

## 상태

**Accepted** (소급 작성: 2026-04-28 cycle-010 / 원 결정 시점: 2026-04-28 cycle-006)

## 컨텍스트 (Why)

cycle-004 W2 vendor 경계 57건 분석에서 `redfish-gather/library/redfish_gather.py` 내부 vendor 분기 17건 발견 (`221-450, 705-706, 747`):

```python
# 예시 — gather_system 내부 OEM 추출
if vendor == 'hpe':
    oem = _safe(data, 'Oem', 'Hpe') or _safe(data, 'Oem', 'Hp') or {}
elif vendor == 'dell':
    oem = _safe(data, 'Oem', 'Dell', 'DellSystem') or {}
elif vendor == 'lenovo':
    oem = _safe(data, 'Oem', 'Lenovo') or {}
elif vendor == 'supermicro':
    oem = _safe(data, 'Oem', 'Supermicro') or {}
```

rule 12 R1 (adapter-vendor-boundary)은 `common/`, `redfish-gather/` 등 코드에 vendor 이름 하드코딩 금지를 선언. `redfish-gather/tasks/vendors/{vendor}/` 또는 adapter YAML capabilities에만 분기 허용.

**문제 본질**: 위 코드의 `Oem.Hpe` / `Oem.Dell` 등은 server-exporter 내부 결정이 아니라 **Redfish API spec 자체가 vendor namespace를 정의** (DMTF Redfish 표준: `/redfish/v1/Systems/{id}/Oem/{Vendor}`). 외부 계약 (rule 96)에 직접 의존.

vendor-agnostic 리팩토링을 강제하려면 OEM extractor를 adapter YAML에 추상화해야 하는데, 이는:

- 영향 vendor (Dell / HPE / Lenovo / Supermicro / Cisco) 전부 회귀 필요
- Round 권장 (실장비 검증)
- 별도 cycle 규모

## 결정 (What)

rule 12 R1에 **Allowed (cycle-006 추가)** 절 추가. `redfish-gather/library/redfish_gather.py`의 다음 영역을 의도된 예외로 명시:

1. `_FALLBACK_VENDOR_MAP` (vendor_aliases.yml load 실패 시 fallback)
2. OEM schema 추출 분기 (`if vendor == 'hpe': oem = _safe(data, 'Oem', 'Hpe')` 등)
3. `_detect_from_product` 의 vendor 시그니처 매핑
4. `bmc_names = {'dell': 'iDRAC', ...}` BMC 표시명 매핑

또한 `os-gather/tasks/{linux,windows}/gather_system.yml`의 hosting_type 판정용 OEM vendor 인식 list (set membership 패턴)도 Allowed.

해당 17 라인 모두 `# nosec rule12-r1` 주석으로 silence (`verify_vendor_boundary.py` 도구 인식).

## 결과 (Impact)

- `verify_vendor_boundary.py` exit 0 (cycle-006 26건 → 0건)
- vendor 추가 시 redfish_gather.py 동기화 의무 발생 (`_FALLBACK_VENDOR_MAP` + OEM extractor + bmc_names 3 위치) — `verify_harness_consistency.py`가 advisory 검증
- Redfish API spec OEM namespace 변경 시 (Redfish 표준 자체 변경) 영향 — rule 96 R1 origin 주석 + adapter YAML metadata로 trace
- 리팩토링 옵션 (옵션 2)은 NEXT_ACTIONS P2 항목으로 보존 — 별도 cycle 진입 시 결정

## 대안 비교 (Considered)

| 옵션 | 설명 | 결정 | 사유 |
|---|---|---|---|
| **옵션 1** | adapter origin metadata에 OEM 정보 기재 + vendor 추가 시 명시 | **부분 채택** | cycle-004에서 13 adapter origin 주석 추가 — 향후 vendor 추가 시 OEM path metadata 기재 의무화 |
| **옵션 2** | redfish_gather.py를 vendor-agnostic으로 리팩토링 (OEM extractor를 adapter capabilities로 위임) | **거절 (현 시점)** | 영향 vendor 전부 회귀 + Round 권장 — 회귀 위험 큼. 별도 cycle 후보로 보존 |
| **옵션 3** | rule 12 R1에 Allowed 절 추가 + nosec silence | **채택** | 외부 계약 (Redfish spec) 직접 의존이라는 본질 인정. 옵션 1 부분 채택과 조합 |

## 관련

- DRIFT: `docs/ai/catalogs/CONVENTION_DRIFT.md` DRIFT-006
- rule: `12-adapter-vendor-boundary` R1 (Allowed cycle-006 추가 절), `96-external-contract-integrity` R1
- 분석: `docs/ai/impact/2026-04-27-vendor-boundary-57.md`
- 도구: `scripts/ai/verify_vendor_boundary.py` (nosec rule12-r1 인식)
- 후속: NEXT_ACTIONS P2 — DRIFT-006 옵션 (2) redfish_gather.py vendor-agnostic 리팩토링 (별도 cycle)
- 정책 trigger: rule 70 R8 (rule 본문 의미 변경) — 본 ADR이 R8 적용 첫 사례

## 작성 메타

- 원 결정 적용: cycle-006 (2026-04-28)
- 본 ADR 소급 작성: cycle-010 (2026-04-28) — rule 70 R8 신설에 따른 governance trace 보강
- 작성자: AI (Claude) / 승인자: hshwang1994
