#!/usr/bin/env python3
"""cycle-016 AI-19 후속 — vault/linux.yml 에 ansible_become_password 추가.

baremetal Linux (10.100.64.96 등) 의 dmidecode 슬롯 정보 수집은 sudo 권한 필요.
현재 vault/linux.yml accounts 에 password 만 있고 ansible_become_password 미정의.

각 account 에 become_password 동일 (== password) 추가. agent 154 SSH로 ansible-vault 작업.
"""
from __future__ import annotations
import sys
import paramiko

import os
AGENT_HOST = os.environ.get('SE_AGENT_HOST', '10.100.64.154')
AGENT_USER = os.environ.get('SE_AGENT_USER', 'cloviradmin')
AGENT_PASS = os.environ['SE_AGENT_PASSWORD']  # 필수 — production-audit (2026-04-29) 하드코딩 제거
WS = '/home/cloviradmin/jenkins-agent/workspace/hshwang-gather'


def run(ssh: paramiko.SSHClient, cmd: str) -> str:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    rc = stdout.channel.recv_exit_status()
    if rc != 0:
        raise RuntimeError(f'cmd={cmd!r} rc={rc}\nstdout={out}\nstderr={err}')
    return out


def main() -> int:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(AGENT_HOST, username=AGENT_USER, password=AGENT_PASS, timeout=30, allow_agent=False, look_for_keys=False)
    try:
        vault_pass = os.environ['SE_VAULT_PASSWORD']  # 필수
        run(ssh, f"echo '{vault_pass}' > /tmp/.vault_pass && chmod 600 /tmp/.vault_pass")
        decrypted = run(ssh, f'cd {WS} && /opt/ansible-env/bin/ansible-vault view --vault-password-file=/tmp/.vault_pass vault/linux.yml')
        print('=== current vault/linux.yml ===')
        print(decrypted)

        if 'ansible_become_pass' in decrypted or 'become_password' in decrypted:
            print('[SKIP] become_pass already in vault/linux.yml')
            return 0

        # 단순화: 파일 끝에 top-level vars 추가 (per-host fallback)
        # ansible_become_pass 는 ansible_password 와 동일 — site.yml 에서 fallback chain 사용
        become_pass = os.environ.get('SE_BECOME_PASSWORD', vault_pass)
        addition = f'\n# cycle-016 AI-19: dmidecode 등 sudo 명령용 become_pass (top-level fallback)\nansible_become_password: "{become_pass}"\n'
        new_yaml = decrypted + addition

        import base64
        b64 = base64.b64encode(new_yaml.encode('utf-8')).decode('ascii')
        run(ssh, f'echo "{b64}" | base64 -d > /tmp/linux-new.yml')
        run(ssh, '/opt/ansible-env/bin/ansible-vault encrypt --vault-password-file=/tmp/.vault_pass /tmp/linux-new.yml')
        run(ssh, f'cp {WS}/vault/linux.yml {WS}/vault/linux.yml.cycle016.bak')
        run(ssh, f'cp /tmp/linux-new.yml {WS}/vault/linux.yml')

        sftp = ssh.open_sftp()
        sftp.get(f'{WS}/vault/linux.yml', 'C:/github/server-exporter/vault/linux.yml')
        sftp.close()
        print('[CHG] vault/linux.yml updated and downloaded')
        run(ssh, 'rm -f /tmp/.vault_pass /tmp/linux-new.yml')
        return 0
    finally:
        ssh.close()


if __name__ == '__main__':
    sys.exit(main())
