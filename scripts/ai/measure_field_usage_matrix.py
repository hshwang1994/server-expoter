#!/usr/bin/env python3
"""scripts/ai/measure_field_usage_matrix.py — rule 28 #13 매트릭스 자동 측정.

schema/field_dictionary.yml 의 65 entries 가 schema/baseline_v1/*.json 8 baseline 에서
실제로 어떻게 채워지는지 자동 측정. 4 상태 (present/null/empty/not_supported/missing)
판정 + 분류 1/2/3 후보 자동 도출 + field_dictionary channel 선언 vs 실측 drift 검출.

호출 시점:
- TTL 14일 만료 시 (rule 28 #13)
- field_dictionary.yml 변경 후
- baseline_v1/*.json 변경 후
- adapter capabilities 변경 후

비활성화 환경변수:
    FIELD_USAGE_MATRIX_SKIP=1  — 본 측정 skip

Usage:
    python scripts/ai/measure_field_usage_matrix.py
    python scripts/ai/measure_field_usage_matrix.py --self-test
    python scripts/ai/measure_field_usage_matrix.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


CHANNELS: tuple[str, ...] = ("redfish", "os", "esxi")

# baseline 파일명 → channel 매핑
BASELINE_CHANNEL_MAP: dict[str, str] = {
    "dell_baseline.json": "redfish",
    "hpe_baseline.json": "redfish",
    "lenovo_baseline.json": "redfish",
    "cisco_baseline.json": "redfish",
    "esxi_baseline.json": "esxi",
    "rhel810_raw_fallback_baseline.json": "os",
    "ubuntu_baseline.json": "os",
    "windows_baseline.json": "os",
}


@dataclass(frozen=True)
class FieldEntry:
    path: str
    priority: str
    channel: tuple[str, ...]


@dataclass(frozen=True)
class CellResult:
    field_path: str
    baseline_name: str
    state: str  # present / null / empty / not_supported / missing


# ─────────────────────────────────────────────────────────────────────────────
# YAML 파싱 — PyYAML 우선, fallback 은 simple regex
# ─────────────────────────────────────────────────────────────────────────────


def load_field_dictionary(yml_path: Path) -> list[FieldEntry]:
    """field_dictionary.yml 파싱 → FieldEntry list.

    YAML 구조 (간략):
        fields:
          schema_version:
            priority: must
            channel: [redfish, os, esxi]
            ...
          hardware.health:
            priority: must
            channel: [redfish]
            ...
    """
    text = yml_path.read_text(encoding="utf-8", errors="replace")
    if yaml is not None:
        try:
            data = yaml.safe_load(text) or {}
            fields_dict = data.get("fields", {})
            entries: list[FieldEntry] = []
            for path, meta in fields_dict.items():
                if not isinstance(meta, dict):
                    continue
                priority = str(meta.get("priority", "")).strip()
                channel_raw = meta.get("channel", [])
                if isinstance(channel_raw, list):
                    channel = tuple(str(c).strip() for c in channel_raw)
                else:
                    channel = ()
                entries.append(FieldEntry(path=str(path), priority=priority, channel=channel))
            return entries
        except Exception as exc:
            print(f"WARN: PyYAML parse failed, fallback to regex: {exc}", file=sys.stderr)
    return _stdlib_yaml_parse_field_dictionary(text)


def _stdlib_yaml_parse_field_dictionary(text: str) -> list[FieldEntry]:
    """PyYAML 부재 시 간이 파서. field entry block 만 추출."""
    entries: list[FieldEntry] = []
    lines = text.splitlines()
    cur_path: str | None = None
    cur_priority = ""
    cur_channel: list[str] = []

    def flush() -> None:
        nonlocal cur_path, cur_priority, cur_channel
        if cur_path is not None:
            entries.append(FieldEntry(
                path=cur_path,
                priority=cur_priority,
                channel=tuple(cur_channel),
            ))
        cur_path = None
        cur_priority = ""
        cur_channel = []

    field_header = re.compile(r"^  ([A-Za-z_][\w\.\[\]\*]*):\s*$")
    priority_re = re.compile(r"^    priority:\s*(\w+)")
    channel_re = re.compile(r"^    channel:\s*\[([^\]]*)\]")

    for line in lines:
        if line.startswith("fields:"):
            continue
        m = field_header.match(line)
        if m:
            flush()
            cur_path = m.group(1)
            continue
        m = priority_re.match(line)
        if m:
            cur_priority = m.group(1).strip()
            continue
        m = channel_re.match(line)
        if m:
            raw = m.group(1)
            cur_channel = [c.strip() for c in raw.split(",") if c.strip()]
            continue
    flush()
    return entries


# ─────────────────────────────────────────────────────────────────────────────
# Baseline 로드 + path resolver
# ─────────────────────────────────────────────────────────────────────────────


def load_baselines(baseline_dir: Path) -> dict[str, dict[str, Any]]:
    """baseline_v1/*.json 8 파일 로드."""
    result: dict[str, dict[str, Any]] = {}
    for fp in sorted(baseline_dir.glob("*_baseline.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            result[fp.name] = data
        except Exception as exc:
            print(f"WARN: baseline load failed: {fp.name}: {exc}", file=sys.stderr)
    return result


def resolve_field(path: str, envelope: dict[str, Any]) -> tuple[str, Any]:
    """field_dictionary path → envelope 경로 + 값 추출.

    Path 표기 규칙 (field_dictionary.yml 주석):
        "status"                   → envelope.status
        "sections.*"               → envelope.sections (dict 자체)
        "correlation.host_ip"      → envelope.correlation.host_ip
        "hardware.health"          → envelope.data.hardware.health
        "physical_disks[]"         → envelope.data.storage.physical_disks
        "physical_disks[].serial"  → 배열 각 항목의 serial — 모두 null=null, 일부=present
        "memory.visible_mb"        → envelope.data.memory.visible_mb
        "users[].name"             → envelope.data.users[].name

    Returns: (state, raw_value)
        state: present / null / empty / missing (not_supported 는 호출자가 별도 판정)
    """
    # envelope 최상위 path (data. 미포함)
    envelope_keys = {
        "schema_version", "target_type", "collection_method", "ip", "hostname",
        "vendor", "status", "sections", "diagnosis", "meta", "correlation", "errors", "data",
    }
    parts = _parse_path_parts(path)
    if not parts:
        return ("missing", None)

    # 첫 part 가 envelope 최상위 key 인지 확인
    first = parts[0]["name"]
    if first in envelope_keys or first.startswith(tuple(envelope_keys)):
        ptr: Any = envelope
        path_parts = parts
    else:
        # data.{section}.{field} 경로
        ptr = envelope.get("data")
        if ptr is None:
            return ("missing", None)
        path_parts = parts

    return _walk(ptr, path_parts)


def _parse_path_parts(path: str) -> list[dict[str, Any]]:
    """path string → list of segments.

    "physical_disks[].serial" → [{name: physical_disks, array: True}, {name: serial}]
    "sections.*"              → [{name: sections, wildcard: True}]
    "correlation.host_ip"     → [{name: correlation}, {name: host_ip}]
    """
    segments = path.split(".")
    parts: list[dict[str, Any]] = []
    for seg in segments:
        if seg == "*":
            if parts:
                parts[-1]["wildcard"] = True
            continue
        is_array = seg.endswith("[]")
        name = seg[:-2] if is_array else seg
        parts.append({"name": name, "array": is_array})
    return parts


def _walk(ptr: Any, parts: list[dict[str, Any]]) -> tuple[str, Any]:
    """parts 따라 ptr walk 후 4 상태 + 값 반환."""
    for i, seg in enumerate(parts):
        name = seg["name"]
        is_array = seg.get("array", False)
        wildcard = seg.get("wildcard", False)
        if not isinstance(ptr, dict):
            return ("missing", None)
        if name not in ptr:
            return ("missing", None)
        ptr = ptr[name]
        if ptr is None:
            return ("null", None)
        if is_array:
            if not isinstance(ptr, list):
                return ("missing", None)
            if len(ptr) == 0:
                return ("empty", [])
            remaining = parts[i + 1:]
            if not remaining:
                # 배열 자체에 대한 조회 (예: physical_disks[])
                return ("present", ptr)
            # 배열 원소별 walk — 모두 null/missing 이면 null, 하나라도 present 면 present
            sub_states: list[str] = []
            for elem in ptr:
                sub_state, _ = _walk(elem, remaining)
                sub_states.append(sub_state)
            if all(s in ("null", "missing", "empty") for s in sub_states):
                if all(s == "missing" for s in sub_states):
                    return ("missing", None)
                return ("null", None)
            return ("present", ptr)
        if wildcard:
            if not isinstance(ptr, dict):
                return ("missing", None)
            if len(ptr) == 0:
                return ("empty", {})
            return ("present", ptr)
    if ptr is None:
        return ("null", None)
    if isinstance(ptr, (list, dict)) and len(ptr) == 0:
        return ("empty", ptr)
    return ("present", ptr)


# ─────────────────────────────────────────────────────────────────────────────
# Section detector — field path 가 어느 section 에 속하는지
# ─────────────────────────────────────────────────────────────────────────────


SECTION_NAMES: tuple[str, ...] = (
    "system", "hardware", "bmc", "cpu", "memory",
    "storage", "network", "firmware", "users", "power",
)


def detect_section(path: str) -> str | None:
    """field path 의 첫 segment 가 section 이면 반환, 아니면 None (envelope 최상위)."""
    first = path.split(".")[0].rstrip("[]")
    return first if first in SECTION_NAMES else None


# ─────────────────────────────────────────────────────────────────────────────
# Cell 판정 + 분류 도출
# ─────────────────────────────────────────────────────────────────────────────


def determine_cell(field: FieldEntry, baseline_name: str, baseline: dict[str, Any]) -> CellResult:
    """field × baseline → 4 상태 판정.

    우선순위: not_supported > missing > empty > null > present
    """
    # section 추출 → sections.{section}=not_supported 인지 확인
    section = detect_section(field.path)
    if section is not None:
        sections_map = baseline.get("sections", {})
        if isinstance(sections_map, dict) and sections_map.get(section) == "not_supported":
            return CellResult(field.path, baseline_name, "not_supported")

    state, _ = resolve_field(field.path, baseline)
    return CellResult(field.path, baseline_name, state)


def derive_category(
    field: FieldEntry,
    cells: list[CellResult],
    baseline_channel: dict[str, str],
) -> dict[str, str]:
    """field × baseline cells → channel 별 분류 (1/2/3 or N/A).

    Returns: {channel: category}
        - "1" — 선언된 channel 의 모든 baseline 이 null/empty/missing (수집 불가)
        - "2" — 일부 present 일부 null (서버 미지원)
        - "3?" — 한 baseline 만 present + 다수 null (코드 버그 의심)
        - "OK" — 모든 baseline 이 present
        - "N/A" — channel 선언 안 됨 또는 모두 not_supported
        - "DRIFT-B?" — channel 선언 안 됐는데 baseline present (선언 누락)

    핵심: field.channel 선언 안 된 channel 은 분류 1/2/3 대상이 아님 (false-positive 차단).
    """
    result: dict[str, str] = {}
    by_channel: dict[str, list[CellResult]] = defaultdict(list)
    for cell in cells:
        ch = baseline_channel.get(cell.baseline_name)
        if ch:
            by_channel[ch].append(cell)

    declared = set(field.channel)

    for channel in CHANNELS:
        bucket = by_channel.get(channel, [])
        if channel not in declared:
            # 선언 안 된 channel — 실측에서 present 면 DRIFT-B? (선언 누락 의심)
            if bucket and any(c.state == "present" for c in bucket):
                result[channel] = "DRIFT-B?"
            else:
                result[channel] = "N/A"
            continue
        if not bucket:
            result[channel] = "N/A"
            continue
        states = [c.state for c in bucket]
        # 모두 not_supported → N/A
        if all(s == "not_supported" for s in states):
            result[channel] = "N/A"
            continue
        non_nsup = [s for s in states if s != "not_supported"]
        if not non_nsup:
            result[channel] = "N/A"
            continue
        present_count = sum(1 for s in non_nsup if s == "present")
        null_count = sum(1 for s in non_nsup if s in ("null", "empty", "missing"))

        if present_count == 0:
            # 선언된 channel 인데 모든 baseline 이 null/empty/missing → 분류 1
            result[channel] = "1"
        elif null_count == 0:
            # 모든 baseline present → 정상
            result[channel] = "OK"
        elif present_count == 1 and null_count >= 2:
            # 한 baseline 만 present + 다른 다수 null → 분류 3? (코드 버그 의심)
            result[channel] = "3?"
        else:
            # 일부 present 일부 null → 분류 2
            result[channel] = "2"

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Drift 검출 (field_dictionary channel ↔ 실측)
# ─────────────────────────────────────────────────────────────────────────────


def detect_drifts(
    field: FieldEntry,
    categories: dict[str, str],
) -> list[str]:
    """field_dictionary channel 선언 vs 실측 cross-check.

    Returns: drift 메시지 list
        - "DRIFT-A: channel 선언했지만 모든 baseline missing" (거짓 선언)
        - "DRIFT-B: channel 미선언이지만 baseline present" (누락 선언)
    """
    drifts: list[str] = []
    declared = set(field.channel)
    for channel in CHANNELS:
        cat = categories.get(channel, "N/A")
        if channel in declared and cat == "1":
            drifts.append(f"DRIFT-A({channel}): 선언했지만 모든 baseline null/missing → channel 제거 후보")
        if channel not in declared and cat in ("OK", "2"):
            drifts.append(f"DRIFT-B({channel}): 미선언이지만 baseline present → channel 추가 후보")
    return drifts


# ─────────────────────────────────────────────────────────────────────────────
# Markdown 출력
# ─────────────────────────────────────────────────────────────────────────────


def render_summary(
    entries: list[FieldEntry],
    baselines: dict[str, dict[str, Any]],
    cells_map: dict[str, list[CellResult]],
    categories_map: dict[str, dict[str, str]],
) -> str:
    """집계 markdown 생성."""
    lines: list[str] = []
    lines.append("# Field Usage Matrix — 측정 결과")
    lines.append("")
    lines.append(f"- field_dictionary entries: {len(entries)}")
    lines.append(f"- baselines: {len(baselines)}")
    lines.append(f"- 총 cells: {len(entries) * len(baselines)}")
    lines.append("")

    # channel 별 cell 카운트
    state_counter: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for field_path, cells in cells_map.items():
        for cell in cells:
            ch = BASELINE_CHANNEL_MAP.get(cell.baseline_name, "?")
            state_counter[ch][cell.state] += 1

    lines.append("## 4 상태 카운트 (channel × state)")
    lines.append("")
    lines.append("| Channel | present | null | empty | not_supported | missing | total |")
    lines.append("|---|---|---|---|---|---|---|")
    for ch in CHANNELS:
        c = state_counter.get(ch, {})
        total = sum(c.values())
        lines.append(
            f"| {ch} | {c.get('present', 0)} | {c.get('null', 0)} | "
            f"{c.get('empty', 0)} | {c.get('not_supported', 0)} | "
            f"{c.get('missing', 0)} | {total} |"
        )
    lines.append("")

    # 분류 1/2/3? 후보 list
    cat_1: list[tuple[str, str]] = []
    cat_2: list[tuple[str, str]] = []
    cat_3q: list[tuple[str, str]] = []
    drifts_all: list[tuple[str, str]] = []
    for field_path, cats in categories_map.items():
        for ch, cat in cats.items():
            if cat == "1":
                cat_1.append((field_path, ch))
            elif cat == "2":
                cat_2.append((field_path, ch))
            elif cat == "3?":
                cat_3q.append((field_path, ch))

    lines.append(f"## 분류 1 후보 (수집 불가 — channel 제거): {len(cat_1)}")
    lines.append("")
    if cat_1:
        for fp, ch in cat_1:
            lines.append(f"- `{fp}` × {ch}")
    lines.append("")

    lines.append(f"## 분류 2 후보 (서버 미지원 — help_ko 명시): {len(cat_2)}")
    lines.append("")
    if cat_2:
        for fp, ch in cat_2:
            lines.append(f"- `{fp}` × {ch}")
    lines.append("")

    lines.append(f"## 분류 3? 후보 (코드 버그 의심 — Phase 2 검증): {len(cat_3q)}")
    lines.append("")
    if cat_3q:
        for fp, ch in cat_3q:
            lines.append(f"- `{fp}` × {ch}")
    lines.append("")

    return "\n".join(lines)


def render_full_matrix(
    entries: list[FieldEntry],
    baseline_names: list[str],
    cells_map: dict[str, list[CellResult]],
    categories_map: dict[str, dict[str, str]],
) -> str:
    """전수 매트릭스 markdown (65 × 8 표)."""
    lines: list[str] = []
    short_names = [n.replace("_baseline.json", "")[:10] for n in baseline_names]
    header = "| Field | Channel 선언 | " + " | ".join(short_names) + " | 분류 |"
    sep = "|" + "|".join(["---"] * (3 + len(baseline_names))) + "|"
    lines.append(header)
    lines.append(sep)

    state_symbol = {
        "present": "O",
        "null": "n",
        "empty": "e",
        "not_supported": "-",
        "missing": "_",
    }

    for entry in entries:
        cells = cells_map.get(entry.path, [])
        by_baseline = {c.baseline_name: c.state for c in cells}
        row_cells = [state_symbol.get(by_baseline.get(bn, "missing"), "?") for bn in baseline_names]
        ch_decl = ",".join(entry.channel) if entry.channel else "-"
        cats = categories_map.get(entry.path, {})
        cat_summary = ",".join(
            f"{ch}:{cat}" for ch, cat in cats.items() if cat not in ("OK", "N/A")
        ) or "OK"
        lines.append(
            f"| `{entry.path}` | {ch_decl} | " + " | ".join(row_cells) + f" | {cat_summary} |"
        )
    lines.append("")
    lines.append("**범례**: O=present / n=null / e=empty / -=not_supported / _=missing")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Self-test
# ─────────────────────────────────────────────────────────────────────────────


def self_test() -> int:
    all_pass = True

    # path parse
    cases_parse = [
        ("schema_version", [{"name": "schema_version", "array": False}]),
        ("correlation.host_ip", [
            {"name": "correlation", "array": False},
            {"name": "host_ip", "array": False},
        ]),
        ("physical_disks[].serial", [
            {"name": "physical_disks", "array": True},
            {"name": "serial", "array": False},
        ]),
        ("sections.*", [{"name": "sections", "array": False, "wildcard": True}]),
    ]
    for path, expected in cases_parse:
        actual = _parse_path_parts(path)
        # wildcard 처리 — expected 의 wildcard 키 추가
        for e in expected:
            e.setdefault("wildcard", False)
        for a in actual:
            a.setdefault("wildcard", False)
        ok = actual == expected
        print(f"{'PASS' if ok else 'FAIL'}: parse '{path}' → {actual}")
        if not ok:
            all_pass = False
            print(f"  expected: {expected}")

    # walk — present
    env = {"data": {"memory": {"visible_mb": 65536}}}
    state, val = resolve_field("memory.visible_mb", env)
    ok = state == "present" and val == 65536
    print(f"{'PASS' if ok else 'FAIL'}: resolve present → {state}/{val}")
    if not ok:
        all_pass = False

    # walk — null
    env = {"data": {"memory": {"visible_mb": None}}}
    state, _ = resolve_field("memory.visible_mb", env)
    ok = state == "null"
    print(f"{'PASS' if ok else 'FAIL'}: resolve null → {state}")
    if not ok:
        all_pass = False

    # walk — missing
    env = {"data": {"memory": {}}}
    state, _ = resolve_field("memory.visible_mb", env)
    ok = state == "missing"
    print(f"{'PASS' if ok else 'FAIL'}: resolve missing → {state}")
    if not ok:
        all_pass = False

    # walk — empty array (path 는 section prefix 포함 — field_dictionary 실제 형식)
    env = {"data": {"storage": {"physical_disks": []}}}
    state, _ = resolve_field("storage.physical_disks[]", env)
    ok = state == "empty"
    print(f"{'PASS' if ok else 'FAIL'}: resolve empty array → {state}")
    if not ok:
        all_pass = False

    # walk — array[].field present
    env = {"data": {"storage": {"physical_disks": [
        {"serial": "ABC123"}, {"serial": None},
    ]}}}
    state, _ = resolve_field("storage.physical_disks[].serial", env)
    ok = state == "present"
    print(f"{'PASS' if ok else 'FAIL'}: resolve array[].field partial → {state}")
    if not ok:
        all_pass = False

    # walk — array[].field all null
    env = {"data": {"storage": {"physical_disks": [
        {"serial": None}, {"serial": None},
    ]}}}
    state, _ = resolve_field("storage.physical_disks[].serial", env)
    ok = state == "null"
    print(f"{'PASS' if ok else 'FAIL'}: resolve array[].field all null → {state}")
    if not ok:
        all_pass = False

    # section detect
    cases_sec = [
        ("memory.visible_mb", "memory"),
        ("storage.physical_disks[].serial", "storage"),
        ("schema_version", None),
        ("correlation.host_ip", None),
        ("sections.*", None),
    ]
    for path, expected in cases_sec:
        actual = detect_section(path)
        ok = actual == expected
        print(f"{'PASS' if ok else 'FAIL'}: detect_section '{path}' → {actual}")
        if not ok:
            all_pass = False

    # determine_cell — not_supported 우선
    field = FieldEntry(path="memory.visible_mb", priority="must", channel=("redfish", "os", "esxi"))
    bl = {"sections": {"memory": "not_supported"}, "data": {"memory": {"visible_mb": 99}}}
    cell = determine_cell(field, "x_baseline.json", bl)
    ok = cell.state == "not_supported"
    print(f"{'PASS' if ok else 'FAIL'}: determine_cell not_supported precedence → {cell.state}")
    if not ok:
        all_pass = False

    # derive_category — 분류 1 (모든 baseline null)
    cells = [
        CellResult("x", "dell_baseline.json", "null"),
        CellResult("x", "hpe_baseline.json", "null"),
        CellResult("x", "lenovo_baseline.json", "null"),
        CellResult("x", "cisco_baseline.json", "null"),
    ]
    field = FieldEntry(path="x", priority="must", channel=("redfish",))
    cats = derive_category(field, cells, BASELINE_CHANNEL_MAP)
    ok = cats.get("redfish") == "1"
    print(f"{'PASS' if ok else 'FAIL'}: derive_category 분류 1 → {cats}")
    if not ok:
        all_pass = False

    # derive_category — 분류 2 (일부 present)
    cells = [
        CellResult("x", "dell_baseline.json", "present"),
        CellResult("x", "hpe_baseline.json", "null"),
        CellResult("x", "lenovo_baseline.json", "null"),
        CellResult("x", "cisco_baseline.json", "present"),
    ]
    cats = derive_category(field, cells, BASELINE_CHANNEL_MAP)
    ok = cats.get("redfish") == "2"
    print(f"{'PASS' if ok else 'FAIL'}: derive_category 분류 2 → {cats}")
    if not ok:
        all_pass = False

    # derive_category — 분류 3? (1 present + 다수 null)
    cells = [
        CellResult("x", "dell_baseline.json", "present"),
        CellResult("x", "hpe_baseline.json", "null"),
        CellResult("x", "lenovo_baseline.json", "null"),
        CellResult("x", "cisco_baseline.json", "null"),
    ]
    cats = derive_category(field, cells, BASELINE_CHANNEL_MAP)
    ok = cats.get("redfish") == "3?"
    print(f"{'PASS' if ok else 'FAIL'}: derive_category 분류 3? → {cats}")
    if not ok:
        all_pass = False

    return 0 if all_pass else 1


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


MD_MARKER_START = "<!-- AUTO-GEN: FIELD_USAGE_MATRIX START -->"
MD_MARKER_END = "<!-- AUTO-GEN: FIELD_USAGE_MATRIX END -->"


def update_md_file(
    md_path: Path,
    entries: list[FieldEntry],
    baselines: dict[str, dict[str, Any]],
    cells_map: dict[str, list[CellResult]],
    categories_map: dict[str, dict[str, str]],
    drifts_map: dict[str, list[str]],
) -> bool:
    """FIELD_USAGE_MATRIX.md 의 marker 사이를 측정 결과로 갱신."""
    if not md_path.exists():
        print(f"WARN: md not found: {md_path}", file=sys.stderr)
        return False
    text = md_path.read_text(encoding="utf-8")
    if MD_MARKER_START not in text or MD_MARKER_END not in text:
        print(f"WARN: marker 부재 — md update skip", file=sys.stderr)
        return False

    block: list[str] = [MD_MARKER_START, ""]
    block.append("> 측정 스크립트 자동 갱신 결과 — 수동 편집 금지. 다음 측정 시 덮어씀.")
    block.append("")
    block.append(render_summary(entries, baselines, cells_map, categories_map))
    if drifts_map:
        block.append("")
        block.append(f"## Drift 검출 ({len(drifts_map)} entries)")
        block.append("")
        for path, drifts in sorted(drifts_map.items()):
            block.append(f"- `{path}`:")
            for d in drifts:
                block.append(f"  - {d}")
        block.append("")
    baseline_names = sorted(baselines.keys())
    block.append("## 전수 매트릭스 (65 × 8)")
    block.append("")
    block.append(render_full_matrix(entries, baseline_names, cells_map, categories_map))
    block.append("")
    block.append(MD_MARKER_END)

    pre, _, rest = text.partition(MD_MARKER_START)
    _, _, post = rest.partition(MD_MARKER_END)
    new_text = pre + "\n".join(block) + post
    md_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="rule 28 #13 field × baseline 사용 실태 매트릭스")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--full", action="store_true", help="65 × 8 전수 매트릭스 출력")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력 (다음 도구 input)")
    parser.add_argument("--update-md", action="store_true",
                        help="docs/ai/catalogs/FIELD_USAGE_MATRIX.md 자동 갱신")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if os.environ.get("FIELD_USAGE_MATRIX_SKIP") == "1":
        return 0

    repo_root = Path(args.repo_root).resolve()
    dict_path = repo_root / "schema" / "field_dictionary.yml"
    baseline_dir = repo_root / "schema" / "baseline_v1"

    if not dict_path.exists():
        print(f"ERROR: field_dictionary not found: {dict_path}", file=sys.stderr)
        return 1
    if not baseline_dir.exists():
        print(f"ERROR: baseline dir not found: {baseline_dir}", file=sys.stderr)
        return 1

    entries = load_field_dictionary(dict_path)
    baselines = load_baselines(baseline_dir)

    cells_map: dict[str, list[CellResult]] = defaultdict(list)
    categories_map: dict[str, dict[str, str]] = {}
    drifts_map: dict[str, list[str]] = {}

    baseline_names = sorted(baselines.keys())

    for entry in entries:
        cells = [determine_cell(entry, bn, baselines[bn]) for bn in baseline_names]
        cells_map[entry.path] = cells
        cats = derive_category(entry, cells, BASELINE_CHANNEL_MAP)
        categories_map[entry.path] = cats
        drifts = detect_drifts(entry, cats)
        if drifts:
            drifts_map[entry.path] = drifts

    if args.json:
        out = {
            "entries": [
                {
                    "path": e.path,
                    "priority": e.priority,
                    "channel": list(e.channel),
                    "categories": categories_map.get(e.path, {}),
                    "cells": {c.baseline_name: c.state for c in cells_map.get(e.path, [])},
                    "drifts": drifts_map.get(e.path, []),
                }
                for e in entries
            ],
            "baseline_names": baseline_names,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    if args.update_md:
        md_path = repo_root / "docs" / "ai" / "catalogs" / "FIELD_USAGE_MATRIX.md"
        if update_md_file(md_path, entries, baselines, cells_map, categories_map, drifts_map):
            print(f"[OK] Updated: {md_path}")
            return 0
        print(f"[FAIL] Could not update: {md_path}", file=sys.stderr)
        return 1

    print(render_summary(entries, baselines, cells_map, categories_map))
    print()

    if drifts_map:
        print(f"## Drift 검출 ({len(drifts_map)} entries)")
        print()
        for path, drifts in sorted(drifts_map.items()):
            print(f"- `{path}`:")
            for d in drifts:
                print(f"  - {d}")
        print()

    if args.full:
        print("## 전수 매트릭스")
        print()
        print(render_full_matrix(entries, baseline_names, cells_map, categories_map))

    return 0


if __name__ == "__main__":
    sys.exit(main())
