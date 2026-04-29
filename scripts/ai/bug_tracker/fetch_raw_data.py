#!/usr/bin/env python3
"""Fetch all raw data from agent to local mirror for analysis."""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_ops import _client

REMOTE_REDFISH = "/tmp/se-raw"
REMOTE_OS = "/tmp/se-raw-os"
LOCAL_BASE = Path(__file__).resolve().parents[3] / "tests" / "evidence" / "2026-04-29-deep-verify"


def fetch_dir(sftp, remote_dir: str, local_dir: Path) -> int:
    local_dir.mkdir(parents=True, exist_ok=True)
    try:
        entries = sftp.listdir(remote_dir)
    except IOError:
        return 0
    n = 0
    for e in entries:
        rp = f"{remote_dir}/{e}"
        lp = local_dir / e
        try:
            attrs = sftp.stat(rp)
        except IOError:
            continue
        if attrs.st_mode and (attrs.st_mode & 0o40000):  # dir
            n += fetch_dir(sftp, rp, lp)
        else:
            try:
                sftp.get(rp, str(lp))
                n += 1
            except IOError:
                pass
    return n


def main() -> int:
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    c = _client()
    try:
        sftp = c.open_sftp()
        rf_local = LOCAL_BASE / "redfish"
        os_local = LOCAL_BASE / "linux"
        n_rf = fetch_dir(sftp, REMOTE_REDFISH, rf_local)
        n_os = fetch_dir(sftp, REMOTE_OS, os_local)
        print(f"redfish: {n_rf} files -> {rf_local}")
        print(f"linux:   {n_os} files -> {os_local}")
        sftp.close()
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
