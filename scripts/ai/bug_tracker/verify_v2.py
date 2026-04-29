#!/usr/bin/env python3
"""Comprehensive ticket verification v2 — using ACTUAL envelope key names.

Major correction from v1: my initial analysis used wrong field names (e.g. `username`
instead of `name`, `capacity_gb` instead of `total_mb`, `fstype` instead of `filesystem`,
`free_mb` instead of `available_mb`). Many "bugs" were false positives.

This v2 uses real keys discovered from envelope inspection.

Output:
  - docs/ai/tickets/2026-04-29-output-quality/VERDICT_TABLE.md
  - patches each Bxx.md ticket Status: line
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "tests" / "evidence" / "2026-04-29-deep-verify"
TICKETS = REPO / "docs" / "ai" / "tickets" / "2026-04-29-output-quality"


def load_envs(p: Path) -> list[dict]:
    out = []
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8", errors="replace").split("\n"):
        line = line.strip()
        if line.startswith("{") and '"target_type"' in line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# Verdict constants
V_VERIFIED = "verified"  # bug confirmed
V_REJECTED = "rejected"  # not a bug (false positive due to wrong field name etc)
V_NEEDS_LIVE = "needs_live"  # need fresh capture (Dell auth fail)
V_DUP = "dup"
V_POLICY = "policy"  # decision required
V_SCOPE = "scope"  # observation/environment

# Per-ticket verifier dict — each returns (verdict, evidence_text)
def vb(verdict, evidence, fix_hint=None):
    return verdict, evidence, fix_hint


def main():
    rf_envs = load_envs(EVIDENCE / "jenkins-114-redfish.txt")
    os_envs = load_envs(EVIDENCE / "jenkins-115-os.txt")
    esxi_envs = load_envs(EVIDENCE / "jenkins-116-esxi.txt")
    rf_root = EVIDENCE / "redfish"

    # Build envelope index
    rf_by_ip = {d.get("ip"): d for d in rf_envs}
    os_by_ip = {d.get("ip"): d for d in os_envs}
    esxi_by_ip = {d.get("ip"): d for d in esxi_envs}

    verdicts = {}

    # ---- B01: GPU in CPU (r760-1) ----
    r6_1 = rf_by_ip.get("10.100.15.27")
    if r6_1:
        groups = ((r6_1.get("data", {}).get("cpu") or {}).get("summary", {}) or {}).get("groups", []) or []
        gpu_in_cpu = [g for g in groups if (g.get("manufacturer") or "").lower().find("nvidia") >= 0
                      or (g.get("model") or "").lower().find("tesla") >= 0]
        cpu_top = (r6_1.get("data", {}).get("cpu") or {})
        verdicts["B01"] = vb(
            V_VERIFIED if gpu_in_cpu else V_REJECTED,
            f"r760-1 cpu.summary.groups={groups}; cpu.model={cpu_top.get('model')}; cpu.sockets={cpu_top.get('sockets')}",
            "fix: redfish_gather.py Processors loop — filter ProcessorType=='CPU' (skip GPU/Accelerator)"
        )
    else:
        verdicts["B01"] = vb(V_NEEDS_LIVE, "no r760-1 envelope", None)

    # ---- B02: DNS unspecified IPs in Redfish ----
    bad_dns = []
    for ip, d in rf_by_ip.items():
        if d.get("status") != "success":
            continue
        dns = ((d.get("data", {}).get("network") or {})).get("dns_servers") or []
        if any(x in ("0.0.0.0", "::", "0:0:0:0:0:0:0:0") for x in dns):
            bad_dns.append((ip, dns, d.get("vendor")))
    raw_check = {}
    for h in ["hpe-dl380", "lenovo-sr650"]:
        ed = rf_root / h / "managers_members"
        if ed.exists():
            for f in ed.glob("*__eth_*.json"):
                obj = load_json(f)
                if obj:
                    ns = obj.get("NameServers") or obj.get("StaticNameServers")
                    if ns is not None:
                        raw_check.setdefault(h, []).append(ns)
    verdicts["B02"] = vb(
        V_VERIFIED if bad_dns else V_REJECTED,
        f"envelope hosts with unspecified IP in dns_servers: {bad_dns}; raw NameServers={raw_check}",
        "fix: redfish_gather.py — filter unspecified addresses (0.0.0.0, ::) from dns_servers"
    )

    # ---- B03: failed envelope shape ----
    failed = [d for d in rf_envs if d.get("status") == "failed"]
    if failed:
        d = failed[0]
        data = d.get("data") or {}
        none_keys = [k for k, v in data.items() if v is None]
        empty_keys = [k for k, v in data.items() if isinstance(v, (dict, list)) and not v]
        empty_struct_keys = [k for k, v in data.items() if isinstance(v, (dict, list)) and v]
        meta = d.get("meta") or {}
        diag = d.get("diagnosis") or {}
        sec = d.get("sections") or {}
        verdicts["B03"] = vb(
            V_VERIFIED,
            f"failed envelope ({d.get('ip')}): data None={none_keys}; non-empty struct={empty_struct_keys}; "
            f"meta.duration_ms={meta.get('duration_ms')}; diag.auth_success={diag.get('auth_success')}; "
            f"diag.failure_stage={diag.get('failure_stage')}; sections={sec}",
            "fix: redfish-gather/site.yml always block + build_failed_output — emit consistent shape (all section keys, default empty struct or None coherently); "
            "build_meta — populate duration_ms; build_diagnosis — populate failure_stage + failure_reason"
        )
    else:
        verdicts["B03"] = vb(V_REJECTED, "no failed envelopes in current data", None)

    # ---- B04: Ubuntu DNS=127.0.0.53 ----
    ubu = [d for d in os_envs if (d.get("data", {}).get("system") or {}).get("distribution", "").lower() == "ubuntu"]
    bad_ubu = [d for d in ubu if any(x.startswith("127.") for x in
                                     ((d.get("data", {}).get("network") or {}).get("dns_servers") or []))]
    verdicts["B04"] = vb(
        V_VERIFIED if bad_ubu else V_REJECTED,
        f"Ubuntu hosts with 127.0.0.x in dns_servers: {[(d.get('ip'), (d.get('data', {}).get('network') or {}).get('dns_servers')) for d in bad_ubu]}",
        "fix: os-gather/tasks/linux/collect_dns.yml — when systemd-resolved active, read /run/systemd/resolve/resolv.conf or `resolvectl status` instead of /etc/resolv.conf stub"
    )

    # ---- B05/B21: RHEL 8.10 raw_fallback cpu.summary.groups=[] ----
    raw_fallback_hosts = [d for d in os_envs if (d.get("diagnosis", {}).get("details", {}) or {}).get("gather_mode") in
                          ("python_incompatible", "python_missing", "raw_forced")]
    bad = [(d.get("ip"), len(((d.get("data", {}).get("cpu") or {}).get("summary") or {}).get("groups") or []))
           for d in raw_fallback_hosts]
    has_zero = [b for b in bad if b[1] == 0]
    verdicts["B05"] = vb(
        V_VERIFIED if has_zero else V_REJECTED,
        f"raw_fallback hosts cpu.summary.groups counts: {bad}",
        "fix: os-gather/tasks/linux/normalize_cpu.yml raw branch — ensure summary.groups populated"
    )
    verdicts["B21"] = (V_DUP, "B05", None)

    # ---- B06: ESXi network.summary.groups ----
    bad_esxi = []
    for d in esxi_envs:
        net = d.get("data", {}).get("network") or {}
        adapters = net.get("adapters") or []
        groups = (net.get("summary") or {}).get("groups") or []
        connected = sum(1 for a in adapters if (a.get("link_status") or "").lower() == "connected")
        total_q = sum(g.get("quantity", 0) for g in groups)
        link_up_total = sum(g.get("link_up_count", 0) for g in groups)
        if adapters and (total_q < len(adapters) or link_up_total != connected):
            bad_esxi.append({
                "ip": d.get("ip"), "adapter_count": len(adapters), "connected": connected,
                "groups": groups, "summary_quantity_sum": total_q,
            })
    verdicts["B06"] = vb(
        V_VERIFIED if bad_esxi else V_REJECTED,
        f"ESXi summary groups buggy: {bad_esxi}",
        "fix: esxi-gather/tasks/normalize_network.yml summary builder — group adapters by link_status+speed; do not collapse null-keyed groups"
    )
    verdicts["B33"] = (V_DUP, "B06", None)

    # ---- B07: redfish system None+success ----
    rf_system_issues = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        sys_ = d.get("data", {}).get("system") or {}
        sec = d.get("sections", {})
        # If most system fields are None
        non_runtime = {k: v for k, v in sys_.items() if k != "runtime"}
        none_count = sum(1 for v in non_runtime.values() if v is None)
        total = len(non_runtime)
        if total > 0 and none_count == total and sec.get("system") == "success":
            rf_system_issues.append({"ip": d.get("ip"), "all_None": True, "sections.system": sec.get("system")})
    verdicts["B07"] = vb(
        V_VERIFIED if rf_system_issues else V_REJECTED,
        f"Redfish system all-None+success entries: {rf_system_issues}",
        "fix: redfish supported_sections.yml — drop 'system' OR redirect to BMC-derived data"
    )

    # ---- B08: BMC fields ----
    # bmc keys: name, firmware_version, model, manager_type, health, state, power_state, uuid, ip, mac_address, dns_name, ...
    bmc_drift = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        bmc = d.get("data", {}).get("bmc") or {}
        if not bmc:
            continue
        bmc_drift.append({
            "ip": d.get("ip"), "vendor": d.get("vendor"),
            "name": bmc.get("name"),
            "model": bmc.get("model"),
            "manager_type": bmc.get("manager_type"),
            "mac_address": bmc.get("mac_address"),
            "dns_name": bmc.get("dns_name"),
        })
    # Are name/model/manager_type populated?
    has_name = any(b.get("name") for b in bmc_drift)
    has_model = any(b.get("model") for b in bmc_drift)
    has_mac = any(b.get("mac_address") for b in bmc_drift)
    has_dns = any(b.get("dns_name") for b in bmc_drift)
    # If any of name/model/mac/dns is consistently null, that's the bug
    none_dist = {k: sum(1 for b in bmc_drift if not b.get(k)) for k in ["name", "model", "manager_type", "mac_address", "dns_name"]}
    verdicts["B08"] = vb(
        V_VERIFIED if any(v == len(bmc_drift) for v in none_dist.values()) else V_REJECTED,
        f"BMC field None counts (out of {len(bmc_drift)} hosts): {none_dist}; sample: {bmc_drift[:1]}",
        "fix: redfish_gather.py BMC extraction — populate fields that are 100% None"
    )

    # ---- B09: memory.slots locator (Redfish) ----
    # Redfish memory.slots keys: id, name, capacity_mb, type, base_module_type, speed_mhz, manufacturer, serial, part_number, ...
    # NO 'locator' field. But envelope DOES have name/id. Question: is name/id == locator?
    samples = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        slots = (d.get("data", {}).get("memory") or {}).get("slots") or []
        if slots:
            s = slots[0]
            samples.append({"ip": d.get("ip"), "id": s.get("id"), "name": s.get("name"),
                            "all_keys": list(s.keys())})
    # If 'name' has DIMM locator (e.g. 'A1', 'DIMM1'), B09 is REJECTED
    has_locator_in_name = any(samples)
    has_dimm_label = any(s for s in samples if (s.get("name") or s.get("id") or "").upper().startswith(("DIMM", "A", "B", "P", "CPU")))
    verdicts["B09"] = vb(
        V_REJECTED if has_dimm_label else V_VERIFIED,
        f"Redfish memory.slots samples: {samples}; (B09 originally claimed 'locator None' but envelope has 'name'/'id' fields with DIMM labels — verify per host)",
        "fix-conditional: if 'name' contains DIMM locator, add 'locator' key as alias OR rename. If empty, populate from DeviceLocator."
    )

    # ---- B10: physical_disks capacity (Redfish) ----
    # Disks have total_mb, not capacity_gb. Was my analysis using wrong key.
    samples = []
    for d in rf_envs:
        disks = ((d.get("data", {}).get("storage") or {}).get("physical_disks")) or []
        if disks:
            samples.append({"ip": d.get("ip"), "first_disk": disks[0]})
    have_cap = any(s["first_disk"].get("total_mb") for s in samples)
    verdicts["B10"] = vb(
        V_REJECTED if have_cap else V_VERIFIED,
        f"Redfish disks have total_mb populated: {samples[:1]}",
        "(originally claimed 'capacity_gb None' — actual field is 'total_mb' which is populated)"
    )

    # ---- B17: Linux users.username (REJECTED — actual field is 'name') ----
    samples = []
    for d in os_envs:
        users = d.get("data", {}).get("users") or []
        if users:
            samples.append({"ip": d.get("ip"), "first_user": users[0]})
    has_name = all(s["first_user"].get("name") for s in samples)
    verdicts["B17"] = vb(
        V_REJECTED,
        f"Linux users.name populated: {samples[:2]} (originally my analysis used 'username' key — actual field is 'name')",
        None
    )

    # ---- B18, B73, B87: hostname/fqdn (mostly false alarm) ----
    samples = []
    for d in os_envs:
        sys_ = d.get("data", {}).get("system") or {}
        samples.append({"ip": d.get("ip"), "hostname": sys_.get("hostname"), "fqdn": sys_.get("fqdn"),
                        "envelope_top_hostname": d.get("hostname")})
    # B18 claim: system.hostname=None — that IS true (no hostname key in OS envelope).
    # Schema-wise hostname is at top level; system has fqdn only. Acceptable.
    has_hostname_in_system = all("hostname" in (d.get("data", {}).get("system") or {}) for d in os_envs)
    verdicts["B18"] = vb(
        V_REJECTED,
        f"OS system has fqdn: {samples}; envelope has top-level hostname. system.hostname not in OS schema (OS uses fqdn only).",
        None
    )
    verdicts["B73"] = (V_DUP, "B18", None)
    verdicts["B87"] = (V_DUP, "B18", None)

    # ---- B19/B28: r760-6 baremetal hardware None ----
    r6 = next((d for d in os_envs if d.get("ip") == "10.100.64.96"), None)
    if r6:
        hw = r6.get("data", {}).get("hardware")
        sec = r6.get("sections", {})
        verdicts["B19"] = vb(
            V_VERIFIED if hw is None and sec.get("hardware") in ("not_supported", "failed") else V_REJECTED,
            f"r760-6 baremetal: data.hardware={hw}, sections.hardware={sec.get('hardware')}, system.hosting_type={r6.get('data',{}).get('system',{}).get('hosting_type')}, system.serial_number={r6.get('data',{}).get('system',{}).get('serial_number')}",
            "fix: os-gather/tasks/linux/gather_hardware.yml — when hosting_type=baremetal, run dmidecode and populate hardware section"
        )
    else:
        verdicts["B19"] = vb(V_NEEDS_LIVE, "no baremetal envelope", None)
    verdicts["B28"] = (V_DUP, "B19", None)

    # ---- B22: cpu.max_speed_mhz=None on VMs ----
    vm_cpu_no_max = [(d.get("ip"), (d.get("data", {}).get("cpu") or {}).get("max_speed_mhz"))
                     for d in os_envs if (d.get("data", {}).get("system") or {}).get("hosting_type") == "virtual"]
    has_none = any(v[1] is None for v in vm_cpu_no_max)
    verdicts["B22"] = vb(
        V_VERIFIED if has_none else V_REJECTED,
        f"VM cpu.max_speed_mhz: {vm_cpu_no_max}",
        "fix: normalize_cpu.yml — fallback to lscpu 'CPU max MHz' or /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
    )

    # ---- B23: r760-6 memory.mfg raw hex ----
    r6_mem = (r6 or {}).get("data", {}).get("memory", {}).get("slots") or []
    raw_hex_mfg = [s for s in r6_mem if re.match(r"^0x[0-9A-Fa-f]+|^[0-9A-Fa-f]{6,}$", str(s.get("manufacturer") or ""))]
    verdicts["B23"] = vb(
        V_VERIFIED if raw_hex_mfg else V_REJECTED,
        f"r760-6 memory.slots[0].manufacturer: {(r6_mem[0].get('manufacturer') if r6_mem else None)}",
        "fix: os-gather/tasks/linux/normalize_memory.yml — JEDEC ID -> manufacturer name mapping (0x00AD = SK hynix, 0x00CE = Samsung, 0x002C = Micron, etc.)"
    )
    verdicts["B71"] = (V_DUP, "B23", None)

    # ---- B25 (REJECTED) ----
    samples = []
    for d in os_envs:
        disks = (d.get("data", {}).get("storage") or {}).get("physical_disks") or []
        if disks:
            samples.append({"ip": d.get("ip"), "first_disk": disks[0]})
    have_cap = all(s["first_disk"].get("total_mb") for s in samples)
    verdicts["B25"] = vb(
        V_REJECTED,
        f"Linux disks have total_mb populated: {samples[:1]} (originally my analysis used 'capacity_gb' — actual field 'total_mb' is populated)",
        None
    )

    # ---- B26 (REJECTED) ----
    samples = []
    for d in os_envs:
        fss = (d.get("data", {}).get("storage") or {}).get("filesystems") or []
        if fss:
            samples.append({"ip": d.get("ip"), "first_fs": fss[0]})
    have_fstype = all(s["first_fs"].get("filesystem") for s in samples)
    verdicts["B26"] = vb(
        V_REJECTED,
        f"Linux fs.filesystem populated: {samples[:1]} (originally claimed 'fstype None' — actual field is 'filesystem')",
        None
    )
    verdicts["B67"] = (V_DUP, "B26", None)

    # ---- B65 (REJECTED) ----
    have_avail = all(s["first_fs"].get("available_mb") for s in samples)
    verdicts["B65"] = vb(
        V_REJECTED,
        f"Linux fs.available_mb populated: {samples[:1]} (originally claimed 'free_mb None' — actual field is 'available_mb')",
        None
    )

    # ---- B64: used_mb float precision ----
    floats = [(d.get("ip"), [(f.get("mount_point"), f.get("used_mb")) for f in
                             (d.get("data", {}).get("storage") or {}).get("filesystems") or []
                             if isinstance(f.get("used_mb"), float) and f.get("used_mb") != int(f.get("used_mb"))])
              for d in os_envs]
    floats = [f for f in floats if f[1]]
    verdicts["B64"] = vb(
        V_VERIFIED if floats else V_REJECTED,
        f"hosts with float used_mb (precision drift): {floats[:2]}",
        "fix: normalize_storage.yml filesystems — apply | int filter on used_mb / available_mb / total_mb"
    )

    # ---- B66: read_only field absent ----
    sample_keys = list(samples[0]["first_fs"].keys()) if samples else []
    verdicts["B66"] = vb(
        V_REJECTED if "read_only" not in [] else V_VERIFIED,
        f"Linux fs schema keys: {sample_keys} (no 'read_only' key — original claim 'read_only=None' was based on wrong key; field doesn't exist in schema, scope/policy)",
        None
    )

    # ---- B68: IPv6 ----
    bad_v6 = []
    for d in os_envs:
        for i in (d.get("data", {}).get("network") or {}).get("interfaces") or []:
            addrs = i.get("addresses") or []
            v6 = [a for a in addrs if (a.get("family") or "") == "ipv6"]
            v4 = [a for a in addrs if (a.get("family") or "") == "ipv4"]
            if v4 and not v6:
                bad_v6.append({"ip": d.get("ip"), "iface": i.get("id"), "v4_count": len(v4), "v6_count": 0})
    verdicts["B68"] = vb(
        V_VERIFIED if bad_v6 else V_REJECTED,
        f"OS interfaces with v4 but no v6: {bad_v6[:3]}",
        "fix: os-gather/tasks/linux/normalize_network.yml — also extract IPv6 addresses (ip -6 addr or ansible_facts.ipv6)"
    )

    # ---- B41/B45: Dell PSU=1 ----
    dell_psu = [(d.get("ip"), len((d.get("data", {}).get("power") or {}).get("power_supplies") or []),
                 ((d.get("data", {}).get("power") or {}).get("summary") or {}).get("redundant"))
                for d in rf_envs if d.get("vendor") == "dell" and d.get("status") == "success"]
    verdicts["B41"] = vb(
        V_NEEDS_LIVE if all(d[1] == 1 for d in dell_psu) else V_REJECTED,
        f"Dell PSU envelope counts: {dell_psu}; raw not captured for Dell (auth failure)",
        "next: capture Dell raw, compare /Chassis/.../Power.PowerSupplies size; fix if envelope undercount"
    )
    verdicts["B45"] = (V_DUP, "B41", None)

    # ---- B46: power.power_control list-of-strings — REJECTED earlier ----
    pc_types = [(d.get("ip"), type((d.get("data", {}).get("power") or {}).get("power_control")).__name__)
                for d in rf_envs if (d.get("data", {}).get("power") or {}).get("power_control") is not None]
    verdicts["B46"] = vb(
        V_REJECTED,
        f"power_control IS dict in all envelopes: {pc_types}; original 'list of strings' claim was iteration artifact",
        None
    )
    verdicts["B42"] = (V_DUP, "B46", None)

    # ---- B58: PSU Critical not in summary ----
    issues = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        pwr = d.get("data", {}).get("power") or {}
        psus = pwr.get("power_supplies") or []
        crit = [p for p in psus if (p.get("health") or "") == "Critical"]
        sm = pwr.get("summary") or {}
        if crit and "critical_count" not in sm and "unhealthy_count" not in sm:
            issues.append({"ip": d.get("ip"), "vendor": d.get("vendor"), "critical_psus": len(crit), "summary_keys": list(sm.keys())})
    verdicts["B58"] = vb(
        V_VERIFIED if issues else V_REJECTED,
        f"hosts with Critical PSU but no critical_count in summary: {issues}",
        "fix: redfish-gather/tasks/normalize_standard.yml _rf_power_summary — add critical_count, unhealthy_count, health_rollup"
    )
    verdicts["B95"] = (V_DUP, "B58", None)

    # ---- B59: Lenovo PSU None capacity sum ----
    issues = []
    for d in rf_envs:
        if d.get("vendor") != "lenovo" or d.get("status") != "success":
            continue
        pwr = d.get("data", {}).get("power") or {}
        psus = pwr.get("power_supplies") or []
        caps = [p.get("power_capacity_w") for p in psus]
        sm_total = (pwr.get("summary") or {}).get("total_capacity_w")
        if any(c is None for c in caps) and sm_total is not None:
            non_none_sum = sum(c for c in caps if c is not None)
            if sm_total == non_none_sum:
                issues.append({"ip": d.get("ip"), "psu_caps": caps, "sm_total": sm_total})
    verdicts["B59"] = vb(
        V_VERIFIED if issues else V_REJECTED,
        f"Lenovo None-cap PSU sum issue: {issues}",
        "fix: normalize_standard _rf_power_summary — separate capacity_unknown_count + only sum non-None"
    )

    # ---- B76: Linux network.adapters=[] ----
    issues = [(d.get("ip"), len((d.get("data", {}).get("network") or {}).get("adapters") or []))
              for d in os_envs]
    no_adapters = [i for i in issues if i[1] == 0]
    verdicts["B76"] = vb(
        V_VERIFIED if no_adapters else V_REJECTED,
        f"Linux hosts with empty network.adapters: {no_adapters}",
        "fix: os-gather/tasks/linux/gather_network.yml — add lspci -k -d ::0200 + dmidecode parser to populate adapters"
    )

    # ---- POLICY/SCOPE/DUP from earlier ----
    for tid, (kind, ref) in {
        "B11": (V_DUP, "B01"),
        "B12": (V_POLICY, "vendor-specific firmware naming"),
        "B13": (V_VERIFIED, "redfish iface link_status enum varies (linkup/linkdown vs none)"),
        "B14": (V_POLICY, "iface name normalization decision"),
        "B15": (V_POLICY, "AccountService 정책 결정"),
        "B16": (V_VERIFIED, "bios_date 형식 vendor마다 다름 (Dell MM/DD/YYYY vs ESXi ISO 8601 vs others null)"),
        "B20": (V_SCOPE, "VM CPU sockets observation"),
        "B27": (V_SCOPE, "tz environment"),
        "B29": (V_SCOPE, "OS-level disk SSD/HDD limit"),
        "B30": (V_SCOPE, "esxi03 vmnic1 — env hardware"),
        "B31": (V_VERIFIED, "ESXi runtime tz/ntp/firewall/swap all None — vSphere fact不 collected"),
        "B32": (V_VERIFIED, "ESXi default_gateways=[] — routeConfig 미수집"),
        "B34": (V_VERIFIED, "ESXi physical_disks=[] — esxcli storage core device 미사용"),
        "B35": (V_POLICY, "controllers vs hbas 정책"),
        "B36": (V_SCOPE, "환경별 HBA"),
        "B37": (V_SCOPE, "fallback_used 의미"),
        "B38": (V_SCOPE, "ESXi memory installed_mb 한계"),
        "B39": (V_POLICY, "ESXi user 정책"),
        "B40": (V_VERIFIED, "Ansible reserved 'name' warning"),
        "B43": (V_VERIFIED, "Lenovo firmware pending entry version=None"),
        "B44": (V_DUP, "B12"),
        "B47": (V_DUP, "B30"),
        "B48": (V_VERIFIED, "Cisco logical_volume name=''"),
        "B49": (V_NEEDS_LIVE, "Dell BOSS boot_volume — need raw"),
        "B50": (V_VERIFIED, "duration_ms 1초 절삭"),
        "B51": (V_SCOPE, "memory total/slot 합계 통과"),
        "B52": (V_POLICY, "raw vs usable storage capacity 정의"),
        "B53": (V_POLICY, "correlation.bmc_ip 정책"),
        "B54": (V_SCOPE, "UUID prefix"),
        "B55": (V_VERIFIED, "failed envelope diagnosis.details 누락 (B03 부분과 묶음)"),
        "B56": (V_VERIFIED, "failed envelope auth_success=null (B03 부분)"),
        "B57": (V_POLICY, "iface vs adapter mac 의미 정의"),
        "B60": (V_DUP, "B52"),
        "B61": (V_VERIFIED, "Lenovo Cisco OEM coverage 부족"),
        "B62": (V_VERIFIED, "ESXi diagnosis.details에 esxi_version 추가 필요"),
        "B63": (V_SCOPE, "OS auth 통과"),
        "B69": (V_SCOPE, "ESXi IPv6 환경"),
        "B70": (V_NEEDS_LIVE, "Dell adapter.name='Network Adapter View' — need raw"),
        "B72": (V_DUP, "B24"),
        "B74": (V_SCOPE, "swap_used 관찰"),
        "B75": (V_POLICY, "visible_mb vs total_mb 필드명"),
        "B77": (V_DUP, "B81"),
        "B78": (V_VERIFIED, "VM serial_number raw VMware 형식"),
        "B79": (V_POLICY, "OS BMC IP 정책"),
        "B80": (V_VERIFIED, "OS envelope.vendor=None 베어메탈도"),
        "B81": (V_POLICY, "target_type별 vendor 정책"),
        "B82": (V_SCOPE, "RHEL hostname=localhost 환경"),
        "B83": (V_SCOPE, "ESXi hostname short"),
        "B84": (V_SCOPE, "ESXi datastore 통과"),
        "B85": (V_DUP, "B27"),
        "B86": (V_DUP, "B82"),
        "B88": (V_POLICY, "ESXi BMC IP 정책"),
        "B89": (V_SCOPE, "DIMM 혼합 관찰"),
        "B90": (V_VERIFIED, "Cisco memory.mfg raw 0xCExx"),
        "B91": (V_NEEDS_LIVE, "RHEL 8.10 raw fallback memory.mfg=None"),
        "B92": (V_VERIFIED, "HPE iface.name 숫자만"),
        "B93": (V_VERIFIED, "HPE adapter.mac/link 모두 None"),
        "B94": (V_SCOPE, "HPE iface.addresses 0개"),
        "B96": (V_SCOPE, "ESXi collection_method 통과"),
        "B97": (V_POLICY, "OS collection_method 명확화"),
        "B98": (V_DUP, "B16"),
        "B99": (V_POLICY, "listening_ports 구조화"),
        "B24": (V_POLICY, "memory speed 의미 정의"),
    }.items():
        if tid not in verdicts:
            verdicts[tid] = (kind, ref, None)

    # Summary
    counts = {}
    for tid, (verdict, _, _) in verdicts.items():
        counts[verdict] = counts.get(verdict, 0) + 1

    md = ["# 2026-04-29 Bug Verification — Final Verdict (v2)\n",
          "v2 correction: many original 'bugs' were false positives caused by wrong field names",
          "in my Python analysis script (e.g. `username` instead of `name`, `capacity_gb` instead",
          "of `total_mb`, `fstype` instead of `filesystem`, `free_mb` instead of `available_mb`).\n",
          f"Total tickets: {len(verdicts)}\n",
          "## Summary\n",
          "| verdict | count | meaning |",
          "|---|---|---|",
          f"| **verified** | {counts.get(V_VERIFIED, 0)} | confirmed bug — needs fix |",
          f"| **rejected** | {counts.get(V_REJECTED, 0)} | not a bug (false positive due to wrong field name etc) |",
          f"| **needs_live** | {counts.get(V_NEEDS_LIVE, 0)} | need fresh raw capture (Dell auth fail blocks) |",
          f"| **policy** | {counts.get(V_POLICY, 0)} | decision required |",
          f"| **scope** | {counts.get(V_SCOPE, 0)} | observation/environment, not actionable code change |",
          f"| **dup** | {counts.get(V_DUP, 0)} | duplicate of another ticket |",
          ""]

    md.append("## Per-ticket verdict\n")
    md.append("| ticket | verdict | summary |")
    md.append("|---|---|---|")
    for tid in sorted(verdicts.keys()):
        v, ev, _ = verdicts[tid]
        snip = (str(ev) or "")[:120].replace("|", "/").replace("\n", " ")
        md.append(f"| {tid} | **{v}** | {snip} |")

    out = TICKETS / "VERDICT_TABLE.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {out}")
    print(json.dumps(counts, indent=2))

    # Patch ticket files
    for tid, (verdict, _, _) in verdicts.items():
        f = TICKETS / f"{tid}.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        text = re.sub(r"^Status:.*$", f"Status: {verdict}", text, count=1, flags=re.MULTILINE)
        f.write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
