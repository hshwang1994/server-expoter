#!/usr/bin/env python3
"""cycle-016 AI-22 final fix — vault/windows.yml 의 administrator 를 primary 로 재배치.

검증:
- pywinrm direct test (NTLM/basic/plaintext × administrator): 모두 PASS
- pywinrm cloviradmin/gooddit/infraops: 모두 invalid creds
- ansible try_credentials reset_connection 한계로 후보 cached connection 누수

Fix: administrator 를 accounts[0] primary 로 재배치 → 첫 시도부터 정확한 자격 사용.
"""
from __future__ import annotations
import sys
import paramiko
import base64

AGENT_HOST = '10.100.64.154'
WS = '/home/cloviradmin/jenkins-agent/workspace/hshwang-gather'

NEW_VAULT = '''---
# cycle-016 AI-22 final: lab Win Server 2022 administrator 가 실 작동 자격.
# 기존 gooddit/infraops 는 lab 에 없어 invalid creds (pywinrm direct 검증).

accounts:
  - { username: administrator, password: "__REDACTED__", label: lab_win_administrator, role: primary   }
  - { username: gooddit,       password: "__REDACTED__", label: windows_legacy,        role: secondary }
  - { username: infraops,      password: "__REDACTED__", label: windows_infraops,      role: secondary }

# Backward-compat — accounts[0] 와 동기화
ansible_user:     "administrator"
ansible_password: "__REDACTED__"
'''


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
    ssh.connect(AGENT_HOST, username='cloviradmin', password='__REDACTED__', timeout=30, allow_agent=False, look_for_keys=False)
    try:
        run(ssh, "echo '__REDACTED__' > /tmp/.vault_pass && chmod 600 /tmp/.vault_pass")
        b64 = base64.b64encode(NEW_VAULT.encode('utf-8')).decode('ascii')
        run(ssh, f'echo "{b64}" | base64 -d > /tmp/win-new.yml')
        run(ssh, '/opt/ansible-env/bin/ansible-vault encrypt --vault-password-file=/tmp/.vault_pass /tmp/win-new.yml')
        run(ssh, f'cp /tmp/win-new.yml {WS}/vault/windows.yml')
        with ssh.open_sftp() as sftp:
            sftp.get(f'{WS}/vault/windows.yml', 'C:/github/server-exporter/vault/windows.yml')
        print('[OK] vault/windows.yml: administrator → primary')
    finally:
        try: run(ssh, 'rm -f /tmp/.vault_pass /tmp/win-new.yml')
        except Exception: pass
        ssh.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
