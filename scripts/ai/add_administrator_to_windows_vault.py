#!/usr/bin/env python3
"""cycle-016 AI-22 fix — vault/windows.yml accounts 에 administrator 추가.

Win Server 2022 (10.100.64.135) 의 NTLM 자격은 administrator/Goodmit0802!.
현재 vault/windows.yml accounts 는 cloviradmin/infraops 만 있어 NTLM 거절.
agent 154 SSH 로 ansible-vault decrypt + entry 추가 + encrypt + 다운로드.
"""
from __future__ import annotations
import sys
import paramiko
import base64

AGENT_HOST = '10.100.64.154'
AGENT_USER = 'cloviradmin'
AGENT_PASS = 'Goodmit0802!'
WS = '/home/cloviradmin/jenkins-agent/workspace/hshwang-gather'

NEW_ACCOUNT = {
    'username': 'administrator',
    'password': 'Goodmit0802!',
    'label': 'lab_win_administrator',
    'role': 'recovery',
}


def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    rc = stdout.channel.recv_exit_status()
    if rc != 0:
        raise RuntimeError(f'cmd={cmd!r} rc={rc}\n{out}\n{err}')
    return out


def main() -> int:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(AGENT_HOST, username=AGENT_USER, password=AGENT_PASS, timeout=30, allow_agent=False, look_for_keys=False)
    try:
        run(ssh, "echo 'Goodmit0802!' > /tmp/.vault_pass && chmod 600 /tmp/.vault_pass")
        decrypted = run(ssh, f'cd {WS} && /opt/ansible-env/bin/ansible-vault view --vault-password-file=/tmp/.vault_pass vault/windows.yml')
        print('=== current vault/windows.yml ===')
        print(decrypted)

        if f"label: {NEW_ACCOUNT['label']}" in decrypted:
            print('[SKIP] administrator entry already present')
            return 0

        # Insert new account at end of accounts list
        lines = decrypted.rstrip('\n').split('\n')
        in_accounts = False
        last_account_idx = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('accounts:'):
                in_accounts = True
                continue
            if in_accounts:
                if line.lstrip().startswith('-'):
                    last_account_idx = i
                elif line.strip() and not line.startswith(' '):
                    in_accounts = False

        if last_account_idx < 0:
            print('[ERR] accounts list not found')
            return 2

        indent = len(lines[last_account_idx]) - len(lines[last_account_idx].lstrip())
        prefix = ' ' * indent
        new_block = [
            f'{prefix}- username: {NEW_ACCOUNT["username"]}',
            f'{prefix}  password: {NEW_ACCOUNT["password"]}',
            f'{prefix}  label: {NEW_ACCOUNT["label"]}',
            f'{prefix}  role: {NEW_ACCOUNT["role"]}',
        ]
        insert_idx = last_account_idx + 1
        while insert_idx < len(lines) and (lines[insert_idx].startswith(' ' * (indent + 2)) or not lines[insert_idx].strip()):
            insert_idx += 1
        new_lines = lines[:insert_idx] + new_block + lines[insert_idx:]
        new_yaml = '\n'.join(new_lines) + '\n'

        b64 = base64.b64encode(new_yaml.encode('utf-8')).decode('ascii')
        run(ssh, f'echo "{b64}" | base64 -d > /tmp/win-new.yml')
        run(ssh, '/opt/ansible-env/bin/ansible-vault encrypt --vault-password-file=/tmp/.vault_pass /tmp/win-new.yml')
        run(ssh, f'cp {WS}/vault/windows.yml {WS}/vault/windows.yml.cycle016.bak && cp /tmp/win-new.yml {WS}/vault/windows.yml')

        with ssh.open_sftp() as sftp:
            sftp.get(f'{WS}/vault/windows.yml', 'C:/github/server-exporter/vault/windows.yml')
        print('[CHG] vault/windows.yml updated and downloaded')
    finally:
        try:
            run(ssh, 'rm -f /tmp/.vault_pass /tmp/win-new.yml')
        except Exception:
            pass
        ssh.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
