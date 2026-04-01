#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Redfish Volume Probe — 실장비에서 Volume 응답을 캡처하여 fixture로 저장.

사용법 (Agent 서버에서 실행):
  # 환경변수로 인증정보 전달
  export BMC_IP=10.100.15.2
  export BMC_USER=admin
  export BMC_PASS=password

  python3 tests/redfish-probe/probe_volumes.py

  # 특정 벤더만
  python3 tests/redfish-probe/probe_volumes.py --vendor cisco

출력:
  tests/fixtures/redfish/{vendor}/volumes_{ctrl_id}.json
  tests/fixtures/redfish/{vendor}/volume_{ctrl_id}_{idx}.json
"""

import urllib.request
import ssl
import json
import base64
import sys
import os
import argparse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SERVERS = {
    'cisco': {
        'ip':   os.environ.get('BMC_CISCO_IP',   '10.100.15.2'),
        'user': os.environ.get('BMC_CISCO_USER', 'admin'),
        'pass': os.environ.get('BMC_CISCO_PASS', 'CHANGE_ME'),
    },
    'dell': {
        'ip':   os.environ.get('BMC_DELL_IP',   '10.100.15.28'),
        'user': os.environ.get('BMC_DELL_USER', 'root'),
        'pass': os.environ.get('BMC_DELL_PASS', 'CHANGE_ME'),
    },
    'hpe': {
        'ip':   os.environ.get('BMC_HPE_IP',   '10.50.11.231'),
        'user': os.environ.get('BMC_HPE_USER', 'admin'),
        'pass': os.environ.get('BMC_HPE_PASS', 'CHANGE_ME'),
    },
    'lenovo': {
        'ip':   os.environ.get('BMC_LENOVO_IP',   '10.50.11.232'),
        'user': os.environ.get('BMC_LENOVO_USER', 'USERID'),
        'pass': os.environ.get('BMC_LENOVO_PASS', 'CHANGE_ME'),
    },
}

FIXTURE_BASE = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'redfish')


def fetch(ip: str, user: str, pw: str, path: str, timeout: int = 20):
    url = f'https://{ip}{path}'
    creds = base64.b64encode(f'{user}:{pw}'.encode()).decode()
    req = urllib.request.Request(url, headers={
        'Authorization': f'Basic {creds}',
        'Accept': 'application/json',
    })
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=timeout)
        return resp.getcode(), json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        print(f'  ERROR: {e}')
        return 0, None


def save_fixture(vendor: str, filename: str, data: dict):
    vendor_dir = os.path.join(FIXTURE_BASE, vendor)
    os.makedirs(vendor_dir, exist_ok=True)
    path = os.path.join(vendor_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f'  SAVED: {path}')


def probe_vendor(vendor: str, cfg: dict):
    ip, user, pw = cfg['ip'], cfg['user'], cfg['pass']
    print(f'\n=== {vendor.upper()} ({ip}) ===')

    # Step 1: Find Systems URI
    st, root = fetch(ip, user, pw, '/redfish/v1/Systems')
    if st != 200 or not root:
        print(f'  Systems collection failed: {st}')
        return

    for sys_member in (root.get('Members') or []):
        sys_uri = sys_member.get('@odata.id', '')
        print(f'  System: {sys_uri}')

        # Step 2: Get Storage collection
        st2, storage_coll = fetch(ip, user, pw, f'{sys_uri}/Storage')
        if st2 != 200 or not storage_coll:
            print(f'  Storage collection failed: {st2}')
            continue

        for stor_member in (storage_coll.get('Members') or []):
            stor_uri = stor_member.get('@odata.id', '')
            st3, stor_data = fetch(ip, user, pw, stor_uri)
            if st3 != 200 or not stor_data:
                continue

            ctrl_id = stor_data.get('Id', 'unknown')
            print(f'\n  Controller: {ctrl_id}')

            # Step 3: Check Volumes link
            vol_link = (stor_data.get('Volumes') or {}).get('@odata.id')
            if not vol_link:
                print(f'    No Volumes link')
                continue

            print(f'    Volumes link: {vol_link}')

            # Step 4: Fetch Volume collection
            st4, vol_coll = fetch(ip, user, pw, vol_link)
            if st4 != 200 or not vol_coll:
                print(f'    Volumes collection failed: {st4}')
                continue

            save_fixture(vendor, f'volumes_{ctrl_id}.json', vol_coll)

            members = vol_coll.get('Members') or []
            print(f'    Volume count: {len(members)}')

            # Step 5: Fetch each Volume
            for idx, v_member in enumerate(members):
                v_uri = v_member.get('@odata.id', '')
                st5, v_data = fetch(ip, user, pw, v_uri)
                if st5 != 200 or not v_data:
                    print(f'    Volume {v_uri} failed: {st5}')
                    continue

                v_id = v_data.get('Id', f'{idx}')
                raid = v_data.get('RAIDType') or v_data.get('VolumeType', 'unknown')
                cap = v_data.get('CapacityBytes')
                cap_gb = round(int(cap) / 1e9, 1) if cap else '?'
                drives = v_data.get('Links', {}).get('Drives', [])
                drive_ids = [d.get('@odata.id', '').rsplit('/', 1)[-1] for d in drives]

                print(f'    Volume {v_id}: {raid}, {cap_gb}GB, drives={drive_ids}')
                save_fixture(vendor, f'volume_{ctrl_id}_{idx}.json', v_data)


def main():
    parser = argparse.ArgumentParser(description='Probe Redfish Volumes')
    parser.add_argument('--vendor', choices=list(SERVERS.keys()),
                        help='Probe specific vendor only')
    args = parser.parse_args()

    targets = {args.vendor: SERVERS[args.vendor]} if args.vendor else SERVERS

    for vendor, cfg in targets.items():
        if cfg['pass'] == 'CHANGE_ME':
            print(f'\n=== {vendor.upper()} ===')
            print(f'  SKIP: password not set (set BMC_{vendor.upper()}_PASS)')
            continue
        probe_vendor(vendor, cfg)


if __name__ == '__main__':
    main()
