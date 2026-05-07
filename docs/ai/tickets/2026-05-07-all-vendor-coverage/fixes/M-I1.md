# M-I1 — storage section 변형 매트릭스 + fallback (PLDM RDE / SmartStorage / OEM Drive / Volume / SimpleStorage)

> status: [PENDING] | depends: M-H1, M-H2, M-H3, M-H4 | priority: P1 | worker: W4 | cycle: 2026-05-07-all-vendor-coverage

## 사용자 의도

> "gather 10 sections 변형 큰 순으로 effort 우선. storage 가 가장 큼 (PLDM RDE / SmartStorage / OEM)." (cycle 진입)

storage section 은 vendor / generation 별 변형 가장 큼. 매트릭스 정리 + redfish_gather.py fallback 로직 보강.

## 작업 범위

| 항목 | 내용 |
|---|---|
| 영향 모듈 | `redfish-gather/library/redfish_gather.py` (storage 수집 fallback 로직 보강), `redfish-gather/tasks/collect.yml`, `normalize_standard.yml` (필요 시) |
| 영향 vendor | 9 vendor — 사이트 검증 4 vendor 영향 0 (Additive) |
| 함께 바뀔 것 | M-J1 (OEM mapping), 각 vendor mock fixture (M-B4 / M-C3 / M-D2 / M-E3 / M-F2 / M-G2 / M-H1~H4) |
| 리스크 top 3 | (1) PLDM RDE → standard fallback 누락 시 iDRAC9 5.x- 회귀 / (2) SmartStorage path 만 사용하는 iLO4 회귀 / (3) SimpleStorage fallback 누락 시 X9/X10 / iDRAC7 회귀 |
| 진행 확인 | M-H1~H4 (4 vendor 미검증 generation) 후 진입 — 매트릭스 입력 |

---

## Storage 변형 매트릭스 (cycle 진입 시점)

| vendor | generation | path | strategy |
|---|---|---|---|
| Dell | iDRAC10 | `/Systems/{id}/Storage/{id}/Volumes` (PLDM RDE) | PLDM RDE only |
| Dell | iDRAC9 6.x+ | 동일 | PLDM RDE only |
| Dell | iDRAC9 5.x | dual | PLDM RDE + standard fallback |
| Dell | iDRAC9 3.x-4.x | `/Systems/{id}/Storage/{id}` | standard |
| Dell | iDRAC8 | 동일 | standard |
| Dell | iDRAC7 (legacy) | `/Systems/{id}/SimpleStorage` | SimpleStorage only |
| HPE | iLO5/6/7 | `/Systems/{id}/Storage/{id}` (SmartStorage OEM) | standard + OEM |
| HPE | iLO4 | `/Systems/{id}/SmartStorage/ArrayControllers` | SmartStorage only (legacy OEM path) |
| HPE | iLO legacy | (Redfish 미지원) | graceful fail |
| Lenovo | XCC/XCC2/XCC3 | `/Systems/{id}/Storage/{id}` | standard + OEM |
| Lenovo | IMM2 | `/Systems/{id}/SimpleStorage` | SimpleStorage only |
| Cisco | UCS X-series | `/Systems/{id}/Storage/{id}` | standard |
| Cisco | CIMC 4.x | 동일 | standard |
| Cisco | CIMC 1.x-2.x | `/Systems/{id}/SimpleStorage` | SimpleStorage |
| Supermicro | X11~X14 | `/Systems/{id}/Storage/{id}` | standard |
| Supermicro | X9/X10 | `/Systems/{id}/SimpleStorage` | SimpleStorage |
| Huawei iBMC | 2.x+ | `/Systems/{id}/Storage/{id}` | standard + OEM |
| Huawei iBMC | 1.x | `/Systems/{id}/SimpleStorage` | SimpleStorage |
| Inspur | ISBMC | `/Systems/{id}/Storage/{id}` | standard |
| Fujitsu | iRMC S4+ | `/Systems/{id}/Storage/{id}` | standard + OEM |
| Fujitsu | iRMC S2 | (Redfish 미지원) | graceful fail |
| Quanta | QCT | `/Systems/{id}/Storage/{id}` | standard |

---

## 구현 (redfish_gather.py 보강 — Additive only)

### Storage 수집 로직 (3 strategy)

```python
def _collect_storage(session, base_url, system_id, adapter_capabilities):
    """Storage 수집 — 3 strategy 분기.

    1. PLDM RDE only — 최신 (iDRAC10, iDRAC9 6.x+)
       → /Systems/{id}/Storage/{id}/Volumes 시도
    2. standard with simple fallback — 일반 (대부분 vendor)
       → /Systems/{id}/Storage/{id} 시도 → 404 시 SimpleStorage fallback
    3. simple_storage only — legacy (iDRAC7, X9/X10, IMM2, CIMC 1.x)
       → /Systems/{id}/SimpleStorage 만 사용

    추가:
    - SmartStorage only — iLO4 (legacy OEM path)
       → /Systems/{id}/SmartStorage/ArrayControllers 시도

    rule 92 R2: 사이트 검증 4 vendor (iDRAC10/iLO7/XCC3/UCS X-series) 영향 0.
    기존 standard path 유지 + 새 환경 fallback 추가만.
    """
    strategy = adapter_capabilities.get("storage_strategy", "standard")

    # 1. PLDM RDE only (최신)
    if strategy == "pldm_rde_only":
        return _collect_storage_pldm(session, base_url, system_id)

    # 2. PLDM RDE + standard fallback (iDRAC9 5.x dual)
    if strategy == "pldm_rde_with_standard_fallback":
        try:
            return _collect_storage_pldm(session, base_url, system_id)
        except (HTTPError, KeyError):
            return _collect_storage_standard(session, base_url, system_id)

    # 3. SmartStorage only (iLO4 legacy)
    if strategy == "smart_storage_only":
        return _collect_storage_smart_storage(session, base_url, system_id)

    # 4. SmartStorage + standard dual (iLO5)
    if strategy == "smart_storage_with_standard_dual":
        smart = _collect_storage_smart_storage(session, base_url, system_id)
        try:
            standard = _collect_storage_standard(session, base_url, system_id)
            return _merge_storage(smart, standard)
        except (HTTPError, KeyError):
            return smart

    # 5. standard with smart_storage fallback (iLO6)
    if strategy == "standard_with_smart_storage_fallback":
        try:
            return _collect_storage_standard(session, base_url, system_id)
        except (HTTPError, KeyError):
            return _collect_storage_smart_storage(session, base_url, system_id)

    # 6. simple_storage only (legacy)
    if strategy == "simple_storage_only":
        return _collect_storage_simple(session, base_url, system_id)

    # 7. standard with simple fallback (default — 대부분 vendor)
    try:
        return _collect_storage_standard(session, base_url, system_id)
    except (HTTPError, KeyError):
        return _collect_storage_simple(session, base_url, system_id)
```

본 함수는 **Additive** — 기존 `_collect_storage_standard` 함수 변경 0. 새 strategy 분기만 추가.

### Storage 4 sub-helper (Additive)

```python
def _collect_storage_pldm(session, base_url, system_id):
    """PLDM RDE — Volumes 우선 (iDRAC10 / iDRAC9 6.x+)"""
    # 기존 _collect_storage_standard 와 거의 동일 (Volumes path 우선)

def _collect_storage_smart_storage(session, base_url, system_id):
    """HPE iLO4-5 SmartStorage path (Oem.Hp / Oem.Hpe)"""
    # /Systems/{id}/SmartStorage/ArrayControllers/* + /HostBusAdapters/*

def _collect_storage_simple(session, base_url, system_id):
    """SimpleStorage path (legacy — iDRAC7 / X9-X10 / IMM2 / CIMC 1.x)"""
    # /Systems/{id}/SimpleStorage 만 — Volumes 영역 없음

def _merge_storage(smart, standard):
    """SmartStorage + standard dual (iLO5)"""
    # 두 응답 dedup + merge
```

### rule 12 R1 R6 — vendor 하드코딩 영역 검증

본 storage 수집 함수는 vendor 이름 분기 없음 (capability strategy 만 사용). vendor namespace 분기 (`Oem.Hp` vs `Oem.Hpe`) 는 SmartStorage helper 안에서만 (rule 12 R1 Allowed — Redfish API spec OEM namespace).

---

## 회귀 / 검증

### 정적 검증

- [ ] `python -m py_compile redfish-gather/library/redfish_gather.py` 통과
- [ ] `verify_vendor_boundary.py` 통과 (vendor 하드코딩 0건 — capability strategy 만)
- [ ] `pytest tests/ -k storage` 통과

### Additive only (rule 92 R2)

- [ ] 기존 `_collect_storage_standard` 함수 변경 0 (git diff 검증)
- [ ] 사이트 검증 4 vendor envelope shape 변경 0 (`scripts/ai/hooks/envelope_change_check.py`)

### 동적 검증 — 매트릭스 별 strategy

```bash
# pytest e2e — 각 strategy 분기 검증
pytest tests/e2e/test_storage_strategies.py -v

# 검증:
# - iDRAC10 mock → pldm_rde_only → Volumes path
# - iDRAC9 5.x mock → pldm_rde_with_standard_fallback (PLDM 시도 → 실패 → standard)
# - iDRAC9 3.x mock → standard
# - iLO4 mock → smart_storage_only
# - iLO5 mock → smart_storage_with_standard_dual
# - iLO6 mock → standard_with_smart_storage_fallback
# - iDRAC7 mock → simple_storage_only
# - X9/X10 mock → simple_storage_only
# - IMM2 mock → simple_storage_only
# - CIMC 1.x mock → simple_storage_only
```

---

## risk

- (MED) PLDM RDE → standard fallback 시 iDRAC9 5.x 응답이 PLDM 부분 + standard 부분 dual → merge 로직 정확성
- (MED) SmartStorage + standard dual (iLO5) → dedup 로직 (같은 disk 두 응답 매핑)
- (LOW) SimpleStorage 응답은 Drive 영역 약함 (Volume 정보 없음) — graceful (storage section 일부 데이터만 emit)

## 완료 조건

- [ ] redfish_gather.py 의 _collect_storage 함수 + 4 sub-helper 추가 (Additive)
- [ ] 기존 _collect_storage_standard 변경 0
- [ ] 사이트 검증 4 vendor envelope shape 변경 0
- [ ] pytest 회귀 PASS (storage 매트릭스 7+ strategy)
- [ ] commit: `feat: [M-I1 DONE] storage section 변형 매트릭스 + 7 strategy fallback (PLDM RDE / SmartStorage / Standard / SimpleStorage)`
- [ ] SESSION-HANDOFF / fixes/INDEX 갱신 + push

## 다음 ticket

W4 → M-I2 (power section 변형).

## 관련

- M-H1, M-H2, M-H3, M-H4 (4 vendor capability 매트릭스 입력)
- M-J1 (OEM mapping)
- rule 12 R1 R6 (vendor 하드코딩 검증)
- rule 22 (Fragment 철학)
- rule 92 R2 (Additive)
- rule 96 R1-A (storage path 변천 — DMTF spec)
