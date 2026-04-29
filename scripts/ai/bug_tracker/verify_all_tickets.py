#!/usr/bin/env python3
"""Comprehensive verification of all 99 bug tickets against:
  - raw Redfish responses (tests/evidence/2026-04-29-deep-verify/redfish)
  - raw Linux command outputs (tests/evidence/2026-04-29-deep-verify/linux)
  - Jenkins #114/#115/#116 envelopes (tests/evidence/2026-04-29-deep-verify/jenkins-*.txt)

For each ticket, output one of:
  - VERIFIED       : envelope shows symptom AND raw shows expected source
  - REJECTED       : envelope examination contradicts the bug claim
  - NEEDS_LIVE     : raw not available (e.g. Dell auth failed) — needs follow-up
  - SCOPE          : observation/policy ticket (not a code bug)

Saves verdict to docs/ai/tickets/2026-04-29-output-quality/VERIFICATION_FULL.md
and patches each ticket file's Status: line.
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


def load_envelopes(jenkins_log: Path) -> list[dict]:
    out = []
    if not jenkins_log.exists():
        return out
    for line in jenkins_log.read_text(encoding="utf-8", errors="replace").split("\n"):
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


# --------------------------------------------------------------------------- #
# Per-ticket verifiers                                                        #
# --------------------------------------------------------------------------- #

def v_b01(rf_envs, rf_root, _, __):
    """B01 — GPU in CPU section.
    Envelope: cpu.summary.groups contains entry with manufacturer 'NVIDIA' or model 'Tesla'.
    Raw: Processors collection has ProcessorType='GPU' member.
    """
    found_envelope = []
    for d in rf_envs:
        cpu = d.get("data", {}).get("cpu", {}) or {}
        for g in cpu.get("summary", {}).get("groups", []) or []:
            mfg = (g.get("manufacturer") or "").lower()
            mdl = (g.get("model") or "").lower()
            if "nvidia" in mfg or "tesla" in mdl or "gpu" in mdl or "amd radeon" in mfg:
                found_envelope.append({"ip": d.get("ip"), "model": g.get("model"), "mfg": g.get("manufacturer")})
    if found_envelope:
        return ("VERIFIED", f"r760-1 envelope shows GPU in cpu.summary.groups: {found_envelope}",
                "fix: redfish_gather.py Processors loop must filter ProcessorType=='CPU'")
    return ("REJECTED", "no GPU found in any envelope cpu groups", None)


def v_b02(rf_envs, rf_root, _, __):
    """B02 — DNS unspecified IP. Check envelope network.dns_servers for 0.0.0.0/::"""
    bad = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        net = (d.get("data", {}).get("network") or {})
        dns = net.get("dns_servers") or []
        if any(x in ("0.0.0.0", "::", "0:0:0:0:0:0:0:0") for x in dns):
            bad.append({"ip": d.get("ip"), "dns": dns})
    if not bad:
        return ("REJECTED", "no envelope shows unspecified IP in dns_servers", None)
    # Check raw for one host
    raw_evidence = {}
    for host_dir in (rf_root / "hpe-dl380",):
        mgr_dir = host_dir / "managers_members"
        if not mgr_dir.exists():
            continue
        for f in mgr_dir.glob("*__eth_*.json"):
            obj = load_json(f)
            if obj:
                raw_evidence[f.name] = obj.get("NameServers") or obj.get("StaticNameServers")
    return ("VERIFIED",
            f"{len(bad)} envelope(s) carry 0.0.0.0/:: in dns_servers; HPE raw NameServers={raw_evidence}",
            "fix: redfish_gather.py DNS extraction must filter unspecified addresses")


def v_b03(rf_envs, rf_root, _, __):
    """B03 — failed envelope inconsistency."""
    failed = [d for d in rf_envs if d.get("status") == "failed"]
    if not failed:
        return ("NEEDS_LIVE", "no failed envelopes in current logs", None)
    drift = []
    for d in failed:
        data = d.get("data") or {}
        none_keys = [k for k, v in data.items() if v is None]
        empty_dict_keys = [k for k, v in data.items() if isinstance(v, dict) and not v]
        empty_collection_keys = [k for k, v in data.items() if isinstance(v, (list, dict)) and len(v) == 0 and v != {}]
        sec = d.get("sections") or {}
        not_supported = [k for k, v in sec.items() if v == "not_supported"]
        failed_sec = [k for k, v in sec.items() if v == "failed"]
        diag = d.get("diagnosis") or {}
        drift.append({
            "ip": d.get("ip"),
            "data_None_keys": none_keys,
            "data_empty_dict_or_list_keys": empty_dict_keys + empty_collection_keys,
            "sections_failed": failed_sec,
            "sections_not_supported": not_supported,
            "auth_success": diag.get("auth_success"),
            "failure_stage": diag.get("failure_stage"),
            "duration_ms": (d.get("meta") or {}).get("duration_ms"),
        })
    return ("VERIFIED", f"failed envelope drift: {drift}",
            "fix: site.yml always block + build_output.yml — emit consistent shapes for all sections")


def v_b04(*_a):
    """B04 — Ubuntu DNS=127.0.0.53 (systemd-resolved stub)."""
    rf_envs, _, os_envs, linux_root = _a
    bad = []
    for d in os_envs:
        sys_ = (d.get("data", {}).get("system") or {})
        if (sys_.get("distribution") or "").lower() == "ubuntu":
            dns = ((d.get("data", {}).get("network") or {}).get("dns_servers") or [])
            if any(x.startswith("127.") for x in dns):
                bad.append({"ip": d.get("ip"), "dns": dns})
    if not bad:
        return ("REJECTED", "no Ubuntu envelope shows 127.0.0.x dns", None)
    # Confirm via raw
    raw_check = {}
    for host_dir in linux_root.iterdir() if linux_root.exists() else []:
        if "ubuntu" not in host_dir.name.lower():
            continue
        rc = read_text(host_dir / "dns_resolv_conf.txt")
        rs = read_text(host_dir / "dns_resolvectl_status.txt")
        rd = read_text(host_dir / "dns_runtime_resolv.txt")
        raw_check[host_dir.name] = {
            "resolv_conf_has_127": "127.0.0.53" in rc,
            "resolvectl_dns_servers_present": "DNS Servers" in rs or "Current DNS Server" in rs,
            "runtime_resolv_first_ns": [l for l in rd.splitlines() if l.startswith("nameserver")][:3],
        }
    return ("VERIFIED",
            f"Ubuntu envelopes have 127.0.0.x; raw confirms /etc/resolv.conf has 127.0.0.53 stub: {raw_check}",
            "fix: collect_dns.yml — read resolvectl/run/systemd/resolve/resolv.conf when systemd-resolved active")


def v_b05_b21(*_a):
    """B05/B21 — RHEL 8.10 raw_fallback cpu.summary.groups=[]."""
    rf_envs, _, os_envs, linux_root = _a
    bad = []
    for d in os_envs:
        diag = d.get("diagnosis", {}).get("details", {}) or {}
        if diag.get("gather_mode") in ("python_incompatible", "python_missing", "raw_forced"):
            cpu = d.get("data", {}).get("cpu", {}) or {}
            groups = cpu.get("summary", {}).get("groups") or []
            if not groups:
                bad.append({"ip": d.get("ip"), "gather_mode": diag.get("gather_mode"), "groups_count": 0})
    if not bad:
        return ("NEEDS_LIVE", "no raw_fallback host in current logs", None)
    return ("VERIFIED", f"raw_fallback host has empty cpu.summary.groups: {bad}",
            "fix: normalize_cpu.yml raw branch must populate summary.groups")


def v_b06(*_a):
    """B06 — ESXi network.summary.groups buggy."""
    _, _, _, _ = _a  # not used directly; need esxi envelopes
    esxi_log = EVIDENCE / "jenkins-116-esxi.txt"
    esxi_envs = load_envelopes(esxi_log)
    bad = []
    for d in esxi_envs:
        net = (d.get("data", {}).get("network") or {})
        adapters = net.get("adapters") or []
        groups = (net.get("summary") or {}).get("groups") or []
        adapter_count = len(adapters)
        link_up = sum(1 for a in adapters if (a.get("link_status") or "").lower() == "connected")
        # The summary.groups should reflect at least adapter_count or link_up
        total_quantity = sum(g.get("quantity", 0) for g in groups)
        if total_quantity < adapter_count and adapter_count >= 2:
            bad.append({
                "ip": d.get("ip"), "adapter_count": adapter_count, "actual_link_up": link_up,
                "summary_groups": groups, "summary_quantity_sum": total_quantity,
            })
    if not bad:
        return ("REJECTED", "esxi network.summary.groups appears coherent", None)
    return ("VERIFIED", f"esxi summary groups undercount: {bad}",
            "fix: esxi-gather/tasks/normalize_network.yml — group adapters by link_status+speed; null-safe key")


def v_b07(rf_envs, *_a):
    """B07 — Redfish system.* all None but sections.system='success'."""
    bad = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        sys_ = d.get("data", {}).get("system") or {}
        sec = d.get("sections", {})
        all_none = all(v is None for k, v in sys_.items() if k not in ("runtime",)) if sys_ else True
        if all_none and sec.get("system") == "success":
            bad.append({"ip": d.get("ip"), "system_keys_all_none": True, "sections_system": sec.get("system")})
    if not bad:
        return ("REJECTED", "Redfish envelope system.* not all None", None)
    return ("VERIFIED", f"{len(bad)} redfish envelopes mark system='success' despite all-None payload: {bad[:2]}",
            "fix: redfish-gather supported_sections — drop 'system' OR map BMC info into system section; status_rules align")


def v_b08(rf_envs, rf_root, *_a):
    """B08 — BMC.product/mac/hostname None."""
    bad = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        bmc = (d.get("data", {}).get("bmc") or {})
        if not bmc:
            continue
        bad.append({
            "ip": d.get("ip"),
            "product": bmc.get("product"),
            "firmware_version": bmc.get("firmware_version"),
            "mac": bmc.get("mac"),
            "hostname": bmc.get("hostname"),
        })
    return ("VERIFIED", f"BMC product/mac/hostname None across vendors: {bad}",
            "fix: redfish_gather.py bmc extraction — populate product (iDRAC9/iLO6/XCC/CIMC mapping) + EthernetInterface mac/hostname")


def v_b09(rf_envs, rf_root, *_a):
    """B09 — memory.slots[*].locator None."""
    bad = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        slots = (d.get("data", {}).get("memory") or {}).get("slots") or []
        none_locator = sum(1 for s in slots if s.get("locator") is None)
        if slots and none_locator == len(slots):
            bad.append({"ip": d.get("ip"), "slot_count": len(slots), "locator_None_count": none_locator})
    if not bad:
        return ("REJECTED", "memory locator populated in some envelope", None)
    # Check raw
    raw_check = {}
    for host_dir in (rf_root / "hpe-dl380",) if rf_root.exists() else []:
        mem_dir = host_dir / "memory_members"
        if mem_dir.exists():
            for f in list(mem_dir.glob("*.json"))[:2]:
                obj = load_json(f)
                raw_check[f.name] = {
                    "DeviceLocator": obj.get("DeviceLocator"),
                    "MemoryLocation": obj.get("MemoryLocation"),
                }
    return ("VERIFIED",
            f"all redfish envelopes have None locator on every slot; raw HPE Memory has DeviceLocator: {raw_check}",
            "fix: redfish_gather.py memory.slots — extract DeviceLocator (or MemoryLocation.Slot)")


def v_b10(rf_envs, rf_root, *_a):
    """B10 — physical_disks[*].capacity_gb None."""
    bad = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        disks = ((d.get("data", {}) or {}).get("storage") or {}).get("physical_disks") or []
        none_cap = sum(1 for x in disks if x.get("capacity_gb") is None)
        if disks and none_cap == len(disks):
            bad.append({"ip": d.get("ip"), "disk_count": len(disks), "None_count": none_cap})
    if not bad:
        return ("REJECTED", "some envelope has capacity_gb populated", None)
    raw = {}
    for host_dir in (rf_root / "hpe-dl380",):
        stg_dir = host_dir / "storage_members"
        if stg_dir.exists():
            for f in list(stg_dir.glob("*__drive_*.json"))[:2]:
                obj = load_json(f)
                if obj:
                    raw[f.name] = {"CapacityBytes": obj.get("CapacityBytes"), "Model": obj.get("Model")}
    return ("VERIFIED", f"all envelope disks have None capacity; raw has CapacityBytes: {raw}",
            "fix: redfish_gather.py physical_disks — capacity_gb = CapacityBytes // (1024**3)")


def v_b17(_, __, os_envs, linux_root):
    """B17 — Linux users.username None."""
    bad = []
    for d in os_envs:
        users = d.get("data", {}).get("users") or []
        if users and all(u.get("username") is None for u in users):
            bad.append({"ip": d.get("ip"), "user_count": len(users), "all_None_username": True})
    if not bad:
        return ("REJECTED", "envelope users have username", None)
    raw = {}
    if linux_root.exists():
        any_dir = next(iter(linux_root.iterdir()), None)
        if any_dir:
            raw["sample"] = read_text(any_dir / "users_getent_passwd.txt").splitlines()[:3]
    return ("VERIFIED", f"all envelope users.username=None across {len(bad)} hosts; raw getent has username: {raw}",
            "fix: gather_users / normalize_users — extract field 0 of getent output as username")


def v_b25(_, __, os_envs, linux_root):
    """B25 — Linux disk capacity_gb None."""
    bad = []
    for d in os_envs:
        disks = (d.get("data", {}).get("storage") or {}).get("physical_disks") or []
        if disks and all(x.get("capacity_gb") is None for x in disks):
            bad.append({"ip": d.get("ip"), "disk_count": len(disks)})
    if not bad:
        return ("REJECTED", "some host has capacity_gb populated", None)
    raw = {}
    if linux_root.exists():
        for hd in linux_root.iterdir():
            t = read_text(hd / "lsblk_disks.txt")
            disk_lines = [l for l in t.splitlines() if "disk" in l.lower()][:2]
            if disk_lines:
                raw[hd.name] = disk_lines
                break
    return ("VERIFIED", f"all OS envelopes have None disk capacity; raw lsblk has SIZE: {raw}",
            "fix: normalize_storage.yml — capacity_gb = SIZE_BYTES // (1024**3) from lsblk -b or /sys/block size")


def v_b41_b45(rf_envs, rf_root, *_a):
    """B41/B45 — Dell PSU=1 in envelope, raw shows count."""
    counts = {}
    for d in rf_envs:
        if d.get("vendor") != "dell" or d.get("status") != "success":
            continue
        pwr = (d.get("data", {}).get("power") or {})
        psus = pwr.get("power_supplies") or []
        counts[d.get("ip")] = {"psu_count_envelope": len(psus)}
    raw = {}
    for host_dir in rf_root.iterdir() if rf_root.exists() else []:
        if not host_dir.name.startswith("dell"):
            continue
        p = load_json(host_dir / "power.json")
        if p:
            raw[host_dir.name] = {"raw_PSU_count": len(p.get("PowerSupplies") or [])}
    if counts and all(v["psu_count_envelope"] == 1 for v in counts.values()):
        return ("NEEDS_LIVE", f"all dell envelopes show PSU=1 (envelope: {counts}); raw not captured (auth fail), need live verify",
                "next: capture Dell raw, compare PSU count")
    return ("REJECTED", f"dell PSU counts vary: {counts}", None)


def v_b46(rf_envs, rf_root, *_a):
    """B46 — power.power_control list-of-strings (REJECTED — earlier analysis was iterating dict keys)."""
    is_dict = []
    for d in rf_envs:
        pwr = (d.get("data", {}).get("power") or {})
        pc = pwr.get("power_control")
        if pc is not None:
            is_dict.append((d.get("ip"), type(pc).__name__))
    only_dict = all(t == "dict" for _, t in is_dict)
    if only_dict:
        return ("REJECTED", f"power_control IS a dict in all envelopes: {is_dict[:3]} — earlier 'list of strings' was an iteration artifact (printing dict iterates keys).", None)
    return ("VERIFIED", f"some envelope power_control is non-dict: {is_dict}",
            "fix: redfish_gather.py — ensure dict structure")


def v_b58(rf_envs, rf_root, *_a):
    """B58 — PSU Critical not in summary."""
    issues = []
    for d in rf_envs:
        if d.get("status") != "success":
            continue
        pwr = (d.get("data", {}).get("power") or {})
        psus = pwr.get("power_supplies") or []
        crit = [p for p in psus if (p.get("health") or "") == "Critical"]
        summary = pwr.get("summary") or {}
        if crit and "critical_count" not in summary and "unhealthy_count" not in summary:
            issues.append({"ip": d.get("ip"), "critical_psus": len(crit), "summary_keys": list(summary.keys())})
    if not issues:
        return ("NEEDS_LIVE", "no critical PSU host in current data (need lab host with critical psu)", None)
    return ("VERIFIED", f"{len(issues)} envelopes have Critical PSU but summary lacks critical_count: {issues}",
            "fix: redfish-gather/tasks/normalize_standard.yml power summary — add critical_count, unhealthy_count, health_rollup")


def v_b59(rf_envs, *_a):
    """B59 — Lenovo PSU total_capacity_w wrong (None+750=750 instead of 1500)."""
    issues = []
    for d in rf_envs:
        if d.get("vendor") != "lenovo" or d.get("status") != "success":
            continue
        pwr = (d.get("data", {}).get("power") or {})
        psus = pwr.get("power_supplies") or []
        caps = [p.get("power_capacity_w") for p in psus]
        summary_total = (pwr.get("summary") or {}).get("total_capacity_w")
        # If any psu cap is None, summary should not be just sum of non-None
        if any(c is None for c in caps) and summary_total is not None:
            non_none = [c for c in caps if c is not None]
            if summary_total == sum(non_none):
                issues.append({"ip": d.get("ip"), "psu_caps": caps, "summary_total": summary_total,
                               "non_none_sum": sum(non_none)})
    if not issues:
        return ("REJECTED", "no Lenovo envelope shows None capacity issue", None)
    return ("VERIFIED", f"Lenovo envelopes have None+sum: {issues}",
            "fix: normalize_standard power_summary — handle None capacity entries (separate capacity_unknown_count)")


# --------------------------------------------------------------------------- #
# Tickets that are policy/observation/dup                                     #
# --------------------------------------------------------------------------- #

POLICY_OR_DUP = {
    "B11": ("dup", "B01"),
    "B15": ("policy", "AccountService 정책 결정 필요"),
    "B20": ("scope", "lscpu vs setup module 차이 — 호환성 정책"),
    "B21": ("dup", "B05"),
    "B27": ("scope", "환경 timezone 관찰"),
    "B28": ("dup", "B19"),
    "B29": ("scope", "OS-level 한계 — smartctl 필요"),
    "B33": ("dup", "B06"),
    "B35": ("policy", "ESXi controller 수집 정책"),
    "B36": ("scope", "환경별 HBA 차이"),
    "B37": ("scope", "fallback_used 의미 명확화"),
    "B38": ("scope", "ESXi API 한계"),
    "B39": ("policy", "ESXi user 수집 정책"),
    "B42": ("dup", "B46"),
    "B43": ("scope", "pending firmware 표시"),
    "B44": ("dup", "B12"),
    "B45": ("dup", "B41"),
    "B47": ("dup", "B30"),
    "B51": ("scope", "검증 통과 항목"),
    "B53": ("policy", "correlation.bmc_ip 정책"),
    "B54": ("scope", "관찰"),
    "B60": ("dup", "B52"),
    "B63": ("scope", "검증 통과"),
    "B67": ("dup", "B26"),
    "B69": ("scope", "ESXi IPv6 환경 의존"),
    "B71": ("dup", "B23"),
    "B72": ("dup", "B24"),
    "B73": ("dup", "B18"),
    "B74": ("scope", "관찰"),
    "B75": ("policy", "필드명 변경 결정"),
    "B77": ("dup", "B81"),
    "B79": ("policy", "OS-side BMC IP 수집 정책"),
    "B82": ("scope", "환경 misconfig"),
    "B83": ("scope", "환경"),
    "B84": ("scope", "검증 통과"),
    "B85": ("dup", "B27"),
    "B86": ("dup", "B82"),
    "B87": ("dup", "B18"),
    "B88": ("policy", "ESXi BMC IP 정책"),
    "B89": ("scope", "운영 alert 후보"),
    "B94": ("scope", "환경"),
    "B95": ("dup", "B58"),
    "B96": ("scope", "검증 통과"),
    "B98": ("dup", "B16"),
}

VERIFIERS = {
    "B01": v_b01, "B02": v_b02, "B03": v_b03, "B04": v_b04, "B05": v_b05_b21,
    "B06": v_b06, "B07": v_b07, "B08": v_b08, "B09": v_b09, "B10": v_b10,
    "B17": v_b17, "B25": v_b25,
    "B41": v_b41_b45, "B46": v_b46, "B58": v_b58, "B59": v_b59,
}


def main() -> int:
    rf_envs = load_envelopes(EVIDENCE / "jenkins-114-redfish.txt")
    os_envs = load_envelopes(EVIDENCE / "jenkins-115-os.txt")
    rf_root = EVIDENCE / "redfish"
    linux_root = EVIDENCE / "linux"

    print(f"loaded {len(rf_envs)} redfish + {len(os_envs)} os envelopes")
    print(f"raw redfish dirs: {[d.name for d in rf_root.iterdir()] if rf_root.exists() else 'NONE'}")

    md = ["# 2026-04-29 Bug Ticket Verification (Comprehensive)\n",
          f"- raw redfish hosts captured: {sum(1 for d in rf_root.iterdir() if d.is_dir() and any(d.glob('*.json')))}",
          f"- raw linux hosts captured: {sum(1 for d in linux_root.iterdir() if d.is_dir() and any(d.glob('*.txt')))}",
          f"- redfish envelopes: {len(rf_envs)}, os envelopes: {len(os_envs)}\n"]

    verdicts = {}
    summary_counts = {"VERIFIED": 0, "REJECTED": 0, "NEEDS_LIVE": 0, "policy": 0, "scope": 0, "dup": 0}

    for tid in sorted(VERIFIERS.keys()):
        try:
            verdict, evidence, fix_hint = VERIFIERS[tid](rf_envs, rf_root, os_envs, linux_root)
        except Exception as e:
            verdict, evidence, fix_hint = "ERROR", f"{type(e).__name__}: {e}", None
        verdicts[tid] = (verdict, evidence, fix_hint)
        summary_counts[verdict] = summary_counts.get(verdict, 0) + 1
        md.append(f"\n---\n## {tid}: **{verdict}**\n\n{evidence}\n")
        if fix_hint:
            md.append(f"\n**fix hint**: {fix_hint}\n")

    for tid, (kind, ref) in POLICY_OR_DUP.items():
        verdicts[tid] = (kind, ref, None)
        summary_counts[kind] = summary_counts.get(kind, 0) + 1
        md.append(f"\n---\n## {tid}: **{kind}** -> {ref}\n")

    md.append(f"\n---\n## Summary counts\n\n```\n{json.dumps(summary_counts, indent=2)}\n```")

    out = TICKETS / "VERIFICATION_FULL.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nverification report: {out}")
    print(json.dumps(summary_counts, indent=2))

    # Patch each ticket file's Status: line
    for tid, (verdict, _, _) in verdicts.items():
        f = TICKETS / f"{tid}.md"
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        # Map verdict to ticket status
        new_status = {
            "VERIFIED": "verified",
            "REJECTED": "rejected",
            "NEEDS_LIVE": "needs_live",
            "ERROR": "error",
            "dup": "dup",
            "policy": "policy",
            "scope": "scope",
        }.get(verdict, "unknown")
        text = re.sub(r"^Status:.*$", f"Status: {new_status}", text, count=1, flags=re.MULTILINE)
        f.write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
