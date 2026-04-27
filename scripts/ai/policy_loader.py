#!/usr/bin/env python3
"""Protected path policy loader.

Reads .claude/policy/protected-paths.yaml and converts glob patterns
to regex tuples. Falls back to hardcoded defaults if YAML not found.
Uses stdlib only (no PyYAML).

server-exporter 도메인:
- absolute_protection: .git/, vault/**, *.log
- ticket_required: ansible.cfg, Jenkinsfile*, schema/sections.yml,
                   schema/field_dictionary.yml, schema/baseline_v1/**
- vendor_boundary: adapters/**, redfish-gather/library/**, common/library/**
- docs_baseline: CLAUDE.md, .claude/rules/, .claude/policy/, ...
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple


def _glob_to_regex(pattern: str) -> str:
    """Convert a simple glob pattern to a regex string."""
    result = pattern.replace(".", r"\.")
    result = result.replace("**/", "(.+/)?")
    result = result.replace("**", ".*")
    result = result.replace("*", "[^/]*")
    return result


def _parse_yaml_paths(yaml_text: str) -> Dict[str, List[str]]:
    """Simple line-based YAML parser for protected-paths.yaml."""
    sections: Dict[str, List[str]] = {}
    current_section = ""
    in_paths = False

    for raw_line in yaml_text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if indent == 0 and stripped.endswith(":"):
            current_section = stripped[:-1].strip()
            sections[current_section] = []
            in_paths = False
            continue

        if indent == 2 and stripped == "paths:":
            in_paths = True
            continue

        if indent == 2 and ":" in stripped and not stripped.startswith("- "):
            in_paths = False
            continue

        if in_paths and stripped.startswith("- "):
            value = stripped[2:].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if current_section and value:
                sections[current_section].append(value)

    return sections


# Section name -> (severity, description prefix)
_SEVERITY_MAP: Dict[str, Tuple[str, str]] = {
    "absolute_protection": ("critical", "절대 보호 경로"),
    "ticket_required":     ("high",     "티켓 필요 경로"),
    "vendor_boundary":     ("medium",   "벤더 경계 경로"),
    "docs_baseline":       ("medium",   "문서 기준선 경로"),
}


def _warn(message: str) -> None:
    """stderr로 경고 출력 (audit trail 용)."""
    sys.stderr.write(f"[policy_loader] WARN: {message}\n")


def load_protected_paths(
    repo_root: Path,
    fallback: List[Tuple[str, str, str]],
) -> List[Tuple[str, str, str]]:
    """정책 YAML에서 보호 경로를 로드한다.

    파일 누락·파싱 실패 시 fallback 반환하되 stderr에 경고 (fail-open + audit).
    """
    yaml_path = repo_root / ".claude" / "policy" / "protected-paths.yaml"

    if not yaml_path.is_file():
        _warn(f"policy YAML not found at {yaml_path} — using hardcoded fallback")
        return list(fallback)

    try:
        yaml_text = yaml_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        _warn(f"failed to read {yaml_path}: {exc} — using hardcoded fallback")
        return list(fallback)

    sections = _parse_yaml_paths(yaml_text)

    result: List[Tuple[str, str, str]] = []
    for section_name, patterns in sections.items():
        severity, desc_prefix = _SEVERITY_MAP.get(
            section_name, ("medium", section_name)
        )
        for pattern in patterns:
            regex = _glob_to_regex(pattern)
            result.append((regex, severity, f"{desc_prefix}: {pattern}"))

    if not result:
        _warn(f"{yaml_path} parsed but no rules extracted — using hardcoded fallback")
        return list(fallback)

    return result
