#!/usr/bin/env python3
"""gather_os_full.py — OS 종합 정보 수집 (Linux + Windows).

목적: ansible setup (full facts) + 광범위 shell 명령 출력을
      distro/ip별 디렉터리에 raw 저장. 향후 schema 추가 / 매핑 검증용.

전제: WSL (ansible / sshpass / pywinrm 설치된 환경)에서 실행 권장.
사용:
    wsl python3 tests/reference/scripts/gather_os_full.py
    wsl python3 tests/reference/scripts/gather_os_full.py --target rhel810-10.100.64.161
    wsl python3 tests/reference/scripts/gather_os_full.py --linux-only
    wsl python3 tests/reference/scripts/gather_os_full.py --skip-existing

저장 위치:
    tests/reference/os/<distro>/<ip>/
      ├── _manifest.json
      ├── ansible_setup.json     — ansible setup 모듈 전체 facts
      ├── cmd_<name>.txt         — 각 shell 명령 출력
      └── _summary.txt
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


REPO_ROOT = Path(__file__).resolve().parents[3]
TARGETS_FILE = REPO_ROOT / "tests" / "reference" / "local" / "targets.yaml"
OUTPUT_BASE = REPO_ROOT / "tests" / "reference" / "os"

# Linux 명령 카탈로그 — 광범위 수집. 실패해도 계속.
LINUX_COMMANDS: list[tuple[str, str, bool]] = [
    # name, command, requires_root
    # === System ID ===
    ("hostnamectl",          "hostnamectl status 2>&1",                              False),
    ("uname",                "uname -a",                                             False),
    ("os_release",           "cat /etc/os-release",                                  False),
    ("redhat_release",       "cat /etc/redhat-release 2>/dev/null || echo N/A",     False),
    ("uptime",               "uptime; cat /proc/uptime",                             False),
    ("timedatectl",          "timedatectl 2>&1",                                     False),
    ("machine_id",           "cat /etc/machine-id 2>/dev/null",                      False),

    # === Hardware (DMI/SMBIOS) ===
    ("dmidecode_full",       "dmidecode 2>&1",                                       True),
    ("dmidecode_system",     "dmidecode -t system 2>&1",                             True),
    ("dmidecode_chassis",    "dmidecode -t chassis 2>&1",                            True),
    ("dmidecode_baseboard",  "dmidecode -t baseboard 2>&1",                          True),
    ("dmidecode_processor",  "dmidecode -t processor 2>&1",                          True),
    ("dmidecode_memory",     "dmidecode -t memory 2>&1",                             True),
    ("dmidecode_bios",       "dmidecode -t bios 2>&1",                               True),
    ("dmidecode_oem",        "dmidecode -t oem-strings 2>&1",                        True),

    # === CPU ===
    ("lscpu",                "lscpu",                                                False),
    ("lscpu_json",           "lscpu -J 2>&1",                                        False),
    ("cpuinfo",              "cat /proc/cpuinfo",                                    False),
    ("cpu_topology",         "lscpu -e 2>&1",                                        False),
    ("cpu_freq_cur",         "cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq 2>/dev/null | head -20", False),

    # === Memory ===
    ("meminfo",              "cat /proc/meminfo",                                    False),
    ("free_h",               "free -h",                                              False),
    ("vmstat",               "vmstat 1 1",                                           False),
    ("swap",                 "swapon --show 2>&1",                                   False),

    # === Storage ===
    ("lsblk_json",           "lsblk -JO 2>&1",                                       False),
    ("lsblk_tree",           "lsblk -f",                                             False),
    ("df_h",                 "df -hT",                                               False),
    ("findmnt_json",         "findmnt -J 2>&1",                                      False),
    ("blkid",                "blkid 2>&1",                                           True),
    ("smartctl_scan",        "smartctl --scan 2>/dev/null",                          True),
    ("smartctl_all",         "for d in $(lsblk -dno NAME | grep -E '^(sd|nvme|hd)'); do echo '=== /dev/'$d' ==='; smartctl -a /dev/$d 2>&1; done", True),
    ("nvme_list",            "nvme list 2>&1",                                       True),
    ("mdstat",               "cat /proc/mdstat 2>/dev/null",                         False),
    ("lvm_pv",               "pvs 2>&1; pvdisplay 2>&1",                             True),
    ("lvm_vg",               "vgs 2>&1; vgdisplay 2>&1",                             True),
    ("lvm_lv",               "lvs 2>&1; lvdisplay 2>&1",                             True),
    ("multipath",            "multipath -ll 2>&1",                                   True),
    ("storcli",              "/opt/MegaRAID/storcli/storcli64 /call show all J 2>&1; storcli /call show all J 2>&1", True),

    # === Network ===
    ("ip_addr",              "ip -j addr 2>&1",                                      False),
    ("ip_link",              "ip -j link 2>&1",                                      False),
    ("ip_route",             "ip -j route 2>&1",                                     False),
    ("ip_route6",            "ip -6 -j route 2>&1",                                  False),
    ("ip_neigh",             "ip -j neigh 2>&1",                                     False),
    ("ip_tunnel",            "ip -j tunnel show 2>&1",                               False),
    ("ip_vrf",               "ip -j vrf show 2>&1",                                  False),
    ("bridge_link",          "bridge -j link show 2>&1",                             False),
    ("bridge_vlan",          "bridge -j vlan show 2>&1",                             False),
    ("bonding",              "for b in /proc/net/bonding/*; do [ -f $b ] && echo '=== '$b' ===' && cat $b; done 2>/dev/null", False),
    ("ss_listen",            "ss -tlnpu 2>&1",                                       True),
    ("ss_estab",             "ss -tnp state established 2>&1",                       True),
    ("ethtool_all",          "for i in $(ip -o link show | awk -F': ' '{print $2}' | sed 's/@.*//'); do echo '=== '$i' ==='; ethtool $i 2>&1; ethtool -i $i 2>&1; ethtool -k $i 2>&1; done", True),
    ("nmcli",                "nmcli -t -f all device 2>&1; nmcli -t -f all connection 2>&1", False),
    ("resolv_conf",          "cat /etc/resolv.conf",                                 False),
    ("hosts_file",           "cat /etc/hosts",                                       False),
    ("nsswitch",             "cat /etc/nsswitch.conf",                               False),
    ("firewall_iptables",    "iptables -L -n -v 2>&1; iptables-save 2>&1",          True),
    ("firewall_nft",         "nft list ruleset 2>&1",                                True),
    ("firewall_firewalld",   "firewall-cmd --list-all 2>&1; firewall-cmd --get-active-zones 2>&1", True),

    # === PCI / USB / OEM ===
    ("lspci_v",              "lspci -vv 2>&1",                                       True),
    ("lspci_nn",             "lspci -nn 2>&1",                                       False),
    ("lspci_tree",           "lspci -tv 2>&1",                                       False),
    ("lsusb",                "lsusb -v 2>&1",                                        True),
    ("lsusb_tree",           "lsusb -t",                                             False),
    ("lshw",                 "lshw -json 2>&1",                                      True),
    ("lshw_short",           "lshw -short 2>&1",                                     True),
    ("inxi",                 "inxi -Fxz 2>&1",                                       False),
    ("hwinfo",               "hwinfo --short 2>&1",                                  True),

    # === BIOS / Firmware ===
    ("biosdecode",           "biosdecode 2>&1",                                      True),
    ("efivars",              "ls /sys/firmware/efi/efivars 2>/dev/null | head -50",  False),
    ("ipmitool_mc",          "ipmitool mc info 2>&1",                                True),
    ("ipmitool_lan",         "ipmitool lan print 2>&1",                              True),
    ("ipmitool_sel",         "ipmitool sel list 2>&1 | tail -50",                    True),
    ("ipmitool_sensor",      "ipmitool sensor list 2>&1",                            True),
    ("ipmitool_chassis",     "ipmitool chassis status 2>&1",                         True),
    ("ipmitool_fru",         "ipmitool fru list 2>&1",                               True),
    ("idrac_racadm",         "racadm getsysinfo 2>&1; racadm hwinventory 2>&1",      True),

    # === Kernel / Module ===
    ("kernel_cmdline",       "cat /proc/cmdline",                                    False),
    ("loaded_modules",       "lsmod",                                                False),
    ("kernel_log_tail",      "dmesg -T 2>&1 | tail -200",                            True),
    ("sysctl_all",           "sysctl -a 2>/dev/null",                                False),

    # === Services / Process ===
    ("systemctl_list",       "systemctl list-units --type=service --all --no-pager 2>&1", False),
    ("systemctl_failed",     "systemctl --failed --no-pager 2>&1",                   False),
    ("systemctl_timers",     "systemctl list-timers --all --no-pager 2>&1",          False),
    ("ps_aux",               "ps auxfww",                                            False),
    ("crontab_root",         "crontab -l 2>/dev/null; ls -la /etc/cron.* 2>&1",     True),

    # === Packages ===
    ("rpm_qa",               "rpm -qa --queryformat '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}\\n' 2>/dev/null | sort", False),
    ("dpkg_l",               "dpkg -l 2>/dev/null",                                  False),
    ("yum_repolist",         "yum repolist all 2>&1; dnf repolist all 2>&1",         False),
    ("apt_sources",          "cat /etc/apt/sources.list 2>/dev/null; ls /etc/apt/sources.list.d/ 2>/dev/null", False),

    # === Users / Auth ===
    ("passwd_users",         "getent passwd",                                        False),
    ("groups",               "getent group",                                         False),
    ("ssh_config",           "cat /etc/ssh/sshd_config 2>/dev/null",                 True),
    ("sudoers",              "cat /etc/sudoers 2>/dev/null; ls -la /etc/sudoers.d/ 2>/dev/null", True),
    ("selinux",              "getenforce 2>&1; sestatus 2>&1",                       False),
    ("apparmor",             "aa-status 2>&1",                                       True),
    ("logged_users",         "who; w; last -n 20",                                   False),

    # === Time / Locale ===
    ("locale",               "locale; cat /etc/locale.conf 2>/dev/null",             False),
    ("ntp_status",           "chronyc tracking 2>&1; chronyc sources 2>&1; ntpq -p 2>&1; timedatectl show-timesync 2>&1", False),

    # === Container / Virt ===
    ("virt_what",            "virt-what 2>&1; systemd-detect-virt 2>&1",             True),
    ("docker_info",          "docker version 2>&1; docker info 2>&1; docker ps -a 2>&1", True),
    ("podman_info",          "podman version 2>&1; podman info 2>&1; podman ps -a 2>&1", False),
    ("k8s_kubelet",          "systemctl status kubelet 2>&1 | head -30; kubectl version 2>&1", False),

    # === Disk Power Stats ===
    ("hdparm_sda",           "hdparm -I /dev/sda 2>&1",                              True),

    # === Logs (snapshots) ===
    ("messages_tail",        "tail -200 /var/log/messages 2>/dev/null || tail -200 /var/log/syslog 2>/dev/null", True),
    ("journal_errors",       "journalctl -p err -b --no-pager 2>&1 | tail -100",     True),
]


WINDOWS_COMMANDS: list[tuple[str, str]] = [
    ("os_caption",           "Get-CimInstance Win32_OperatingSystem | Select-Object * | ConvertTo-Json -Depth 4"),
    ("computer_system",      "Get-CimInstance Win32_ComputerSystem | Select-Object * | ConvertTo-Json -Depth 4"),
    ("bios",                 "Get-CimInstance Win32_BIOS | Select-Object * | ConvertTo-Json -Depth 4"),
    ("baseboard",            "Get-CimInstance Win32_BaseBoard | Select-Object * | ConvertTo-Json -Depth 4"),
    ("system_enclosure",     "Get-CimInstance Win32_SystemEnclosure | Select-Object * | ConvertTo-Json -Depth 4"),
    ("processor",            "Get-CimInstance Win32_Processor | Select-Object * | ConvertTo-Json -Depth 4"),
    ("memory_module",        "Get-CimInstance Win32_PhysicalMemory | Select-Object * | ConvertTo-Json -Depth 4"),
    ("disk_drive",           "Get-CimInstance Win32_DiskDrive | Select-Object * | ConvertTo-Json -Depth 4"),
    ("logical_disk",         "Get-CimInstance Win32_LogicalDisk | Select-Object * | ConvertTo-Json -Depth 4"),
    ("volume",               "Get-CimInstance Win32_Volume | Select-Object * | ConvertTo-Json -Depth 4"),
    ("partition",            "Get-CimInstance Win32_DiskPartition | Select-Object * | ConvertTo-Json -Depth 4"),
    ("network_adapter",      "Get-NetAdapter | Select-Object * | ConvertTo-Json -Depth 4"),
    ("ip_config",            "Get-NetIPConfiguration -All | ConvertTo-Json -Depth 6"),
    ("dns_client",           "Get-DnsClientServerAddress | ConvertTo-Json -Depth 4"),
    ("route_print",          "Get-NetRoute | ConvertTo-Json -Depth 4"),
    ("services",             "Get-Service | Select-Object Name, Status, StartType, DisplayName | ConvertTo-Json -Depth 4"),
    ("processes",            "Get-Process | Select-Object Id, ProcessName, Path, Company, Description | ConvertTo-Json -Depth 4"),
    ("hotfix",               "Get-HotFix | Select-Object * | ConvertTo-Json -Depth 4"),
    ("env",                  "[Environment]::GetEnvironmentVariables() | ConvertTo-Json -Depth 4"),
    ("system_info",          "systeminfo /FO CSV"),
    ("ipconfig_all",         "ipconfig /all"),
    ("netstat_ano",          "netstat -ano"),
    ("powercfg",             "powercfg /list"),
    ("local_users",          "Get-LocalUser | ConvertTo-Json -Depth 4; Get-LocalGroup | ConvertTo-Json -Depth 4"),
    ("firewall_profile",     "Get-NetFirewallProfile | ConvertTo-Json -Depth 4"),
    ("installed_features",   "Get-WindowsOptionalFeature -Online 2>&1 | Where-Object State -eq Enabled | Select-Object FeatureName, State | ConvertTo-Json -Depth 4"),
    ("video_controller",     "Get-CimInstance Win32_VideoController | Select-Object * | ConvertTo-Json -Depth 4"),
    ("driver",               "Get-WmiObject Win32_PnPSignedDriver | Select-Object DeviceName, Manufacturer, DriverVersion, DriverDate, ClassGuid | ConvertTo-Json -Depth 4"),
    ("event_system_errors",  "Get-WinEvent -LogName System -MaxEvents 100 -ErrorAction SilentlyContinue | Where-Object {$_.LevelDisplayName -eq 'Error'} | Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message | ConvertTo-Json -Depth 4"),
]


def load_targets() -> dict[str, Any]:
    if not TARGETS_FILE.exists():
        print(f"ERROR: {TARGETS_FILE} 없음", file=sys.stderr)
        sys.exit(2)
    with TARGETS_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_ssh_command(host: str, user: str, password: str, cmd: str, timeout: int = 60, become: bool = False, become_pw: str | None = None) -> tuple[int, str, str]:
    """paramiko SSH command runner. become=True 시 sudo -S 사용."""
    try:
        import paramiko
    except ImportError:
        return -1, "", "paramiko not installed"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=15, banner_timeout=15, auth_timeout=15, look_for_keys=False, allow_agent=False)
    except Exception as e:
        return -1, "", f"SSH connect fail: {e}"

    try:
        if become and become_pw:
            full_cmd = f"sudo -S -p '' bash -c {bash_quote(cmd)}"
            stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout, get_pty=True)
            stdin.write(become_pw + "\n")
            stdin.flush()
        else:
            stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err
    except Exception as e:
        return -1, "", f"exec fail: {e}"
    finally:
        client.close()


def bash_quote(s: str) -> str:
    return "'" + s.replace("'", "'\"'\"'") + "'"


def run_winrm_command(host: str, user: str, password: str, cmd: str, timeout: int = 120) -> tuple[int, str, str]:
    try:
        import winrm  # type: ignore
    except ImportError:
        return -1, "", "pywinrm not installed"
    try:
        s = winrm.Session(f"https://{host}:5986/wsman", auth=(user, password), transport="ntlm", server_cert_validation="ignore", read_timeout_sec=timeout, operation_timeout_sec=timeout - 10)
        r = s.run_ps(cmd)
        return r.status_code, r.std_out.decode("utf-8", errors="replace"), r.std_err.decode("utf-8", errors="replace")
    except Exception as e:
        # HTTPS 실패 시 HTTP 5985 fallback
        try:
            s = winrm.Session(f"http://{host}:5985/wsman", auth=(user, password), transport="ntlm", read_timeout_sec=timeout, operation_timeout_sec=timeout - 10)
            r = s.run_ps(cmd)
            return r.status_code, r.std_out.decode("utf-8", errors="replace"), r.std_err.decode("utf-8", errors="replace")
        except Exception as e2:
            return -1, "", f"winrm fail https={e}, http={e2}"


def gather_linux(target: dict[str, Any], skip_existing: bool = False) -> dict[str, Any]:
    name = target["name"]
    ip = target["ip"]
    user = target["user"]
    password = target["password"]
    distro = target["distro"]
    become_pw = target.get("become_password", password)

    out_dir = OUTPUT_BASE / distro / ip.replace(".", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== Linux: {name} ({ip}) → {out_dir.relative_to(REPO_ROOT)} ===")

    summary: dict[str, Any] = {"target": name, "ip": ip, "distro": distro, "started_at": datetime.now(timezone.utc).isoformat(), "commands": [], "errors": []}
    started = time.monotonic()

    # 1. 연결 테스트
    rc, out, err = run_ssh_command(ip, user, password, "echo OK", timeout=10)
    if rc != 0:
        summary["errors"].append({"step": "connect", "rc": rc, "err": err})
        print(f"  CONNECT FAIL: {err}")
        return summary
    print(f"  CONNECT OK")

    # 2. 각 명령 실행
    for cmd_name, cmd, requires_root in LINUX_COMMANDS:
        out_file = out_dir / f"cmd_{cmd_name}.txt"
        if skip_existing and out_file.exists() and out_file.stat().st_size > 0:
            summary["commands"].append({"name": cmd_name, "status": "cached"})
            continue
        rc, out, err = run_ssh_command(ip, user, password, cmd, timeout=120, become=requires_root, become_pw=become_pw)
        with out_file.open("w", encoding="utf-8") as f:
            f.write(f"# command: {cmd}\n# rc: {rc}\n# requires_root: {requires_root}\n# fetched: {datetime.now(timezone.utc).isoformat()}\n#\n")
            f.write(out)
            if err.strip():
                f.write("\n# === stderr ===\n")
                f.write(err)
        summary["commands"].append({"name": cmd_name, "rc": rc, "size": len(out)})
        tag = "OK" if rc == 0 else f"rc={rc}"
        print(f"  [{tag:8s}] {cmd_name:25s} ({len(out):8d}b)")

    # 3. ansible setup (별도 실행 — 실패해도 계속)
    setup_file = out_dir / "ansible_setup.json"
    if not (skip_existing and setup_file.exists() and setup_file.stat().st_size > 0):
        try:
            inv_line = f"{ip} ansible_user={user} ansible_password={password} ansible_become_password={become_pw} ansible_host_key_checking=False ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'"
            inv_path = out_dir / "_inventory.tmp"
            inv_path.write_text(f"[target]\n{inv_line}\n")
            cp = subprocess.run(["ansible", "target", "-i", str(inv_path), "-m", "setup"], capture_output=True, text=True, timeout=180)
            # ansible setup output: "ip | SUCCESS => { ... }"
            stdout = cp.stdout
            if "=>" in stdout:
                json_part = stdout.split("=>", 1)[1].strip()
                try:
                    data = json.loads(json_part)
                    setup_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
                    print(f"  [OK     ] ansible_setup            ({len(json_part):8d}b)")
                    summary["commands"].append({"name": "ansible_setup", "rc": 0, "size": len(json_part)})
                except json.JSONDecodeError as je:
                    setup_file.write_text(f"# json decode err: {je}\n# raw stdout:\n{stdout}\n# stderr:\n{cp.stderr}")
                    summary["errors"].append({"step": "ansible_setup_decode", "err": str(je)})
            else:
                setup_file.write_text(f"# ansible setup unexpected output\n# stdout:\n{stdout}\n# stderr:\n{cp.stderr}")
                summary["errors"].append({"step": "ansible_setup", "stdout_head": stdout[:300]})
            inv_path.unlink(missing_ok=True)
        except Exception as e:
            summary["errors"].append({"step": "ansible_setup_exception", "err": str(e)})

    summary["elapsed_seconds"] = round(time.monotonic() - started, 1)
    summary["completed_at"] = datetime.now(timezone.utc).isoformat()
    (out_dir / "_manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    lines = [f"# OS Gather — {name}", f"distro: {distro}", f"ip: {ip}", f"elapsed: {summary['elapsed_seconds']}s",
             f"commands: {len(summary['commands'])}", f"errors: {len(summary['errors'])}", ""]
    for c in summary["commands"]:
        lines.append(f"  {c.get('rc','?'):>4}  {c['name']}")
    (out_dir / "_summary.txt").write_text("\n".join(lines))
    print(f"  TOTAL: {len(summary['commands'])} commands, {summary['elapsed_seconds']}s")
    return summary


def gather_windows(target: dict[str, Any], skip_existing: bool = False) -> dict[str, Any]:
    name = target["name"]
    ip = target["ip"]
    user = target["user"]
    password = target["password"]
    distro = target["distro"]

    out_dir = OUTPUT_BASE / distro / ip.replace(".", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== Windows: {name} ({ip}) → {out_dir.relative_to(REPO_ROOT)} ===")

    summary: dict[str, Any] = {"target": name, "ip": ip, "distro": distro, "started_at": datetime.now(timezone.utc).isoformat(), "commands": [], "errors": []}
    started = time.monotonic()

    rc, out, err = run_winrm_command(ip, user, password, "Write-Output OK", timeout=30)
    if rc != 0:
        summary["errors"].append({"step": "connect", "rc": rc, "err": err})
        print(f"  CONNECT FAIL: {err}")
        return summary
    print(f"  CONNECT OK")

    for cmd_name, cmd in WINDOWS_COMMANDS:
        out_file = out_dir / f"ps_{cmd_name}.txt"
        if skip_existing and out_file.exists() and out_file.stat().st_size > 0:
            summary["commands"].append({"name": cmd_name, "status": "cached"})
            continue
        rc, out, err = run_winrm_command(ip, user, password, cmd, timeout=120)
        with out_file.open("w", encoding="utf-8") as f:
            f.write(f"# command: {cmd[:200]}{'...' if len(cmd)>200 else ''}\n# rc: {rc}\n# fetched: {datetime.now(timezone.utc).isoformat()}\n#\n")
            f.write(out)
            if err.strip():
                f.write("\n# === stderr ===\n")
                f.write(err)
        summary["commands"].append({"name": cmd_name, "rc": rc, "size": len(out)})
        tag = "OK" if rc == 0 else f"rc={rc}"
        print(f"  [{tag:8s}] {cmd_name:25s} ({len(out):8d}b)")

    summary["elapsed_seconds"] = round(time.monotonic() - started, 1)
    summary["completed_at"] = datetime.now(timezone.utc).isoformat()
    (out_dir / "_manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", help="단일 target name")
    parser.add_argument("--linux-only", action="store_true")
    parser.add_argument("--windows-only", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--parallel", type=int, default=3, help="동시 실행 host 수")
    args = parser.parse_args()

    targets_doc = load_targets()
    os_targets = targets_doc.get("os", [])
    if args.target:
        os_targets = [t for t in os_targets if t["name"] == args.target]

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    linux_targets = [t for t in os_targets if t.get("transport") != "winrm" and not args.windows_only]
    windows_targets = [t for t in os_targets if t.get("transport") == "winrm" and not args.linux_only]

    print(f"OS gather — Linux={len(linux_targets)} Windows={len(windows_targets)} (parallel={args.parallel})")

    results = []
    with ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futures = {ex.submit(gather_linux, t, args.skip_existing): t for t in linux_targets}
        for w in windows_targets:
            futures[ex.submit(gather_windows, w, args.skip_existing)] = w
        for f in as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                t = futures[f]
                results.append({"target": t["name"], "error": str(e)})

    print(f"\n{'='*60}\n  TOTAL SUMMARY\n{'='*60}")
    for r in results:
        if "error" in r:
            print(f"  ERROR  {r['target']}: {r['error']}")
        else:
            n_cmd = len(r.get("commands", []))
            n_err = len(r.get("errors", []))
            elapsed = r.get("elapsed_seconds", 0)
            print(f"  {r['target']:35s} cmds={n_cmd:3d} err={n_err:2d} elapsed={elapsed:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
