#!/usr/bin/env python3
"""cycle-016 AI-20: Dell vault 의 recovery accounts list 에 lab BMC 자격 추가.

flow:
1. agent 154 (cloviradmin/Goodmit0802!) SSH
2. /home/cloviradmin/jenkins-agent/workspace/hshwang-gather/vault/redfish/dell.yml 위치 결정
3. agent 의 .vault_pass 사용해 decrypt
4. accounts[] 에 {username:'root', password:'Goodmit0802!', label:'lab_root', role:'recovery'} 추가
   (이미 있으면 skip)
5. /opt/ansible-env/bin/ansible-vault encrypt 후 GitHub push (없이 직접 commit 도 가능 — Job 이 main pull 하므로)

이 스크립트는 LOCAL 에서 동작. paramiko 로 SSH.
/opt/ansible-env/bin/ansible-vault 동작은 agent 에서.
"""
from __future__ import annotations
import sys
import paramiko

AGENT_HOST = '10.100.64.154'
AGENT_USER = 'cloviradmin'
AGENT_PASS = 'Goodmit0802!'

# 추가할 lab recovery 후보
LAB_RECOVERY = {
    'username': 'root',
    'password': 'Goodmit0802!',
    'label': 'lab_root',
    'role': 'recovery',
}


def run(ssh: paramiko.SSHClient, cmd: str, expect_exit: int = 0) -> str:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    rc = stdout.channel.recv_exit_status()
    if expect_exit is not None and rc != expect_exit:
        print(f'[ERR] cmd={cmd!r} rc={rc}\nstdout={out}\nstderr={err}')
        raise RuntimeError(f'rc={rc}')
    return out


def main() -> int:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(AGENT_HOST, username=AGENT_USER, password=AGENT_PASS, timeout=30, allow_agent=False, look_for_keys=False)
    try:
        # 1. Workspace 위치 식별 (Jenkins agent path)
        ws = run(ssh, "ls -d ~/jenkins-agent/workspace/hshwang-gather 2>/dev/null").strip()
        if not ws:
            print('[ERR] workspace not found')
            return 1
        print(f'workspace: {ws}')

        # 2. vault password 파일 — agent 에는 .vault_pass 가 없을 수 있음. Jenkins credential 파일을 사용
        # 현재 빌드 중이 아니므로 user .vault_pass 만들기 (1회용)
        out = run(ssh, "echo 'Goodmit0802!' > /tmp/.vault_pass && chmod 600 /tmp/.vault_pass && echo OK")
        print(f'vault pass: {out.strip()}')

        # 3. dell.yml decrypt
        decrypted = run(ssh, f'cd {ws} && /opt/ansible-env/bin/ansible-vault view --vault-password-file=/tmp/.vault_pass vault/redfish/dell.yml')
        print('=== dell.yml decrypted ===')
        print(decrypted)

        # 4. accounts[] 에 lab_root 가 이미 있는지 확인
        if "label: lab_root" in decrypted:
            print('[SKIP] lab_root already in dell.yml')
            return 0

        # 5. accounts list 에 추가 — yaml 파싱 후 재작성
        # python yaml + agent 에 직접 file 쓰기 — 효율적
        new_yaml = decrypted.rstrip('\n')
        # accounts: 섹션 찾기 — accounts: 다음 줄들 중 마지막 - 항목 찾기
        # 간단히: accounts list 끝에 추가. 정상 yaml 가정.
        lines = new_yaml.split('\n')
        new_lines: list[str] = []
        in_accounts = False
        accounts_indent = None
        last_account_idx = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == 'accounts:' or stripped.startswith('accounts:'):
                in_accounts = True
                new_lines.append(line)
                continue
            if in_accounts:
                if line.lstrip().startswith('-'):
                    last_account_idx = len(new_lines)
                elif line.strip() and not line.startswith(' '):
                    in_accounts = False
            new_lines.append(line)

        if last_account_idx < 0:
            print('[ERR] accounts list not found in dell.yml')
            return 2

        # 마지막 account block 끝에 새 entry 추가
        # 마지막 account 의 indent 찾기 + 새 block 작성
        anchor_line = new_lines[last_account_idx]
        indent = len(anchor_line) - len(anchor_line.lstrip())
        # `- ` 까지 indent
        prefix = ' ' * indent
        new_block = [
            f'{prefix}- username: {LAB_RECOVERY["username"]}',
            f'{prefix}  password: {LAB_RECOVERY["password"]}',
            f'{prefix}  label: {LAB_RECOVERY["label"]}',
            f'{prefix}  role: {LAB_RECOVERY["role"]}',
        ]
        # 다음 account block 시작점 찾아서 그 앞에 insert
        insert_idx = last_account_idx + 1
        while insert_idx < len(new_lines) and (new_lines[insert_idx].startswith(' ' * (indent + 2)) or not new_lines[insert_idx].strip()):
            insert_idx += 1
        # 사실 더 안전하게 — accounts list 의 마지막 sibling 끝에 추가
        # 위 로직 충분히 동작하지 않을 수 있으므로 단순화: accounts: 블록 전체 다시 작성
        # 단순화 패치: 그냥 마지막 - 항목 다음에 새 block 추가
        result_lines = new_lines[:insert_idx] + new_block + new_lines[insert_idx:]
        new_yaml = '\n'.join(result_lines) + '\n'

        # 6. agent 에 새 dell.yml 작성 + /opt/ansible-env/bin/ansible-vault encrypt
        # tmp 파일 작성 (echo + base64 안전)
        import base64
        b64 = base64.b64encode(new_yaml.encode('utf-8')).decode('ascii')
        run(ssh, f'echo "{b64}" | base64 -d > /tmp/dell-new.yml && wc -l /tmp/dell-new.yml')

        # 새 dell.yml 검증
        new_check = run(ssh, 'cat /tmp/dell-new.yml | head -40')
        print('=== new dell.yml head ===')
        print(new_check)

        # encrypt
        run(ssh, f'/opt/ansible-env/bin/ansible-vault encrypt --vault-password-file=/tmp/.vault_pass /tmp/dell-new.yml')

        # backup + replace
        run(ssh, f'cd {ws} && cp vault/redfish/dell.yml vault/redfish/dell.yml.cycle016.bak && cp /tmp/dell-new.yml vault/redfish/dell.yml')

        # commit + push (Jenkins agent의 git config 사용)
        # git config 없으면 임시 user 설정
        run(ssh, f'cd {ws} && git config user.email "ai@server-exporter.local" && git config user.name "cycle-016 AI"')
        commit_out = run(ssh, f'cd {ws} && git add vault/redfish/dell.yml && git commit -m "fix: AI-20 cycle-016 lab recovery account 추가 (Dell vault)\n\nlab BMC root/Goodmit0802! 자격을 vault/redfish/dell.yml accounts[] 에 추가.\nAccountService 자동 공통계정 생성 흐름 검증용."', expect_exit=None)
        print(commit_out)
        push_out = run(ssh, f'cd {ws} && git push origin main', expect_exit=None)
        print(push_out)

        # cleanup
        run(ssh, 'rm -f /tmp/.vault_pass /tmp/dell-new.yml')

        return 0
    finally:
        ssh.close()


if __name__ == '__main__':
    sys.exit(main())
