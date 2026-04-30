"""Regression for precheck_bundle.probe_os (WinRM 분기).

배경: WinRM /wsman 화이트리스트가 (200/401/405) 만 → SPN 불일치/잠긴 계정
(403), IIS 재시작 중 (503) 응답 시 "WinRM 미응답" 오판정. probe_redfish 와
동일 정합으로 403/503 추가.
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


def test_winrm_5986_200_ok():
    payload = {"status_code": 200, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(True, None, payload)):
        ok, _, facts = precheck_bundle.probe_os("10.1.1.1", 5986, 6.0)
    assert ok is True
    assert facts["transport"] == "winrm"
    assert facts["scheme"] == "https"
    assert facts["port"] == 5986


def test_winrm_5985_401_treated_as_supported():
    """기존 동작: 401은 WinRM 살아있고 인증 필요 — 유지."""
    payload = {"status_code": 401, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 401", payload)):
        ok, _, facts = precheck_bundle.probe_os("10.1.1.1", 5985, 6.0)
    assert ok is True
    assert facts["scheme"] == "http"


def test_winrm_403_treated_as_supported():
    """회귀 차단: 403 = SPN 불일치 / 잠긴 계정 — endpoint는 살아있음."""
    payload = {"status_code": 403, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 403", payload)):
        ok, _, facts = precheck_bundle.probe_os("10.1.1.1", 5986, 6.0)
    assert ok is True
    assert facts["root_status_code"] == 403


def test_winrm_503_treated_as_supported():
    """회귀 차단: 503 = IIS 재시작 중 — endpoint는 살아있음."""
    payload = {"status_code": 503, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 503", payload)):
        ok, _, facts = precheck_bundle.probe_os("10.1.1.1", 5986, 6.0)
    assert ok is True
    assert facts["root_status_code"] == 503


def test_winrm_405_treated_as_supported():
    """기존 동작 유지: 405는 GET 메서드 미지원 — POST(SOAP) 본 수집 가능."""
    payload = {"status_code": 405, "json": None}
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "HTTP 405", payload)):
        ok, _, facts = precheck_bundle.probe_os("10.1.1.1", 5986, 6.0)
    assert ok is True
    assert facts["root_status_code"] == 405


def test_winrm_timeout_real_failure():
    with patch.object(precheck_bundle, "http_get", _http_get_returning(False, "요청 시간 초과", None)):
        ok, err, facts = precheck_bundle.probe_os("10.1.1.1", 5986, 6.0)
    assert ok is False
    assert facts is None


def test_unsupported_port():
    """알려지지 않은 포트는 fail."""
    ok, err, facts = precheck_bundle.probe_os("10.1.1.1", 9999, 6.0)
    assert ok is False
    assert "지원하지 않는 OS 포트" in err
    assert facts is None
