#!/usr/bin/env python3
"""편집 전 보호 경로 가드 — server-exporter 보호 경로 적용.

server-exporter 보호 경로:
- absolute (block): .git/, vault/**, *.log, *.env, *.pem, *.key
- ticket (ask): ansible.cfg, Jenkinsfile*, schema/sections.yml, schema/field_dictionary.yml,
                schema/baseline_v1/**
- vendor_boundary (ask): adapters/**, redfish-gather/library/**, common/library/**
- docs_baseline (ask): CLAUDE.md, .claude/{rules,policy,skills,agents,ai-context,templates}/

Hook 모드 stdin JSON → permissionDecision JSON stdout
CLI 모드: 직접 file_path 인자.

Exit codes (CLI):
    0 = 정상
    1 = 실행 에러
    2 = block (critical)
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from policy_loader import load_protected_paths

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# YAML 로드 실패 시 fallback (server-exporter 도메인)
_FALLBACK_PROTECTED_PATHS = [
    # critical (block)
    (r"^\.git/", "critical", ".git 내부 — 절대 금지"),
    (r"^vault/", "critical", "Vault 비밀값 — 절대 금지"),
    (r"\.env(\..+)?$", "critical", "환경변수 — 절대 금지"),
    (r"\.pem$", "critical", "개인키 — 절대 금지"),
    (r"\.key$", "critical", "키 파일 — 절대 금지"),
    (r"\.log$", "critical", "로그 — 절대 금지"),

    # high (ticket required)
    (r"^Jenkinsfile($|_)", "high", "Jenkins 파이프라인 — 티켓 필요"),
    (r"^ansible\.cfg$", "high", "Ansible 설정 — 티켓 필요"),
    (r"^schema/sections\.yml$", "high", "출력 섹션 정의 — 티켓 필요"),
    (r"^schema/field_dictionary\.yml$", "high", "필드 사전 — 티켓 필요"),
    (r"^schema/baseline_v1/", "high", "Baseline 회귀 기준선 — 티켓 필요"),

    # medium (vendor boundary / harness control plane)
    (r"^adapters/", "medium", "벤더 어댑터 — 경계 보호"),
    (r"^redfish-gather/library/", "medium", "Redfish 라이브러리 — 경계 보호"),
    (r"^common/library/", "medium", "공통 라이브러리 — 경계 보호"),
    (r"^CLAUDE\.md$", "medium", "Tier 0 정본"),
    (r"^GUIDE_FOR_AI\.md$", "medium", "AI 가이드 정본"),
    (r"^REQUIREMENTS\.md$", "medium", "요구사항 정본"),
    (r"^\.claude/rules/", "medium", "하네스 규칙"),
    (r"^\.claude/policy/", "medium", "하네스 정책"),
    (r"^\.claude/skills/", "medium", "하네스 스킬"),
    (r"^\.claude/agents/", "medium", "하네스 agent 정의"),
    (r"^\.claude/ai-context/", "medium", "하네스 ai-context"),
    (r"^\.claude/templates/", "medium", "하네스 템플릿"),
    (r"^docs/ai/policy/", "medium", "하네스 정책 문서"),
    (r"^docs/ai/decisions/", "medium", "하네스 결정 기록 (ADR)"),
    (r"^docs/ai/roadmap/", "medium", "하네스 로드맵"),
    (r"^docs/ai/workflows/", "medium", "하네스 워크플로"),
]


def check_file(file_path: str, repo_root: Path, protected_paths=None) -> dict:
    if protected_paths is None:
        protected_paths = _FALLBACK_PROTECTED_PATHS
    try:
        abs_path = Path(file_path).resolve()
        if abs_path.is_relative_to(repo_root):
            rel_path = str(abs_path.relative_to(repo_root)).replace("\\", "/")
        else:
            rel_path = file_path.replace("\\", "/")
    except (ValueError, TypeError):
        rel_path = file_path.replace("\\", "/")

    for pattern, severity, description in protected_paths:
        if re.search(pattern, rel_path):
            return {
                "file": file_path,
                "relative_path": rel_path,
                "protected": True,
                "severity": severity,
                "description": description,
                "action": "block" if severity == "critical" else "warn",
            }

    return {
        "file": file_path,
        "relative_path": rel_path,
        "protected": False,
        "severity": "none",
        "description": "보호 대상 아님",
        "action": "allow",
    }


def _read_payload_from_stdin() -> dict | None:
    if sys.stdin.isatty():
        return None
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        return json.loads(raw)
    except (json.JSONDecodeError, AttributeError):
        return None


def _emit_hook_decision(severity: str, description: str, rel_path: str) -> None:
    if severity == "critical":
        decision = "deny"
        reason = f"절대 보호 경로 차단 — {description} ({rel_path})"
    elif severity in ("high", "medium"):
        decision = "ask"
        reason = f"[{severity}] {description} — 사용자 확인 필요 ({rel_path})"
    else:
        decision = "allow"
        reason = ""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
        }
    }
    if reason:
        output["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(output, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="편집 전 보호 경로 가드")
    parser.add_argument("file_path", nargs="?", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    payload = _read_payload_from_stdin() if not args.file_path else None
    is_hook_mode = bool(payload and payload.get("hook_event_name"))

    file_path = args.file_path
    if not file_path and payload:
        tool_input = payload.get("tool_input", {}) if isinstance(payload, dict) else {}
        file_path = tool_input.get("file_path")
    if not file_path:
        if is_hook_mode:
            _emit_hook_decision("none", "", "")
        return 0

    repo_root = Path(args.repo_root).resolve()

    try:
        protected_paths = load_protected_paths(repo_root, _FALLBACK_PROTECTED_PATHS)
        result = check_file(file_path, repo_root, protected_paths)
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        if is_hook_mode:
            _emit_hook_decision("high", f"policy load 실패: {e}", str(file_path))
            return 0
        return 1

    if is_hook_mode:
        _emit_hook_decision(result["severity"], result["description"], result["relative_path"])
        return 0

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["action"] == "block":
            print(f"차단: {result['file']}\n  사유: {result['description']}\n  등급: {result['severity'].upper()}")
        elif result["action"] == "warn":
            print(f"경고: {result['file']}\n  사유: {result['description']}\n  등급: {result['severity'].upper()}")
        else:
            print(f"허용: {result['file']}")

    return 2 if result["action"] == "block" else 0


if __name__ == "__main__":
    sys.exit(main())
