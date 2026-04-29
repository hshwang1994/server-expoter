"""List Jenkins agent nodes + labels."""
import json
import paramiko

MASTER = "10.100.64.152"
SSH_USER = "cloviradmin"
SSH_PASS = __import__("os").environ["LAB_SSH_PASS"]
JK_URL = "http://localhost:8080"
JK_USER = "cloviradmin"
JK_PASS = __import__("os").environ["LAB_SSH_PASS"]


def ssh_exec(cmd):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(MASTER, username=SSH_USER, password=SSH_PASS, timeout=15)
    stdin, stdout, stderr = c.exec_command(cmd, timeout=30)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    rc = stdout.channel.recv_exit_status()
    c.close()
    return out, err, rc


def main():
    # /computer/api/json includes labels
    cmd = (
        f"curl -sS -m 10 -u '{JK_USER}:{JK_PASS}' "
        f"'{JK_URL}/computer/api/json?tree=computer%5BdisplayName,offline,assignedLabels%5Bname%5D%5D'"
    )
    out, err, rc = ssh_exec(cmd)
    data = json.loads(out)
    nodes = []
    for n in data.get("computer", []):
        nodes.append({
            "name": n.get("displayName"),
            "offline": n.get("offline"),
            "labels": [l.get("name") for l in n.get("assignedLabels", [])],
        })
    out_path = "tests/evidence/2026-04-29-full-lab-sweep/_nodes.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes}, f, ensure_ascii=False, indent=2)
    print(f"WROTE {out_path}")
    for n in nodes:
        print(n)


if __name__ == "__main__":
    main()
