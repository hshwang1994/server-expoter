"""Jenkins discovery — find URL, list jobs, check auth model.

Strategy: SSH to master, run curl locally (loopback), examine /api/json + /script.
"""
import json
import sys
import paramiko

MASTER = "10.100.64.152"
USER = "cloviradmin"
PASS = __import__("os").environ["LAB_SSH_PASS"]
JK_URL = "http://localhost:8080"


def ssh_exec(ip: str, cmd: str, timeout: int = 30) -> tuple[str, str, int]:
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(ip, username=USER, password=PASS, timeout=15)
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    rc = stdout.channel.recv_exit_status()
    c.close()
    return out, err, rc


def main():
    findings = {}

    # 1. Anonymous /api/json (jobs list)
    out, err, rc = ssh_exec(MASTER, f"curl -sS -m 10 {JK_URL}/api/json?tree=jobs[name,url,color,description]")
    findings["anonymous_api_json"] = {"rc": rc, "len": len(out), "preview": out[:800], "err": err[:200]}
    try:
        data = json.loads(out)
        findings["jobs"] = data.get("jobs", [])
    except Exception as e:
        findings["jobs_parse_error"] = str(e)

    # 2. Whoami
    out, err, rc = ssh_exec(MASTER, f"curl -sS -m 10 {JK_URL}/whoAmI/api/json")
    findings["whoami_anonymous"] = {"rc": rc, "preview": out[:300]}

    # 3. Jenkins version
    out, err, rc = ssh_exec(MASTER, f"curl -sSI -m 10 {JK_URL}/ | grep -i 'X-Jenkins'")
    findings["jenkins_version_header"] = out.strip()

    # 4. Crumb (CSRF)
    out, err, rc = ssh_exec(MASTER, f"curl -sS -m 10 {JK_URL}/crumbIssuer/api/json")
    findings["crumb_anonymous"] = {"rc": rc, "preview": out[:300]}

    # 5. Check users dir (admin user existence)
    out, err, rc = ssh_exec(MASTER, "ls -la /var/lib/jenkins/users/ 2>&1 | head -20")
    findings["jenkins_users_dir"] = out[:1000]

    # 6. Check secrets/initialAdminPassword (if first install)
    out, err, rc = ssh_exec(MASTER, "ls -la /var/lib/jenkins/secrets/ 2>&1 | head -10")
    findings["secrets_dir"] = out[:500]

    # 7. Look for a credentials.xml hint of admin
    out, err, rc = ssh_exec(MASTER, "ls /var/lib/jenkins/ 2>&1 | head -20")
    findings["jenkins_home_top"] = out[:500]

    print(json.dumps(findings, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
