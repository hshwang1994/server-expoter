"""Quick status check — last 3 builds of hshwang-gather."""
import json
import paramiko

MASTER = "10.100.64.152"
SSH_USER = "cloviradmin"
SSH_PASS = __import__("os").environ["LAB_SSH_PASS"]
JK_URL = "http://localhost:8080"
JK_USER = "cloviradmin"
JK_PASS = __import__("os").environ["LAB_SSH_PASS"]
JOB = "hshwang-gather"


def ssh_exec(cmd):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(MASTER, username=SSH_USER, password=SSH_PASS, timeout=15)
    stdin, stdout, stderr = c.exec_command(cmd, timeout=30)
    out = stdout.read().decode("utf-8", errors="replace")
    rc = stdout.channel.recv_exit_status()
    c.close()
    return out, rc


def main():
    out, _ = ssh_exec(
        f"curl -sS -m 10 -u '{JK_USER}:{JK_PASS}' "
        f"'{JK_URL}/job/{JOB}/api/json?tree=builds%5Bnumber,result,building,timestamp,duration,actions%5Bparameters%5Bname,value%5D%5D%5D%7B0,5%7D'"
    )
    try:
        data = json.loads(out)
        builds = data.get("builds", [])
        for b in builds[:5]:
            params = {}
            for a in b.get("actions", []):
                if "parameters" in a:
                    for p in a["parameters"]:
                        if p.get("name") in ("loc", "target_type"):
                            params[p["name"]] = p.get("value")
            print(f"#{b['number']:4d} building={b['building']!s:5} result={b.get('result') or '...':<10} target_type={params.get('target_type', '?'):<8} dur_s={(b.get('duration') or 0)/1000:.0f}")
    except Exception as e:
        print(f"PARSE ERR: {e}\nRAW: {out[:500]}")

    # Queue
    qout, _ = ssh_exec(
        f"curl -sS -m 10 -u '{JK_USER}:{JK_PASS}' "
        f"'{JK_URL}/queue/api/json?tree=items%5Bid,task%5Bname%5D,why%5D'"
    )
    try:
        q = json.loads(qout)
        items = q.get("items", [])
        if items:
            print(f"\nQueue: {len(items)} item(s)")
            for it in items:
                print(f"  - {it.get('task', {}).get('name', '?')} (why: {it.get('why', '')[:120]})")
        else:
            print("\nQueue: empty")
    except Exception as e:
        print(f"Q PARSE ERR: {e}")


if __name__ == "__main__":
    main()
