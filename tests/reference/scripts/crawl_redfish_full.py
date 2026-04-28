#!/usr/bin/env python3
"""crawl_redfish_full.py — Redfish 재귀 endpoint crawler.

목적: ServiceRoot부터 도달 가능한 모든 Redfish endpoint를 follow하여
      vendor/ip별 디렉터리에 raw JSON 응답 저장. 재실행 idempotent.

사용:
    python tests/reference/scripts/crawl_redfish_full.py                 # 전체
    python tests/reference/scripts/crawl_redfish_full.py --target dell-10.100.15.27  # 1대만
    python tests/reference/scripts/crawl_redfish_full.py --vendor dell   # 벤더 전수
    python tests/reference/scripts/crawl_redfish_full.py --skip-existing # 기존 파일 skip
    python tests/reference/scripts/crawl_redfish_full.py --max-depth 8   # 재귀 깊이 제한

저장 위치:
    tests/reference/redfish/<vendor>/<ip>/
      ├── _manifest.json     — 전체 endpoint list / status / timing
      ├── _summary.txt       — 사람이 읽는 요약
      └── <path-derived>.json — 각 endpoint 응답

보안: 자격은 tests/reference/local/targets.yaml (gitignored)에서 로드.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Windows console (cp949) 우회: stdout/stderr를 UTF-8 강제
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import yaml  # type: ignore
except ImportError:
    print("ERROR: PyYAML 필요. pip install pyyaml 또는 ansible 환경에서 실행", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[3]
TARGETS_FILE = REPO_ROOT / "tests" / "reference" / "local" / "targets.yaml"
OUTPUT_BASE = REPO_ROOT / "tests" / "reference" / "redfish"

DEFAULT_TIMEOUT = 20
MAX_ENDPOINTS_PER_HOST = 5000  # safety guard
DEFAULT_MAX_DEPTH = 10

# Endpoint that are typically "expand action" or hugely nested - we still follow but limit
# Path that should NOT recurse into (to avoid infinite loops or overwhelming)
SKIP_PATH_PREFIXES = (
    "/redfish/v1/EventService/Subscriptions",  # subscriptions are dynamic
    "/redfish/v1/SessionService/Sessions",     # sessions are dynamic
    "/redfish/v1/TaskService/Tasks",            # tasks are dynamic
    # Dell: SEL / LC log (huge, dynamic)
    "/redfish/v1/Systems/System.Embedded.1/LogServices/Sel/Entries",
    "/redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Lclog/Entries",
    # HPE: IML / Event / SL / Security logs (huge — 200~500 entries each, 2026-04-28 측정)
    "/redfish/v1/Managers/1/LogServices/IML/Entries",
    "/redfish/v1/Systems/1/LogServices/IML/Entries",
    "/redfish/v1/Systems/1/LogServices/Event/Entries",
    "/redfish/v1/Systems/1/LogServices/SL/Entries",
    "/redfish/v1/Managers/1/LogServices/IEL/Entries",
    "/redfish/v1/Managers/1/LogServices/SL/Entries",
    # Lenovo XCC: ActiveLog / AuditLog (방어적)
    "/redfish/v1/Systems/1/LogServices/ActiveLog/Entries",
    "/redfish/v1/Managers/1/LogServices/Audit/Entries",
    # Supermicro AMI: Log
    "/redfish/v1/Systems/Self/LogServices/Log1/Entries",
    # JsonSchemas — 정적 schema 정의. 일부 BMC (Cisco CIMC) 응답 매우 느려 (>1.5s/req × 700+) 전체 시간 폭증.
    # 향후 schema 검증 필요 시 별도 --no-skip-jsonschemas 플래그 도입 검토.
    "/redfish/v1/JsonSchemas/",
)

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def load_targets() -> dict[str, Any]:
    if not TARGETS_FILE.exists():
        sample = TARGETS_FILE.with_suffix(".yaml.sample")
        print(f"ERROR: {TARGETS_FILE} 없음. {sample} 복사 후 채우기", file=sys.stderr)
        sys.exit(2)
    with TARGETS_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch(ip: str, user: str, password: str, path: str, timeout: int = DEFAULT_TIMEOUT) -> tuple[int, Any, float]:
    """Returns (status_code, body_or_error_dict, elapsed_seconds)."""
    url = f"https://{ip}{path}"
    creds = base64.b64encode(f"{user}:{password}".encode()).decode()
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {creds}",
        "Accept": "application/json",
    })
    start = time.monotonic()
    try:
        resp = urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout)
        body = resp.read()
        elapsed = time.monotonic() - start
        try:
            return resp.getcode(), json.loads(body), elapsed
        except json.JSONDecodeError:
            return resp.getcode(), {"_raw_body": body.decode("utf-8", errors="replace")}, elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.monotonic() - start
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
        return e.code, body, elapsed
    except Exception as e:
        elapsed = time.monotonic() - start
        return 0, {"_error": str(e), "_type": type(e).__name__}, elapsed


def path_to_filename(path: str) -> str:
    """/redfish/v1/Systems/System.Embedded.1/Memory/DIMM.Socket.A1
       → redfish_v1_systems_system.embedded.1_memory_dimm.socket.a1.json"""
    safe = path.strip("/").replace("/", "_").replace("?", "_q_").replace("&", "_a_").replace("=", "_e_")
    if not safe:
        safe = "root"
    # Windows 파일시스템 비호환 문자 처리
    for ch in '<>:"|*':
        safe = safe.replace(ch, "_")
    if not safe.endswith(".json"):
        safe += ".json"
    # 너무 긴 path는 hash 추가 (Windows MAX_PATH 260; dirpath 여유 고려해 130 컷)
    if len(safe) > 130:
        import hashlib
        digest = hashlib.sha1(safe.encode()).hexdigest()[:10]
        safe = safe[:115] + "_" + digest + ".json"
    return safe.lower()


def discover_links(data: Any) -> list[str]:
    """JSON dict에서 모든 @odata.id 값을 재귀 추출."""
    found: list[str] = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "@odata.id" and isinstance(v, str):
                found.append(v)
            else:
                found.extend(discover_links(v))
    elif isinstance(data, list):
        for item in data:
            found.extend(discover_links(item))
    return found


def should_skip_path(path: str, skip_prefixes: tuple[str, ...] = SKIP_PATH_PREFIXES) -> bool:
    for prefix in skip_prefixes:
        if path.startswith(prefix):
            # 예외: prefix 자체 (collection root)는 1회 수집 OK
            if path.rstrip("/") == prefix.rstrip("/"):
                return False
            return True
    return False


def crawl_target(target: dict[str, Any], skip_existing: bool = False, max_depth: int = DEFAULT_MAX_DEPTH, skip_prefixes: tuple[str, ...] = SKIP_PATH_PREFIXES) -> dict[str, Any]:
    name = target["name"]
    ip = target["ip"]
    user = target["user"]
    password = target["password"]
    vendor = target.get("vendor", "unknown")

    if not password:
        return {"name": name, "skipped": True, "reason": "password 비어있음"}
    if target.get("skip_reason"):
        return {"name": name, "skipped": True, "reason": target["skip_reason"]}

    out_dir = OUTPUT_BASE / vendor / ip.replace(".", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  [{vendor}] {name} ({ip}) → {out_dir.relative_to(REPO_ROOT)}")
    print(f"{'='*70}")

    visited: set[str] = set()
    to_visit: deque[tuple[str, int]] = deque([("/redfish/v1/", 0)])
    manifest: list[dict[str, Any]] = []
    started = time.monotonic()

    while to_visit and len(visited) < MAX_ENDPOINTS_PER_HOST:
        path, depth = to_visit.popleft()
        if path in visited:
            continue
        if depth > max_depth:
            continue
        if should_skip_path(path, skip_prefixes):
            continue
        # Normalize: query string 제거하고 visit 체크 (선택)
        norm = path.split("?")[0]
        if norm in visited:
            continue
        visited.add(norm)

        fname = path_to_filename(path)
        fpath = out_dir / fname

        if skip_existing and fpath.exists():
            try:
                with fpath.open(encoding="utf-8") as f:
                    cached = json.load(f)
                manifest.append({
                    "path": path, "depth": depth, "status": "cached",
                    "file": fname, "code": cached.get("_meta", {}).get("code"),
                })
                # cached 데이터에서도 link 추출 (재귀 계속)
                if isinstance(cached, dict) and "_data" in cached:
                    for link in discover_links(cached["_data"]):
                        if link and link.startswith("/redfish/v1/") and link.split("?")[0] not in visited:
                            to_visit.append((link, depth + 1))
                continue
            except Exception:
                pass  # 손상된 캐시 — 재수집

        code, body, elapsed = fetch(ip, user, password, path)
        wrapped = {
            "_meta": {
                "uri": path,
                "code": code,
                "depth": depth,
                "elapsed_ms": round(elapsed * 1000, 1),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
            "_data": body,
        }
        try:
            with fpath.open("w", encoding="utf-8") as f:
                json.dump(wrapped, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"  [{depth:2d}] {path:80s} WRITE_FAIL ({e})")
            manifest.append({
                "path": path, "depth": depth, "code": code,
                "elapsed_ms": round(elapsed * 1000, 1), "file": fname,
                "write_error": str(e),
            })
            # link follow는 아래에서 계속
        else:
            status_tag = "OK" if code == 200 else f"HTTP {code}"
            print(f"  [{depth:2d}] {path:80s} {status_tag} ({elapsed*1000:.0f}ms)")
            manifest.append({
                "path": path, "depth": depth, "code": code,
                "elapsed_ms": round(elapsed * 1000, 1), "file": fname,
            })

        # 200이면 link follow
        if code == 200 and isinstance(body, (dict, list)):
            for link in discover_links(body):
                if link and link.startswith("/redfish/v1/"):
                    norm_link = link.split("?")[0]
                    if norm_link not in visited:
                        to_visit.append((link, depth + 1))

    total_elapsed = time.monotonic() - started
    summary = {
        "target": name,
        "ip": ip,
        "vendor": vendor,
        "endpoints_total": len(manifest),
        "endpoints_ok": sum(1 for e in manifest if e.get("code") == 200),
        "endpoints_fail": sum(1 for e in manifest if e.get("code") and e["code"] != 200),
        "endpoints_cached": sum(1 for e in manifest if e.get("status") == "cached"),
        "elapsed_seconds": round(total_elapsed, 1),
        "max_depth_reached": max((e["depth"] for e in manifest), default=0),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "manifest": manifest,
    }
    with (out_dir / "_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Human-readable summary
    lines = [
        f"# Redfish Crawl Summary — {name}",
        "",
        f"- IP: {ip}",
        f"- Vendor: {vendor}",
        f"- Total endpoints: {summary['endpoints_total']}",
        f"- OK (HTTP 200): {summary['endpoints_ok']}",
        f"- Fail (non-200): {summary['endpoints_fail']}",
        f"- Cached (skip): {summary['endpoints_cached']}",
        f"- Elapsed: {summary['elapsed_seconds']}s",
        f"- Max depth: {summary['max_depth_reached']}",
        f"- Completed: {summary['completed_at']}",
        "",
        "## Endpoint list (status / depth)",
        "",
    ]
    for e in manifest:
        status = e.get("status") or f"HTTP {e.get('code')}"
        lines.append(f"  [{e['depth']:2d}] {status:10s} {e['path']}")
    with (out_dir / "_summary.txt").open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n  Total: {summary['endpoints_total']} endpoints, "
          f"OK={summary['endpoints_ok']}, FAIL={summary['endpoints_fail']}, "
          f"elapsed={summary['elapsed_seconds']}s")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", help="단일 target name (예: dell-10.100.15.27)")
    parser.add_argument("--vendor", help="vendor 전수 (dell/hpe/lenovo/cisco/supermicro)")
    parser.add_argument("--skip-existing", action="store_true", help="기존 파일 skip (link follow는 계속)")
    parser.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH, help=f"재귀 최대 깊이 (default {DEFAULT_MAX_DEPTH})")
    parser.add_argument("--include-jsonschemas", action="store_true", help="JsonSchemas (정적 schema 정의) 포함 — 느린 BMC에서 시간 폭증 주의")
    parser.add_argument("--include-logs", action="store_true", help="LogServices/*/Entries 포함 — 매우 큼")
    args = parser.parse_args()

    targets_doc = load_targets()
    bmcs = targets_doc.get("bmc", [])

    if args.target:
        bmcs = [b for b in bmcs if b["name"] == args.target]
    if args.vendor:
        bmcs = [b for b in bmcs if b.get("vendor") == args.vendor]

    if not bmcs:
        print("선택된 BMC 없음", file=sys.stderr)
        return 2

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    # 동적 SKIP_PATH 계산 — 인자에 따라 일부 prefix 제외
    effective_skip = list(SKIP_PATH_PREFIXES)
    if args.include_jsonschemas:
        effective_skip = [p for p in effective_skip if not p.startswith("/redfish/v1/JsonSchemas")]
    if args.include_logs:
        effective_skip = [p for p in effective_skip if "Log" not in p and "Entries" not in p]
    effective_skip_t = tuple(effective_skip)
    print(f"crawl_redfish_full — {len(bmcs)} target(s), output={OUTPUT_BASE.relative_to(REPO_ROOT)}")
    print(f"  SKIP prefixes: {len(effective_skip_t)} (include_jsonschemas={args.include_jsonschemas}, include_logs={args.include_logs})")

    results = []
    for bmc in bmcs:
        try:
            results.append(crawl_target(bmc, skip_existing=args.skip_existing, max_depth=args.max_depth, skip_prefixes=effective_skip_t))
        except KeyboardInterrupt:
            print("\n[중단]")
            break
        except Exception as e:
            print(f"  ERROR on {bmc['name']}: {e}", file=sys.stderr)
            results.append({"name": bmc["name"], "error": str(e)})

    # Top-level summary
    print(f"\n{'='*70}\n  TOTAL SUMMARY\n{'='*70}")
    for r in results:
        if "error" in r:
            print(f"  ERROR  {r['name']}: {r['error']}")
        elif r.get("skipped"):
            print(f"  SKIP   {r['name']}: {r['reason']}")
        else:
            print(f"  OK     {r['target']:35s} ep={r['endpoints_total']:4d} "
                  f"ok={r['endpoints_ok']:4d} fail={r['endpoints_fail']:3d} "
                  f"elapsed={r['elapsed_seconds']:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
