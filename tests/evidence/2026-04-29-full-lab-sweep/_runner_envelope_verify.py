"""Verify JSON envelope 13 fields per rule 13 R5 from console logs.

Logic:
1. Parse each console log
2. Extract OUTPUT task ok blocks (json_only callback emits envelope as task result)
3. For each envelope: check 13 fields presence + types + status validity + sections shape
4. Cross-check: each host in inventory got an envelope back
"""
import json
import re
import sys
from pathlib import Path

OUT = Path("tests/evidence/2026-04-29-full-lab-sweep")
INV = json.loads((OUT / "_inventory.json").read_text(encoding="utf-8"))

REQUIRED_13 = [
    "target_type",
    "collection_method",
    "ip",
    "hostname",
    "vendor",
    "status",
    "sections",
    "diagnosis",
    "meta",
    "correlation",
    "errors",
    "data",
    "schema_version",
]

EXPECTED_TYPES = {
    "target_type": str,
    "collection_method": str,
    "ip": str,
    "hostname": str,
    "vendor": (str, type(None)),
    "status": str,
    "sections": dict,
    "diagnosis": (dict, type(None)),
    "meta": (dict, type(None)),
    "correlation": (dict, type(None)),
    "errors": list,
    "data": dict,
    "schema_version": str,
}

ALLOWED_STATUS = {"success", "partial", "failed"}


def extract_envelopes_from_console(text: str) -> list[dict]:
    """Extract envelope JSONs from console.

    json_only callback emits each task result as JSON line.
    OUTPUT task name pattern: 'OUTPUT: ...'
    """
    envelopes = []
    # Strategy 1: Look for full JSON objects that contain target_type + schema_version
    # Use brace-balanced extraction starting at lines where '"target_type"' occurs
    # Multiple regex attempts:

    # First: try to find {...} blocks with target_type + status keys
    # json_only emits each OUTPUT task as a separate JSON object.
    # We'll scan for "{" then balance braces until matching "}".

    i = 0
    n = len(text)
    while i < n:
        # Find next '{' that begins envelope (heuristic: nearby contains "target_type")
        idx = text.find('{"target_type"', i)
        if idx < 0:
            idx = text.find('"target_type":', i)
            if idx < 0:
                break
            # back up to nearest preceding '{'
            j = idx
            while j > 0 and text[j] != '{':
                j -= 1
            if j == 0 and text[j] != '{':
                i = idx + 1
                continue
            idx = j
        # balance braces
        depth = 0
        j = idx
        in_str = False
        esc = False
        while j < n:
            ch = text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == '\\':
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[idx:j+1]
                        try:
                            obj = json.loads(candidate)
                            if isinstance(obj, dict) and "target_type" in obj:
                                envelopes.append(obj)
                        except Exception:
                            pass
                        i = j + 1
                        break
            j += 1
        else:
            break
    return envelopes


def verify_envelope(env: dict) -> dict:
    """Return dict {field_results, type_results, status_ok, summary}."""
    result = {
        "ip": env.get("ip"),
        "vendor": env.get("vendor"),
        "target_type": env.get("target_type"),
        "status": env.get("status"),
        "missing_fields": [],
        "wrong_type": [],
        "status_invalid": False,
        "sections_count": None,
        "sections_collected": None,
        "errors_count": None,
        "data_keys": None,
        "diagnosis_shape_ok": True,
        "schema_version": env.get("schema_version"),
    }
    for f in REQUIRED_13:
        if f not in env:
            result["missing_fields"].append(f)
        else:
            expected = EXPECTED_TYPES[f]
            if not isinstance(env[f], expected):
                result["wrong_type"].append({"field": f, "expected": str(expected), "actual": type(env[f]).__name__})
    if env.get("status") not in ALLOWED_STATUS:
        result["status_invalid"] = True
    sections = env.get("sections", {})
    if isinstance(sections, dict):
        result["sections_count"] = len(sections)
        result["sections_collected"] = [k for k, v in sections.items() if v == "collected"]
    if isinstance(env.get("errors"), list):
        result["errors_count"] = len(env["errors"])
    if isinstance(env.get("data"), dict):
        result["data_keys"] = sorted(env["data"].keys())
    diag = env.get("diagnosis")
    if diag is not None and not isinstance(diag, dict):
        result["diagnosis_shape_ok"] = False
    result["pass"] = (
        not result["missing_fields"]
        and not result["wrong_type"]
        and not result["status_invalid"]
        and result["diagnosis_shape_ok"]
    )
    return result


def expected_ips(channel: str) -> set:
    if channel == "redfish":
        return {h["ip"] for h in INV["redfish"]["hosts"]}
    if channel == "os":
        return {h["ip"] for h in INV["os"]["hosts"]}
    if channel == "esxi":
        return {h["ip"] for h in INV["esxi"]["hosts"]}
    return set()


def main():
    overall = {"channels": {}, "totals": {"envelopes": 0, "pass": 0, "fail": 0}}
    for channel in ["redfish", "os", "esxi"]:
        cpath = OUT / f"_console_{channel}.txt"
        if not cpath.exists():
            print(f"[{channel}] NO CONSOLE LOG — skipping")
            overall["channels"][channel] = {"error": "no console"}
            continue
        text = cpath.read_text(encoding="utf-8", errors="replace")
        envs = extract_envelopes_from_console(text)
        per_host = []
        for env in envs:
            v = verify_envelope(env)
            per_host.append(v)
            overall["totals"]["envelopes"] += 1
            if v["pass"]:
                overall["totals"]["pass"] += 1
            else:
                overall["totals"]["fail"] += 1

        seen_ips = {v["ip"] for v in per_host}
        exp_ips = expected_ips(channel)
        missing_ips = list(exp_ips - seen_ips)
        extra_ips = list(seen_ips - exp_ips)

        overall["channels"][channel] = {
            "envelopes_found": len(envs),
            "expected_hosts": len(exp_ips),
            "missing_envelopes": missing_ips,
            "extra_envelopes": extra_ips,
            "per_host": per_host,
        }

    out_path = OUT / "_envelope_verification.json"
    out_path.write_text(json.dumps(overall, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {out_path}")
    print(f"Totals: envelopes={overall['totals']['envelopes']} pass={overall['totals']['pass']} fail={overall['totals']['fail']}")
    for ch, info in overall["channels"].items():
        if "error" in info:
            print(f"  [{ch}] {info['error']}")
            continue
        print(f"  [{ch}] envelopes={info['envelopes_found']}/{info['expected_hosts']} missing={info['missing_envelopes']} extra={info['extra_envelopes']}")
        fails = [v for v in info["per_host"] if not v["pass"]]
        for f in fails:
            print(f"    FAIL {f['ip']}: missing={f['missing_fields']} wrong_type={f['wrong_type']} status_invalid={f['status_invalid']}")


if __name__ == "__main__":
    main()
