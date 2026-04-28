"""One-off (2026-04-28 full-sweep): redfish 12 adapter에 rule 96 R1 origin metadata 주석 일괄 추가."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

ADAPTERS = {
    "cisco_cimc.yml": {
        "vendor": "Cisco",
        "firmware": "4.x / 5.x",
        "origin": "Cisco UCS Manager / CIMC Redfish API documentation",
        "notes": "UCS C-Series. strategy: standard_only (OEM 디렉터리 미생성).",
    },
    "dell_idrac.yml": {
        "vendor": "Dell Inc. / Dell EMC",
        "firmware": "iDRAC 모든 세대 (3.x ~ 7.x)",
        "origin": "Dell support.dell.com / Redfish API guide",
        "notes": "generic dell fallback (priority=10). 세대별 미매치 시 사용.",
    },
    "dell_idrac8.yml": {
        "vendor": "Dell Inc. / Dell EMC",
        "firmware": "iDRAC 8 — 2.x / 3.x",
        "origin": "Dell support.dell.com / Redfish API guide (iDRAC 8)",
        "notes": "PowerEdge R630/R730 등 13G 시스템. 일부 endpoint 비표준 가능.",
    },
    "dell_idrac9.yml": {
        "vendor": "Dell Inc. / Dell EMC",
        "firmware": "iDRAC 9 — 4.x / 5.x / 6.x / 7.x",
        "origin": "Dell support.dell.com / Redfish API guide (iDRAC 9)",
        "notes": "PowerEdge 14G/15G/16G. Storage Volumes 5.x+ 표준.",
    },
    "hpe_ilo.yml": {
        "vendor": "HPE / Hewlett Packard Enterprise",
        "firmware": "iLO 모든 세대",
        "origin": "HPE iLO Redfish API documentation",
        "notes": "generic hpe fallback (priority=10). 세대별 미매치 시 사용.",
    },
    "hpe_ilo4.yml": {
        "vendor": "HPE / Hewlett Packard Enterprise",
        "firmware": "iLO 4 — 2.x",
        "origin": "HPE iLO 4 Redfish API documentation",
        "notes": "ProLiant Gen9. Redfish 부분 지원.",
    },
    "hpe_ilo5.yml": {
        "vendor": "HPE / Hewlett Packard Enterprise",
        "firmware": "iLO 5 — 2.x",
        "origin": "HPE iLO 5 Redfish API documentation",
        "notes": "ProLiant Gen10/Gen10 Plus. Redfish 1.x 표준 호환.",
    },
    "hpe_ilo6.yml": {
        "vendor": "HPE / Hewlett Packard Enterprise",
        "firmware": "iLO 6 — 1.x / 2.x",
        "origin": "HPE iLO 6 Redfish API documentation",
        "notes": "ProLiant Gen11. Redfish 1.x 표준 호환.",
    },
    "lenovo_xcc.yml": {
        "vendor": "Lenovo",
        "firmware": "XCC — 1.x / 2.x / 3.x",
        "origin": "Lenovo XCC Redfish API documentation",
        "notes": "ThinkSystem 모던 세대 (SR/ST). Redfish 1.x 표준 호환.",
    },
    "lenovo_imm2.yml": {
        "vendor": "Lenovo / IBM",
        "firmware": "IMM2 — 1.x (legacy)",
        "origin": "Lenovo IMM2 Redfish API documentation (legacy)",
        "notes": "구세대 System x 또는 IBM 시절 BMC. Redfish 부분 지원.",
    },
    "supermicro_bmc.yml": {
        "vendor": "Supermicro / Super Micro Computer",
        "firmware": "BMC firmware 1.x / 2.x",
        "origin": "Supermicro BMC Redfish API documentation",
        "notes": "generic Supermicro BMC fallback. 세대 무관.",
    },
    "supermicro_x9.yml": {
        "vendor": "Supermicro / Super Micro Computer",
        "firmware": "X9 generation BMC",
        "origin": "Supermicro X9 BMC documentation",
        "notes": "X9 메인보드 세대 (구). Redfish 부분 지원.",
    },
    "supermicro_x11.yml": {
        "vendor": "Supermicro / Super Micro Computer",
        "firmware": "X11 generation BMC",
        "origin": "Supermicro X11 BMC documentation",
        "notes": "X11 메인보드 세대. Redfish 1.x 표준 호환.",
    },
}


def render_block(meta):
    return (
        "# ── Origin metadata (rule 96 R1) ──────────────────────────────────────────────\n"
        f"# Vendor: {meta['vendor']}\n"
        f"# Firmware: {meta['firmware']}\n"
        f"# Origin: {meta['origin']}\n"
        "# Last sync: 2026-04-28 (full-sweep)\n"
        f"# Notes: {meta['notes']}\n"
        "# Tested against: 실장비 검증 결과는 schema/baseline_v1/<vendor>_baseline.json + tests/evidence/ 참조\n"
        "# ──────────────────────────────────────────────────────────────────────────────\n"
    )


def main():
    base = ROOT / "adapters" / "redfish"
    applied = 0
    skipped = []
    for fname, meta in ADAPTERS.items():
        p = base / fname
        if not p.exists():
            skipped.append(f"missing: {fname}")
            continue
        txt = p.read_text(encoding="utf-8")
        if "# ── Origin metadata" in txt:
            skipped.append(f"already has origin: {fname}")
            continue
        # YAML 헤더 `---` 다음에 origin 블록 삽입
        if txt.startswith("---\n"):
            new_txt = "---\n" + render_block(meta) + txt[4:]
        else:
            new_txt = render_block(meta) + txt
        p.write_text(new_txt, encoding="utf-8")
        applied += 1
    print(f"applied: {applied} / {len(ADAPTERS)}")
    for s in skipped:
        print("  -", s)


if __name__ == "__main__":
    main()
