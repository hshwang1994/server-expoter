#!/usr/bin/env python3
"""pre-commit hook — staged 파일에 대한 보호 경로 / 비밀값 / 잔재 어휘 검사.

검사:
- staged 파일에 vault/* / *.env / *.pem 같은 비밀값 파일 → block
- staged 파일에 clovirone 잔재 어휘 (Java/Spring/MyBatis/...) → block (advisory 가능)
- staged 파일에 평문 password / api_key 의심 → warn

Usage:
    pre-commit hook이 자동 호출. 수동:
    python scripts/ai/hooks/pre_commit_policy.py

Exit codes:
    0 = 통과
    2 = 보호 경로 위반 (block)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# 비밀값 파일 (절대 commit 금지)
SECRET_PATTERNS = [
    re.compile(r"^vault/.*\.yml$"),
    re.compile(r"\.env(\..+)?$"),
    re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
    re.compile(r"id_rsa(\.pub)?$"),
    re.compile(r"\.p12$"),
    re.compile(r"\.jks$"),
]

# 잔재 어휘 (server-exporter는 등장하면 안 됨)
FORBIDDEN_WORDS = [
    "BillingCalculator", "clovircm-domain", "clovircm-web",
    "plugin-posco", "plugin-smilegate", "sk-hynix-dev",
]

# 평문 비밀값 의심 패턴
SECRET_VALUE_RE = re.compile(
    r"(password|secret|api_key|token|bmc_password|idrac_password)"
    r"\s*[:=]\s*[\"']([a-zA-Z0-9!@#$%^&*\-_=+]{6,})[\"']",
    re.IGNORECASE,
)


def _staged_files(repo_root: Path) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
        return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    except Exception:
        return []


def _staged_content(repo_root: Path, file_path: str) -> str:
    try:
        r = subprocess.run(
            ["git", "show", f":{file_path}"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=5,
            encoding="utf-8", errors="replace",
        )
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    if os.environ.get("PRE_COMMIT_POLICY_SKIP") == "1":
        return 0

    repo_root = Path(".").resolve()
    files = _staged_files(repo_root)
    if not files:
        return 0

    blocks = []
    warnings = []

    for f in files:
        # 비밀값 파일
        for sp in SECRET_PATTERNS:
            if sp.search(f):
                blocks.append(f"비밀값 파일 staged: {f}")
                break

        # 잔재 어휘
        if f.endswith((".md", ".py", ".yml", ".yaml", ".json")):
            content = _staged_content(repo_root, f)
            for word in FORBIDDEN_WORDS:
                if word in content:
                    warnings.append(f"clovirone 잔재 어휘 '{word}' in {f}")

            # 평문 비밀값
            for m in SECRET_VALUE_RE.finditer(content):
                key = m.group(1)
                # vault placeholder는 허용
                if "{{" in m.group(2) or m.group(2) in ("CHANGE_ME", "TODO", "EXAMPLE"):
                    continue
                warnings.append(f"평문 비밀값 의심 {key}=... in {f}")

    if blocks:
        print("[pre-commit] 보호 경로 위반 — commit 차단:", file=sys.stderr)
        for b in blocks:
            print(f"  - {b}", file=sys.stderr)
        print("\n  의도적 commit 시: PRE_COMMIT_POLICY_SKIP=1 git commit ...", file=sys.stderr)
        return 2

    if warnings:
        print("[pre-commit] 경고 (commit 허용):", file=sys.stderr)
        for w in warnings[:10]:
            print(f"  - {w}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
