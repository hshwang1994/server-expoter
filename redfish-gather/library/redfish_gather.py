#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Ansible Custom Module: redfish_gather  v4
------------------------------------------
검증된 벤더별 URI 구조 (공식 문서 기반):

  HPE iLO 5/6  : Systems/1               / Managers/1   (Oem.Hpe / Oem.Hp fallback)
  Dell iDRAC 9 : Systems/System.Embedded.1 / Managers/iDRAC.Embedded.1  (Oem.Dell)
  Lenovo XCC   : Systems/1               / Managers/1   (Oem.Lenovo)
  Supermicro   : Systems/1               / Managers/1   (Oem.Supermicro)
    Manufacturer = "Super Micro Computer, Inc."
  Cisco CIMC   : Systems/<serial>        / Managers/CIMC (Oem.Cisco — 옵션)
    Manufacturer = "Cisco Systems"

외부 라이브러리 불필요 — Python stdlib(urllib, ssl, socket) 만 사용
"""

__metaclass__ = type

DOCUMENTATION = r'''
module: redfish_gather
short_description: Gather hardware info via Redfish API (Dell/HPE/Lenovo/Supermicro/Cisco)
options:
  bmc_ip:     required, str
  username:   required, str
  password:   required, str, no_log
  timeout:    optional, int, default 30
  verify_ssl: optional, bool, default false
'''

import json, socket, sys, traceback

def _removeprefix(s, prefix):
    """str.removeprefix() 호환 (Python 3.8 이하 지원)"""
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def _safe_int(x, default=None):
    """Redfish 응답 robustness — string/None/non-numeric → default.

    rule 96 외부 계약 drift 대비. 펌웨어 변경으로 capacity 필드가 비-숫자
    문자열 또는 None을 반환할 때 ValueError로 모듈 자체가 죽는 사고 차단.
    """
    if x is None:
        return default
    try:
        return int(x)  # rule 95 R1 #7 ok: try/except 보호 안
    except (ValueError, TypeError):
        return default

try:
    import urllib.request as urlreq
    import urllib.error as urlerr
    import ssl, base64
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

from ansible.module_utils.basic import AnsibleModule


# ── HTTP 유틸 ────────────────────────────────────────────────────────────────

def _ctx(verify_ssl):
    """HTTPS context — verify_ssl=False 시 self-signed BMC 인증서 허용.

    cycle 2026-04-30: 구 BMC (HPE iLO4, Lenovo IMM2, 일부 iDRAC7/8 펌웨어) 호환.
    OpenSSL 3.x legacy renegotiation + weak cipher 허용 — verify=False 환경 한정.
    curl -k 와 동등한 관용성. 사내 BMC self-signed 망 한정.
    """
    ctx = ssl.create_default_context()
    if not verify_ssl:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if hasattr(ssl, 'OP_LEGACY_SERVER_CONNECT'):
            ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
        try:
            ctx.set_ciphers('DEFAULT@SECLEVEL=0')
        except ssl.SSLError:
            pass
    return ctx

def _auth(username, password):
    return 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()

def _get(bmc_ip, path, username, password, timeout, verify_ssl):
    url = f'https://{bmc_ip}/redfish/v1/{path.lstrip("/")}'
    # cycle 2026-04-30 hotfix: User-Agent 추가가 Lenovo XCC 일부 펌웨어 reject 유발 (사이트 검증).
    # Accept + OData-Version 만 유지 (cycle 전부터 동작 검증된 헤더 셋).
    req = urlreq.Request(url, headers={
        'Authorization': _auth(username, password),
        'Accept': 'application/json',
        'OData-Version': '4.0',
    })
    try:
        with urlreq.urlopen(req, context=_ctx(verify_ssl), timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8', errors='replace')), None
    except urlerr.HTTPError as e:
        try:    body = json.loads(e.read().decode('utf-8', errors='replace'))
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError): body = {}
        return e.code, body, f'HTTP {e.code}: {e.reason}'
    except urlerr.URLError as e:
        return 0, {}, f'URLError: {e.reason}'
    except socket.timeout:
        return 0, {}, f'Timeout after {timeout}s'
    except (OSError, ValueError) as e:
        return 0, {}, f'Unexpected: {type(e).__name__}: {e}'

def _post(bmc_ip, path, body, username, password, timeout, verify_ssl):
    """P2 (cycle 2026-04-28): AccountService 계정 생성 (POST /Accounts)."""
    url = f'https://{bmc_ip}/redfish/v1/{path.lstrip("/")}'
    payload = json.dumps(body).encode('utf-8')
    req = urlreq.Request(url, data=payload, method='POST', headers={
        'Authorization': _auth(username, password),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-Version': '4.0',
    })
    try:
        with urlreq.urlopen(req, context=_ctx(verify_ssl), timeout=timeout) as resp:
            raw = resp.read()
            try:
                data = json.loads(raw.decode('utf-8', errors='replace')) if raw else {}
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                data = {}
            return resp.status, data, None
    except urlerr.HTTPError as e:
        try:    body_err = json.loads(e.read().decode('utf-8', errors='replace'))
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError): body_err = {}
        return e.code, body_err, f'HTTP {e.code}: {e.reason}'
    except urlerr.URLError as e:
        return 0, {}, f'URLError: {e.reason}'
    except socket.timeout:
        return 0, {}, f'Timeout after {timeout}s'
    except (OSError, ValueError) as e:
        return 0, {}, f'Unexpected: {type(e).__name__}: {e}'

def _patch(bmc_ip, path, body, username, password, timeout, verify_ssl):
    """P2 (cycle 2026-04-28): AccountService 계정 update (PATCH /Accounts/{id})."""
    url = f'https://{bmc_ip}/redfish/v1/{path.lstrip("/")}'
    payload = json.dumps(body).encode('utf-8')
    req = urlreq.Request(url, data=payload, method='PATCH', headers={
        'Authorization': _auth(username, password),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'OData-Version': '4.0',
    })
    try:
        with urlreq.urlopen(req, context=_ctx(verify_ssl), timeout=timeout) as resp:
            raw = resp.read()
            try:
                data = json.loads(raw.decode('utf-8', errors='replace')) if raw else {}
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                data = {}
            return resp.status, data, None
    except urlerr.HTTPError as e:
        try:    body_err = json.loads(e.read().decode('utf-8', errors='replace'))
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError): body_err = {}
        return e.code, body_err, f'HTTP {e.code}: {e.reason}'
    except urlerr.URLError as e:
        return 0, {}, f'URLError: {e.reason}'
    except socket.timeout:
        return 0, {}, f'Timeout after {timeout}s'
    except (OSError, ValueError) as e:
        return 0, {}, f'Unexpected: {type(e).__name__}: {e}'

def _p(uri):
    """@odata.id URI → _get() path 인수"""
    return _removeprefix(_removeprefix(uri.lstrip('/'), 'redfish/v1/'), 'redfish/v1').rstrip('/')

def _safe(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict): return default
        d = d.get(k, default)
        if d is None: return default
    return d

def _err(section, message, detail=None):
    return {'section': section, 'message': str(message), 'detail': detail}


# 2026-04-29 fix B90 / B23: JEDEC ID -> vendor name normalization (rule 10 stdlib only)
# Cisco CIMC returns Memory.Manufacturer as raw '0xCExx' (Samsung) instead of name.
# JEP106 standard: 7-bit ID byte (MSB = parity). Common DRAM vendors below.
_JEDEC_VENDORS = {
    "01": "AMD",
    "0B": "Intel",
    "1F": "Atmel",
    "2C": "Micron Technology",
    "98": "Kingston",
    "AD": "SK hynix",
    "B3": "IDT",
    "BA": "PNY Electronics",
    "CE": "Samsung",
    "04": "Fujitsu",
    "07": "Hitachi",
}


# 2026-04-30 추가: vendor 이름 변형 → canonical name (cross-vendor consistency).
# BMC마다 같은 제조사를 다른 표기로 노출 (Dell="Hynix Semiconductor", Linux dmidecode="SK hynix").
_VENDOR_NAME_NORMALIZATION = {
    "hynix": "SK hynix",
    "hynix semiconductor": "SK hynix",
    "sk hynix": "SK hynix",
    "skhynix": "SK hynix",
    "samsung electronics": "Samsung",
    "samsung electronic": "Samsung",
    "micron": "Micron Technology",
    "micron technology": "Micron Technology",
    "kingston technology": "Kingston",
}


def _canonical_vendor_name(name):
    """Map vendor-name variants to canonical form. Used for memory.manufacturer cross-vendor consistency."""
    if not name or not isinstance(name, str):
        return name
    return _VENDOR_NAME_NORMALIZATION.get(name.strip().lower(), name)


def _normalize_jedec(value):
    """Normalize a JEDEC manufacturer ID hex string to vendor name.

    Handles:
      - "0xCE00" / "0xCE" / "0xAD00" (Cisco CIMC)
      - "00CE" / "00AD063200AD" (raw JEDEC, dmidecode style)
      - "Samsung" / "Hynix Semiconductor" — canonical normalization (cross-vendor)
      - None / "" / "Unknown" / "Not Specified" -> None
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.lower() in ("unknown", "not specified", "none"):
        return None
    # 0x prefixed hex (Cisco CIMC)
    if s.lower().startswith("0x"):
        hp = s[2:].upper()
        if hp[:2] in _JEDEC_VENDORS:
            return _JEDEC_VENDORS[hp[:2]]
        return s  # unknown — keep raw for traceability
    # Vendor name (contains non-hex alpha or whitespace)
    if " " in s or any(c.isalpha() and c not in "ABCDEFabcdef" for c in s):
        return _canonical_vendor_name(s)
    # Plain hex string
    if all(c in "0123456789ABCDEFabcdef" for c in s) and len(s) >= 2:
        # Try first byte (some BMCs) or 2nd byte (continuation+ID)
        for idx in (slice(2, 4), slice(0, 2)):
            byte = s[idx].upper() if len(s) >= idx.stop else None
            if byte and byte in _JEDEC_VENDORS:
                return _JEDEC_VENDORS[byte]
        return s
    return _canonical_vendor_name(s)


def _strip_or_none(value):
    """Strip whitespace and convert empty/sentinel strings to None.

    Cisco BMC가 일부 필드를 trailing space 포함하여 emit ('M386A8K40BM1-CRC    ').
    Cross-vendor 정합성 위해 모든 string 값을 strip 후 빈 문자열은 None.
    Non-string은 unchanged.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    s = value.strip()
    return s or None


# ── 벤더 정규화 ──────────────────────────────────────────────────────────────

# 내장 벤더 매핑 (vendor_aliases.yml 로드 불가 시 fallback)
# ※ common/vars/vendor_aliases.yml과 동기화 필요 — 변경 시 양쪽 모두 수정할 것
# canonical vendors: dell, hpe, lenovo, supermicro, cisco
# nosec rule12-r1: 아래 dict는 vendor 분기 코드가 아니라 Ansible runtime 외 환경
# (pytest / 직접 invoke)에서 vendor_aliases.yml load 실패 시 fallback 정규화 맵.
# vendor_aliases.yml이 primary, 본 dict는 secondary. 신규 alias 추가 시 vendor_aliases.yml만
# 갱신하면 충분 (verify_harness_consistency.py 동기화 게이트로 drift 검출).
_FALLBACK_VENDOR_MAP = {
    'dell': 'dell', 'dell inc.': 'dell', 'dell emc': 'dell',                # nosec rule12-r1
    'hpe': 'hpe', 'hewlett packard enterprise': 'hpe',                      # nosec rule12-r1
    'hewlett packard enterprise co.': 'hpe', 'hewlett-packard': 'hpe',      # nosec rule12-r1
    'hp enterprise': 'hpe', 'hp': 'hpe',                                    # nosec rule12-r1
    'lenovo': 'lenovo', 'lenovo group ltd.': 'lenovo',                      # nosec rule12-r1
    'lenovo group limited': 'lenovo', 'ibm': 'lenovo',                      # nosec rule12-r1
    'supermicro': 'supermicro', 'super micro computer, inc.': 'supermicro', # nosec rule12-r1
    'super micro computer': 'supermicro', 'smci': 'supermicro',             # nosec rule12-r1
    'cisco': 'cisco', 'cisco systems inc': 'cisco',                         # nosec rule12-r1
    'cisco systems inc.': 'cisco', 'cisco systems, inc': 'cisco',           # nosec rule12-r1
    'cisco systems, inc.': 'cisco', 'cisco systems': 'cisco',               # nosec rule12-r1
}
# 호환 alias (외부 코드가 _BUILTIN_VENDOR_MAP 이름 참조 시)
_BUILTIN_VENDOR_MAP = _FALLBACK_VENDOR_MAP

# BMC 시그니처 → vendor (Redfish ServiceRoot Product/Name 필드의 BMC 제품명 매칭)
# nosec rule12-r1: ServiceRoot v1.0~1.4 펌웨어는 Vendor/Product 표준 필드 부재.
# BMC 제품명이 vendor 시그니처로 사실상 외부 Redfish spec 일부 (HPE Hpe namespace,
# Dell iDRAC, Lenovo XClarity 등). vendor 분기 코드가 아니라 정규화 맵.
_BMC_PRODUCT_HINTS = {
    'idrac': 'dell', 'integrated dell': 'dell',                             # nosec rule12-r1
    'ilo': 'hpe', 'proliant': 'hpe',                                        # nosec rule12-r1
    'xclarity': 'lenovo', 'thinksystem': 'lenovo',                          # nosec rule12-r1
    'xcc': 'lenovo', 'imm2': 'lenovo',                                      # nosec rule12-r1
    'megarac': 'supermicro',                                                # nosec rule12-r1
    'cimc': 'cisco', 'ucs': 'cisco',                                        # nosec rule12-r1
}


def _load_vendor_aliases_file():
    """vendor_aliases.yml을 로드합니다. 실패 시 빈 dict 반환.

    Path resolution 우선순위:
      1. SE_VENDOR_ALIASES_PATH 환경변수 (명시 override)
      2. REPO_ROOT 환경변수 + common/vars/vendor_aliases.yml
      3. __file__ 기반 ../../common/vars/vendor_aliases.yml (Ansible 표준 배치)
    """
    import os
    try:
        import yaml
    except ImportError:
        return {}

    candidates = []
    # 1. 명시 override
    explicit = os.environ.get('SE_VENDOR_ALIASES_PATH', '')
    if explicit:
        candidates.append(explicit)
    # 2. REPO_ROOT 기반
    repo_root = os.environ.get('REPO_ROOT', '')
    if repo_root:
        candidates.append(os.path.join(repo_root, 'common', 'vars', 'vendor_aliases.yml'))
    # 3. __file__ 기반 (redfish-gather/library/redfish_gather.py → common/vars/...)
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        # __file__ → redfish-gather/library/ → ../../common/vars/
        candidates.append(os.path.normpath(os.path.join(here, '..', '..', 'common', 'vars', 'vendor_aliases.yml')))
    except NameError:
        pass

    for path in candidates:
        if not path or not os.path.isfile(path):
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            mapping = {}
            for canonical, alias_list in data.get('vendor_aliases', {}).items():
                for alias in alias_list:
                    mapping[alias.strip().lower()] = canonical
            if mapping:
                return mapping
        except (IOError, OSError, yaml.YAMLError, AttributeError, TypeError):
            continue
    return {}

def _normalize_vendor_from_aliases(mfr_lower):
    """
    Manufacturer 문자열(소문자)을 정규화된 벤더명으로 변환합니다.
    1차: vendor_aliases.yml (REPO_ROOT 기반)
    2차: 내장 fallback 맵
    3차: 부분 매칭 (substring)
    """
    # vendor_aliases.yml 시도 (primary)
    aliases = _load_vendor_aliases_file()
    # aliases (YAML primary) 우선, fallback dict는 보조
    merged = {**_FALLBACK_VENDOR_MAP, **aliases}

    # 정확 매칭
    if mfr_lower in merged:
        return merged[mfr_lower]

    # 부분 매칭 (기존 로직 호환)
    for key, canon in merged.items():
        if key in mfr_lower or mfr_lower in key:
            return canon

    return 'unknown'


# ── 벤더 감지 ────────────────────────────────────────────────────────────────

def _probe_realm_hint(bmc_ip, timeout, verify_ssl):
    """G6 (cycle 2026-04-30): 401/403 응답의 WWW-Authenticate realm에서 vendor hint 추출.

    ServiceRoot 본문이 비어 vendor 식별 불가한 BMC에서도 401 응답 헤더의
    `WWW-Authenticate: Basic realm="iDRAC"` / `realm="iLO"` / `realm="XClarity Controller"`
    같은 realm 문자열로 vendor를 추정한다. 부가 fallback (필수 아님).

    Returns: vendor canonical name 또는 None
    """
    import re
    url = f'https://{bmc_ip}/redfish/v1/'
    req = urlreq.Request(url, headers={'Accept': 'application/json', 'OData-Version': '4.0'})
    realm_header = None
    try:
        # 무인증으로 시도 — 200이면 realm 없음 (이미 다른 단계에서 처리)
        with urlreq.urlopen(req, context=_ctx(verify_ssl), timeout=timeout) as resp:
            return None
    except urlerr.HTTPError as e:
        # 401/403일 때 WWW-Authenticate 헤더에서 realm 추출
        if e.code in (401, 403):
            realm_header = e.headers.get('WWW-Authenticate') or ''
    except (urlerr.URLError, socket.timeout, OSError, ValueError):
        return None

    if not realm_header:
        return None

    # realm="..." 추출
    m = re.search(r'realm\s*=\s*"([^"]+)"', realm_header, re.IGNORECASE)
    if not m:
        m = re.search(r"realm\s*=\s*'([^']+)'", realm_header, re.IGNORECASE)
    if not m:
        return None
    realm = m.group(1).lower().strip()

    # vendor_aliases + BMC product hints 매칭
    aliases_yaml = _load_vendor_aliases_file()
    vm = {**_FALLBACK_VENDOR_MAP, **aliases_yaml}
    for alias, canon in vm.items():
        if alias and alias in realm:
            return canon
    # nosec rule12-r1: realm BMC 시그니처
    for hint, canon in _BMC_PRODUCT_HINTS.items():                              # nosec rule12-r1
        if hint in realm:                                                       # nosec rule12-r1
            return canon                                                        # nosec rule12-r1
    return None


def _get_noauth(bmc_ip, path, timeout, verify_ssl):
    """인증 없이 GET 요청 (ServiceRoot 등 무인증 엔드포인트용)"""
    url = f'https://{bmc_ip}/redfish/v1/{path.lstrip("/")}'
    req = urlreq.Request(url, headers={
        'Accept': 'application/json',
        'OData-Version': '4.0',
    })
    try:
        with urlreq.urlopen(req, context=_ctx(verify_ssl), timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8', errors='replace')), None
    except urlerr.HTTPError as e:
        try:    body = json.loads(e.read().decode('utf-8', errors='replace'))
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError): body = {}
        return e.code, body, f'HTTP {e.code}: {e.reason}'
    except urlerr.URLError as e:
        return 0, {}, f'URLError: {e.reason}'
    except socket.timeout:
        return 0, {}, f'Timeout after {timeout}s'
    except (OSError, ValueError) as e:
        return 0, {}, f'Unexpected: {type(e).__name__}: {e}'


def _detect_vendor_from_service_root(root):
    """
    ServiceRoot 응답에서 벤더를 식별합니다 (무인증).

    식별 알고리즘 (대소문자 무시):
      1. Oem 객체의 키 이름 확인
      2. Vendor 필드 확인
      3. Product 필드에 벤더명 포함 확인
      4. Name 필드에 벤더명 포함 확인
      5. 모두 해당 없으면 None 반환

    Returns: vendor 문자열 ('dell', 'hpe', 'lenovo', 'supermicro', 'cisco') 또는 None
    """
    # production-audit (2026-04-29): vendor_aliases.yml + fallback merge.
    # 기존 _BUILTIN_VENDOR_MAP만 사용 시 YAML에 추가된 alias가 detect에 반영 안 되는 drift 차단.
    aliases_yaml = _load_vendor_aliases_file()
    vm = {**_FALLBACK_VENDOR_MAP, **aliases_yaml}

    # 1. Oem 객체의 키 이름 확인
    oem = _safe(root, 'Oem')
    if isinstance(oem, dict):
        # 1-A. 정확 매칭 (예: Oem.Lenovo, Oem.Hpe, Oem.Dell)
        for key in oem:
            k = key.lower()
            if k in vm:
                return vm[k]
        # 1-B. namespace prefix 매칭 — Lenovo XCC2/XCC3 'Lenovo_xxx', 일부 펌웨어 'Hpe_xxx' 등
        # nosec rule12-r1: BMC vendor OEM namespace prefix → vendor 식별 (외부 Redfish spec)
        for key in oem:                                                       # nosec rule12-r1
            k = key.lower()                                                   # nosec rule12-r1
            for alias, canon in vm.items():                                   # nosec rule12-r1
                if not alias:                                                 # nosec rule12-r1
                    continue                                                  # nosec rule12-r1
                if k.startswith(alias + '_') or k.startswith(alias + '.'):    # nosec rule12-r1
                    return canon                                              # nosec rule12-r1

    # 2. Vendor 필드 확인 — ServiceRoot v1.5.0+ 표준
    # G7 (cycle 2026-04-30): 'Dell Inc.' 같은 trailing dot/whitespace + substring 매칭
    vendor_field = _safe(root, 'Vendor')
    if vendor_field and isinstance(vendor_field, str):
        v = vendor_field.lower().strip()
        # 2-A. 정확 매칭 (원형 + trailing dot 제거 두 형식 둘 다 시도)
        for cand in (v, v.rstrip('.').strip()):
            if cand in vm:
                return vm[cand]
        # 2-B. substring 매칭 (Product/Name과 동일 정신)
        for alias, canonical in vm.items():
            if alias and alias in v:
                return canonical

    # 3. Product 필드에 벤더명 포함 확인 — ServiceRoot v1.3.0+ 표준
    product = _safe(root, 'Product')
    if product and isinstance(product, str):
        p = product.lower()
        for alias, canonical in vm.items():
            if alias in p:
                return canonical
        # nosec rule12-r1: BMC 시그니처 → vendor 식별 (외부 Redfish spec OEM namespace)
        for hint, canon in _BMC_PRODUCT_HINTS.items():                        # nosec rule12-r1
            if hint in p:                                                     # nosec rule12-r1
                return canon                                                  # nosec rule12-r1

    # 4. Name 필드에 벤더명 포함 확인 — Cisco "Cisco RESTful Root Service" 등
    name = _safe(root, 'Name')
    if name and isinstance(name, str):
        n = name.lower()
        for alias, canonical in vm.items():
            if alias in n:
                return canonical
        # nosec rule12-r1: BMC 시그니처 fallback (Name 필드)
        for hint, canon in _BMC_PRODUCT_HINTS.items():                        # nosec rule12-r1
            if hint in n:                                                     # nosec rule12-r1
                return canon                                                  # nosec rule12-r1

    # 5. 해당 없음
    return None


def _fetch_service_root(bmc_ip, username, password, timeout, verify_ssl):
    """ServiceRoot(/redfish/v1/) 응답 fetch — 무인증 → 인증 fallback.

    Returns: (root_dict_or_none, errors_list)
    """
    errors = []
    st, root, err = _get_noauth(bmc_ip, '', timeout, verify_ssl)
    if err or st != 200:
        # 무인증 실패 시 인증으로 재시도 (일부 BMC는 ServiceRoot도 인증 필요)
        st, root, err = _get(bmc_ip, '', username, password, timeout, verify_ssl)
        if err or st != 200:
            errors.append(_err('vendor_detect', f'ServiceRoot 실패: {err or st}'))
            return None, errors
    return root, errors


def _endpoint_with_fallback(bmc_ip, primary_path, fallback_path, username,
                            password, timeout, verify_ssl, section_name='generic'):
    """primary endpoint 시도 → 404 / 미지원 시 fallback endpoint 시도.

    cycle 2026-05-01 신설 (rule 22 R5 헬퍼 추상화 / HARNESS B5).
    Storage→SimpleStorage / Power→PowerSubsystem / 향후 ThermalSubsystem 같은
    DMTF 변천 호환 패턴을 재사용 가능한 단일 함수로 추상화.

    Behavior:
    - primary GET → 200 이면 (data, [], 'primary') 반환
    - primary 404 → fallback GET → 200 이면 (data, [], 'fallback') 반환
    - fallback 404 → ({}, [], 'not_supported') 반환 (호출자가 분류)
    - 5xx / 401 / 403 / 그 외 → ({}, [error], 'failed')

    호환성 fallback only — envelope 신 키 추가 안 함 (rule 96 R1-B Additive).

    Args:
        bmc_ip: BMC IP
        primary_path: 우선 시도 path (예: /Chassis/{id}/Power)
        fallback_path: 404 시 fallback path (예: /Chassis/{id}/PowerSubsystem)
        username, password, timeout, verify_ssl: 표준 HTTP 옵션
        section_name: error 분류 라벨 (envelope errors[] 의 stage)

    Returns:
        (data_dict, errors_list, source_label)
        source_label: 'primary' | 'fallback' | 'not_supported' | 'failed'
    """
    errors = []
    st, data, err = _get(bmc_ip, primary_path, username, password, timeout, verify_ssl)

    if not err and st == 200:
        return data, errors, 'primary'

    if st == 404:
        st_fb, data_fb, err_fb = _get(bmc_ip, fallback_path, username, password,
                                      timeout, verify_ssl)
        if not err_fb and st_fb == 200:
            return data_fb, errors, 'fallback'
        if st_fb == 404:
            return {}, errors, 'not_supported'
        errors.append(_err(section_name,
                           f'fallback {fallback_path} 실패: {err_fb or st_fb}'))
        return {}, errors, 'failed'

    errors.append(_err(section_name, f'{primary_path} 실패: {err or st}'))
    return {}, errors, 'failed'


def _resolve_first_member_uri(bmc_ip, coll_uri, username, password, timeout, verify_ssl):
    """컬렉션 URI → 첫 번째 Member의 @odata.id 추출.

    Managers/Chassis 등 N+1 컬렉션에서 첫 멤버만 반환 (NEXT_ACTIONS T3-05 — 향후 결정).
    Returns: (member_uri_or_none, status_code, error_msg)
    """
    if not coll_uri:
        return None, None, 'collection uri 없음'
    st, coll, err = _get(bmc_ip, _p(coll_uri), username, password, timeout, verify_ssl)
    if err or st != 200:
        return None, st, err or f'HTTP {st}'
    members = _safe(coll, 'Members') or []
    if not members:
        return None, st, 'members 없음'
    return _safe(members[0], '@odata.id'), st, None


def detect_vendor(bmc_ip, username, password, timeout, verify_ssl):
    """ServiceRoot(무인증)에서 벤더 식별 + Systems/Managers/Chassis URI 해석.

    Returns: (vendor, system_uri, manager_uri, chassis_uri, errors)
    """
    root, errors = _fetch_service_root(bmc_ip, username, password, timeout, verify_ssl)
    if root is None:
        return 'unknown', None, None, None, errors

    vendor = _detect_vendor_from_service_root(root)
    if vendor is None:
        vendor = 'unknown'
        errors.append(_err('vendor_detect', 'ServiceRoot에서 벤더 식별 불가'))

    systems_uri  = _safe(root, 'Systems',  '@odata.id')
    if not systems_uri:
        errors.append(_err('vendor_detect', 'ServiceRoot 에 Systems 링크 없음'))
        return vendor, None, None, None, errors

    system_uri, st, serr = _resolve_first_member_uri(
        bmc_ip, systems_uri, username, password, timeout, verify_ssl
    )
    if not system_uri:
        errors.append(_err('vendor_detect', f'Systems 컬렉션 실패: {serr}'))
        return vendor, None, None, None, errors

    # Managers / Chassis는 실패해도 errors에 등재하지 않음 — 후속 섹션에서 재시도/스킵
    manager_uri, _, _ = _resolve_first_member_uri(
        bmc_ip, _safe(root, 'Managers', '@odata.id'),
        username, password, timeout, verify_ssl,
    )
    chassis_uri, _, _ = _resolve_first_member_uri(
        bmc_ip, _safe(root, 'Chassis', '@odata.id'),
        username, password, timeout, verify_ssl,
    )

    # G3 (cycle 2026-04-30): vendor=unknown 시 Chassis/Managers/System Manufacturer fallback.
    # ServiceRoot v1.0~1.4 펌웨어는 Vendor/Product 표준 필드 부재 — Manufacturer는 표준.
    if vendor == 'unknown':
        for fb_uri, fb_label in (
            (chassis_uri, 'Chassis'),
            (manager_uri, 'Managers'),
            (system_uri, 'Systems'),
        ):
            if not fb_uri:
                continue
            fst, fdata, _ferr = _get(bmc_ip, _p(fb_uri), username, password, timeout, verify_ssl)
            if fst != 200 or not isinstance(fdata, dict):
                continue
            mfr = _safe(fdata, 'Manufacturer')
            if mfr and isinstance(mfr, str):
                fb_vendor = _normalize_vendor_from_aliases(mfr.strip().lower())
                if fb_vendor and fb_vendor != 'unknown':
                    vendor = fb_vendor
                    # errors에서 'ServiceRoot에서 벤더 식별 불가' 제거 (해소됨)
                    errors = [e for e in errors if 'ServiceRoot에서 벤더 식별 불가' not in (e.get('message') or '')]
                    errors.append(_err('vendor_detect',
                        f'{fb_label} Manufacturer fallback로 vendor={fb_vendor} 식별 (ServiceRoot 정보 부족)'))
                    break

    # G6 (cycle 2026-04-30): G3까지 fail이면 401 WWW-Authenticate realm 헤더로 마지막 추정.
    if vendor == 'unknown':
        realm_vendor = _probe_realm_hint(bmc_ip, timeout, verify_ssl)
        if realm_vendor:
            vendor = realm_vendor
            errors = [e for e in errors if 'ServiceRoot에서 벤더 식별 불가' not in (e.get('message') or '')]
            errors.append(_err('vendor_detect',
                f'WWW-Authenticate realm fallback로 vendor={realm_vendor} 식별 (ServiceRoot/Resources 본문 부족)'))

    return vendor, system_uri, manager_uri, chassis_uri, errors


# ── 섹션별 수집 ───────────────────────────────────────────────────────────────

# nosec rule12-r1 (전체 _extract_oem_*): 외부 계약 (rule 96 R1) 직접 의존.
# Redfish API spec 자체가 vendor namespace 정의 (Oem.Hpe / Oem.Dell / Oem.Lenovo ...)
# — adapter YAML로 위임 불가하므로 라이브러리에서 vendor 분기 허용.

def _extract_oem_hpe(data):                                                   # nosec rule12-r1
    """HPE OEM (iLO 5/6 = Oem.Hpe, iLO 4 이하 = Oem.Hp fallback).

    Underscore-prefixed keys (e.g. `_bios_date`) are hoisted to hardware-level
    by gather_system via _hoist_oem_extras. They populate **existing** envelope
    fields only (no new keys).
    Verified 2026-04-29 against HPE iLO 6 v1.73 (10.50.11.231): Bios.Current.Date
    populated; Manager.Oem.Hpe.Type field does not exist (former mapping was bug).
    """
    oem = _safe(data, 'Oem', 'Hpe') or _safe(data, 'Oem', 'Hp') or {}         # nosec rule12-r1
    ahs = _safe(oem, 'AggregateHealthStatus') or {}
    bios_oem = _safe(oem, 'Bios', 'Current') or {}
    return {
        # Hoisted to hardware.bios_date (rule 96 — HPE OEM contract)
        '_bios_date':              _safe(bios_oem, 'Date'),
        'post_state':              _safe(oem, 'PostState'),
        'server_signature':        _safe(oem, 'ServerSignature'),
        'aggregate_server_health': _safe(ahs, 'AggregateServerHealth'),
        'fan_redundancy':          _safe(ahs, 'FanRedundancy'),
        'psu_redundancy':          _safe(ahs, 'PowerSupplyRedundancy'),
        'subsystem_health': {
            'fans':         _safe(ahs, 'Fans', 'Status', 'Health'),
            'memory':       _safe(ahs, 'Memory', 'Status', 'Health'),
            'network':      _safe(ahs, 'Network', 'Status', 'Health'),
            'power':        _safe(ahs, 'PowerSupplies', 'Status', 'Health'),
            'processors':   _safe(ahs, 'Processors', 'Status', 'Health'),
            'storage':      _safe(ahs, 'Storage', 'Status', 'Health'),
            'temperatures': _safe(ahs, 'Temperatures', 'Status', 'Health'),
        },
    }


def _extract_oem_dell(data):                                                  # nosec rule12-r1
    """Dell OEM (Oem.Dell.DellSystem).

    Round 11 raw 검증 (10.100.15.27, iDRAC 7.10.70.00): 정확한 키는
    'EstimatedExhaustTemperatureCelsius'. 일부 구 펌웨어에서 'Cel' 변형 가능성
    있어 Celsius 우선, Cel fallback.
    """
    oem = _safe(data, 'Oem', 'Dell', 'DellSystem') or {}                      # nosec rule12-r1
    bios_date = _safe(oem, 'BIOSReleaseDate')
    return {
        # Hoisted to hardware.bios_date by gather_system (envelope consistency w/ HPE)
        '_bios_date':              bios_date,
        'lifecycle_version':       _safe(oem, 'LifecycleControllerVersion'),
        'bios_release_date':       bios_date,
        'current_rollup_status':   _safe(oem, 'CurrentRollupStatus'),
        'cpu_rollup_status':       _safe(oem, 'CPURollupStatus'),
        'fan_rollup_status':       _safe(oem, 'FanRollupStatus'),
        'battery_rollup_status':   _safe(oem, 'BatteryRollupStatus'),
        'intrusion_rollup_status': _safe(oem, 'IntrusionRollupStatus'),
        'storage_rollup_status':   _safe(oem, 'StorageRollupStatus'),
        'chassis_service_tag':     _safe(oem, 'ChassisServiceTag'),
        'express_service_code':    _safe(oem, 'ExpressServiceCode'),
        'estimated_exhaust_temp':  (_safe(oem, 'EstimatedExhaustTemperatureCelsius')
                                    or _safe(oem, 'EstimatedExhaustTemperatureCel')),
    }


def _extract_oem_lenovo(data, chassis_data=None):                             # nosec rule12-r1
    """Lenovo OEM (Oem.Lenovo).

    실측 (Lenovo XCC SR650 V2, 2026-04-28): ProductName은 System.Oem.Lenovo
    가 아닌 Chassis.Oem.Lenovo 에 존재. chassis_data 가 주어지면 Chassis 우선,
    없으면 System.Model 로 fallback.

    2026-04-29 fix B61: 추가 OEM 키 추출 — System.Oem.Lenovo의 운영 메타.
    """
    sys_oem = _safe(data, 'Oem', 'Lenovo') or {}                              # nosec rule12-r1
    cha_oem = _safe(chassis_data or {}, 'Oem', 'Lenovo') or {} if chassis_data else {}  # nosec rule12-r1
    product_name = (
        _safe(sys_oem, 'ProductName')
        or _safe(cha_oem, 'ProductName')
        or _safe(data, 'Model')
    )
    return {
        'product_name':         product_name,
        'system_status':        _safe(sys_oem, 'SystemStatus'),
        'fru_serial':           _safe(cha_oem, 'FruSerialNumber'),
        'machine_type':         _safe(cha_oem, 'MachineType'),
        'machine_level':        _safe(cha_oem, 'MachineLevel'),
        'product_id':           _safe(cha_oem, 'ProductId'),
        'system_id':            _safe(cha_oem, 'SystemId'),
        'health_summary':       _safe(sys_oem, 'HealthSummary'),
        'led_indicator':        _safe(cha_oem, 'LEDIndicators') or _safe(cha_oem, 'IndicatorLED'),
    }


def _extract_oem_supermicro(data):                                            # nosec rule12-r1
    """Supermicro OEM (Oem.Supermicro)."""
    oem = _safe(data, 'Oem', 'Supermicro') or {}                              # nosec rule12-r1
    return {
        'board_id':   _safe(oem, 'BoardID'),
        'node_id':    _safe(oem, 'NodeID'),
    }


def _extract_oem_cisco(data, chassis_data=None):                              # nosec rule12-r1
    """Cisco OEM (Oem.Cisco).

    2026-04-29 fix B61: Cisco CIMC C220 M4 (Round 11): ServiceRoot.Oem 빈 dict
    이지만 System/Chassis Oem.Cisco는 BoardSerial / Locator 등 일부 노출.
    """
    sys_oem = _safe(data, 'Oem', 'Cisco') or {}                               # nosec rule12-r1
    cha_oem = _safe(chassis_data or {}, 'Oem', 'Cisco') or {} if chassis_data else {}  # nosec rule12-r1
    return {
        'board_serial':       _safe(sys_oem, 'BoardSerialNumber') or _safe(cha_oem, 'BoardSerialNumber'),
        'platform_name':      _safe(sys_oem, 'PlatformName') or _safe(cha_oem, 'PlatformName'),
        'asset_tag':          _safe(sys_oem, 'AssetTag') or _safe(cha_oem, 'AssetTag'),
        'description':        _safe(sys_oem, 'Description') or _safe(cha_oem, 'Description'),
        'locator_led':        _safe(sys_oem, 'LocatorLED') or _safe(cha_oem, 'LocatorLED'),
    }


def _hoist_oem_extras(oem_dict, target):                                      # nosec rule12-r1
    """Move underscore-prefixed keys from OEM extractor result into target dict.

    Vendor extractors emit `_field` keys to populate **existing** envelope fields
    at hardware level (e.g. `_bios_date` -> hardware.bios_date). Only keys
    already present in `target` are filled — never adds new envelope keys.
    Unknown `_*` keys are silently dropped.
    Returns the cleaned OEM dict (without `_*` keys).
    """
    if not isinstance(oem_dict, dict):
        return oem_dict
    cleaned = {}
    for k, v in oem_dict.items():
        if isinstance(k, str) and k.startswith('_'):
            field = k[1:]
            if field in target and v is not None:
                # 2026-04-29 fix B16: bios_date / bios_release_date를 ISO 8601로 정규화.
                # Dell '09/10/2024' (MM/DD/YYYY) / HPE '03/01/2024' / 등 → 'YYYY-MM-DD'.
                if field in ('bios_date', 'bios_release_date'):
                    target[field] = _normalize_bios_date(v)
                else:
                    target[field] = v
            # else: silently drop — never add new envelope keys
        else:
            cleaned[k] = v
    return cleaned


def _normalize_link_status(value):
    """Normalize Redfish LinkStatus to standard enum.

    Vendor variations seen:
      - Dell iDRAC: 'LinkUp' / 'LinkDown' (raw spec)
      - HPE iLO:    'NoLink' / null
      - Cisco CIMC: 'Connected' / 'Disconnected' / null
      - Lenovo XCC: 'LinkUp' / 'LinkDown'

    Standard enum:
      'up'      — link active
      'down'    — link inactive (NoLink, LinkDown, Disconnected)
      'unknown' — null/unknown response
    """
    if value is None:
        return 'unknown'
    s = str(value).strip().lower()
    if not s or s in ('none', 'unknown', 'null'):
        return 'unknown'
    if s in ('linkup', 'up', 'connected', 'enabled', 'active'):
        return 'up'
    if s in ('linkdown', 'down', 'nolink', 'disconnected', 'disabled', 'inactive', 'offline'):
        return 'down'
    return s  # unknown vendor-specific value — preserve raw


def _normalize_bios_date(value):
    """Normalize BIOS date to ISO 8601 (YYYY-MM-DD) where possible.

    Handles common formats:
      - 'MM/DD/YYYY'        (Dell iDRAC, HPE iLO inline)
      - 'YYYY-MM-DDT...'    (ESXi already ISO)
      - '03/01/2024'         (HPE — but ambiguous; assume MM/DD if year > 12)
      - None/'N/A' -> None
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() in ('N/A', 'NONE', 'NOT SPECIFIED'):
        return None
    # Already ISO date prefix (YYYY-MM-DD)
    import re as _re
    if _re.match(r'^\d{4}-\d{2}-\d{2}', s):
        return s[:10]
    # MM/DD/YYYY
    m = _re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if m:
        mm, dd, yyyy = m.group(1), m.group(2), m.group(3)
        # Heuristic: if first part > 12, it's DD/MM/YYYY (European)
        try:
            if int(mm) > 12:
                mm, dd = dd, mm
        except ValueError:
            pass
        return f"{yyyy}-{int(mm):02d}-{int(dd):02d}"
    # DD-MM-YYYY or YYYY-MM-DD plain (no T)
    m = _re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # Couldn't parse — return raw to preserve data
    return s


# 주의 (2026-04-28 / NEXT_ACTIONS T3-03):
# cisco는 의도적으로 OEM helper 없음 — adapter cisco_cimc.yml strategy=standard_only,
# Round 11 실측 ServiceRoot.Oem 키가 비어있음 확인.
_OEM_EXTRACTORS = {                                                           # nosec rule12-r1
    'hpe':        _extract_oem_hpe,                                           # nosec rule12-r1
    'dell':       _extract_oem_dell,                                          # nosec rule12-r1
    'lenovo':     _extract_oem_lenovo,                                        # nosec rule12-r1
    'supermicro': _extract_oem_supermicro,                                    # nosec rule12-r1
    # 2026-04-29 fix B61: Cisco CIMC OEM 추출 추가 (이전 ServiceRoot.Oem 빈 dict이라 skip했지만
    # System/Chassis Oem.Cisco는 일부 운영 메타 노출).
    'cisco':      _extract_oem_cisco,                                         # nosec rule12-r1
}


def gather_system(bmc_ip, system_uri, vendor, username, password, timeout, verify_ssl,
                  chassis_uri=None):
    st, data, err = _get(bmc_ip, _p(system_uri), username, password, timeout, verify_ssl)
    errors = []
    if err or st != 200:
        errors.append(_err('system', f'System 수집 실패: {err or st}'))
        return {}, errors

    # Lenovo 등 일부 벤더는 ProductName 이 Chassis.Oem 에 위치 (System.Oem 에는 없음).
    # OEM extractor 가 chassis 데이터를 활용할 수 있도록 1회 fetch.
    chassis_data = None
    if chassis_uri:
        cst, cdata, _cerr = _get(bmc_ip, _p(chassis_uri), username, password, timeout, verify_ssl)
        if not _cerr and cst == 200:
            chassis_data = cdata

    # HostName: HPE는 빈 문자열("") 반환 가능 → None으로 변환
    hostname = _safe(data, 'HostName')
    if isinstance(hostname, str) and not hostname.strip():
        hostname = None

    # IndicatorLED fallback: HPE Gen11은 IndicatorLED 미제공, LocationIndicatorActive 사용
    led_state = _safe(data, 'IndicatorLED')
    if led_state is None:
        loc_active = _safe(data, 'LocationIndicatorActive')
        if loc_active is not None:
            led_state = 'Blinking' if loc_active else 'Off'

    # MemorySummary.Status: HPE는 Health 미제공, HealthRollup만 제공
    mem_health = _safe(data, 'MemorySummary', 'Status', 'Health')
    if mem_health is None:
        mem_health = _safe(data, 'MemorySummary', 'Status', 'HealthRollup')

    # cycle-016 Phase N: System 의 raw API 풍부 필드 추가 (asset/lastreset/tpm)
    tpm_modules = _safe(data, 'TrustedModules') or []
    tpm_summary = None
    if isinstance(tpm_modules, list) and tpm_modules:
        first_tpm = tpm_modules[0] if isinstance(tpm_modules[0], dict) else {}
        tpm_summary = {
            'interface_type':   _safe(first_tpm, 'InterfaceType'),
            'firmware_version': _safe(first_tpm, 'FirmwareVersion'),
            'state':            _safe(first_tpm, 'Status', 'State'),
        }

    # 빈 문자열 → None 정규화 helper. HPE: AssetTag/PartNumber 등이 "" 반환 케이스.
    # 호출자가 None 과 "" 두 가지 상태를 동일 처리하도록 강제하지 않기 위함.
    # 2026-04-30 추가: Cisco 등 일부 BMC가 trailing whitespace 포함하는 PartNumber 반환 →
    # cross-vendor consistency 위해 strip().
    def _ne(*keys):
        v = _safe(data, *keys)
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
        return v

    result = {
        'manufacturer':   _ne('Manufacturer'),
        'model':          _ne('Model'),
        'serial':         _ne('SerialNumber'),
        'sku':            _ne('SKU'),
        'uuid':           _ne('UUID'),
        'hostname':       hostname,
        'power_state':    _safe(data, 'PowerState'),
        'health':         _safe(data, 'Status', 'Health'),
        'state':          _safe(data, 'Status', 'State'),
        'led_state':      led_state,
        'bios_version':   _ne('BiosVersion'),
        # bios_date: 표준 Redfish 에는 키가 없음 — 벤더 OEM extractor 의 `_bios_date`
        # underscore-prefix 키를 _hoist_oem_extras 가 여기로 끌어올림.
        'bios_date':      None,
        'asset_tag':      _ne('AssetTag'),
        'system_type':    _safe(data, 'SystemType'),
        'part_number':    _ne('PartNumber'),
        'last_reset_time': _safe(data, 'LastResetTime'),
        'boot_progress':  _safe(data, 'BootProgress', 'LastState'),
        'tpm':            tpm_summary,
        'cpu_summary': {
            'count':  _safe(data, 'ProcessorSummary', 'Count'),
            'core_count':              _safe(data, 'ProcessorSummary', 'CoreCount'),
            'logical_processor_count': _safe(data, 'ProcessorSummary', 'LogicalProcessorCount'),
            'model':  _safe(data, 'ProcessorSummary', 'Model'),
            'health': _safe(data, 'ProcessorSummary', 'Status', 'Health'),
        },
        'memory_summary': {
            'total_gib': _safe(data, 'MemorySummary', 'TotalSystemMemoryGiB'),
            'health':    mem_health,
        },
        'oem': {},
    }

    # 벤더별 OEM 확장 dispatch (helper 함수에 위임)
    extractor = _OEM_EXTRACTORS.get(vendor)                                   # nosec rule12-r1
    if extractor is not None:
        # _extract_oem_lenovo / _extract_oem_cisco 는 chassis_data 인자 추가 (rule 96 R3 외부 계약).
        if vendor in ('lenovo', 'cisco'):                                     # nosec rule12-r1
            raw_oem = extractor(data, chassis_data=chassis_data)              # nosec rule12-r1
        else:
            raw_oem = extractor(data)
        # `_*` prefix 키 (예: `_bios_date`) 를 result hardware-level 로 끌어올린 뒤
        # OEM dict 에서는 제거. 기존 envelope 키만 채움 — 새 키 추가 없음.
        result['oem'] = _hoist_oem_extras(raw_oem, result)

    # 주요 필드 누락은 경고 수준 — 수집 자체는 성공으로 처리.
    # errors에 추가하지 않아 _run()에서 failed로 분류되지 않음.

    return result, errors


def gather_bmc(bmc_ip, manager_uri, vendor, username, password, timeout, verify_ssl):
    if not manager_uri:
        return {}, [_err('bmc', 'manager_uri 없음')]

    st, data, err = _get(bmc_ip, _p(manager_uri), username, password, timeout, verify_ssl)
    errors = []
    if err or st != 200:
        errors.append(_err('bmc', f'BMC 수집 실패: {err or st}'))
        return {}, errors

    # nosec rule12-r1: vendor → BMC 표시명 매핑 (외부 spec 기반 표준 이름)
    bmc_names = {'dell': 'iDRAC', 'hpe': 'iLO', 'lenovo': 'XCC', 'supermicro': 'BMC',
                 'cisco': 'CIMC'}                                              # nosec rule12-r1
    # cycle-016 Phase M/N: BMC 운영 정보 강화 — datetime / dns / mac / uuid / last_reset / timezone / power_state
    result = {
        'name':             bmc_names.get(vendor, 'BMC'),
        'firmware_version': _safe(data, 'FirmwareVersion'),
        'model':            _safe(data, 'Model'),
        'manager_type':     _safe(data, 'ManagerType'),
        'health':           _safe(data, 'Status', 'Health'),
        'state':            _safe(data, 'Status', 'State'),
        'power_state':      _safe(data, 'PowerState'),
        'uuid':             _safe(data, 'UUID'),
        'last_reset_time':  _safe(data, 'LastResetTime'),
        'timezone':         _safe(data, 'TimeZoneName'),
        'ip':               None,
        'mac_address':      None,
        'dns_name':         None,
        'datetime':         _safe(data, 'DateTime'),
        'datetime_offset':  _safe(data, 'DateTimeLocalOffset'),
        'oem': {},
    }

    # Manager EthernetInterfaces에서 BMC IP / MAC / FQDN + NameServers / Gateway 추출
    # 2026-04-29 cisco-critical-review: BMC NIC 의 NameServers / IPv4Addresses[*].Gateway
    # 를 envelope 비노출 임시 키 (_network_meta) 로 캐시한다. normalize_standard.yml 이
    # dns_servers / default_gateways 정규화에 사용 후 _network_meta 키 자체는 envelope
    # 에서 제거한다 (rule 13 R5 / 22 / envelope 키 추가 금지).
    bmc_name_servers = []
    bmc_static_name_servers = []
    bmc_gateways = []
    nic_link = _safe(data, 'EthernetInterfaces', '@odata.id')
    if nic_link:
        nst, ncoll, nerr = _get(bmc_ip, _p(nic_link), username, password, timeout, verify_ssl)
        if not nerr and nst == 200:
            for nm in (_safe(ncoll, 'Members') or []):
                nuri = _safe(nm, '@odata.id')
                if not nuri:
                    continue
                nst2, ndata, nerr2 = _get(bmc_ip, _p(nuri), username, password, timeout, verify_ssl)
                if nerr2 or nst2 != 200:
                    continue
                # IPv4 — 첫 매칭만 result['ip']/['mac_address']/['dns_name'] 에 사용,
                # 모든 NIC 의 Gateway 는 누적 (멀티 NIC: dedicated + shared 등 대비)
                nic_first_ip = None
                for addr in (_safe(ndata, 'IPv4Addresses') or []):
                    ip = _safe(addr, 'Address')
                    if ip and ip not in ('0.0.0.0', ''):
                        if nic_first_ip is None:
                            nic_first_ip = ip
                        gw = _safe(addr, 'Gateway')
                        if gw and gw not in ('0.0.0.0', '') and gw not in bmc_gateways:
                            bmc_gateways.append(gw)
                # NameServers / StaticNameServers — 모든 NIC 누적 (중복 제거 + placeholder skip).
                # 실측 (Lenovo XCC SR650 V2): NameServers=["","","","::","::","::"] 처럼
                # 미설정 슬롯이 빈 문자열 / "::" / "0.0.0.0" 같은 placeholder 로 채워지므로 필터.
                _ns_placeholders = ('', '0.0.0.0', '::', '::0', '::1')
                for ns in (_safe(ndata, 'NameServers') or []):
                    if ns and ns not in _ns_placeholders and ns not in bmc_name_servers:
                        bmc_name_servers.append(ns)
                for ns in (_safe(ndata, 'StaticNameServers') or []):
                    if ns and ns not in _ns_placeholders and ns not in bmc_static_name_servers:
                        bmc_static_name_servers.append(ns)
                # MAC + FQDN — IP 가 있는 첫 NIC 에서 추출 (기존 동작 유지)
                if nic_first_ip:
                    if not result['ip']:
                        result['ip'] = nic_first_ip
                    if not result['mac_address']:
                        result['mac_address'] = _safe(ndata, 'MACAddress') or _safe(ndata, 'PermanentMACAddress')
                    if not result['dns_name']:
                        result['dns_name'] = _safe(ndata, 'FQDN') or _safe(ndata, 'HostName')

    # envelope 비노출 — normalize_standard.yml 의 _rf_d_bmc_clean 단계에서 제거된다.
    result['_network_meta'] = {
        'name_servers':        bmc_name_servers,
        'static_name_servers': bmc_static_name_servers,
        'ipv4_gateways':       bmc_gateways,
    }

    # 벤더별 BMC OEM 확장 (Redfish API spec)
    if vendor == 'hpe':                                                       # nosec rule12-r1
        oem = _safe(data, 'Oem', 'Hpe') or _safe(data, 'Oem', 'Hp') or {}     # nosec rule12-r1
        # 2026-04-29 raw 검증 (10.50.11.231 iLO 6 v1.73): Manager.Oem.Hpe 에 `Type`
        # 필드 부재 — 이전 매핑은 항상 null. 의미 있는 값은 Firmware.Current.VersionString.
        result['oem'] = {
            'ilo_version': (_safe(oem, 'Firmware', 'Current', 'VersionString')
                            or _safe(data, 'Model')),
        }
    elif vendor == 'supermicro':                                              # nosec rule12-r1
        oem = _safe(data, 'Oem', 'Supermicro') or {}                          # nosec rule12-r1
        result['oem'] = {'bmc_ip': _safe(oem, 'BMCIPv4Address')}
        if not result['ip'] and result['oem'].get('bmc_ip'):
            result['ip'] = result['oem']['bmc_ip']
    elif vendor == 'lenovo':                                                  # nosec rule12-r1
        # Lenovo XCC: Manager.Oem.Lenovo.release_name 등 운영 상태 메타.
        # 실측 (XCC SR650 V2, 2026-04-28): release_name="whitley_gp_23-5".
        oem = _safe(data, 'Oem', 'Lenovo') or {}                              # nosec rule12-r1
        result['oem'] = {'release_name': _safe(oem, 'release_name')}

    return result, errors


def gather_processors(bmc_ip, system_uri, username, password, timeout, verify_ssl):
    path = _p(system_uri) + '/Processors'
    st, coll, err = _get(bmc_ip, path, username, password, timeout, verify_ssl)
    errors = []
    if err or st != 200:
        errors.append(_err('processors', f'Processor 컬렉션 실패: {err or st}'))
        return [], errors

    processors = []
    for member in (_safe(coll, 'Members') or []):
        uri = _safe(member, '@odata.id')
        if not uri: continue
        st, pdata, perr = _get(bmc_ip, _p(uri), username, password, timeout, verify_ssl)
        if perr or st != 200:
            errors.append(_err('processors', f'Processor {uri} 실패: {perr or st}'))
            continue
        if _safe(pdata, 'Status', 'State') in ('Absent', 'Disabled'):
            continue
        # 2026-04-29 raw 검증 (HPE iLO 6): SerialNumber / PartNumber 가 빈 문자열 ""
        # 반환 (BMC 한계). "" 은 의미상 None — 호출자가 truthy 비교만으로 판정 가능하도록
        # None 으로 정규화. cycle-016 Phase N 풍부 필드는 그대로 유지.
        # 2026-04-30: Cisco 등 trailing whitespace 정규화 추가.
        def _ne_p(*ks):
            v = _safe(pdata, *ks)
            if isinstance(v, str):
                v = v.strip()
                if not v:
                    return None
            return v

        processors.append({
            'id':                _safe(pdata, 'Id'),
            'name':              _ne_p('Name'),
            'model':             _ne_p('Model'),
            'manufacturer':      _ne_p('Manufacturer'),
            'socket':            _safe(pdata, 'Socket'),
            'total_cores':       _safe(pdata, 'TotalCores'),
            'total_threads':     _safe(pdata, 'TotalThreads'),
            'speed_mhz':         _safe(pdata, 'MaxSpeedMHz'),
            'health':            _safe(pdata, 'Status', 'Health'),
            'processor_type':    _safe(pdata, 'ProcessorType'),
            'architecture':      _safe(pdata, 'ProcessorArchitecture'),
            'instruction_set':   _safe(pdata, 'InstructionSet'),
            'serial_number':     _ne_p('SerialNumber'),
            'part_number':       _ne_p('PartNumber'),
        })
    return processors, errors


def gather_memory(bmc_ip, system_uri, username, password, timeout, verify_ssl):
    path = _p(system_uri) + '/Memory'
    st, coll, err = _get(bmc_ip, path, username, password, timeout, verify_ssl)
    errors = []
    if err or st != 200:
        errors.append(_err('memory', f'Memory 컬렉션 실패: {err or st}'))
        return {'total_mib': None, 'slots': []}, errors

    slots, total_mib = [], 0
    for member in (_safe(coll, 'Members') or []):
        uri = _safe(member, '@odata.id')
        if not uri: continue
        st, mdata, merr = _get(bmc_ip, _p(uri), username, password, timeout, verify_ssl)
        if merr or st != 200:
            errors.append(_err('memory', f'Memory {uri} 실패: {merr or st}'))
            continue
        if _safe(mdata, 'Status', 'State') == 'Absent':
            continue
        cap = _safe(mdata, 'CapacityMiB') or 0
        cap_int = _safe_int(cap)
        if cap_int:
            total_mib += cap_int
        # cycle-016 Phase N: BaseModuleType / RankCount / ErrorCorrection / DataWidth 추가
        # Phase P: 3 채널 키 일관성 — capacity_mb (이전 capacity_mib) 로 통일
        # 2026-04-29 fix B90: Cisco CIMC가 Manufacturer를 raw JEDEC ID '0xCExx'로 emit.
        # _normalize_jedec()로 vendor 이름 정규화 (Samsung/SK hynix/Micron 등).
        # 2026-04-29 fix B09: locator (DIMM 물리 위치) 추가 — 교체 작업 시 식별용.
        slots.append({
            'id':              _safe(mdata, 'Id'),
            'name':            _safe(mdata, 'Name'),
            # 'locator' 별도 키: DeviceLocator (벤더 표준 — 'A1','DIMM_A1','PROC1.DIMMA1' 등)
            # MemoryLocation.Slot 도 폴백 (Dell iDRAC 일부 펌웨어).
            'locator':         _safe(mdata, 'DeviceLocator') or _safe(mdata, 'MemoryLocation', 'Slot'),
            'capacity_mb':     cap_int,
            'type':            _safe(mdata, 'MemoryDeviceType'),
            'base_module_type': _safe(mdata, 'BaseModuleType'),
            'speed_mhz':       _safe(mdata, 'OperatingSpeedMhz'),
            'manufacturer':    _normalize_jedec(_safe(mdata, 'Manufacturer')),
            'serial':          _strip_or_none(_safe(mdata, 'SerialNumber')),
            # 2026-04-30: Cisco 등 trailing whitespace 정규화.
            'part_number':     _strip_or_none(_safe(mdata, 'PartNumber')),
            'rank_count':      _safe(mdata, 'RankCount'),
            'data_width_bits': _safe(mdata, 'DataWidthBits'),
            'bus_width_bits':  _safe(mdata, 'BusWidthBits'),
            'error_correction': _safe(mdata, 'ErrorCorrection'),
            'health':          _safe(mdata, 'Status', 'Health'),
        })
    return {'total_mib': total_mib or None, 'slots': slots}, errors


def _gather_simple_storage(bmc_ip, members, username, password, timeout, verify_ssl):
    """SimpleStorage 경로 — 플랫 디바이스 목록 (구형 BMC 호환)."""
    controllers = []
    errors = []
    for member in members:
        uri = _safe(member, '@odata.id')
        if not uri:
            continue
        st, sdata, serr = _get(bmc_ip, _p(uri), username, password, timeout, verify_ssl)
        if serr or st != 200:
            errors.append(_err('storage', f'SimpleStorage {uri} 실패: {serr or st}'))
            continue
        drives = []
        for dev in (_safe(sdata, 'Devices') or []):
            cap_int = _safe_int(_safe(dev, 'CapacityBytes'))
            drives.append({
                'id':             None,
                'name':           _safe(dev, 'Name'),
                'model':          _safe(dev, 'Model'),
                'serial':         None,
                'manufacturer':   _safe(dev, 'Manufacturer'),
                'media_type':     None,
                'protocol':       None,
                'capacity_bytes': cap_int,
                'capacity_gb':    round(cap_int / 1e9, 2) if cap_int else None,
                'health':         _safe(dev, 'Status', 'Health'),
            })
        controllers.append({
            'id': _safe(sdata, 'Id'), 'name': _safe(sdata, 'Name'),
            'health': _safe(sdata, 'Status', 'Health'), 'drives': drives,
        })
    return controllers, errors


def _extract_storage_controller_info(sdata, bmc_ip, username, password, timeout, verify_ssl):
    """컨트롤러 메타 추출 — StorageControllers 인라인 우선, Controllers 서브링크 fallback.

    controller_name 은 실제 하드웨어 모델명 (예: "ThinkSystem RAID 930-8i 2GB Flash PCIe").
    Storage 객체의 Name 은 "RAID Storage" 같은 컨테이너 라벨이라 별개로 보존.
    """
    # 반환 (dict, errors_list) — 401/403/503 응답을 silent fail 로 두지 않고
    # errors 에 누적해 호출자가 "controller 정보 부재" 사유를 추적할 수 있게 한다.
    # 이전 구현은 cst != 200 인 모든 응답을 빈 dict 로만 반환해 권한 부족/일시 과부하를
    # 정상 부재와 구분 불가했음.
    errors = []
    inline_ctrls = _safe(sdata, 'StorageControllers') or []
    if inline_ctrls:
        c = inline_ctrls[0]
        return {
            'controller_name':         _safe(c, 'Name'),
            'controller_model':        _safe(c, 'Model'),
            'controller_firmware':     _safe(c, 'FirmwareVersion'),
            'controller_manufacturer': _safe(c, 'Manufacturer'),
            'controller_health':       _safe(c, 'Status', 'Health'),
        }, errors
    ctrl_link = _safe(sdata, 'Controllers', '@odata.id')
    if not ctrl_link:
        return {}, errors
    cst, ctrl_coll, cerr = _get(bmc_ip, _p(ctrl_link), username, password, timeout, verify_ssl)
    if cerr or cst != 200:
        # 401/403/503: BMC 가 응답한 의미 있는 에러 — errors 에 기록
        errors.append(_err('storage',
                           f'Controllers 컬렉션 fetch 실패 ({ctrl_link}): {cerr or cst}',
                           detail={'status_code': cst}))
        return {'controller_fetch_status': cst}, errors
    ctrl_members = _safe(ctrl_coll, 'Members') or []
    if not ctrl_members:
        return {}, errors
    c_uri = _safe(ctrl_members[0], '@odata.id')
    if not c_uri:
        return {}, errors
    cst2, cdata, cerr2 = _get(bmc_ip, _p(c_uri), username, password, timeout, verify_ssl)
    if cerr2 or cst2 != 200:
        errors.append(_err('storage',
                           f'Controller fetch 실패 ({c_uri}): {cerr2 or cst2}',
                           detail={'status_code': cst2}))
        return {'controller_fetch_status': cst2}, errors
    return {
        'controller_name':         _safe(cdata, 'Name'),
        'controller_model':        _safe(cdata, 'Model'),
        'controller_firmware':     _safe(cdata, 'FirmwareVersion'),
        'controller_manufacturer': _safe(cdata, 'Manufacturer'),
        'controller_health':       _safe(cdata, 'Status', 'Health'),
    }, errors


def _extract_storage_drives(sdata, bmc_ip, username, password, timeout, verify_ssl):
    """Drives 추출 — Empty Bay 필터링 + 정규화."""
    drives = []
    errors = []
    for d_member in (_safe(sdata, 'Drives') or []):
        d_uri = _safe(d_member, '@odata.id')
        if not d_uri:
            continue
        dst, ddata, derr = _get(bmc_ip, _p(d_uri), username, password, timeout, verify_ssl)
        if derr or dst != 200:
            errors.append(_err('storage', f'Drive {d_uri} 실패: {derr or dst}'))
            continue
        # Q-09: HPE Empty Bay 필터 — CapacityBytes가 없거나 Name에 "Empty" 포함 시 스킵
        drive_name = _safe(ddata, 'Name') or ''
        cap_int = _safe_int(_safe(ddata, 'CapacityBytes'), default=0)
        if not cap_int:
            continue
        if 'empty' in drive_name.lower():
            continue
        # PredictedMediaLifeLeftPercent: HPE float / others int → normalize to int
        life_pct = _safe(ddata, 'PredictedMediaLifeLeftPercent')
        if life_pct is not None:
            life_pct = _safe_int(life_pct)
        drives.append({
            'id':             _safe(ddata, 'Id'),
            'name':           _safe(ddata, 'Name'),
            'model':          _safe(ddata, 'Model'),
            'serial':         _safe(ddata, 'SerialNumber'),
            'manufacturer':   _safe(ddata, 'Manufacturer'),
            'media_type':     _safe(ddata, 'MediaType'),
            'protocol':       _safe(ddata, 'Protocol'),
            'capacity_bytes': cap_int,
            'capacity_gb':    round(cap_int / 1e9, 2) if cap_int else None,
            'health':         _safe(ddata, 'Status', 'Health') or _safe(ddata, 'Status', 'HealthRollup'),
            'failure_predicted':      _safe(ddata, 'FailurePredicted'),
            'predicted_life_percent': life_pct,
        })
    return drives, errors


def _extract_storage_volumes(sdata, controller_id, bmc_ip, username, password, timeout, verify_ssl):
    """Volumes 추출 — RAID 정규화 + JBOD 필터링."""
    volumes = []
    errors = []
    vol_link = _safe(sdata, 'Volumes', '@odata.id')
    if not vol_link:
        return volumes, errors
    vst, vcoll, verr = _get(bmc_ip, _p(vol_link), username, password, timeout, verify_ssl)
    if verr or vst != 200:
        # Volumes 미지원(HBA 모드 등)은 정상 — 에러 추가하지 않음
        return volumes, errors
    raid_map = {
        'NonRedundant': 'RAID0', 'Mirrored': 'RAID1',
        'StripedWithParity': 'RAID5', 'SpannedMirrors': 'RAID10',
        'SpannedStripesWithParity': 'RAID50',
    }
    for v_member in (_safe(vcoll, 'Members') or []):
        v_uri = _safe(v_member, '@odata.id')
        if not v_uri:
            continue
        vst2, vdata, verr2 = _get(bmc_ip, _p(v_uri), username, password, timeout, verify_ssl)
        if verr2 or vst2 != 200:
            errors.append(_err('storage', f'Volume {v_uri} 실패: {verr2 or vst2}'))
            continue
        # RAIDType 표준 우선, Dell VolumeType fallback
        raid_type = _safe(vdata, 'RAIDType') or raid_map.get(_safe(vdata, 'VolumeType'))
        # member_drive_ids: Links.Drives[]의 @odata.id에서 마지막 path segment
        member_ids = [
            d_oid.rstrip('/').rsplit('/', 1)[-1]
            for d_link in (_safe(vdata, 'Links', 'Drives') or [])
            for d_oid in [_safe(d_link, '@odata.id')] if d_oid
        ]
        # JBOD/pass-through 필터: Non-RAID 모드에서 물리 디스크를 개별 Volume으로 노출
        vol_id = _safe(vdata, 'Id')
        if raid_type is None and len(member_ids) == 1 and member_ids[0] == vol_id:
            continue
        vcap_int = _safe_int(_safe(vdata, 'CapacityBytes'))
        # BUG-16 fix: Volume Name / DisplayName trailing whitespace 제거 (raw 'VD_0   ' 사고)
        v_name_raw = _safe(vdata, 'Name')
        v_name = v_name_raw.strip() if isinstance(v_name_raw, str) else v_name_raw
        # 2026-04-29 fix B48: Cisco CIMC가 Volume.Name을 빈 문자열 "" 로 emit.
        # 호출자 친화 fallback: 'Volume {id}' 또는 '{raid_level} Volume'.
        if not v_name:
            if vol_id:
                v_name = f"Volume {vol_id}"
            elif raid_type:
                v_name = f"{raid_type} Volume"
            else:
                v_name = None
        # BUG-15 fix: 표준 Redfish Volume.BootVolume 우선, 없으면 Dell Oem fallback.
        # 표준 필드가 명시 false 인 경우도 보존하기 위해 None 비교 사용.
        std_boot = _safe(vdata, 'BootVolume')
        if std_boot is not None:
            boot_volume = bool(std_boot)
        elif _safe(vdata, 'Oem', 'Dell'):                                              # nosec rule12-r1
            boot_volume = _safe(vdata, 'Oem', 'Dell', 'DellVolume', 'BootVolumeSource') is not None  # nosec rule12-r1
        else:
            boot_volume = None
        volumes.append({
            'id':               _safe(vdata, 'Id'),
            'name':             v_name,
            'controller_id':    controller_id,
            'member_drive_ids': member_ids,
            'raid_level':       raid_type,
            'total_mb':         (vcap_int // 1048576) if vcap_int else None,
            # BUG-19 fix: drive 와 동일하게 Status.Health 누락 시 HealthRollup fallback.
            'health':           _safe(vdata, 'Status', 'Health') or _safe(vdata, 'Status', 'HealthRollup'),
            'state':            _safe(vdata, 'Status', 'State'),
            'boot_volume':      boot_volume,
        })
    return volumes, errors


def _gather_standard_storage(bmc_ip, members, username, password, timeout, verify_ssl):
    """Storage 정규경로 — 컨트롤러 → 드라이브 → 볼륨 계층."""
    controllers = []
    volumes = []
    errors = []
    for member in members:
        uri = _safe(member, '@odata.id')
        if not uri:
            continue
        st, sdata, serr = _get(bmc_ip, _p(uri), username, password, timeout, verify_ssl)
        if serr or st != 200:
            errors.append(_err('storage', f'Storage {uri} 실패: {serr or st}'))
            continue
        ctrl_info, c_errs = _extract_storage_controller_info(sdata, bmc_ip, username, password, timeout, verify_ssl)
        errors.extend(c_errs)
        drives, d_errs = _extract_storage_drives(sdata, bmc_ip, username, password, timeout, verify_ssl)
        errors.extend(d_errs)
        # name 우선순위: controller_name (실제 하드웨어 모델) → Storage 객체 Name fallback.
        # 실측 (Lenovo XCC SR650 V2): 컨트롤러 식별 정보 손실 차단.
        ctrl_name = ctrl_info.get('controller_name') or _safe(sdata, 'Name')
        ctrl_entry = {
            'id':     _safe(sdata, 'Id'),
            'name':   ctrl_name,
            'health': _safe(sdata, 'Status', 'Health') or _safe(sdata, 'Status', 'HealthRollup'),
            'drives': drives,
        }
        ctrl_entry.update(ctrl_info)
        controllers.append(ctrl_entry)
        vols, v_errs = _extract_storage_volumes(sdata, _safe(sdata, 'Id'), bmc_ip, username, password, timeout, verify_ssl)
        volumes.extend(vols)
        errors.extend(v_errs)
    return controllers, volumes, errors


def gather_storage(bmc_ip, system_uri, username, password, timeout, verify_ssl):
    """Storage 진입 — Storage → SimpleStorage fallback dispatcher."""
    path = _p(system_uri) + '/Storage'
    st, coll, err = _get(bmc_ip, path, username, password, timeout, verify_ssl)
    errors = []

    # Storage 실패 시 SimpleStorage fallback (구형 BMC 호환)
    use_simple = False
    if err or st != 200:
        simple_path = _p(system_uri) + '/SimpleStorage'
        st2, coll2, err2 = _get(bmc_ip, simple_path, username, password, timeout, verify_ssl)
        if not err2 and st2 == 200:
            use_simple = True
            coll = coll2
            errors.append(_err('storage', 'Storage 미지원, SimpleStorage fallback 사용'))
        else:
            errors.append(_err('storage', f'Storage/SimpleStorage 모두 실패: {err or st}'))
            return {'controllers': [], 'volumes': []}, errors

    members = _safe(coll, 'Members') or []
    if use_simple:
        controllers, sub_errors = _gather_simple_storage(bmc_ip, members, username, password, timeout, verify_ssl)
        errors.extend(sub_errors)
        return {'controllers': controllers, 'volumes': []}, errors
    controllers, volumes, sub_errors = _gather_standard_storage(bmc_ip, members, username, password, timeout, verify_ssl)
    errors.extend(sub_errors)
    return {'controllers': controllers, 'volumes': volumes}, errors


def gather_network(bmc_ip, system_uri, username, password, timeout, verify_ssl):
    """Systems/{id}/EthernetInterfaces — 호스트 서버 NIC"""
    path = _p(system_uri) + '/EthernetInterfaces'
    st, coll, err = _get(bmc_ip, path, username, password, timeout, verify_ssl)
    errors = []
    if err or st != 200:
        errors.append(_err('network', f'EthernetInterfaces 실패: {err or st}'))
        return [], errors

    nics = []
    for member in (_safe(coll, 'Members') or []):
        uri = _safe(member, '@odata.id')
        if not uri: continue
        st, ndata, nerr = _get(bmc_ip, _p(uri), username, password, timeout, verify_ssl)
        if nerr or st != 200:
            errors.append(_err('network', f'NIC {uri} 실패: {nerr or st}'))
            continue
        ipv4_addrs = [
            {'address': a.get('Address'), 'subnet_mask': a.get('SubnetMask'),
             'gateway': a.get('Gateway'), 'address_origin': a.get('AddressOrigin')}
            for a in (_safe(ndata, 'IPv4Addresses') or [])
            if a.get('Address') not in (None, '0.0.0.0', '')
        ]
        # 2026-04-29 fix B13: link_status enum 정규화 — Dell linkup/linkdown / HPE NoLink / Cisco Connected/Disconnected → up/down/unknown
        nics.append({
            'id': _safe(ndata, 'Id'), 'name': _safe(ndata, 'Name') or _safe(ndata, 'Id') or '',
            'mac': _safe(ndata, 'MACAddress'), 'speed_mbps': _safe(ndata, 'SpeedMbps'),
            'mtu': _safe(ndata, 'MTUSize'),
            'link_status': _normalize_link_status(_safe(ndata, 'LinkStatus')),
            'health': _safe(ndata, 'Status', 'Health'),
            'ipv4': ipv4_addrs,
        })
    return nics, errors


def gather_network_adapters_chassis(bmc_ip, chassis_uri, username, password, timeout, verify_ssl):
    """P4 (cycle 2026-04-28): Chassis/{id}/NetworkAdapters 수집.

    NetworkAdapters → adapters[] (NIC 카드 모델/firmware)
    NetworkPorts    → ports[]    (port-level link state)
    PortType 기반 분류 → fc_hbas[] / infiniband[] (HBA/IB 별도 buckets)

    일부 vendor (Cisco CIMC 등)에서 미지원 가능 → 빈 결과로 graceful degradation.
    """
    out = {'adapters': [], 'ports': [], 'fc_hbas': [], 'infiniband': []}
    errors = []
    if not chassis_uri:
        return out, errors

    base = _p(chassis_uri) + '/NetworkAdapters'
    st, coll, err = _get(bmc_ip, base, username, password, timeout, verify_ssl)
    if err or st != 200:
        # 미지원 vendor 는 errors 에 기록하되 graceful degradation
        errors.append(_err('network_adapters',
                           f'NetworkAdapters 미지원 또는 실패: {err or st}'))
        return out, errors

    for member in (_safe(coll, 'Members') or []):
        adp_uri = _safe(member, '@odata.id')
        if not adp_uri:
            continue
        st2, adata, aerr = _get(bmc_ip, _p(adp_uri), username, password, timeout, verify_ssl)
        if aerr or st2 != 200:
            errors.append(_err('network_adapters', f'NetworkAdapter {adp_uri} 실패: {aerr or st2}'))
            continue

        adapter_id = _safe(adata, 'Id')
        # FirmwareVersion: Controllers[0].FirmwarePackageVersion 또는 root
        fw_ver = None
        ctrls = _safe(adata, 'Controllers', default=[]) or []
        if ctrls and isinstance(ctrls, list):
            fw_ver = _safe(ctrls[0], 'FirmwarePackageVersion')
        # 빈 placeholder NetworkAdapter 필터:
        # 일부 BMC (실측 Lenovo XCC SR650 V2)는 PCIe slot 자체를 NetworkAdapters 컬렉션에
        # 빈 entry 로 노출. Controllers[0].ControllerCapabilities.NetworkPortCount=0 또는
        # manufacturer/model 모두 빈 문자열이면 실제 NIC 가 아니므로 skip.
        port_count = 0
        if ctrls and isinstance(ctrls, list):
            caps = _safe(ctrls[0], 'ControllerCapabilities') or {}
            port_count = _safe_int(_safe(caps, 'NetworkPortCount'), default=0) or 0
        mfr = (_safe(adata, 'Manufacturer') or '').strip()
        model = (_safe(adata, 'Model') or '').strip()
        if port_count == 0 and not mfr and not model:
            continue
        # 2026-04-29 fix B93: HPE iLO NetworkAdapter는 mac/link/speed 가 NetworkAdapter root에 없고
        # NetworkPorts/Ports collection에만 존재. adapter level에 fold-in (첫 번째 활성 port의 메타).
        # Dell/Lenovo는 NetworkAdapter root에 정보 있어 그대로 보존.
        adapter_info = {
            'id':               adapter_id,
            'name':             _safe(adata, 'Name'),
            'manufacturer':     mfr or None,
            'model':            model or None,
            'part_number':      _safe(adata, 'PartNumber') or None,
            'serial_number':    _safe(adata, 'SerialNumber') or None,
            'firmware_version': fw_ver or None,
            'mac':              None,  # ports fold-in으로 채워짐 (B93)
            'link_status':      'unknown',  # 동일 (B93)
            'speed_mbps':       None,
            'port_count':       port_count,
        }
        out['adapters'].append(adapter_info)
        adapter_idx = len(out['adapters']) - 1

        # NetworkPorts (Redfish 1.5 이전) 또는 Ports (1.6+)
        ports_link = (_safe(adata, 'NetworkPorts', '@odata.id')
                      or _safe(adata, 'Ports', '@odata.id'))
        if not ports_link:
            continue
        st3, pcoll, perr = _get(bmc_ip, _p(ports_link), username, password, timeout, verify_ssl)
        if perr or st3 != 200:
            errors.append(_err('network_adapters',
                               f'NetworkPorts {ports_link} 실패: {perr or st3}'))
            continue

        for pmember in (_safe(pcoll, 'Members') or []):
            p_uri = _safe(pmember, '@odata.id')
            if not p_uri:
                continue
            st4, pdata, perr2 = _get(bmc_ip, _p(p_uri), username, password, timeout, verify_ssl)
            if perr2 or st4 != 200:
                continue
            speed_mbps = _safe(pdata, 'CurrentLinkSpeedMbps')
            speed_gbps = (speed_mbps / 1000.0) if isinstance(speed_mbps, (int, float)) else None
            assoc = _safe(pdata, 'AssociatedNetworkAddresses', default=[]) or []
            primary_addr = assoc[0] if assoc else None
            port_type = _safe(pdata, 'PortType') or ''
            # 2026-04-29 fix B13: ports의 link_status도 동일 enum 정규화.
            normalized_link = _normalize_link_status(_safe(pdata, 'LinkStatus'))
            port_info = {
                'adapter_id':              adapter_id,
                'adapter_model':           adapter_info['model'],
                'port_id':                 _safe(pdata, 'Id'),
                'name':                    _safe(pdata, 'Name'),
                'physical_port_number':    _safe(pdata, 'PhysicalPortNumber'),
                'link_status':             normalized_link,
                'link_state':              _safe(pdata, 'LinkState'),
                'current_link_speed_mbps': speed_mbps,
                'port_type':               port_type,
                'health':                  _safe(pdata, 'Status', 'Health'),
                'associated_address':      primary_addr,
            }
            out['ports'].append(port_info)
            # 2026-04-29 fix B93: adapter level에 ports의 첫 active 메타 fold-in.
            # 우선순위: link_status='up' > mac/speed 존재 > 첫 port.
            cur = out['adapters'][adapter_idx]
            if cur.get('mac') is None and primary_addr:
                cur['mac'] = primary_addr
            if cur.get('link_status') == 'unknown' or (cur.get('link_status') != 'up' and normalized_link == 'up'):
                cur['link_status'] = normalized_link
            if cur.get('speed_mbps') is None and speed_mbps:
                cur['speed_mbps'] = speed_mbps

            pt_lower = (port_type or '').lower()
            if 'fibrechannel' in pt_lower or pt_lower == 'fc':
                out['fc_hbas'].append({
                    'adapter_id':       adapter_id,
                    'adapter_model':    adapter_info['model'],
                    'port_id':          _safe(pdata, 'Id'),
                    'wwpn':             primary_addr,
                    'link_status':      _safe(pdata, 'LinkStatus'),
                    'link_speed_gbps':  speed_gbps,
                })
            elif 'infiniband' in pt_lower or pt_lower == 'ib':
                out['infiniband'].append({
                    'adapter_id':       adapter_id,
                    'adapter_model':    adapter_info['model'],
                    'port_id':          _safe(pdata, 'Id'),
                    'link_status':      _safe(pdata, 'LinkStatus'),
                    'link_speed_gbps':  speed_gbps,
                })

    return out, errors


def gather_firmware(bmc_ip, username, password, timeout, verify_ssl):
    """
    UpdateService/FirmwareInventory — 벤더 공통
    Members 에 상세 필드 없으면 개별 URI 조회 (Dell/HPE/Supermicro 모두 해당)
    """
    path = 'UpdateService/FirmwareInventory'
    st, coll, err = _get(bmc_ip, path, username, password, timeout, verify_ssl)
    errors = []
    if err or st != 200:
        errors.append(_err('firmware', f'FirmwareInventory 실패: {err or st}'))
        return [], errors

    fw_list = []
    for member in (_safe(coll, 'Members') or []):
        member_uri = _safe(member, '@odata.id')
        # Members 에 Name/Version 없으면 개별 URI 조회 (벤더 공통)
        if not _safe(member, 'Name') and member_uri:
            st2, fw_data, ferr = _get(bmc_ip, _p(member_uri), username, password, timeout, verify_ssl)
            if not ferr and st2 == 200:
                member = fw_data
        fw_id = _safe(member, 'Id') or (member_uri.split('/')[-1] if member_uri else None)
        # Q-14: Dell Previous- 항목 스킵 (비활성 이전 버전)
        if fw_id and isinstance(fw_id, str) and fw_id.startswith('Previous-'):
            continue
        # 2026-04-29 cisco-critical-review: Cisco CIMC 의 "N/A" 빈 슬롯 (slot-1, slot-2
        # 등 PCIe 미장착 슬롯) 노이즈 필터. Version 이 "N/A"/""/"NA" 면 firmware 컴포넌트가
        # 부재 — 호출자에게 노이즈로 전달되지 않도록 skip (기존 키 유지, list 길이만 정확).
        ver = _safe(member, 'Version')
        if isinstance(ver, str) and ver.strip().upper() in ('N/A', 'NA', ''):
            continue
        # Q-13: SoftwareId가 문자열 "null"이면 Python None으로 변환
        component = _safe(member, 'SoftwareId')
        if isinstance(component, str) and component.lower() == 'null':
            component = None
        # 2026-04-29 fix B43: Lenovo XCC pending firmware (BMC-Primary-Pending, UEFI-Pending)는
        # version=null + ID에 'Pending' 포함. version=null만으로는 호출자가 단순 누락인지 의도된
        # pending 인지 모름 → pending 메타필드 추가 (정책: pending=true이고 version=null은 정상,
        # pending=false이고 version=null은 데이터 누락).
        is_pending = bool(fw_id and isinstance(fw_id, str) and 'pending' in fw_id.lower())
        fw_list.append({
            'id':         fw_id,
            'name':       _safe(member, 'Name'),
            'version':    ver,
            'updateable': _safe(member, 'Updateable'),
            'component':  component or fw_id,
            'pending':    is_pending,
        })
    return fw_list, errors


def _gather_power_subsystem(bmc_ip, chassis_uri, username, password, timeout, verify_ssl):
    """DMTF 2020.4 (Redfish 1.13+) PowerSubsystem fallback parser.

    cycle 2026-05-01: 신 펌웨어 (HPE iLO 6 / Lenovo XCC2-3 / Dell iDRAC9 5.x+ /
    Supermicro X14+) 가 /Power 대신 /PowerSubsystem 응답. 기본 PSU 정보는 공통.
    PowerControl 같은 system-level metric 은 PowerSubsystem 에 직접 없고
    EnvironmentMetrics 로 분리됨 — 본 fallback 은 PSU info 만 매핑 (호출자 envelope
    유지). PowerControl 미응답이면 None.
    """
    errors = []
    ps_path = _p(chassis_uri) + '/PowerSubsystem'
    st, ps_data, perr = _get(bmc_ip, ps_path, username, password, timeout, verify_ssl)
    if perr or st != 200:
        # PowerSubsystem 도 없으면 진짜 미지원 — 호출자가 not_supported 분류
        return {}, [_err('power', f'PowerSubsystem 미지원: {perr or st}')] if st != 404 else []

    # PowerSubsystem.PowerSupplies 컬렉션 fetch
    psu_link = _safe(ps_data, 'PowerSupplies', '@odata.id')
    psus = []
    if psu_link:
        st_c, coll, _err_c = _get(bmc_ip, _p(psu_link), username, password, timeout, verify_ssl)
        if st_c == 200:
            for member in (_safe(coll, 'Members') or []):
                m_uri = _safe(member, '@odata.id')
                if not m_uri:
                    continue
                st_m, mdata, _err_m = _get(bmc_ip, _p(m_uri), username, password, timeout, verify_ssl)
                if st_m != 200:
                    continue
                psus.append({
                    'name':             _safe(mdata, 'Name'),
                    'model':            _safe(mdata, 'Model'),
                    'serial':           _safe(mdata, 'SerialNumber'),
                    'manufacturer':     _safe(mdata, 'Manufacturer'),
                    'power_capacity_w': _safe_int(_safe(mdata, 'PowerCapacityWatts')),
                    'firmware_version': _safe(mdata, 'FirmwareVersion'),
                    'health':           _safe(mdata, 'Status', 'Health'),
                    'state':            _safe(mdata, 'Status', 'State'),
                })

    # PowerControl 은 PowerSubsystem 표준에 없음 — chassis-level 합산 또는 None
    pc_capacity = None
    psu_caps = [p['power_capacity_w'] for p in psus if p['power_capacity_w'] is not None]
    if psu_caps:
        pc_capacity = sum(psu_caps)
    power_control = {
        'power_consumed_watts':  None,
        'power_capacity_watts':  pc_capacity,
        'interval_in_min':       None,
        'min_consumed_watts':    None,
        'avg_consumed_watts':    None,
        'max_consumed_watts':    None,
    } if psus else None

    return {'power_supplies': psus, 'power_control': power_control}, errors


def gather_power(bmc_ip, chassis_uri, username, password, timeout, verify_ssl):
    """Chassis/{id}/Power — PSU 정보. chassis_uri는 detect_vendor()에서 전달.

    cycle 2026-05-01: /Power 404 시 /PowerSubsystem fallback (DMTF 2020.4 신 schema).
    Storage SimpleStorage fallback 패턴 따름 (line 1417).
    """
    errors = []
    if not chassis_uri:
        errors.append(_err('power', 'chassis_uri 없음 (detect_vendor 에서 Chassis 미발견)'))
        return {}, errors

    power_path = _p(chassis_uri) + '/Power'
    st, pdata, perr = _get(bmc_ip, power_path, username, password, timeout, verify_ssl)

    # cycle 2026-05-01: 404 = 신 펌웨어 가능 → PowerSubsystem fallback
    if st == 404:
        return _gather_power_subsystem(bmc_ip, chassis_uri, username, password, timeout, verify_ssl)

    if perr or st != 200:
        errors.append(_err('power', f'Power 정보 실패: {perr or st}'))
        return {}, errors

    # 2026-04-29 cisco-critical-review: PSU 정격 (power_capacity_w) fallback —
    # Cisco CIMC / 일부 vendor 는 PowerSupplies[*].PowerCapacityWatts 를 응답하지 않고
    # InputRanges[0].OutputWattage 에 PSU 정격을 둔다. envelope 키는 그대로,
    # null 이던 값을 채운다.
    psus = []
    for psu in (_safe(pdata, 'PowerSupplies') or []):
        psu_capacity = _safe(psu, 'PowerCapacityWatts')
        if psu_capacity is None:
            ranges = _safe(psu, 'InputRanges') or []
            if isinstance(ranges, list) and ranges and isinstance(ranges[0], dict):
                psu_capacity = _safe_int(ranges[0].get('OutputWattage'))
        psus.append({
            'name':             _safe(psu, 'Name'),
            'model':            _safe(psu, 'Model'),
            'serial':           _safe(psu, 'SerialNumber'),
            'manufacturer':     _safe(psu, 'Manufacturer'),
            'power_capacity_w': psu_capacity,
            'firmware_version': _safe(psu, 'FirmwareVersion'),
            'health':           _safe(psu, 'Status', 'Health'),
            'state':            _safe(psu, 'Status', 'State'),
        })

    # PowerControl — system-level power consumption (Safe Common: 3 vendors verified)
    # production-audit (2026-04-29): pdata가 dict가 아닌 list/None일 가능성 방어 (Cisco/Supermicro edge)
    pc_list = (pdata.get('PowerControl') if isinstance(pdata, dict) else None) or []
    pc0 = pc_list[0] if pc_list else {}
    pm = pc0.get('PowerMetrics') or {}
    # 2026-04-29 cisco-critical-review: chassis level power_capacity_watts fallback —
    # Cisco 는 PowerControl[0].PowerCapacityWatts 를 null 응답. PSU power_capacity_w
    # 합산으로 fallback (PSU 770W × 2 = 1540W 형태).
    pc_capacity = _safe(pc0, 'PowerCapacityWatts')
    if pc_capacity is None:
        psu_caps = [p['power_capacity_w'] for p in psus if p['power_capacity_w'] is not None]
        if psu_caps:
            pc_capacity = sum(psu_caps)
    power_control = {
        'power_consumed_watts':  _safe(pc0, 'PowerConsumedWatts'),
        'power_capacity_watts':  pc_capacity,
        'interval_in_min':       _safe(pm, 'IntervalInMin'),
        'min_consumed_watts':    _safe(pm, 'MinConsumedWatts'),
        'avg_consumed_watts':    _safe(pm, 'AverageConsumedWatts'),
        'max_consumed_watts':    _safe(pm, 'MaxConsumedWatts'),
    } if pc0 else None

    return {'power_supplies': psus, 'power_control': power_control}, errors


# ── 메인 ─────────────────────────────────────────────────────────────────────

def _is_404_only_error(errs):
    """모든 errors가 'HTTP 404' 시그널이면 True (endpoint 자체 부재 = capability 미지원).

    cycle 2026-05-01: 404 = "endpoint 없음 = vendor/펌웨어 미지원" — errors[] 노이즈
    분리. 5xx / timeout / 401 / 403 과 분리해 'unsupported' 시그널로 분류.
    """
    if not errs:
        return False
    for e in errs:
        if not isinstance(e, dict):
            return False
        detail = (e.get('detail') or '')
        msg = (e.get('message') or '')
        # 'HTTP 404' 패턴: detail에 'HTTP 404' 또는 message에 '404' 단독 정수
        if 'HTTP 404' in detail or 'HTTP 404' in msg:
            continue
        # message가 정확히 '...: 404' (st 정수 그대로) 패턴
        if msg.endswith(': 404') or msg.endswith(' 404'):
            continue
        return False
    return True


def _make_section_runner(all_errors, collected, failed, unsupported=None):
    """섹션 collector wrapper — 예외/errors 누적 + collected/failed/unsupported 추적.

    rule 60: stacktrace는 stderr console verbose에만, errors[]에는 type+message만.
    cycle 2026-05-01: 404 시그널은 unsupported list로 분리 (endpoint 부재 = capability 미지원).
    호환성: unsupported 인자 미전달 시 기존 동작 유지 (back-compat).
    """
    def _run(section, fn, *args):
        try:
            val, errs = fn(*args)
            # 404 only면 unsupported로 분류, errors[]에서 제외 (호출자 noise 차단)
            if unsupported is not None and _is_404_only_error(errs):
                unsupported.append(section)
                return val
            all_errors.extend(errs)
            collected.append(section)
            if errs:
                failed.append(section)
            return val
        except Exception as e:
            sys.stderr.write(
                "[redfish_gather] %s 예외: %s\n%s\n" %
                (section, type(e).__name__, traceback.format_exc(limit=3))
            )
            all_errors.append(_err(
                section, '예외 발생',
                "%s: %s" % (type(e).__name__, str(e)[:200])
            ))
            failed.append(section)
            return None
    return _run


def _collect_all_sections(bmc_ip, vendor, system_uri, manager_uri, chassis_uri,
                          username, password, timeout, verify_ssl,
                          all_errors, collected, failed, unsupported=None):
    """9개 섹션 dispatch (system / bmc / processors / memory / storage / network /
    firmware / power / network_adapters[P4]).

    cycle 2026-05-01: unsupported list 추가 — 404 응답 섹션을 별도 분류
    (capability 미지원 = noise 아님).
    """
    _run = _make_section_runner(all_errors, collected, failed, unsupported)
    creds = (username, password, timeout, verify_ssl)
    return {
        'system':            _run('system',     gather_system,     bmc_ip, system_uri, vendor, *creds, chassis_uri),
        'bmc':               _run('bmc',        gather_bmc,        bmc_ip, manager_uri, vendor, *creds),
        'processors':        _run('processors', gather_processors, bmc_ip, system_uri,          *creds),
        'memory':            _run('memory',     gather_memory,     bmc_ip, system_uri,          *creds),
        'storage':           _run('storage',    gather_storage,    bmc_ip, system_uri,          *creds),
        'network':           _run('network',    gather_network,    bmc_ip, system_uri,          *creds),
        'firmware':          _run('firmware',   gather_firmware,   bmc_ip,                      *creds),
        'power':             _run('power',      gather_power,      bmc_ip, chassis_uri,         *creds),
        # P4 (cycle 2026-04-28): NIC 카드 + port-level + FC HBA / InfiniBand 분류
        'network_adapters':  _run('network_adapters',
                                   gather_network_adapters_chassis,
                                   bmc_ip, chassis_uri, *creds),
    }


def _compute_final_status(collected, failed, errors=None):
    """collected / failed list → final_status (success / partial / failed).

    cycle 2026-04-30: errors[]에 인증 실패 (HTTP 401/403) 흔적 발견 시 'failed' 강제.
    이전 동작은 1개 섹션이라도 collected에 들어가면 'partial' 반환 — try_one_account
    loop가 'partial'을 success로 판정해 두 번째 자격증명으로 fallback 안 함 (Dell vault
    accounts 순서 사고). 인증 자체가 거부된 상태에서 partial로 emit하면 호출자도
    "데이터 일부 받음"으로 오해. auth fail 명시적으로 'failed'로 분류.
    """
    clean = [s for s in collected if s not in failed]

    # 인증 실패 시그널이 errors[]에 있으면 partial/success로 끌어올리지 않음
    if errors:
        for e in errors:
            if not isinstance(e, dict):
                continue
            detail = (e.get('detail') or '')
            msg = (e.get('message') or '')
            if 'HTTP 401' in detail or 'HTTP 403' in detail:
                return 'failed', clean
            if '401' in msg and 'auth' in msg.lower():
                return 'failed', clean

    if not clean:
        return 'failed', clean
    if failed:
        return 'partial', clean
    return 'success', clean


# ── P2 (cycle 2026-04-28): AccountService — 공통계정 자동 생성/복구 ──────────
# vendor 분기는 Redfish API spec OEM namespace 의존 (rule 96 R1 외부 계약).
# Dell  : slot 기반 PATCH (/Accounts/{N}, N=1..17). POST 미지원
# HPE / Lenovo / Supermicro: POST /Accounts 표준
# Cisco : AccountService 표준 미지원 (errors[]에 not_supported 기록 후 종료)

def account_service_get(bmc_ip, username, password, timeout, verify_ssl):
    """GET /redfish/v1/AccountService + Accounts 컬렉션 enumerate.

    Returns: (acct_service: dict|None, accounts: list[{slot_uri, username, role_id, enabled}], errors)
    """
    errors = []
    code, root_data, err = _get(bmc_ip, 'AccountService', username, password, timeout, verify_ssl)
    if code != 200 or err:
        errors.append(_err('account_service', f'GET AccountService 실패', detail=err or f'HTTP {code}'))
        return None, [], errors
    accounts_link = _safe(root_data, 'Accounts', '@odata.id')
    if not accounts_link:
        errors.append(_err('account_service', 'AccountService.Accounts 링크 없음', detail=str(root_data)[:200]))
        return root_data, [], errors
    code, acc_coll, err = _get(bmc_ip, _p(accounts_link), username, password, timeout, verify_ssl)
    if code != 200 or err:
        errors.append(_err('account_service', 'GET Accounts 컬렉션 실패', detail=err or f'HTTP {code}'))
        return root_data, [], errors
    members = _safe(acc_coll, 'Members', default=[]) or []
    accounts = []
    for m in members:
        slot_uri = _safe(m, '@odata.id')
        if not slot_uri:
            continue
        code_a, acc_data, err_a = _get(bmc_ip, _p(slot_uri), username, password, timeout, verify_ssl)
        if code_a != 200 or err_a:
            errors.append(_err('account_service', f'GET {slot_uri} 실패', detail=err_a or f'HTTP {code_a}'))
            continue
        accounts.append({
            'slot_uri': slot_uri,
            'id':       _safe(acc_data, 'Id'),
            'username': _safe(acc_data, 'UserName', default=''),
            'role_id':  _safe(acc_data, 'RoleId',   default=''),
            'enabled':  bool(_safe(acc_data, 'Enabled', default=False)),
        })
    return root_data, accounts, errors


def account_service_find_user(accounts, target_username):
    """기존 사용자 slot URI 검색. None 반환 = 미존재."""
    for acc in accounts:
        if (acc.get('username') or '') == target_username:
            return acc
    return None


def account_service_find_empty_slot(accounts):
    """빈 사용자 슬롯 검색 (Dell PATCH 패턴). UserName='' 인 첫 슬롯 반환."""
    for acc in accounts:
        if not (acc.get('username') or ''):
            return acc
    return None


def account_service_provision(
    bmc_ip, vendor, current_username, current_password,
    target_username, target_password, target_role,
    timeout, verify_ssl, dryrun=True,
):
    """공통계정(target) 생성 또는 복구.

    Args:
        bmc_ip:           BMC IP
        vendor:           정규화 vendor (dell/hpe/lenovo/supermicro/cisco) — vendor 분기용
        current_username: recovery 자격 (현재 인증된 사용자)
        current_password: recovery 자격 비밀번호
        target_username:  생성/복구할 공통계정명 (예: 'infraops')
        target_password:  설정할 공통계정 비밀번호
        target_role:      RoleId (예: 'Administrator')
        timeout:          HTTP timeout
        verify_ssl:       BMC 인증서 검증
        dryrun:           True 시 실제 PATCH/POST 호출하지 않고 시뮬레이션 (default ON)

    Returns:
        dict: {
          'recovered': bool,
          'method':    'patch_existing' | 'patch_empty_slot' | 'post_new' | 'noop' | 'not_supported',
          'slot_uri':  '...' or None,
          'dryrun':    bool,
          'errors':    [_err(...), ...],
        }
    """
    out = {
        'recovered': False,
        'method':    'noop',
        'slot_uri':  None,
        'dryrun':    bool(dryrun),
        'errors':    [],
    }

    # 1) AccountService GET
    _, accounts, errs = account_service_get(
        bmc_ip, current_username, current_password, timeout, verify_ssl
    )
    out['errors'].extend(errs)

    # Cisco CIMC 등 표준 미지원 처리
    if vendor == 'cisco':                                                     # nosec rule12-r1
        out['method'] = 'not_supported'
        out['errors'].append(_err(
            'account_service',
            'Cisco CIMC AccountService 표준 미지원 — 운영자 수동 복구 필요',  # nosec rule12-r1
        ))
        return out

    # 2) 기존 사용자 검색
    existing = account_service_find_user(accounts, target_username)

    if existing:
        out['method']   = 'patch_existing'
        out['slot_uri'] = existing.get('slot_uri')
        if dryrun:
            return out
        # 비밀번호 + Enabled + RoleId + Locked 갱신
        # cycle 2026-04-30: 명세 "있는데 사용을 못하면 enable" — Locked: False 명시 추가.
        # disabled (Enabled=False) + locked (consecutive failed login) 둘 다 풀어 사용 가능 상태로.
        body_full = {
            'Password': target_password,
            'Enabled':  True,
            'Locked':   False,
            'RoleId':   target_role,
        }
        code, _, err = _patch(
            bmc_ip, _p(existing['slot_uri']), body_full,
            current_username, current_password, timeout, verify_ssl,
        )
        # 일부 펌웨어가 Locked 필드 PATCH 거부 (read-only) — Locked 빼고 1회 retry
        if code not in (200, 204) and code in (400, 405):
            body_no_locked = {k: v for k, v in body_full.items() if k != 'Locked'}
            code, _, err = _patch(
                bmc_ip, _p(existing['slot_uri']), body_no_locked,
                current_username, current_password, timeout, verify_ssl,
            )
            if code in (200, 204) and not err:
                out['errors'].append(_err(
                    'account_service',
                    'Locked 필드 PATCH 거부 — Locked 빼고 retry 성공 (BMC 펌웨어가 Locked read-only)',
                ))
        if code in (200, 204) and not err:
            out['recovered'] = True
        else:
            out['errors'].append(_err(
                'account_service',
                f'PATCH 기존 사용자 실패 (slot={existing.get("id")})',
                detail=err or f'HTTP {code}',
            ))
        return out

    # 3) 신규 생성 — vendor 분기 (Dell=slot PATCH, 그 외=POST)
    if vendor == 'dell':                                                      # nosec rule12-r1
        empty = account_service_find_empty_slot(accounts)
        if not empty:
            out['errors'].append(_err(
                'account_service', 'Dell iDRAC 빈 슬롯 없음 — 사용자 정리 필요',  # nosec rule12-r1
            ))
            return out
        out['method']   = 'patch_empty_slot'
        out['slot_uri'] = empty.get('slot_uri')
        if dryrun:
            return out
        body = {
            'UserName': target_username,
            'Password': target_password,
            'Enabled':  True,
            'RoleId':   target_role,
        }
        code, _, err = _patch(
            bmc_ip, _p(empty['slot_uri']), body,
            current_username, current_password, timeout, verify_ssl,
        )
        if code in (200, 204) and not err:
            out['recovered'] = True
        else:
            out['errors'].append(_err(
                'account_service',
                f'Dell PATCH 빈 슬롯 실패 (slot={empty.get("id")})',  # nosec rule12-r1
                detail=err or f'HTTP {code}',
            ))
        return out

    # HPE / Lenovo / Supermicro: POST 표준
    out['method'] = 'post_new'
    if dryrun:
        return out
    body = {
        'UserName': target_username,
        'Password': target_password,
        'Enabled':  True,
        'RoleId':   target_role,
    }
    code, resp_data, err = _post(
        bmc_ip, 'AccountService/Accounts', body,
        current_username, current_password, timeout, verify_ssl,
    )
    if code in (200, 201, 204) and not err:
        out['recovered'] = True
        out['slot_uri']  = _safe(resp_data, '@odata.id')
    else:
        out['errors'].append(_err(
            'account_service',
            'POST /AccountService/Accounts 실패',
            detail=err or f'HTTP {code}',
        ))
    return out


def main():
    module = AnsibleModule(
        argument_spec=dict(
            bmc_ip          = dict(type='str',  required=True),
            username        = dict(type='str',  required=True),
            password        = dict(type='str',  required=True, no_log=True),
            timeout         = dict(type='int',  default=30),
            verify_ssl      = dict(type='bool', default=False),
            # P2 (cycle 2026-04-28): AccountService 통합
            mode            = dict(type='str',  default='gather',
                                   choices=['gather', 'account_provision']),
            target_username = dict(type='str',  default=''),
            target_password = dict(type='str',  default='', no_log=True),
            target_role     = dict(type='str',  default='Administrator'),
            dryrun          = dict(type='bool', default=True),
        ),
        supports_check_mode=True,
    )

    if not HAS_URLLIB:
        module.fail_json(msg='Python urllib 를 import 할 수 없습니다')

    p = module.params
    bmc_ip, username, password = p['bmc_ip'], p['username'], p['password']
    timeout, verify_ssl = p['timeout'], p['verify_ssl']
    mode = p['mode']

    # ── P2: AccountService provision mode ────────────────────────────────
    if mode == 'account_provision':
        target_username = p['target_username']
        target_password = p['target_password']
        target_role     = p['target_role']
        dryrun          = p['dryrun']

        if not target_username or not target_password:
            module.fail_json(
                msg='mode=account_provision 시 target_username/target_password 필수'
            )

        # detect_vendor 로 vendor 정규화 (분기 라우팅 용도)
        vendor, _, _, _, det_errors = detect_vendor(
            bmc_ip, username, password, timeout, verify_ssl
        )
        result = account_service_provision(
            bmc_ip, vendor, username, password,
            target_username, target_password, target_role,
            timeout, verify_ssl, dryrun=dryrun,
        )
        result['errors'] = list(det_errors) + (result.get('errors') or [])
        module.exit_json(
            changed=bool(result.get('recovered')),
            mode='account_provision',
            vendor=vendor,
            account_service=result,
        )
        return

    # ── 기존 gather mode (cycle 2026-05-01: unsupported 분류 추가) ──────
    all_errors, collected, failed, unsupported = [], [], [], []

    vendor, system_uri, manager_uri, chassis_uri, det_errors = detect_vendor(
        bmc_ip, username, password, timeout, verify_ssl
    )
    all_errors.extend(det_errors)

    if not system_uri:
        module.exit_json(
            changed=False, status='failed', vendor=vendor,
            collected=[], failed_sections=['all'], unsupported_sections=[],
            errors=all_errors, data={},
        )

    result_data = _collect_all_sections(
        bmc_ip, vendor, system_uri, manager_uri, chassis_uri,
        username, password, timeout, verify_ssl,
        all_errors, collected, failed, unsupported,
    )

    final_status, clean = _compute_final_status(collected, failed, all_errors)

    module.exit_json(
        changed=False, status=final_status, vendor=vendor,
        collected=clean, failed_sections=list(set(failed)),
        unsupported_sections=list(set(unsupported)),
        errors=all_errors, data=result_data,
    )


if __name__ == '__main__':
    main()
