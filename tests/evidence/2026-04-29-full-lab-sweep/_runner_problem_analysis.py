"""Per-host status / errors / sections analysis from console envelopes."""
import json
import sys
from pathlib import Path

OUT = Path("tests/evidence/2026-04-29-full-lab-sweep")
sys.path.insert(0, str(OUT))
from _runner_envelope_verify import extract_envelopes_from_console  # noqa


def main():
    findings = {"by_channel": {}, "summary": {"success": 0, "partial": 0, "failed": 0}}
    for channel in ["redfish", "os", "esxi"]:
        cpath = OUT / f"_console_{channel}.txt"
        if not cpath.exists():
            continue
        text = cpath.read_text(encoding="utf-8", errors="replace")
        envs = extract_envelopes_from_console(text)
        per_host = []
        for e in envs:
            sections = e.get("sections", {})
            errors = e.get("errors", [])
            data = e.get("data", {})
            diag = e.get("diagnosis") or {}
            per_host.append({
                "ip": e.get("ip"),
                "vendor": e.get("vendor"),
                "hostname": e.get("hostname"),
                "status": e.get("status"),
                "schema_version": e.get("schema_version"),
                "sections_supported": sorted([k for k, v in sections.items() if v in ("success", "failed")]),
                "sections_collected": sorted([k for k, v in sections.items() if v == "success"]),
                "sections_failed": sorted([k for k, v in sections.items() if v == "failed"]),
                "sections_not_supported": sorted([k for k, v in sections.items() if v == "not_supported"]),
                "_section_values_distinct": sorted(set(sections.values())) if isinstance(sections, dict) else None,
                "errors_count": len(errors),
                "errors": errors[:10],  # cap
                "data_section_keys": sorted(data.keys()) if isinstance(data, dict) else None,
                "diagnosis_precheck": diag.get("precheck") if isinstance(diag, dict) else None,
                "diagnosis_details_keys": sorted(diag.get("details", {}).keys()) if isinstance(diag, dict) and isinstance(diag.get("details"), dict) else None,
            })
            findings["summary"][e.get("status", "unknown")] = findings["summary"].get(e.get("status", "unknown"), 0) + 1
        findings["by_channel"][channel] = per_host

    out_path = OUT / "_problem_analysis.json"
    out_path.write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding="utf-8")

    # Pretty summary to a separate text file (avoid Windows cp949 stdout issues)
    txt_path = OUT / "_problem_summary.txt"
    lines = []
    lines.append(f"Status summary: {findings['summary']}")
    lines.append("")
    for ch, hosts in findings["by_channel"].items():
        lines.append(f"=== {ch} ({len(hosts)} hosts) ===")
        for h in hosts:
            tag = "[OK]" if h["status"] == "success" else ("[WARN]" if h["status"] == "partial" else "[NG]")
            sec_sum = (
                f"ok={len(h['sections_collected'])}"
                + (f" fail={len(h['sections_failed'])}" if h["sections_failed"] else "")
                + (f" ns={len(h['sections_not_supported'])}" if h["sections_not_supported"] else "")
            )
            lines.append(f"  {tag} {h['ip']:<15} v={(h['vendor'] or '-'):<10} {h['status']:<8} sec[{sec_sum}] errs={h['errors_count']} hostname={h['hostname']}")
            if h["sections_failed"]:
                lines.append(f"        failed sections: {h['sections_failed']}")
            if h["errors"]:
                for err in h["errors"][:3]:
                    msg = err.get("message", "") if isinstance(err, dict) else str(err)
                    et = err.get("section") or err.get("error_type", "?") if isinstance(err, dict) else "?"
                    lines.append(f"        err[{et}]: {msg[:200]}")
        lines.append("")
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {out_path}")
    print(f"WROTE {txt_path}")
    print(f"Status summary: {findings['summary']}")


if __name__ == "__main__":
    main()
