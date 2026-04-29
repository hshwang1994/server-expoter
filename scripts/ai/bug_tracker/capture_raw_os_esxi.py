#!/usr/bin/env python3
"""Capture raw OS / ESXi probe data for bug verification.

Runs on Jenkins agent. For Linux: SSH (paramiko) into each target with vault creds and
runs diagnostic commands. For ESXi: vSphere host_system facts via community.vmware.

Output:
    /tmp/se-raw-os/<ip>/<command>.txt
    /tmp/se-raw-esxi/<ip>/<facts>.json

Linux command set covers tickets B04 (DNS), B17 (users), B18 (hostname), B19 (baremetal hw),
B22 (max_mhz), B23 (mfg JEDEC), B25 (disk capacity), B26/B66 (fstype/mount opts),
B65 (free_mb), B68 (IPv6), B73 (fqdn), B76 (PCI NIC), B78/B80 (vendor/serial),
B91 (raw fallback memory), B99 (listening ports).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import paramiko

WORKSPACE = Path("/home/cloviradmin/jenkins-agent/workspace/hshwang-gather")
VAULT_PASS = "/tmp/.vault_pass_se"

LINUX_TARGETS = [
    ("ubuntu-r760-6-baremetal", "10.100.64.96"),
    ("rhel-810-raw-fallback",   "10.100.64.161"),
    ("rhel-92",                 "10.100.64.163"),
    ("rhel-96",                 "10.100.64.165"),
    ("rocky-96",                "10.100.64.169"),
    ("ubuntu-2404",             "10.100.64.167"),
]

ESXI_TARGETS = [
    ("esxi01", "10.100.64.1"),
    ("esxi02", "10.100.64.2"),
    ("esxi03", "10.100.64.3"),
]

LINUX_CMDS = [
    # B04 DNS
    ("dns_resolv_conf", "cat /etc/resolv.conf 2>&1"),
    ("dns_resolvectl_status", "resolvectl status 2>&1 || systemd-resolve --status 2>&1 || echo 'no resolvectl'"),
    ("dns_resolved_runtime", "cat /run/systemd/resolve/resolv.conf 2>&1 || echo 'absent'"),
    ("dns_nm", "nmcli dev show 2>&1 | grep -E 'IP4.DNS|IP6.DNS' | head -10 || echo 'no nmcli'"),
    # B17 users + B18 hostname + B73 fqdn
    ("users_getent", "getent passwd | head -30"),
    ("users_etc_passwd", "cat /etc/passwd | head -30"),
    ("hostname_short", "hostname"),
    ("hostname_fqdn", "hostname -f 2>&1; hostname -A 2>&1"),
    ("hostnamectl", "hostnamectl 2>&1 | head -20"),
    # B19/B80 hardware (baremetal vs VM)
    ("dmi_chassis", "sudo -n dmidecode -t chassis 2>&1 | head -30 || dmidecode -t chassis 2>&1 | head -30 || echo 'no dmidecode'"),
    ("dmi_system", "sudo -n dmidecode -t system 2>&1 | head -30 || dmidecode -t system 2>&1 | head -30 || echo 'no dmidecode'"),
    ("dmi_baseboard", "sudo -n dmidecode -t baseboard 2>&1 | head -20 || dmidecode -t baseboard 2>&1 | head -20 || echo 'no'"),
    # B22 cpu max mhz
    ("cpu_lscpu", "lscpu 2>&1 | head -25"),
    ("cpu_max_mhz_sys", "cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>&1 || echo absent"),
    # B23/B91 memory mfg
    ("dmi_memory", "sudo -n dmidecode -t memory 2>&1 | head -80 || dmidecode -t memory 2>&1 | head -80 || echo 'no'"),
    # B25 disk capacity
    ("lsblk_disks", "lsblk -b -o NAME,KNAME,SIZE,TYPE,MODEL,VENDOR,ROTA,TRAN 2>&1 | head -30"),
    ("sys_block", "for d in /sys/block/*; do echo \"$d $(cat $d/size 2>/dev/null) $(cat $d/queue/rotational 2>/dev/null)\"; done | head -20"),
    # B26/B66 fstype / mount options / B65 free
    ("df_T", "df -T -B1 2>&1 | head -20"),
    ("findmnt", "findmnt -t ext4,xfs,btrfs,vfat -o TARGET,SOURCE,FSTYPE,OPTIONS,SIZE,USED,AVAIL 2>&1 | head -20"),
    ("proc_mounts", "cat /proc/mounts | head -30"),
    # B68 IPv6
    ("ip6_addr", "ip -6 addr 2>&1 | head -30"),
    ("ip4_addr", "ip -4 addr 2>&1 | head -30"),
    # B76 PCI NIC
    ("lspci_nic", "lspci -k -d ::0200 2>&1 | head -30"),
    # B78 VM serial
    ("dmi_serial", "sudo -n dmidecode -s system-serial-number 2>&1 || dmidecode -s system-serial-number 2>&1 || echo 'no'"),
    ("dmi_uuid", "sudo -n dmidecode -s system-uuid 2>&1 || dmidecode -s system-uuid 2>&1 || echo 'no'"),
    # B99 listening ports
    ("ss_listen", "ss -tnlpH 2>&1 | head -30"),
    ("ss_listen_udp", "ss -unlpH 2>&1 | head -20"),
    # Misc
    ("python_version", "python3 --version 2>&1; /usr/bin/python --version 2>&1"),
    ("os_release", "cat /etc/os-release | head -10"),
]


def linux_creds() -> tuple[str | None, str | None]:
    cmd = [
        "/opt/ansible-env/bin/ansible-vault", "view",
        "--vault-password-file", VAULT_PASS,
        str(WORKSPACE / "vault" / "linux.yml"),
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.PIPE, timeout=10).decode()
    try:
        import yaml
        d = yaml.safe_load(out) or {}
    except ImportError:
        d = {}
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("#") or not line or ":" not in line:
                continue
            k, _, v = line.partition(":")
            v = v.strip().strip('"').strip("'")
            d[k.strip()] = v
    accounts = d.get("accounts") if isinstance(d, dict) else None
    if isinstance(accounts, list) and accounts:
        primary = next((a for a in accounts if isinstance(a, dict) and a.get("role") == "primary"), accounts[0])
        if isinstance(primary, dict):
            return primary.get("username"), primary.get("password")
    return d.get("ansible_user"), d.get("ansible_password")


def run_linux(label: str, ip: str, user: str, pwd: str, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"label": label, "ip": ip, "commands": {}, "errors": []}
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(ip, username=user, password=pwd, timeout=8, allow_agent=False, look_for_keys=False, banner_timeout=8)
    except Exception as e:
        summary["errors"].append({"step": "connect", "error": str(e)})
        return summary
    try:
        for slug, cmd in LINUX_CMDS:
            try:
                si, so, se = c.exec_command(cmd, timeout=10)
                out = so.read().decode(errors="replace")
                err = se.read().decode(errors="replace")
                rc = so.channel.recv_exit_status()
                fp = out_dir / f"{slug}.txt"
                fp.write_text(out + ("\n[stderr]\n" + err if err else ""), encoding="utf-8")
                summary["commands"][slug] = {"rc": rc, "bytes": len(out), "err_bytes": len(err)}
            except Exception as e:
                summary["errors"].append({"step": slug, "error": str(e)})
    finally:
        c.close()
    return summary


ESXI_VSPHERE_PLAYBOOK = """---
- hosts: localhost
  connection: local
  gather_facts: no
  tasks:
    - name: vsphere host info
      community.vmware.vmware_host_facts:
        hostname: "{{ esxi_ip }}"
        username: "{{ esxi_user }}"
        password: "{{ esxi_pass }}"
        validate_certs: false
      register: vh

    - name: dump
      copy:
        content: "{{ vh | to_nice_json }}"
        dest: "/tmp/se-raw-esxi/{{ esxi_ip }}/host_facts.json"
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ip", help="filter to single IP")
    p.add_argument("--out-linux", default="/tmp/se-raw-os")
    p.add_argument("--skip-esxi", action="store_true")
    a = p.parse_args()

    user, pwd = linux_creds()
    if not user or not pwd:
        print("[fatal] could not load Linux vault creds", file=sys.stderr)
        return 2
    print(f"[info] linux user={user}")

    out_root = Path(a.out_linux)
    out_root.mkdir(parents=True, exist_ok=True)

    targets = LINUX_TARGETS
    if a.ip:
        targets = [t for t in targets if t[1] == a.ip]

    overall = {"started": time.time(), "linux": []}
    for label, ip in targets:
        print(f"[capture-os] {label} {ip} ...")
        s = run_linux(label, ip, user, pwd, out_root / label)
        overall["linux"].append(s)
        print(f"  done: cmds={len(s.get('commands',{}))} errors={len(s.get('errors',[]))}")

    overall["finished"] = time.time()
    (out_root / "summary.json").write_text(json.dumps(overall, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"summary: {out_root}/summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
