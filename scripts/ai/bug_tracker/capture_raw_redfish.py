#!/usr/bin/env python3
"""Capture raw Redfish responses for bug verification.

Runs on Jenkins agent. Pulls vault credentials via ansible-vault and queries
each lab BMC for the endpoints needed by tickets B01..B99.

Outputs each raw response to:
    /tmp/se-raw/<ip>/<sanitized_path>.json
plus a top-level summary.json.

Usage (on agent):
    python3 capture_raw_redfish.py [--ip IP[,IP...]]

Stdlib-only (urllib/ssl/json) — same constraint as redfish_gather.py (rule 10).
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from base64 import b64encode
from pathlib import Path

WORKSPACE = Path("/home/cloviradmin/jenkins-agent/workspace/hshwang-gather")
VAULT_PASS = "/tmp/.vault_pass_se"
OUT_ROOT = Path("/tmp/se-raw")

# (label, ip, vault_file)
TARGETS = [
    ("dell-r760-1", "10.100.15.27", "vault/redfish/dell.yml"),
    ("dell-r760-2", "10.100.15.28", "vault/redfish/dell.yml"),
    ("dell-r760-3", "10.100.15.31", "vault/redfish/dell.yml"),
    ("dell-r760-5", "10.100.15.33", "vault/redfish/dell.yml"),
    ("dell-r760-6", "10.100.15.34", "vault/redfish/dell.yml"),
    ("dell-r740",   "10.50.11.162", "vault/redfish/dell.yml"),
    ("hpe-dl380",   "10.50.11.231", "vault/redfish/hpe.yml"),
    ("lenovo-sr650","10.50.11.232", "vault/redfish/lenovo.yml"),
    ("cisco-c220",  "10.100.15.2",  "vault/redfish/cisco.yml"),
]

# Endpoints to capture per ticket — descriptive labels include ticket refs.
ENDPOINTS = [
    # Identity
    ("/redfish/v1/", "service_root"),
    # CPU related (B01 ProcessorType)
    ("/redfish/v1/Systems", "systems_collection"),
    ("/redfish/v1/Systems/{system_id}", "system"),
    ("/redfish/v1/Systems/{system_id}/Processors", "processors_collection"),
    # Memory (B09 locator, B23 mfg, B72 speed)
    ("/redfish/v1/Systems/{system_id}/Memory", "memory_collection"),
    # Network (B02 DNS, B13 link_status, B14 name, B57 iface vs adapter, B70/B92/B93)
    ("/redfish/v1/Systems/{system_id}/EthernetInterfaces", "ethernet_interfaces_collection"),
    ("/redfish/v1/Systems/{system_id}/NetworkInterfaces", "network_interfaces_collection"),
    ("/redfish/v1/Chassis", "chassis_collection"),
    # Power (B41/B45 PSU count, B46 PowerControl, B58/B59 Critical)
    ("/redfish/v1/Chassis/{chassis_id}/Power", "power"),
    # Storage (B10 disk capacity, B48/B49 volume name/boot, B52 grand_total)
    ("/redfish/v1/Systems/{system_id}/Storage", "storage_collection"),
    # BMC (B08 product/mac/hostname)
    ("/redfish/v1/Managers", "managers_collection"),
    # Firmware (B12/B43)
    ("/redfish/v1/UpdateService/FirmwareInventory", "firmware_inventory"),
    # Users (B15)
    ("/redfish/v1/AccountService", "account_service"),
    ("/redfish/v1/AccountService/Accounts", "account_accounts"),
]


def decrypt_vault(vault_path: Path) -> dict:
    """Run ansible-vault view and parse YAML via PyYAML (installed in agent env)."""
    cmd = [
        "/opt/ansible-env/bin/ansible-vault",
        "view",
        "--vault-password-file",
        VAULT_PASS,
        str(vault_path),
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.PIPE, timeout=10).decode()
    try:
        import yaml  # type: ignore
        return yaml.safe_load(out) or {}
    except ImportError:
        # Fallback: flat key:value lines (won't catch list of dicts)
        result: dict = {}
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, _, v = line.partition(":")
                v = v.strip()
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                elif v.startswith("'") and v.endswith("'"):
                    v = v[1:-1]
                result[k.strip()] = v
        return result


def pick_credentials(creds: dict) -> list[tuple[str, str, str]]:
    """Extract list of (user, password, label) from vault dict, ordered by priority.

    Priority:
      1. accounts[*] list (vault P1 schema) — primary first, then secondary, then recovery
      2. ansible_user / ansible_password (backward-compat) as final fallback
    """
    out: list[tuple[str, str, str]] = []
    accounts = creds.get("accounts") if isinstance(creds, dict) else None
    if isinstance(accounts, list):
        # Order: primary -> secondary -> recovery (preserve original list order within same role)
        priority = {"primary": 0, "secondary": 1, "recovery": 2}
        ordered = sorted(
            (a for a in accounts if isinstance(a, dict) and a.get("username") and a.get("password")),
            key=lambda a: priority.get(a.get("role", "recovery"), 9),
        )
        for a in ordered:
            out.append((a.get("username"), a.get("password"), a.get("label") or a.get("role") or "anon"))
    if isinstance(creds, dict):
        u = creds.get("ansible_user") or creds.get("redfish_user") or creds.get("redfish_username") or creds.get("username")
        p = creds.get("ansible_password") or creds.get("redfish_password") or creds.get("password")
        if u and p and not any(c[0] == u and c[1] == p for c in out):
            out.append((u, p, "ansible_user"))
    return out


def find_working_credential(ip: str, candidates: list[tuple[str, str, str]]) -> tuple[str | None, str | None, str | None]:
    """Try Systems endpoint (auth-required) with each candidate, with backoff between
    attempts to avoid BMC rate-limiting. Returns first that returns 200."""
    for idx, (user, pwd, label) in enumerate(candidates):
        if idx > 0:
            time.sleep(5)  # Spacer between attempts to avoid lock-out
        status, obj, _ = http_get(ip, "/redfish/v1/Systems", user, pwd, timeout=12)
        if status == 200 and obj is not None:
            return user, pwd, label
        if status == 401:
            continue  # Wrong password — keep trying
        if status == -1:
            time.sleep(20)  # Likely throttled — pause longer
    return None, None, None


def http_get(ip: str, path: str, user: str, pwd: str, timeout: int = 12) -> tuple[int, dict | None, str]:
    url = f"https://{ip}{path}"
    auth = b64encode(f"{user}:{pwd}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}", "Accept": "application/json"})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body), ""
            except json.JSONDecodeError:
                return resp.status, None, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return e.code, None, body
    except Exception as e:
        return -1, None, str(e)


def resolve_id(coll: dict, key: str) -> str | None:
    members = (coll or {}).get("Members") or []
    if not members:
        return None
    first = members[0].get("@odata.id") or ""
    return first.rsplit("/", 1)[-1] if first else None


def capture_target(label: str, ip: str, vault_file: str, out_root: Path) -> dict:
    out_dir = out_root / label
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"label": label, "ip": ip, "endpoints": {}, "errors": []}

    try:
        creds = decrypt_vault(WORKSPACE / vault_file)
    except Exception as e:
        summary["errors"].append({"step": "vault", "error": str(e)})
        return summary

    candidates = pick_credentials(creds)
    if not candidates:
        summary["errors"].append({"step": "vault_keys", "keys": list(creds.keys()) if isinstance(creds, dict) else "non-dict"})
        return summary
    summary["candidates_tried"] = [c[2] for c in candidates]

    user, pwd, label = find_working_credential(ip, candidates)
    if not user or not pwd:
        summary["errors"].append({"step": "auth", "tried": [c[2] for c in candidates]})
        return summary

    summary["auth_user"] = user
    summary["auth_label"] = label
    system_id = None
    chassis_id = None

    for raw_path, slug in ENDPOINTS:
        path = raw_path
        # Resolve placeholders
        if "{system_id}" in path:
            if not system_id:
                continue
            path = path.replace("{system_id}", system_id)
        if "{chassis_id}" in path:
            if not chassis_id:
                continue
            path = path.replace("{chassis_id}", chassis_id)

        status, obj, body = http_get(ip, path, user, pwd)
        record = {"path": path, "status": status}
        out_file = out_dir / f"{slug}.json"
        if obj is not None:
            out_file.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
            record["saved"] = str(out_file)
            record["bytes"] = out_file.stat().st_size
            # Resolve IDs from collections
            if slug == "systems_collection" and not system_id:
                system_id = resolve_id(obj, "system")
                record["resolved_system_id"] = system_id
            elif slug == "chassis_collection" and not chassis_id:
                chassis_id = resolve_id(obj, "chassis")
                record["resolved_chassis_id"] = chassis_id
        else:
            (out_dir / f"{slug}.error.txt").write_text(body, encoding="utf-8")
            record["error_body_bytes"] = len(body or "")
        summary["endpoints"][slug] = record

    # Now drill into per-member endpoints
    if system_id:
        # Memory members
        mem_coll_path = out_dir / "memory_collection.json"
        if mem_coll_path.exists():
            mem_coll = json.loads(mem_coll_path.read_text(encoding="utf-8"))
            mem_dir = out_dir / "memory_members"
            mem_dir.mkdir(exist_ok=True)
            for mem_id_obj in (mem_coll.get("Members") or [])[:8]:
                mem_uri = mem_id_obj.get("@odata.id")
                if not mem_uri:
                    continue
                mid = mem_uri.rsplit("/", 1)[-1]
                status, obj, body = http_get(ip, mem_uri, user, pwd)
                if obj is not None:
                    (mem_dir / f"{mid}.json").write_text(
                        json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8"
                    )

        # Processor members (CPU + GPU mix detection)
        proc_coll_path = out_dir / "processors_collection.json"
        if proc_coll_path.exists():
            proc_coll = json.loads(proc_coll_path.read_text(encoding="utf-8"))
            proc_dir = out_dir / "processors_members"
            proc_dir.mkdir(exist_ok=True)
            for p in (proc_coll.get("Members") or [])[:8]:
                uri = p.get("@odata.id")
                if not uri:
                    continue
                pid = uri.rsplit("/", 1)[-1]
                status, obj, body = http_get(ip, uri, user, pwd)
                if obj is not None:
                    (proc_dir / f"{pid}.json").write_text(
                        json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8"
                    )

        # Ethernet members
        eth_coll_path = out_dir / "ethernet_interfaces_collection.json"
        if eth_coll_path.exists():
            eth_coll = json.loads(eth_coll_path.read_text(encoding="utf-8"))
            eth_dir = out_dir / "ethernet_members"
            eth_dir.mkdir(exist_ok=True)
            for it in (eth_coll.get("Members") or [])[:8]:
                uri = it.get("@odata.id")
                if not uri:
                    continue
                eid = uri.rsplit("/", 1)[-1]
                status, obj, body = http_get(ip, uri, user, pwd)
                if obj is not None:
                    (eth_dir / f"{eid}.json").write_text(
                        json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8"
                    )

        # Storage detail (drives + volumes)
        stg_coll_path = out_dir / "storage_collection.json"
        if stg_coll_path.exists():
            stg_coll = json.loads(stg_coll_path.read_text(encoding="utf-8"))
            stg_dir = out_dir / "storage_members"
            stg_dir.mkdir(exist_ok=True)
            for s in (stg_coll.get("Members") or [])[:6]:
                uri = s.get("@odata.id")
                if not uri:
                    continue
                sid = uri.rsplit("/", 1)[-1]
                status, obj, body = http_get(ip, uri, user, pwd)
                if obj is not None:
                    (stg_dir / f"{sid}.json").write_text(
                        json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8"
                    )
                    # Drive detail
                    for d in (obj.get("Drives") or [])[:8]:
                        duri = d.get("@odata.id")
                        if not duri:
                            continue
                        did = duri.rsplit("/", 1)[-1]
                        ds, dobj, _ = http_get(ip, duri, user, pwd)
                        if dobj is not None:
                            (stg_dir / f"{sid}__drive_{did}.json").write_text(
                                json.dumps(dobj, indent=2, ensure_ascii=False), encoding="utf-8"
                            )
                    # Volumes collection link
                    vols_link = obj.get("Volumes", {}).get("@odata.id") if isinstance(obj.get("Volumes"), dict) else None
                    if vols_link:
                        vs, vobj, _ = http_get(ip, vols_link, user, pwd)
                        if vobj is not None:
                            (stg_dir / f"{sid}__volumes_collection.json").write_text(
                                json.dumps(vobj, indent=2, ensure_ascii=False), encoding="utf-8"
                            )
                            for v in (vobj.get("Members") or [])[:8]:
                                vuri = v.get("@odata.id")
                                if not vuri:
                                    continue
                                vid = vuri.rsplit("/", 1)[-1]
                                vs2, vobj2, _ = http_get(ip, vuri, user, pwd)
                                if vobj2 is not None:
                                    (stg_dir / f"{sid}__volume_{vid}.json").write_text(
                                        json.dumps(vobj2, indent=2, ensure_ascii=False), encoding="utf-8"
                                    )

    # Manager members
    mgr_coll_path = out_dir / "managers_collection.json"
    if mgr_coll_path.exists():
        mgr_coll = json.loads(mgr_coll_path.read_text(encoding="utf-8"))
        mgr_dir = out_dir / "managers_members"
        mgr_dir.mkdir(exist_ok=True)
        for m in (mgr_coll.get("Members") or [])[:4]:
            uri = m.get("@odata.id")
            if not uri:
                continue
            mid = uri.rsplit("/", 1)[-1]
            status, obj, body = http_get(ip, uri, user, pwd)
            if obj is not None:
                (mgr_dir / f"{mid}.json").write_text(
                    json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                # Manager EthernetInterfaces (BMC NIC + DNS)
                eth_link = obj.get("EthernetInterfaces", {}).get("@odata.id") if isinstance(obj.get("EthernetInterfaces"), dict) else None
                if eth_link:
                    es, eobj, _ = http_get(ip, eth_link, user, pwd)
                    if eobj is not None:
                        (mgr_dir / f"{mid}__eth_collection.json").write_text(
                            json.dumps(eobj, indent=2, ensure_ascii=False), encoding="utf-8"
                        )
                        for e in (eobj.get("Members") or [])[:4]:
                            euri = e.get("@odata.id")
                            if not euri:
                                continue
                            eid = euri.rsplit("/", 1)[-1]
                            es2, eobj2, _ = http_get(ip, euri, user, pwd)
                            if eobj2 is not None:
                                (mgr_dir / f"{mid}__eth_{eid}.json").write_text(
                                    json.dumps(eobj2, indent=2, ensure_ascii=False), encoding="utf-8"
                                )
                # NetworkProtocol (DNS settings)
                np_link = obj.get("NetworkProtocol", {}).get("@odata.id") if isinstance(obj.get("NetworkProtocol"), dict) else None
                if np_link:
                    ns, nobj, _ = http_get(ip, np_link, user, pwd)
                    if nobj is not None:
                        (mgr_dir / f"{mid}__network_protocol.json").write_text(
                            json.dumps(nobj, indent=2, ensure_ascii=False), encoding="utf-8"
                        )

    # Chassis detail (PSU / NetworkAdapters)
    if chassis_id:
        cha_dir = out_dir / "chassis_members"
        cha_dir.mkdir(exist_ok=True)
        # NetworkAdapters
        na_path = f"/redfish/v1/Chassis/{chassis_id}/NetworkAdapters"
        s, obj, _ = http_get(ip, na_path, user, pwd)
        if obj is not None:
            (cha_dir / "network_adapters_collection.json").write_text(
                json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            for n in (obj.get("Members") or [])[:6]:
                uri = n.get("@odata.id")
                if not uri:
                    continue
                nid = uri.rsplit("/", 1)[-1]
                s2, nobj, _ = http_get(ip, uri, user, pwd)
                if nobj is not None:
                    (cha_dir / f"net_adapter_{nid}.json").write_text(
                        json.dumps(nobj, indent=2, ensure_ascii=False), encoding="utf-8"
                    )
                    # Ports
                    ports_link = nobj.get("Ports", {}).get("@odata.id") if isinstance(nobj.get("Ports"), dict) else None
                    if ports_link:
                        ps, pobj, _ = http_get(ip, ports_link, user, pwd)
                        if pobj is not None:
                            (cha_dir / f"net_adapter_{nid}__ports_collection.json").write_text(
                                json.dumps(pobj, indent=2, ensure_ascii=False), encoding="utf-8"
                            )

    return summary


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ip", help="filter to single IP or comma list")
    p.add_argument("--out", default=str(OUT_ROOT))
    args = p.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    targets = TARGETS
    if args.ip:
        ips = set(args.ip.split(","))
        targets = [t for t in TARGETS if t[1] in ips]

    overall = {"started": time.time(), "targets": []}
    for label, ip, vault in targets:
        print(f"[capture] {label} {ip} ...", flush=True)
        s = capture_target(label, ip, vault, out_root)
        overall["targets"].append(s)
        print(f"  done: endpoints={len(s.get('endpoints',{}))} errors={len(s.get('errors',[]))}")

    overall["finished"] = time.time()
    summary_path = out_root / "summary.json"
    summary_path.write_text(json.dumps(overall, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsummary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
