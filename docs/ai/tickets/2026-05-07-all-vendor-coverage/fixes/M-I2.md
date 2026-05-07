# M-I2 — power section 변형 매트릭스 + fallback (Power deprecated → PowerSubsystem 마이그레이션)

> status: [PENDING] | depends: M-I1 | priority: P1 | worker: W4 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "Power deprecated → PowerSubsystem 마이그레이션 진행도 매트릭스 + fallback." (cycle 진입)

DMTF Redfish 의 `/Chassis/{id}/Power` (deprecated) → `/Chassis/{id}/PowerSubsystem` 마이그레이션 — vendor 별 진행도 다름. 본 ticket 에서 fallback 로직 정합.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (power 수집 fallback 로직 보강) |
| 영향 vendor | 9 vendor — 사이트 검증 4 vendor 영향 0 (Additive) |
| 함께 바뀔 것 | M-J1 OEM mapping |
| 리스크 top 3 | (1) PowerSubsystem 우선 시도 → 404 fallback 누락 시 legacy generation 회귀 / (2) Power + PowerSubsystem dual (iDRAC9 5.x / iLO6) merge 정확성 / (3) DMTF spec 변천 — DSP0268 v1.13+ PowerSubsystem 표준 |
| 진행 확인 | M-I1 후 진입 — storage 와 동일 패턴 |

---

## Power 변형 매트릭스 (cycle 진입 시점)

| vendor | generation | path | strategy |
|---|---|---|---|
| Dell | iDRAC10 | `/Chassis/{id}/PowerSubsystem` | subsystem_only |
| Dell | iDRAC9 5.x+ | dual | subsystem_with_legacy_dual |
| Dell | iDRAC9 3.x-4.x | `/Chassis/{id}/Power` | legacy_only |
| Dell | iDRAC7-8 | 동일 | legacy_only |
| HPE | iLO7 | `/Chassis/{id}/PowerSubsystem` | subsystem_only |
| HPE | iLO5/6 | dual | subsystem_with_legacy_dual |
| HPE | iLO4- | `/Chassis/{id}/Power` | legacy_only |
| Lenovo | XCC3 | dual | subsystem_with_legacy_dual |
| Lenovo | XCC/XCC2 | `/Chassis/{id}/Power` | legacy_only |
| Lenovo | IMM2 | 동일 | legacy_only |
| Cisco | UCS X-series | `/Chassis/{id}/PowerSubsystem` | subsystem_only |
| Cisco | CIMC 4.x | dual (일부) | subsystem_with_legacy_fallback |
| Cisco | CIMC 1.x-3.x | `/Chassis/{id}/Power` | legacy_only |
| Supermicro | X12-X14 | dual | subsystem_with_legacy_dual |
| Supermicro | X9-X11 | `/Chassis/{id}/Power` | legacy_only |
| Huawei iBMC | 3.x+ | dual | subsystem_with_legacy_fallback |
| Huawei iBMC | 1.x-2.x | `/Chassis/{id}/Power` | legacy_only |
| Inspur | ISBMC | `/Chassis/{id}/Power` | legacy_only (확인 필요) |
| Fujitsu | iRMC S6+ | dual (일부) | subsystem_with_legacy_fallback |
| Fujitsu | iRMC S2-S5 | `/Chassis/{id}/Power` | legacy_only |
| Quanta | QCT | `/Chassis/{id}/Power` | legacy_only |

---

## 구현 (redfish_gather.py 보강 — Additive)

```python
def _collect_power(session, base_url, chassis_id, adapter_capabilities):
    """Power 수집 — 4 strategy 분기 (DSP0268 v1.13+ PowerSubsystem 마이그레이션 대응).

    1. subsystem_only — 최신 (iDRAC10 / iLO7 / UCS X-series)
       → /Chassis/{id}/PowerSubsystem 만 사용
    2. subsystem_with_legacy_dual — dual (iDRAC9 5.x / iLO5-6 / XCC3 / X12-X14)
       → 두 path 모두 시도 + merge
    3. subsystem_with_legacy_fallback — fallback (Huawei iBMC 3.x+ / Fujitsu iRMC S6+ / CIMC 4.x)
       → PowerSubsystem 시도 → 404 시 legacy fallback
    4. legacy_only — 구형 (iDRAC7-8, iLO4-, XCC/XCC2/IMM2, CIMC 1-3, X9-X11, iBMC 1-2, iRMC S2-S5, ISBMC, QCT)
       → /Chassis/{id}/Power 만 사용

    rule 92 R2: 사이트 검증 4 vendor 영향 0.
    """
    strategy = adapter_capabilities.get("power_strategy", "legacy_only")

    if strategy == "subsystem_only":
        return _collect_power_subsystem(session, base_url, chassis_id)

    if strategy == "subsystem_with_legacy_dual":
        subsystem = _collect_power_subsystem(session, base_url, chassis_id)
        legacy = _collect_power_legacy(session, base_url, chassis_id)
        return _merge_power(subsystem, legacy)

    if strategy == "subsystem_with_legacy_fallback":
        try:
            return _collect_power_subsystem(session, base_url, chassis_id)
        except (HTTPError, KeyError):
            return _collect_power_legacy(session, base_url, chassis_id)

    # legacy_only (default)
    return _collect_power_legacy(session, base_url, chassis_id)
```

기존 `_collect_power_legacy` 함수 변경 0. `_collect_power_subsystem` + `_merge_power` 신규 (Additive).

---

## 회귀 / 검증

### 정적 검증

- [ ] `python -m py_compile redfish-gather/library/redfish_gather.py` 통과
- [ ] `verify_vendor_boundary.py` 통과 (vendor 하드코딩 0건)
- [ ] `pytest tests/ -k power` 통과

### Additive only

- [ ] 기존 `_collect_power_legacy` 함수 변경 0
- [ ] 사이트 검증 4 vendor envelope shape 변경 0

### 동적 검증

```bash
pytest tests/e2e/test_power_strategies.py -v

# 검증 매트릭스:
# - iDRAC10 mock → subsystem_only
# - iDRAC9 5.x mock → subsystem_with_legacy_dual (merge 정확성)
# - iDRAC9 3.x mock → legacy_only
# - iLO7 mock → subsystem_only
# - iLO5/6 mock → subsystem_with_legacy_dual
# - X12 mock → subsystem_with_legacy_dual
# - X9 mock → legacy_only
# - iBMC 3.x mock → subsystem_with_legacy_fallback (PowerSubsystem 404 → legacy fallback)
```

---

## risk

- (MED) Power + PowerSubsystem dual merge — PSU duplicate 처리 (같은 PSU 두 응답)
- (LOW) PowerSubsystem path 404 응답 처리 — graceful (legacy fallback)

## 완료 조건

- [ ] _collect_power 함수 + 3 sub-helper 추가 (Additive)
- [ ] 기존 _collect_power_legacy 변경 0
- [ ] 사이트 검증 4 vendor envelope shape 변경 0
- [ ] pytest 회귀 PASS (power 4 strategy)
- [ ] commit: `feat: [M-I2 DONE] power section 변형 매트릭스 + 4 strategy fallback (PowerSubsystem 마이그레이션)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W4 → M-I3 (bmc / firmware section).

## 관련

- M-I1 (storage 동일 패턴)
- rule 92 R2 (Additive)
- rule 96 R1 (DMTF DSP0268 v1.13+ PowerSubsystem 표준 — origin)
