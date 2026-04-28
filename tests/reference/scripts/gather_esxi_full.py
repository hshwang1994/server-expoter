#!/usr/bin/env python3
"""gather_esxi_full.py — ESXi 종합 정보 수집 (vSphere API + esxcli + SSH).

목적: pyVmomi 객체 dump + esxcli 광범위 명령 + ssh raw 출력을
      ip별 디렉터리에 저장. 향후 schema 추가 / OEM 검증용.

사용:
    wsl python3 tests/reference/scripts/gather_esxi_full.py
    wsl python3 tests/reference/scripts/gather_esxi_full.py --target esxi-10.100.64.1
    wsl python3 tests/reference/scripts/gather_esxi_full.py --skip-existing
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    print("ERROR: PyYAML required", file=sys.stderr)
    sys.exit(2)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


REPO_ROOT = Path(__file__).resolve().parents[3]
TARGETS_FILE = REPO_ROOT / "tests" / "reference" / "local" / "targets.yaml"
OUTPUT_BASE = REPO_ROOT / "tests" / "reference" / "esxi"


# ESXi shell 명령 (SSH 통해)
ESXI_SHELL_COMMANDS: list[tuple[str, str]] = [
    ("uname",                   "uname -a"),
    ("vmware_version",          "vmware -v; vmware -l"),
    ("hostname",                "hostname; cat /etc/hostname"),
    ("uptime",                  "uptime"),
    # esxcli system
    ("esxcli_system_version",   "esxcli system version get"),
    ("esxcli_system_uuid",      "esxcli system uuid get"),
    ("esxcli_system_hostname",  "esxcli system hostname get"),
    ("esxcli_system_module",    "esxcli system module list"),
    ("esxcli_system_settings_advanced", "esxcli system settings advanced list"),
    ("esxcli_system_settings_kernel",   "esxcli system settings kernel list"),
    ("esxcli_system_stats_uptime",      "esxcli system stats uptime get"),
    ("esxcli_system_account_user",      "esxcli system account list"),
    # hardware
    ("esxcli_hw_platform",      "esxcli hardware platform get"),
    ("esxcli_hw_cpu_global",    "esxcli hardware cpu global get"),
    ("esxcli_hw_cpu_list",      "esxcli hardware cpu list"),
    ("esxcli_hw_memory",        "esxcli hardware memory get"),
    ("esxcli_hw_pci_list",      "esxcli hardware pci list"),
    ("esxcli_hw_clock",         "esxcli hardware clock get"),
    ("esxcli_hw_bootdevice",    "esxcli hardware bootdevice list"),
    ("esxcli_hw_trusted_boot",  "esxcli hardware trustedboot get"),
    # storage
    ("esxcli_storage_core_dev", "esxcli storage core device list"),
    ("esxcli_storage_core_path","esxcli storage core path list"),
    ("esxcli_storage_filesys",  "esxcli storage filesystem list"),
    ("esxcli_storage_vmfs",     "esxcli storage vmfs extent list; esxcli storage vmfs snapshot list"),
    ("esxcli_storage_nvme",     "esxcli nvme controller list; esxcli nvme namespace list"),
    ("esxcli_storage_iscsi",    "esxcli iscsi adapter list 2>&1"),
    ("esxcli_storage_san",      "esxcli storage san fc list 2>&1; esxcli storage san sas list 2>&1"),
    # network
    ("esxcli_network_nic",      "esxcli network nic list"),
    ("esxcli_network_nic_stats","for n in $(esxcli network nic list | awk 'NR>2{print $1}'); do echo '=== '$n' ==='; esxcli network nic get -n $n; done"),
    ("esxcli_network_ip_iface", "esxcli network ip interface list"),
    ("esxcli_network_ip_ipv4",  "esxcli network ip interface ipv4 get"),
    ("esxcli_network_ip_route", "esxcli network ip route ipv4 list; esxcli network ip route ipv6 list"),
    ("esxcli_network_dns",      "esxcli network ip dns server list; esxcli network ip dns search list"),
    ("esxcli_network_vswitch_std", "esxcli network vswitch standard list"),
    ("esxcli_network_vswitch_dvs", "esxcli network vswitch dvs vmware list 2>&1"),
    ("esxcli_network_portgroup","esxcli network vswitch standard portgroup list 2>&1"),
    ("esxcli_network_firewall", "esxcli network firewall ruleset list"),
    # software / patches
    ("esxcli_software_vib",     "esxcli software vib list"),
    ("esxcli_software_profile", "esxcli software profile get"),
    ("esxcli_software_baseimg", "esxcli software baseimage get 2>&1"),
    # vm
    ("esxcli_vm_process",       "esxcli vm process list"),
    # iovm/sched
    ("esxcli_sched_swap",       "esxcli sched swap system get 2>&1"),
    # hardware sensor (deprecated in 7.0+ but try)
    ("esxcli_hw_ipmi",          "esxcli hardware ipmi sel list 2>&1; esxcli hardware ipmi fru list 2>&1"),
    # host status
    ("vim_cmd_hostsvc",         "vim-cmd hostsvc/hosthardware 2>&1; vim-cmd hostsvc/hostsummary 2>&1"),
    ("vim_cmd_listsvc",         "vim-cmd hostsvc/service/status_all 2>&1"),
    ("vim_cmd_vmsvc",           "vim-cmd vmsvc/getallvms 2>&1"),
    # kernel / log
    ("vmkernel_log_tail",       "tail -200 /var/log/vmkernel.log 2>&1"),
    ("hostd_log_tail",          "tail -100 /var/log/hostd.log 2>&1"),
    ("vobd_log_tail",           "tail -100 /var/log/vobd.log 2>&1"),
    # config files
    ("esx_conf",                "cat /etc/vmware/esx.conf 2>&1 | head -200"),
    ("services_xml",            "head -200 /etc/vmware/services/services.xml 2>&1"),
    # vsan / dvs
    ("esxcli_vsan",             "esxcli vsan storage list 2>&1; esxcli vsan cluster get 2>&1"),
]


def load_targets() -> dict[str, Any]:
    if not TARGETS_FILE.exists():
        print(f"ERROR: {TARGETS_FILE} 없음", file=sys.stderr)
        sys.exit(2)
    with TARGETS_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_ssh(host: str, user: str, password: str, cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    try:
        import paramiko
    except ImportError:
        return -1, "", "paramiko required"
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=20, banner_timeout=20, auth_timeout=20, look_for_keys=False, allow_agent=False)
    except Exception as e:
        return -1, "", f"SSH connect fail: {e}"
    try:
        _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err
    except Exception as e:
        return -1, "", f"exec fail: {e}"
    finally:
        client.close()


def collect_pyvmomi(host: str, user: str, password: str) -> dict[str, Any]:
    """pyvmomi로 host object 전체 dump."""
    try:
        from pyVim.connect import SmartConnect, Disconnect  # type: ignore
        from pyVmomi import vim  # type: ignore
        import ssl as ssl_mod
    except ImportError as e:
        return {"_error": f"pyvmomi not available: {e}"}

    ctx = ssl_mod._create_unverified_context()
    try:
        si = SmartConnect(host=host, user=user, pwd=password, port=443, sslContext=ctx, disableSslCertValidation=True)
    except Exception as e:
        return {"_error": f"connect fail: {e}"}

    try:
        content = si.content
        ah = content.searchIndex.FindByIp(None, host, False) or content.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0]
        out: dict[str, Any] = {}
        # 다양한 host-level property 추출
        try:
            out["name"] = ah.name
            out["hardware_systemInfo"] = vim_to_dict(ah.summary.hardware)
            out["config_product"] = vim_to_dict(ah.summary.config.product)
            out["runtime"] = vim_to_dict(ah.summary.runtime)
            out["network_pnic"] = [vim_to_dict(p) for p in ah.config.network.pnic]
            out["network_vnic"] = [vim_to_dict(v) for v in ah.config.network.vnic]
            out["network_vswitch"] = [vim_to_dict(v) for v in ah.config.network.vswitch]
            out["network_portgroup"] = [vim_to_dict(p) for p in ah.config.network.portgroup]
            out["storage_device"] = [vim_to_dict(d) for d in ah.config.storageDevice.scsiLun]
            out["storage_hba"] = [vim_to_dict(h) for h in ah.config.storageDevice.hostBusAdapter]
            out["filesystem"] = [vim_to_dict(m) for m in (ah.config.fileSystemVolume.mountInfo or [])]
            out["service"] = [vim_to_dict(s) for s in ah.config.service.service]
            out["firewall_rules"] = [vim_to_dict(r) for r in (ah.config.firewall.ruleset or [])]
            out["dns_config"] = vim_to_dict(ah.config.network.dnsConfig)
            out["host_summary"] = vim_to_dict(ah.summary)
        except Exception as e:
            out["_partial_error"] = str(e)
        return out
    finally:
        Disconnect(si)


def vim_to_dict(obj: Any, depth: int = 0, max_depth: int = 5) -> Any:
    """pyvmomi 객체를 dict로 (max_depth 제한)."""
    if depth > max_depth:
        return f"<truncated:{type(obj).__name__}>"
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [vim_to_dict(x, depth + 1, max_depth) for x in obj]
    if isinstance(obj, dict):
        return {str(k): vim_to_dict(v, depth + 1, max_depth) for k, v in obj.items()}
    # vmodl object
    try:
        from pyVmomi import vmodl  # type: ignore
        if hasattr(obj, "_propList"):
            d = {}
            for p in obj._propList:
                try:
                    val = getattr(obj, p.name, None)
                    d[p.name] = vim_to_dict(val, depth + 1, max_depth)
                except Exception as e:
                    d[p.name] = f"<err:{e}>"
            return d
    except Exception:
        pass
    return str(obj)


def gather_esxi(target: dict[str, Any], skip_existing: bool = False) -> dict[str, Any]:
    name = target["name"]
    ip = target["ip"]
    user = target["user"]
    password = target["password"]

    out_dir = OUTPUT_BASE / ip.replace(".", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== ESXi: {name} ({ip}) → {out_dir.relative_to(REPO_ROOT)} ===")

    summary: dict[str, Any] = {"target": name, "ip": ip, "started_at": datetime.now(timezone.utc).isoformat(), "commands": [], "errors": []}
    started = time.monotonic()

    # 1. SSH 연결 테스트
    rc, _, err = run_ssh(ip, user, password, "echo OK", timeout=15)
    ssh_ok = rc == 0
    if not ssh_ok:
        summary["errors"].append({"step": "ssh_connect", "rc": rc, "err": err})
        print(f"  SSH FAIL: {err} (vSphere API만 시도)")
    else:
        print(f"  SSH OK")
        # 2. 각 명령 실행
        for cmd_name, cmd in ESXI_SHELL_COMMANDS:
            out_file = out_dir / f"esxcli_{cmd_name}.txt"
            if skip_existing and out_file.exists() and out_file.stat().st_size > 0:
                summary["commands"].append({"name": cmd_name, "status": "cached"})
                continue
            rc, out, err = run_ssh(ip, user, password, cmd, timeout=90)
            with out_file.open("w", encoding="utf-8") as f:
                f.write(f"# command: {cmd}\n# rc: {rc}\n# fetched: {datetime.now(timezone.utc).isoformat()}\n#\n")
                f.write(out)
                if err.strip():
                    f.write("\n# === stderr ===\n")
                    f.write(err)
            summary["commands"].append({"name": cmd_name, "rc": rc, "size": len(out)})
            tag = "OK" if rc == 0 else f"rc={rc}"
            print(f"  [{tag:8s}] {cmd_name:35s} ({len(out):6d}b)")

    # 3. pyvmomi
    pyvmomi_file = out_dir / "pyvmomi_host_dump.json"
    if not (skip_existing and pyvmomi_file.exists() and pyvmomi_file.stat().st_size > 0):
        print(f"  collecting pyvmomi host dump...")
        data = collect_pyvmomi(ip, user, password)
        pyvmomi_file.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False))
        summary["commands"].append({"name": "pyvmomi", "size": pyvmomi_file.stat().st_size})

    summary["elapsed_seconds"] = round(time.monotonic() - started, 1)
    summary["completed_at"] = datetime.now(timezone.utc).isoformat()
    (out_dir / "_manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    targets = load_targets().get("esxi", [])
    if args.target:
        targets = [t for t in targets if t["name"] == args.target]

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    print(f"ESXi gather — {len(targets)} target(s)")

    results = []
    for t in targets:
        try:
            results.append(gather_esxi(t, args.skip_existing))
        except Exception as e:
            results.append({"target": t["name"], "error": str(e)})

    print(f"\n{'='*60}\n  TOTAL\n{'='*60}")
    for r in results:
        if "error" in r:
            print(f"  ERROR  {r['target']}: {r['error']}")
        else:
            print(f"  {r['target']:30s} cmds={len(r.get('commands',[])):3d} err={len(r.get('errors',[])):2d} elapsed={r.get('elapsed_seconds',0):.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
