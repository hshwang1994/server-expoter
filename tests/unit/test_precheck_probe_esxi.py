"""Regression for precheck_bundle.probe_esxi.

배경: probe_esxi의 status_code 화이트리스트가 (200/301/302/404/405/500) 만
포함 → vCenter SSO / 인증 요구 ESXi 환경에서 /sdk 가 401/403 던지면
"vSphere endpoint 미응답" 으로 오판정. probe_redfish 와 동일 정합으로 401/403/503
추가.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "common" / "library"))

_stub_basic = types.ModuleType("ansible.module_utils.basic")
_stub_basic.AnsibleModule = object
_stub_module_utils = types.ModuleType("ansible.module_utils")
_stub_module_utils.basic = _stub_basic
_stub_ansible = types.ModuleType("ansible")
_stub_ansible.module_utils = _stub_module_utils
sys.modules.setdefault("ansible", _stub_ansible)
sys.modules.setdefault("ansible.module_utils", _stub_module_utils)
sys.modules.setdefault("ansible.module_utils.basic", _stub_basic)

import precheck_bundle  # noqa: E402


def _http_get_returning(ok, err, payload):
    def fake(url, timeout, verify=False, auth=None):
        return ok, err, payload
    return fake


def test_sdk_200_ok():
    payload = {"status_code": 200, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(True, None, payload)):
        ok, _, facts = precheck_bundle.probe_esxi("10.1.1.1", 443, 6.0)
    assert ok is True
    assert facts["vsphere_endpoint"].endswith("/sdk")


def test_sdk_404_esxi7_normal():
    """ESXi 7+ 에서 GET /sdk → 404, POST(SOAP) 정상."""
    payload = {"status_code": 404, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 404", payload)):
        ok, _, facts = precheck_bundle.probe_esxi("10.1.1.1", 443, 6.0)
    assert ok is True
    assert facts["root_status_code"] == 404


def test_sdk_401_treated_as_supported():
    """회귀 차단: 401 = vCenter SSO / 인증 요구 — endpoint는 살아있음."""
    payload = {"status_code": 401, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 401", payload)):
        ok, _, facts = precheck_bundle.probe_esxi("10.1.1.1", 443, 6.0)
    assert ok is True
    assert facts["root_status_code"] == 401
    assert facts["requires_auth_at_root"] is True


def test_sdk_403_treated_as_supported():
    payload = {"status_code": 403, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 403", payload)):
        ok, _, facts = precheck_bundle.probe_esxi("10.1.1.1", 443, 6.0)
    assert ok is True
    assert facts["root_status_code"] == 403
    assert facts["requires_auth_at_root"] is True


def test_sdk_503_treated_as_supported():
    payload = {"status_code": 503, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 503", payload)):
        ok, _, facts = precheck_bundle.probe_esxi("10.1.1.1", 443, 6.0)
    assert ok is True
    assert facts["root_status_code"] == 503
    assert facts["requires_auth_at_root"] is False


def test_sdk_timeout_real_failure():
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "요청 시간 초과 (timeout=6.0s)", None)):
        ok, err, facts = precheck_bundle.probe_esxi("10.1.1.1", 443, 6.0)
    assert ok is False
    assert "시간 초과" in err
    assert facts is None
