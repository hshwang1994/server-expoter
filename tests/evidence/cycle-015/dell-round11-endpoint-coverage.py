"""cycle-015 AI-12 — Dell × 5 Round 11 endpoint coverage probe.

redfish_gather.py가 사용하는 핵심 endpoint를 Dell × 5에 직접 호출하여 응답 가능성 검증.
baseline_v1/dell_baseline.json 갱신 시 어떤 섹션을 채울 수 있는지 확인.

stdlib only (rule 10 R2 정신).
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

ENDPOINTS = [
    ("ServiceRoot", "/redfish/v1/", False),
    ("Systems_index", "/redfish/v1/Systems", True),
    ("Chassis_index", "/redfish/v1/Chassis", True),
    ("Managers_index", "/redfish/v1/Managers", True),
    ("UpdateService", "/redfish/v1/UpdateService", True),
    ("UpdateService_FW", "/redfish/v1/UpdateService/FirmwareInventory", True),
    ("AccountService", "/redfish/v1/AccountService", True),
    ("AccountService_Accounts", "/redfish/v1/AccountService/Accounts", True),
    ("EventService", "/redfish/v1/EventService", True),
    ("SessionService", "/redfish/v1/SessionService", True),
]


def fetch(url: str, auth: tuple[str, str] | None = None, timeout: int = 8):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    if auth:
        token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return -1, None


def probe(bmc: dict) -> dict:
    ip = bmc["bmc_ip"]
    auth = (bmc["username"], bmc["password"])
    result = {"ip": ip, "endpoints": {}, "deep": {}}

    # 기본 endpoint 매트릭스
    for name, path, need_auth in ENDPOINTS:
        code, body = fetch(f"https://{ip}{path}", auth if need_auth else None)
        result["endpoints"][name] = code
        if name == "Systems_index" and code == 200 and body:
            members = body.get("Members", [])
            result["deep"]["systems_count"] = len(members)
            if members:
                # 첫 system 진입
                sys_path = members[0]["@odata.id"]
                code2, body2 = fetch(f"https://{ip}{sys_path}", auth)
                if code2 == 200 and body2:
                    result["deep"]["model"] = body2.get("Model")
                    result["deep"]["serial"] = body2.get("SerialNumber")
                    result["deep"]["bios"] = body2.get("BiosVersion")
                    result["deep"]["mem_gb"] = (body2.get("MemorySummary") or {}).get(
                        "TotalSystemMemoryGiB"
                    )
                    cpu = body2.get("ProcessorSummary") or {}
                    result["deep"]["cpu_count"] = cpu.get("Count")
                    result["deep"]["cpu_model"] = cpu.get("Model")
                    storage = (body2.get("Storage") or {}).get("@odata.id")
                    if storage:
                        code3, body3 = fetch(f"https://{ip}{storage}", auth)
                        if code3 == 200 and body3:
                            result["deep"]["storage_controllers"] = len(
                                body3.get("Members", [])
                            )
                    eth = (body2.get("EthernetInterfaces") or {}).get("@odata.id")
                    if eth:
                        code4, body4 = fetch(f"https://{ip}{eth}", auth)
                        if code4 == 200 and body4:
                            result["deep"]["nic_count"] = len(
                                body4.get("Members", [])
                            )
        elif name == "UpdateService_FW" and code == 200 and body:
            result["deep"]["fw_inventory_count"] = len(body.get("Members", []))
        elif name == "AccountService_Accounts" and code == 200 and body:
            result["deep"]["accounts_count"] = len(body.get("Members", []))

    return result


def main() -> int:
    creds = yaml.safe_load(LAB_CREDS.read_text(encoding="utf-8"))
    dells = creds.get("redfish_targets", {}).get("dell", [])
    print(f"=== Dell × {len(dells)} Round 11 endpoint coverage ===\n")

    results = []
    for bmc in dells:
        r = probe(bmc)
        results.append(r)
        d = r["deep"]
        e = r["endpoints"]
        print(f"[{r['ip']}] Model={d.get('model', '?')[:25]} Serial={d.get('serial', '?')[:15]}")
        print(f"   BIOS={d.get('bios', '?')[:15]}  CPU={d.get('cpu_count', '?')}× '{(d.get('cpu_model') or '')[:35]}'")
        print(f"   Mem={d.get('mem_gb', '?')}GB  NIC={d.get('nic_count', '?')}  Storage_ctrl={d.get('storage_controllers', '?')}  FW_inv={d.get('fw_inventory_count', '?')}  Accts={d.get('accounts_count', '?')}")
        ep_summary = " ".join(f"{k}={v}" for k, v in e.items() if v != 200)
        if ep_summary:
            print(f"   non-200: {ep_summary}")
        print()

    out = Path(__file__).parent / "dell-round11-endpoint-coverage.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"결과: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
