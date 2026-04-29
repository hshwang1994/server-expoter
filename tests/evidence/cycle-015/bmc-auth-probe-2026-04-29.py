"""cycle-015 BMC primary auth + endpoint probe (Windows 직접 stdlib).

OPS-3 (vault sync) 검증 + AI-12 (Dell × 5 Round 11) + OPS-11 (Cisco 1, 3 재확인).
lab credentials의 BMC password가 실 BMC와 일치하는지 검증.

stdlib only (urllib + ssl + json) — rule 10 R2 정신.
"""
from __future__ import annotations

import base64
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

LAB_CREDS = Path(__file__).resolve().parents[3] / "vault" / ".lab-credentials.yml"


def load_creds() -> dict:
    with open(LAB_CREDS, encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch(
    url: str, username: str | None = None, password: str | None = None, timeout: int = 8
) -> tuple[int, dict | None, str | None]:
    """Returns (status_code, json_body or None, error_message or None)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    if username and password:
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(body), None
            except json.JSONDecodeError:
                return r.status, None, body[:200]
    except urllib.error.HTTPError as e:
        return e.code, None, e.reason
    except Exception as e:
        return -1, None, f"{type(e).__name__}: {e}"


def probe_bmc(bmc: dict) -> dict:
    ip = bmc["bmc_ip"]
    user = bmc["username"]
    pwd = bmc["password"]
    result: dict = {"ip": ip, "vendor": bmc["vendor"], "user": user}

    # 1. ServiceRoot (no auth)
    code, body, err = fetch(f"https://{ip}/redfish/v1/")
    result["serviceroot"] = code
    if body:
        result["product"] = body.get("Product")
        result["redfish_version"] = body.get("RedfishVersion")
    elif err:
        result["error_serviceroot"] = err

    # 2. Authenticated /Systems
    code2, body2, err2 = fetch(f"https://{ip}/redfish/v1/Systems", user, pwd)
    result["systems_auth"] = code2
    if code2 == 200 and body2:
        result["systems_count"] = len(body2.get("Members", []))
    elif err2:
        result["error_systems"] = err2

    # 3. Authenticated /Managers
    code3, body3, err3 = fetch(f"https://{ip}/redfish/v1/Managers", user, pwd)
    result["managers_auth"] = code3

    return result


def main() -> int:
    creds = load_creds()
    rf = creds.get("redfish_targets", {})
    rows = []
    for vendor in ("dell", "hpe", "lenovo", "cisco"):
        for bmc in rf.get(vendor, []):
            rows.append(probe_bmc(bmc))

    print(f"=== BMC auth probe ({len(rows)} hosts) ===\n")
    print(
        f"{'IP':<16} {'Vendor':<10} {'SR':>4} {'Auth':>5} {'Mgr':>4} {'Product':<48} {'Note':<30}"
    )
    print("-" * 120)
    for r in rows:
        product = (r.get("product") or "")[:46]
        note_parts = []
        if r.get("error_serviceroot"):
            note_parts.append(f"SR_err={r['error_serviceroot'][:20]}")
        if r.get("systems_auth") == 200:
            note_parts.append(f"systems={r.get('systems_count', '?')}")
        elif r.get("error_systems"):
            note_parts.append(f"sys_err={r['error_systems'][:20]}")
        print(
            f"{r['ip']:<16} {r['vendor']:<10} {r['serviceroot']:>4} "
            f"{r.get('systems_auth', '?'):>5} {r.get('managers_auth', '?'):>4} "
            f"{product:<48} {' '.join(note_parts):<30}"
        )

    out = Path(__file__).parent / "bmc-auth-probe-2026-04-29.json"
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n결과: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
