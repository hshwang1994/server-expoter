"""Regression for redfish_gather._extract_storage_controller_info.

배경: Controllers 컬렉션 fetch 시 401/403/503 응답을 silent 빈 dict 로
처리해 권한 부족/일시 과부하를 정상 부재와 구분 불가했음. probe_redfish 와
같은 정합으로 errors 누적 + status_code 메타 추가.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "redfish-gather" / "library"))

_stub_basic = types.ModuleType("ansible.module_utils.basic")
_stub_basic.AnsibleModule = object
_stub_module_utils = types.ModuleType("ansible.module_utils")
_stub_module_utils.basic = _stub_basic
_stub_ansible = types.ModuleType("ansible")
_stub_ansible.module_utils = _stub_module_utils
sys.modules.setdefault("ansible", _stub_ansible)
sys.modules.setdefault("ansible.module_utils", _stub_module_utils)
sys.modules.setdefault("ansible.module_utils.basic", _stub_basic)

import redfish_gather as rg  # noqa: E402


def _mk_get(responses):
    """순차 응답 list → _get mock. 각 응답: (status, data, err)."""
    it = iter(responses)

    def fake(bmc_ip, path, username, password, timeout, verify_ssl):
        return next(it)

    return fake


def test_inline_storage_controllers_no_extra_get():
    """StorageControllers inline 데이터 있으면 추가 GET 없이 즉시 반환."""
    sdata = {
        "StorageControllers": [{
            "Name": "PERC H755", "Model": "H755", "FirmwareVersion": "52.16.1",
            "Manufacturer": "Dell", "Status": {"Health": "OK"},
        }],
    }
    info, errors = rg._extract_storage_controller_info(
        sdata, "10.1.1.1", "u", "p", 30, False
    )
    assert info["controller_name"] == "PERC H755"
    assert info["controller_health"] == "OK"
    assert errors == []


def test_no_controllers_link_returns_empty():
    """Controllers 링크 부재 → 빈 dict, errors 없음."""
    sdata = {}
    info, errors = rg._extract_storage_controller_info(
        sdata, "10.1.1.1", "u", "p", 30, False
    )
    assert info == {}
    assert errors == []


def test_controllers_403_records_error():
    """회귀 차단: Controllers fetch 403 → controller_fetch_status 메타 + errors."""
    sdata = {"Controllers": {"@odata.id": "/redfish/v1/Systems/1/Storage/A/Controllers"}}
    with patch.object(rg, "_get", _mk_get([(403, {}, "HTTP 403: Forbidden")])):
        info, errors = rg._extract_storage_controller_info(
            sdata, "10.1.1.1", "u", "p", 30, False
        )
    assert info == {"controller_fetch_status": 403}
    assert len(errors) == 1
    assert errors[0]["section"] == "storage"
    assert errors[0]["detail"]["status_code"] == 403


def test_controllers_503_records_error():
    sdata = {"Controllers": {"@odata.id": "/redfish/v1/Systems/1/Storage/A/Controllers"}}
    with patch.object(rg, "_get", _mk_get([(503, {}, "HTTP 503: Service Unavailable")])):
        info, errors = rg._extract_storage_controller_info(
            sdata, "10.1.1.1", "u", "p", 30, False
        )
    assert info == {"controller_fetch_status": 503}
    assert len(errors) == 1
    assert errors[0]["detail"]["status_code"] == 503


def test_controller_detail_404_records_error():
    """컬렉션은 OK인데 controller detail이 404 → errors 기록."""
    sdata = {"Controllers": {"@odata.id": "/redfish/v1/Systems/1/Storage/A/Controllers"}}
    coll = {"Members": [{"@odata.id": "/redfish/v1/Systems/1/Storage/A/Controllers/0"}]}
    with patch.object(rg, "_get", _mk_get([
        (200, coll, None),
        (404, {}, "HTTP 404"),
    ])):
        info, errors = rg._extract_storage_controller_info(
            sdata, "10.1.1.1", "u", "p", 30, False
        )
    assert info == {"controller_fetch_status": 404}
    assert len(errors) == 1


def test_controller_detail_200_returns_full_info():
    """정상 흐름: Controllers 컬렉션 + detail 모두 200."""
    sdata = {"Controllers": {"@odata.id": "/redfish/v1/Systems/1/Storage/A/Controllers"}}
    coll = {"Members": [{"@odata.id": "/redfish/v1/Systems/1/Storage/A/Controllers/0"}]}
    detail = {
        "Name": "PERC H755", "Model": "H755", "FirmwareVersion": "52.16.1",
        "Manufacturer": "Dell", "Status": {"Health": "OK"},
    }
    with patch.object(rg, "_get", _mk_get([
        (200, coll, None),
        (200, detail, None),
    ])):
        info, errors = rg._extract_storage_controller_info(
            sdata, "10.1.1.1", "u", "p", 30, False
        )
    assert info["controller_name"] == "PERC H755"
    assert info["controller_health"] == "OK"
    assert errors == []


def test_empty_members_returns_empty_no_error():
    """Controllers 컬렉션은 OK이지만 Members 빈 list → 빈 dict, errors 없음."""
    sdata = {"Controllers": {"@odata.id": "/redfish/v1/Systems/1/Storage/A/Controllers"}}
    with patch.object(rg, "_get", _mk_get([(200, {"Members": []}, None)])):
        info, errors = rg._extract_storage_controller_info(
            sdata, "10.1.1.1", "u", "p", 30, False
        )
    assert info == {}
    assert errors == []
