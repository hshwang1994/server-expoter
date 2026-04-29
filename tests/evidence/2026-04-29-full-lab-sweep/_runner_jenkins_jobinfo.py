"""Inspect gather jobs — config.xml + parameter definitions + last build."""
import json
import paramiko

MASTER = "10.100.64.152"
SSH_USER = "cloviradmin"
SSH_PASS = __import__("os").environ["LAB_SSH_PASS"]
JK_URL = "http://localhost:8080"
JK_USER = "cloviradmin"
JK_PASS = __import__("os").environ["LAB_SSH_PASS"]

JOBS = ["clovirone-server-gather", "grafana-server-gather", "hshwang-gather"]


def ssh_exec(cmd: str, timeout: int = 30):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(MASTER, username=SSH_USER, password=SSH_PASS, timeout=15)
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    rc = stdout.channel.recv_exit_status()
    c.close()
    return out, err, rc


def main():
    findings = {}
    for job in JOBS:
        # Job api/json with parameters
        cmd = (
            f"curl -sS -m 10 -u '{JK_USER}:{JK_PASS}' "
            f"'{JK_URL}/job/{job}/api/json?tree=name,buildable,description,"
            f"property%5BparameterDefinitions%5BdefaultParameterValue%5Bvalue%5D,name,type,choices%5D%5D,"
            f"lastBuild%5Bnumber,result,timestamp%5D,lastSuccessfulBuild%5Bnumber%5D'"
        )
        out, err, rc = ssh_exec(cmd)
        try:
            findings[job] = {"rc": rc, "data": json.loads(out)}
        except Exception as e:
            findings[job] = {"rc": rc, "raw": out[:1500], "err": str(e)}

        # Last build console (50 lines tail)
        cmd2 = (
            f"curl -sS -m 10 -u '{JK_USER}:{JK_PASS}' "
            f"'{JK_URL}/job/{job}/lastBuild/consoleText' 2>&1 | tail -60"
        )
        out2, _, _ = ssh_exec(cmd2)
        findings[job]["last_console_tail"] = out2[-3000:]

    out_path = "tests/evidence/2026-04-29-full-lab-sweep/_jobinfo.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, ensure_ascii=False, indent=2)
    print(f"WROTE {out_path}")


if __name__ == "__main__":
    main()
