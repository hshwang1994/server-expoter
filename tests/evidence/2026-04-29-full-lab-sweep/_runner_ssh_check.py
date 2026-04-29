"""SSH connectivity test for Jenkins master + agent — autonomous lab sweep.

Tests cloviradmin@10.100.64.{152,153,154,155} reachability + sudo + key facts.
Output: stdout JSON summary.
"""
import json
import sys
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed

HOSTS = [
    ("master-152", "10.100.64.152"),
    ("master-153", "10.100.64.153"),
    ("agent-154", "10.100.64.154"),
    ("agent-155", "10.100.64.155"),
]
USER = "cloviradmin"
PASS = __import__("os").environ["LAB_SSH_PASS"]
TIMEOUT = 10


def probe(name: str, ip: str) -> dict:
    result = {"name": name, "ip": ip, "ok": False, "facts": {}, "error": None}
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(ip, username=USER, password=PASS, timeout=TIMEOUT, banner_timeout=TIMEOUT)
        # core facts
        cmds = {
            "hostname": "hostname",
            "os": "cat /etc/os-release | grep -E '^PRETTY_NAME|^VERSION_ID' | head -2",
            "uname": "uname -r",
            "java": "java -version 2>&1 | head -1",
            "ansible": "ansible --version 2>&1 | head -1 || echo 'NO_ANSIBLE'",
            "jenkins_proc": "ps -ef | grep -E 'jenkins|java -jar' | grep -v grep | head -3",
            "jenkins_url_hint": "ss -tlnp 2>/dev/null | grep -E ':(8080|8443|80|443)' | head -3 || sudo -n ss -tlnp 2>&1 | grep -E ':(8080|8443)' | head -3",
            "sudo": "sudo -n true 2>&1 && echo 'SUDO_OK' || echo 'SUDO_NEEDS_PASS'",
        }
        for k, cmd in cmds.items():
            stdin, stdout, stderr = c.exec_command(cmd, timeout=15)
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            result["facts"][k] = (out or err)[:500]
        result["ok"] = True
        c.close()
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def main():
    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(probe, n, ip): n for n, ip in HOSTS}
        for f in as_completed(futs):
            results.append(f.result())
    results.sort(key=lambda r: r["ip"])
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not all(r["ok"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
