"""Try Jenkins auth as cloviradmin / hshwang1994 with given password."""
import json
import paramiko

MASTER = "10.100.64.152"
SSH_USER = "cloviradmin"
SSH_PASS = __import__("os").environ["LAB_SSH_PASS"]
JK_URL = "http://localhost:8080"

_PW = __import__("os").environ["LAB_SSH_PASS"]
CANDIDATES = [
    ("cloviradmin", _PW),
    ("hshwang1994", _PW),
    ("root", _PW),
    ("admin", _PW),
]


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
    out_all = {}
    for u, p in CANDIDATES:
        # whoAmI with basic auth
        cmd = f"curl -sS -m 10 -u '{u}:{p}' {JK_URL}/whoAmI/api/json"
        out, err, rc = ssh_exec(cmd)
        out_all[u] = {"rc": rc, "preview": out[:300], "err": err[:200]}

    # Also list Jenkins jobs with the first user that authenticates
    auth_user = None
    auth_pass = None
    for u, p in CANDIDATES:
        info = out_all.get(u, {}).get("preview", "")
        if '"authenticated":true' in info and '"anonymous":false' in info:
            auth_user, auth_pass = u, p
            break
    out_all["_first_auth_user"] = auth_user

    if auth_user:
        # Get crumb
        crumb_cmd = (
            f"curl -sS -m 10 -u '{auth_user}:{auth_pass}' "
            f"'{JK_URL}/crumbIssuer/api/json'"
        )
        co, _, crc = ssh_exec(crumb_cmd)
        out_all["crumb"] = {"rc": crc, "preview": co[:400]}

        # List jobs (escape brackets via URL encode)
        jobs_cmd = (
            f"curl -sS -m 10 -u '{auth_user}:{auth_pass}' "
            f"'{JK_URL}/api/json?tree=jobs%5Bname,url,color%5D'"
        )
        jo, _, jrc = ssh_exec(jobs_cmd)
        out_all["jobs_list"] = {"rc": jrc, "preview": jo[:3000]}
        try:
            jobs = json.loads(jo).get("jobs", [])
            out_all["jobs_count"] = len(jobs)
            out_all["job_names"] = [j["name"] for j in jobs]
            out_all["server_exporter_jobs"] = [j for j in jobs if "server-exporter" in j.get("name", "").lower() or "gather" in j.get("name", "").lower()]
        except Exception as e:
            out_all["jobs_parse_err"] = str(e)

    print(json.dumps(out_all, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
