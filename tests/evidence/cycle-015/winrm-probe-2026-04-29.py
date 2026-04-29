"""cycle-015 — WinRM probe (Win Server 2022 10.100.64.135).

pywinrm으로 인증 + 핵심 PowerShell 실행 (Windows gather raw 검증).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import winrm
import yaml

LAB_CREDS = Path(__file__).resolve().parents[3] / "vault" / ".lab-credentials.yml"


def probe(host: dict) -> dict:
    ip = host["host"]
    user = host["winrm_user"]
    pwd = host["winrm_password"]
    port = host.get("winrm_port", 5985)

    result: dict = {"ip": ip, "distro": host["distro"], "user": user, "port": port}
    try:
        session = winrm.Session(
            f"http://{ip}:{port}/wsman",
            auth=(user, pwd),
            transport="ntlm",
            server_cert_validation="ignore",
        )

        # 1. PowerShell 응답 기본
        r = session.run_ps("$PSVersionTable.PSVersion.ToString()")
        result["ps_version"] = r.std_out.decode().strip() if r.status_code == 0 else None
        result["ps_status"] = r.status_code

        # 2. OS 정보 (gather_system 시나리오)
        r = session.run_ps(
            "Get-CimInstance Win32_OperatingSystem | "
            "Select-Object Caption,Version,BuildNumber,OSArchitecture | "
            "ConvertTo-Json -Compress"
        )
        if r.status_code == 0:
            result["os_info"] = json.loads(r.std_out.decode())

        # 3. Memory (gather_memory)
        r = session.run_ps(
            "(Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum"
        )
        if r.status_code == 0 and r.std_out.strip():
            try:
                result["mem_total_gb"] = round(int(r.std_out.decode().strip()) / 1024 / 1024 / 1024, 1)
            except ValueError:
                pass

        # 4. CPU (gather_cpu)
        r = session.run_ps(
            "Get-CimInstance Win32_Processor | "
            "Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | "
            "ConvertTo-Json -Compress"
        )
        if r.status_code == 0:
            try:
                result["cpu_info"] = json.loads(r.std_out.decode())
            except json.JSONDecodeError:
                pass

        # 5. NIC count (gather_network)
        r = session.run_ps(
            "(Get-NetAdapter | Where-Object Status -eq 'Up').Count"
        )
        if r.status_code == 0:
            try:
                result["nic_up_count"] = int(r.std_out.decode().strip())
            except ValueError:
                pass

        result["winrm_ok"] = True
    except Exception as e:
        result["winrm_ok"] = False
        result["error"] = f"{type(e).__name__}: {e}"[:200]

    return result


def main() -> int:
    creds = yaml.safe_load(LAB_CREDS.read_text(encoding="utf-8"))
    hosts = creds.get("os_targets_windows", [])
    print(f"=== Windows WinRM probe ({len(hosts)} 호스트) ===\n")

    results = []
    for h in hosts:
        r = probe(h)
        results.append(r)
        if r.get("winrm_ok"):
            os = r.get("os_info", {})
            print(f"[PASS] {r['ip']} ({r['distro']})")
            print(f"  OS         : {os.get('Caption', '?')} build {os.get('BuildNumber', '?')}")
            print(f"  PS         : {r.get('ps_version', '?')}")
            print(f"  Mem        : {r.get('mem_total_gb', '?')} GB")
            cpu = r.get("cpu_info") or {}
            if isinstance(cpu, dict):
                print(f"  CPU        : {cpu.get('Name', '?')[:50]} cores={cpu.get('NumberOfCores', '?')}")
            print(f"  NIC up     : {r.get('nic_up_count', '?')}")
        else:
            print(f"[FAIL] {r['ip']} — {r.get('error', '?')}")

    out = Path(__file__).parent / "winrm-probe-2026-04-29.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n결과: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
