#!/usr/bin/env python3
"""
verify_redfish_4vendor_auth.py — OPS-3 후 4 vendor BMC 인증 검증

cycle-014에서 발견된 vault ↔ BMC sync 불일치 (4 vendor 모두 HTTP 401)를
OPS-3 (운영팀 password 회전 + vault 갱신) 후 즉시 검증.

용도:
- OPS-3 완료 직후 cycle-016 진입 가능 여부 판정
- 4 vendor primary 자격 인증 성공 확인
- account_service 분기 진입 시나리오 검증 (recovery 자격으로만 인증 가능한 BMC 식별)

사용:
    # agent 154 또는 vault password 보유 호스트에서 실행
    python verify_redfish_4vendor_auth.py \\
        --workspace /home/cloviradmin/jenkins-agent/workspace/hshwang-gather@2 \\
        --vault-password-file /tmp/.vault_pass_se

출력:
    각 vendor 별 ServiceRoot HTTP / primary auth HTTP / recovery auth HTTP
    + cycle-016 진입 가능 여부 판정

vendor / IP는 schema/baseline_v1/ 정본에서 자동 추출 (사용자 명시 4 vendor 한정).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SUPPORTED_VENDORS = ['dell', 'hpe', 'lenovo', 'cisco']  # cycle-014 기준 4 vendor


def _build_https_ctx() -> ssl.SSLContext:
    """자체 서명 BMC 인증서 환경 (cycle-011: rule 60 해제, 코드 의도 주석)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _http_get(url: str, *, auth: str | None = None, timeout: float = 8.0) -> tuple[int, str]:
    headers: dict[str, str] = {}
    if auth:
        headers['Authorization'] = f'Basic {auth}'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_build_https_ctx()) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return 0, str(e)


def _baseline_vendor_ips(repo_root: Path) -> dict[str, str]:
    """schema/baseline_v1/{vendor}_baseline.json 에서 IP 추출."""
    out: dict[str, str] = {}
    for vendor in SUPPORTED_VENDORS:
        fp = repo_root / 'schema' / 'baseline_v1' / f'{vendor}_baseline.json'
        if not fp.exists():
            continue
        with fp.open(encoding='utf-8') as f:
            d = json.load(f)
        ip = d.get('ip')
        if ip:
            out[vendor] = ip
    return out


def _vault_accounts(repo_root: Path, vault_pwd_file: Path, vendor: str) -> list[dict[str, str]]:
    """vault/redfish/{vendor}.yml decrypt 후 accounts list 반환.

    transcript에 password 노출 안 됨 — caller만 사용.
    """
    fp = repo_root / 'vault' / 'redfish' / f'{vendor}.yml'
    if not fp.exists():
        return []
    proc = subprocess.run(
        ['ansible-vault', 'view', str(fp), '--vault-password-file', str(vault_pwd_file)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        return []
    try:
        import yaml  # type: ignore[import-not-found]

        data = yaml.safe_load(proc.stdout) or {}
    except ImportError:
        return []
    return list(data.get('accounts') or [])


def _check_vendor(vendor: str, ip: str, accounts: list[dict[str, str]]) -> dict[str, Any]:
    """1 vendor BMC 인증 검증."""
    result: dict[str, Any] = {
        'vendor': vendor,
        'ip': ip,
        'serviceroot': None,
        'primary': None,
        'recovery': None,
    }

    # ServiceRoot 무인증
    code, _ = _http_get(f'https://{ip}/redfish/v1/')
    result['serviceroot'] = code

    for acc in accounts[:2]:
        role = acc.get('role') or 'primary'
        user = acc.get('username') or ''
        pwd = acc.get('password') or ''
        if not user:
            continue
        creds = base64.b64encode(f'{user}:{pwd}'.encode()).decode()
        code, _ = _http_get(f'https://{ip}/redfish/v1/Systems', auth=creds)
        # role 키에 결과 저장 (자격 자체는 저장 안 함)
        result[role] = {'username': user, 'http_code': code}

    return result


def _verdict(results: list[dict[str, Any]]) -> str:
    """cycle-016 진입 가능 여부 판정."""
    primary_ok = sum(1 for r in results if isinstance(r.get('primary'), dict) and r['primary'].get('http_code') == 200)
    recovery_only = sum(
        1
        for r in results
        if isinstance(r.get('primary'), dict)
        and r['primary'].get('http_code') == 401
        and isinstance(r.get('recovery'), dict)
        and r['recovery'].get('http_code') == 200
    )
    total = len(results)

    if primary_ok == total:
        return f'[PASS] 모든 {total} vendor primary auth 성공 → cycle-016 redfish 공통계정 검증 진입 가능'
    if recovery_only > 0:
        return (
            f'[INFO] {recovery_only} vendor primary fail + recovery success → '
            f'account_service 자동 진입 가능 (dryrun=true 기본)'
        )
    return (
        f'[FAIL] primary OK={primary_ok}/{total} — OPS-3 회전 미완료 또는 vault 갱신 필요'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--workspace',
        type=Path,
        default=Path.cwd(),
        help='server-exporter repo root (기본: cwd)',
    )
    parser.add_argument(
        '--vault-password-file',
        type=Path,
        required=True,
        help='ansible-vault password 파일',
    )
    args = parser.parse_args()

    repo = args.workspace
    if not (repo / 'schema' / 'baseline_v1').exists():
        print(f'[ERR] {repo}는 server-exporter repo 아님', file=sys.stderr)
        return 2

    ips = _baseline_vendor_ips(repo)
    if not ips:
        print('[ERR] baseline_v1에서 vendor IP 추출 실패', file=sys.stderr)
        return 2

    print(f'=== 4 vendor BMC 인증 검증 (cycle-014 후 OPS-3 검증용) ===')
    print(f'workspace: {repo}')
    print(f'vault password: {args.vault_password_file}')
    print()

    results: list[dict[str, Any]] = []
    for vendor in SUPPORTED_VENDORS:
        ip = ips.get(vendor)
        if not ip:
            print(f'[SKIP] {vendor}: baseline_v1 부재')
            continue
        accounts = _vault_accounts(repo, args.vault_password_file, vendor)
        if not accounts:
            print(f'[SKIP] {vendor}: vault/redfish/{vendor}.yml decrypt 실패 또는 accounts 부재')
            continue
        r = _check_vendor(vendor, ip, accounts)
        results.append(r)

        sr = r['serviceroot']
        p = r.get('primary') or {}
        rec = r.get('recovery') or {}
        print(
            f'  {vendor:10s} {ip:15s}  ServiceRoot HTTP {sr}  '
            f'primary({p.get("username","-"):>10s})={p.get("http_code","-")}  '
            f'recovery({rec.get("username","-"):>10s})={rec.get("http_code","-")}'
        )

    print()
    print(_verdict(results))
    return 0


if __name__ == '__main__':
    sys.exit(main())
