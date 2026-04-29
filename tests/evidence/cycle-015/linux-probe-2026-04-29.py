"""cycle-015 AI-13 — Linux 6 호스트 SSH probe + raw fallback 검증.

paramiko로 SSH → Python 버전 감지 → rule 10 R4 (raw fallback) 시나리오 검증.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import paramiko
import yaml

LAB_CREDS = Path(__file__).resolve().parents[3] / "vault" / ".lab-credentials.yml"


@dataclass
class HostResult:
    ip: str
    distro: str
    type: str
    ssh_ok: bool
    python_path: str | None
    python_version: str | None
    python_mode: str  # python_ok / python_missing / python_incompatible
    raw_uname: str | None
    raw_meminfo_total_kb: int | None
    raw_dmidecode_ok: bool
    selinux_status: str | None
    error: str | None


def ssh_exec(ssh: paramiko.SSHClient, cmd: str, timeout: int = 10) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return code, out, err


def probe_host(host: dict) -> HostResult:
    ip = host["host"]
    user = host["ssh_user"]
    pwd = host["ssh_password"]
    distro = host["distro"]
    htype = host["type"]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(
            hostname=ip,
            username=user,
            password=pwd,
            timeout=8,
            allow_agent=False,
            look_for_keys=False,
        )
    except Exception as e:
        return HostResult(
            ip=ip, distro=distro, type=htype,
            ssh_ok=False, python_path=None, python_version=None,
            python_mode="ssh_failed",
            raw_uname=None, raw_meminfo_total_kb=None,
            raw_dmidecode_ok=False, selinux_status=None,
            error=f"{type(e).__name__}: {e}"[:200],
        )

    try:
        # Python 버전 (preflight.yml과 동일 절차)
        py_path: str | None = None
        py_ver: str | None = None
        for cand in ("/usr/bin/python3", "/usr/local/bin/python3", "python3", "python"):
            code, out, err = ssh_exec(ssh, f"command -v {cand}")
            if code == 0 and out:
                py_path = out
                code2, out2, err2 = ssh_exec(ssh, f"{out} -V")
                if code2 == 0:
                    py_ver = (out2 or err2).strip()
                break

        # python_mode 분류 (rule 10 R4)
        if not py_path:
            mode = "python_missing"
        elif py_ver:
            try:
                # "Python 3.6.8" → (3, 6, 8)
                parts = py_ver.split()[1].split(".")
                major, minor = int(parts[0]), int(parts[1])
                if major < 3 or (major == 3 and minor < 9):
                    mode = "python_incompatible"
                else:
                    mode = "python_ok"
            except Exception:
                mode = "python_ok"  # fallback
        else:
            mode = "python_ok"

        # raw 명령들 (gather_*.yml raw fallback 경로 시나리오)
        # 1. uname -a (정상 응답 검증)
        _, uname, _ = ssh_exec(ssh, "uname -a")

        # 2. /proc/meminfo MemTotal (memory section, raw fallback에서 사용)
        code, mt, _ = ssh_exec(ssh, "awk '/^MemTotal:/ {print $2}' /proc/meminfo")
        mem_kb = None
        if code == 0 and mt.isdigit():
            mem_kb = int(mt)

        # 3. dmidecode 가용성 (raw fallback의 hardware section)
        code, _, _ = ssh_exec(ssh, "test -x /usr/sbin/dmidecode || test -x /sbin/dmidecode")
        dmi_ok = code == 0

        # 4. SELinux (raw fallback에서 normalize, RHEL/Rocky 한정)
        code, sel, _ = ssh_exec(ssh, "command -v getenforce >/dev/null && getenforce 2>/dev/null || echo n/a")
        sel_status = sel.strip().lower() if sel else None

        return HostResult(
            ip=ip, distro=distro, type=htype,
            ssh_ok=True, python_path=py_path, python_version=py_ver,
            python_mode=mode,
            raw_uname=uname[:100] if uname else None,
            raw_meminfo_total_kb=mem_kb,
            raw_dmidecode_ok=dmi_ok,
            selinux_status=sel_status,
            error=None,
        )
    finally:
        ssh.close()


def main() -> int:
    creds = yaml.safe_load(LAB_CREDS.read_text(encoding="utf-8"))
    hosts = creds.get("os_targets_linux", [])
    print(f"=== Linux SSH probe + raw fallback 시나리오 ({len(hosts)} 호스트) ===\n")

    print(
        f"{'IP':<16} {'Distro':<14} {'Type':<10} {'SSH':>4} "
        f"{'Py mode':<22} {'Py ver':<14} {'Mem GB':>7} {'DMI':>5} {'SEL':<10}"
    )
    print("-" * 110)

    results: list[HostResult] = []
    for h in hosts:
        r = probe_host(h)
        results.append(r)
        mem_gb = f"{r.raw_meminfo_total_kb / 1024 / 1024:.1f}" if r.raw_meminfo_total_kb else "-"
        py_v = (r.python_version or "-")[:12]
        sel = (r.selinux_status or "-")[:8]
        print(
            f"{r.ip:<16} {r.distro:<14} {r.type:<10} {'OK' if r.ssh_ok else 'FAIL':>4} "
            f"{r.python_mode:<22} {py_v:<14} {mem_gb:>7} {'Y' if r.raw_dmidecode_ok else 'N':>5} {sel:<10}"
        )
        if r.error:
            print(f"    [ERROR] {r.error}")

    out = Path(__file__).parent / "linux-probe-2026-04-29.json"
    out.write_text(
        json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n결과: {out}")

    # rule 10 R4 검증 요약
    print("\n=== rule 10 R4 (Linux 2-tier) 검증 요약 ===")
    by_mode: dict[str, list[str]] = {}
    for r in results:
        by_mode.setdefault(r.python_mode, []).append(r.ip)
    for mode, ips in by_mode.items():
        print(f"  {mode}: {len(ips)} ({', '.join(ips)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
