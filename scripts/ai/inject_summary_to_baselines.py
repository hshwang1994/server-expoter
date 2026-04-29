#!/usr/bin/env python3
"""cycle-016 (2026-04-29): 기존 baseline 7종에 summary.groups 주입.

각 baseline 의 data.{memory,storage,network,cpu} 에서:
  - memory: slots[] -> summary.groups (unit_capacity_gb x quantity)
  - storage: physical_disks[] -> summary.groups (unit_capacity_gb x media_type x quantity)
  - network: interfaces[] -> summary.groups (speed_mbps x quantity x link_up_count)
  - cpu: model 1개씩 group + sockets/cores

idempotent: 이미 summary 있으면 재계산해서 덮어씀.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path


def compute_memory_summary(memory: dict) -> dict:
    slots = memory.get('slots') or []
    groups: list[dict] = []
    seen: dict[str, int] = {}
    total = 0
    for s in slots:
        if not isinstance(s, dict):
            continue
        cap_mb = int(s.get('capacity_mib') or s.get('size_mib') or s.get('capacity_mb') or 0)
        if cap_mb <= 0:
            continue
        cap_gb = cap_mb // 1024
        t = s.get('memory_type') or s.get('type')
        key = f"{cap_gb}|{t}"
        if key in seen:
            idx = seen[key]
            groups[idx]['quantity'] += 1
            groups[idx]['group_total_gb'] = groups[idx]['quantity'] * cap_gb
        else:
            seen[key] = len(groups)
            groups.append({
                'unit_capacity_gb': cap_gb,
                'type': t,
                'quantity': 1,
                'group_total_gb': cap_gb,
            })
        total += cap_gb
    if total == 0:
        # fallback: total_mb / 1024
        total_mb = memory.get('total_mb') or memory.get('installed_mb') or 0
        try:
            total = int(total_mb) // 1024
        except (ValueError, TypeError):
            total = 0
    return {'groups': groups, 'grand_total_gb': total}


def compute_storage_summary(storage: dict) -> dict:
    disks = storage.get('physical_disks') or []
    groups: list[dict] = []
    seen: dict[str, int] = {}
    total = 0
    for d in disks:
        if not isinstance(d, dict):
            continue
        total_mb = d.get('total_mb')
        if not total_mb:
            continue
        try:
            cap_gb = int(total_mb) // 1024
        except (ValueError, TypeError):
            continue
        mt = d.get('media_type')
        pr = d.get('protocol')
        key = f"{cap_gb}|{mt}|{pr}"
        if key in seen:
            idx = seen[key]
            groups[idx]['quantity'] += 1
            groups[idx]['group_total_gb'] = groups[idx]['quantity'] * cap_gb
        else:
            seen[key] = len(groups)
            groups.append({
                'unit_capacity_gb': cap_gb,
                'media_type': mt,
                'protocol': pr,
                'quantity': 1,
                'group_total_gb': cap_gb,
            })
        total += cap_gb
    # ESXi: datastores 합계 fallback
    if total == 0:
        for ds in storage.get('datastores') or []:
            if not isinstance(ds, dict):
                continue
            try:
                total += (int(ds.get('total_mb') or 0)) // 1024
            except (ValueError, TypeError):
                pass
    return {'groups': groups, 'grand_total_gb': total}


def compute_network_summary(network: dict) -> dict:
    ifaces = network.get('interfaces') or []
    groups: list[dict] = []
    seen: dict[str, int] = {}
    for n in ifaces:
        if not isinstance(n, dict):
            continue
        sp = n.get('speed_mbps')
        link_up = (n.get('link_status') or '').lower() in ('up', 'linkup')
        key = str(sp)
        if key in seen:
            idx = seen[key]
            groups[idx]['quantity'] += 1
            if link_up:
                groups[idx]['link_up_count'] += 1
        else:
            seen[key] = len(groups)
            groups.append({
                'speed_mbps': sp,
                'link_type': None,
                'quantity': 1,
                'link_up_count': 1 if link_up else 0,
            })
    return {'groups': groups}


def compute_cpu_summary(cpu: dict) -> dict:
    """단일 model 가정 (Redfish data 는 model 평탄화). 멀티 model 은 P5+ 확장."""
    model = cpu.get('model') or 'unknown'
    sockets = int(cpu.get('sockets') or 0)
    total_cores = int(cpu.get('cores_physical') or 0)
    cores_per_socket = (total_cores // sockets) if sockets > 0 else total_cores
    if sockets == 0 and total_cores == 0:
        return {'groups': []}
    return {
        'groups': [{
            'model': model,
            'sockets': sockets,
            'cores_per_socket': cores_per_socket,
            'total_cores': total_cores,
        }]
    }


def inject(baseline_path: Path) -> bool:
    with baseline_path.open('r', encoding='utf-8') as f:
        doc = json.load(f)
    data = doc.get('data') or {}
    changed = False

    if 'memory' in data and isinstance(data['memory'], dict):
        new = compute_memory_summary(data['memory'])
        if data['memory'].get('summary') != new:
            data['memory']['summary'] = new
            changed = True

    if 'storage' in data and isinstance(data['storage'], dict):
        new = compute_storage_summary(data['storage'])
        if data['storage'].get('summary') != new:
            data['storage']['summary'] = new
            changed = True

    if 'network' in data and isinstance(data['network'], dict):
        new = compute_network_summary(data['network'])
        if data['network'].get('summary') != new:
            data['network']['summary'] = new
            changed = True

    if 'cpu' in data and isinstance(data['cpu'], dict):
        new = compute_cpu_summary(data['cpu'])
        if data['cpu'].get('summary') != new:
            data['cpu']['summary'] = new
            changed = True

    if changed:
        with baseline_path.open('w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            f.write('\n')
    return changed


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    baseline_dir = repo / 'schema' / 'baseline_v1'
    examples_dir = repo / 'schema' / 'examples'
    targets = list(baseline_dir.glob('*.json')) + list(examples_dir.glob('*.json'))
    total_changed = 0
    for p in targets:
        try:
            if inject(p):
                print(f'[CHG] {p.relative_to(repo)}')
                total_changed += 1
            else:
                print(f'[OK]  {p.relative_to(repo)} (no change)')
        except (json.JSONDecodeError, OSError) as e:
            print(f'[ERR] {p.relative_to(repo)}: {e}')
    print(f'\nTotal changed: {total_changed} / {len(targets)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
