#!/usr/bin/env python3
"""SSH ops helper for Jenkins agent — paramiko-based password auth.

Usage:
    python scripts/ai/bug_tracker/agent_ops.py sync-branch
    python scripts/ai/bug_tracker/agent_ops.py exec '<bash command>'
    python scripts/ai/bug_tracker/agent_ops.py fetch '<remote path>' '<local path>'
    python scripts/ai/bug_tracker/agent_ops.py raw-capture
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from pathlib import Path

import paramiko

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

AGENT_HOST = os.environ.get("SE_AGENT_HOST", "10.100.64.154")
AGENT_USER = os.environ.get("SE_AGENT_USER", "cloviradmin")
AGENT_PASS = os.environ.get("SE_AGENT_PASS", "Goodmit0802!")
AGENT_WS = os.environ.get(
    "SE_AGENT_WORKSPACE", "/home/cloviradmin/jenkins-agent/workspace/hshwang-gather"
)
BRANCH = os.environ.get("SE_BRANCH", "fix/output-quality-99bugs-2026-04-29")


def _client() -> paramiko.SSHClient:
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(
        AGENT_HOST,
        username=AGENT_USER,
        password=AGENT_PASS,
        timeout=20,
        allow_agent=False,
        look_for_keys=False,
    )
    return c


def exec_remote(cmd: str, timeout: int = 600) -> tuple[int, str, str]:
    c = _client()
    try:
        si, so, se = c.exec_command(cmd, timeout=timeout)
        out = so.read().decode(errors="replace")
        err = se.read().decode(errors="replace")
        rc = so.channel.recv_exit_status()
        return rc, out, err
    finally:
        c.close()


def sync_branch() -> int:
    cmd = (
        f"cd {AGENT_WS} && "
        "git fetch origin --prune --quiet && "
        f"git checkout -B {BRANCH} origin/{BRANCH} 2>&1 | tail -3 && "
        f"git log -1 --oneline && "
        f"git status --short | head -10"
    )
    rc, out, err = exec_remote(cmd)
    print(out)
    if err:
        print(f"[stderr]\n{err}", file=sys.stderr)
    return rc


def fetch_remote(remote: str, local: str) -> int:
    Path(local).parent.mkdir(parents=True, exist_ok=True)
    c = _client()
    try:
        sftp = c.open_sftp()
        if remote.endswith("/"):
            # Directory recursive fetch (1-level for now)
            for entry in sftp.listdir(remote):
                rp = remote + entry
                lp = os.path.join(local, entry)
                try:
                    sftp.get(rp, lp)
                    print(f"  fetched {rp} -> {lp}")
                except IOError as e:
                    print(f"  skip {rp}: {e}")
        else:
            sftp.get(remote, local)
            print(f"  fetched {remote} -> {local}")
        sftp.close()
        return 0
    finally:
        c.close()


def put_remote(local: str, remote: str) -> int:
    c = _client()
    try:
        sftp = c.open_sftp()
        sftp.put(local, remote)
        print(f"  uploaded {local} -> {remote}")
        sftp.close()
        return 0
    finally:
        c.close()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("op", choices=["sync-branch", "exec", "fetch", "put", "raw-capture"])
    p.add_argument("args", nargs="*")
    a = p.parse_args()

    if a.op == "sync-branch":
        return sync_branch()
    if a.op == "exec":
        if not a.args:
            print("usage: exec '<command>'", file=sys.stderr)
            return 2
        rc, out, err = exec_remote(a.args[0])
        print(out, end="")
        if err:
            print(f"[stderr]\n{err}", file=sys.stderr, end="")
        return rc
    if a.op == "fetch":
        if len(a.args) < 2:
            print("usage: fetch <remote> <local>", file=sys.stderr)
            return 2
        return fetch_remote(a.args[0], a.args[1])
    if a.op == "put":
        if len(a.args) < 2:
            print("usage: put <local> <remote>", file=sys.stderr)
            return 2
        return put_remote(a.args[0], a.args[1])
    return 1


if __name__ == "__main__":
    sys.exit(main())
