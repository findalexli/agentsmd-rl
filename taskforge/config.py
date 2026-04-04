"""Shared configuration and utilities for taskforge.

Single source of truth for agent config file patterns, GitHub API helpers,
and file classification logic. Import from here — don't redefine.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from typing import Sequence

# ---------------------------------------------------------------------------
# Agent config file patterns
# ---------------------------------------------------------------------------

CONFIG_PATTERNS: list[str] = [
    r"CLAUDE\.md$",
    r"AGENTS\.md$",
    r"SKILL\.md$",
    r"\.cursorrules$",
    r"\.cursor/rules",
    r"copilot-instructions\.md$",
    r"\.windsurfrules$",
    r"\.clinerules$",
    r"\.continuerules$",
    r"\.cody/",
    r"CONVENTIONS\.md$",
    r"CONTRIBUTING\.md$",
    r"CHANGELOG\.md$",
    r"README\.md$",
    r"\.mdc$",
]

CONFIG_RE = re.compile("|".join(CONFIG_PATTERNS), re.IGNORECASE)

NON_CODE_EXTENSIONS = frozenset({
    ".md", ".rst", ".txt", ".toml", ".cfg", ".ini",
    ".yml", ".yaml", ".json", ".lock", ".sum",
})

NON_CODE_PREFIXES = (
    "docs/", "doc/", ".github/workflows/", ".github/ISSUE_TEMPLATE/",
)


def is_config_file(path: str) -> bool:
    """Check if a file path matches an agent config pattern."""
    return bool(CONFIG_RE.search(path))


def is_code_file(path: str) -> bool:
    """Check if a file is a real code file (not docs/config/lockfile)."""
    if is_config_file(path):
        return False
    ext = "." + path.rsplit(".", 1)[-1] if "." in path else ""
    if ext.lower() in NON_CODE_EXTENSIONS:
        return False
    if any(path.startswith(pfx) for pfx in NON_CODE_PREFIXES):
        return False
    return True


# ---------------------------------------------------------------------------
# Diff parsing utilities
# ---------------------------------------------------------------------------

def extract_config_hunks(diff_text: str) -> dict[str, str]:
    """Extract config file hunks from a unified diff.

    Returns {filepath: hunk_text} for each config file modified.
    Works on both gold patches (from solve.sh) and agent diffs.
    """
    hunks: dict[str, str] = {}
    current_file: str | None = None
    current_lines: list[str] = []

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if current_file and CONFIG_RE.search(current_file):
                hunks[current_file] = "\n".join(current_lines)
            match = re.match(r"diff --git a/(.*?) b/(.*)", line)
            current_file = match.group(2) if match else None
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_file and CONFIG_RE.search(current_file):
        hunks[current_file] = "\n".join(current_lines)

    return hunks


def extract_added_lines(hunk: str) -> str:
    """Get just the added lines from a diff hunk (no +++ prefix lines)."""
    return "\n".join(
        line[1:] for line in hunk.split("\n")
        if line.startswith("+") and not line.startswith("+++")
    ).strip()


# ---------------------------------------------------------------------------
# GitHub API helper
# ---------------------------------------------------------------------------

def gh_json(cmd: list[str], retries: int = 3, timeout: int = 120) -> list | dict:
    """Run a gh command and parse JSON output, with retries for rate limits."""
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["gh"] + cmd,
                capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"  gh timeout (attempt {attempt + 1})", file=sys.stderr)
            continue

        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return []
        if "rate limit" in result.stderr.lower() or "abuse" in result.stderr.lower():
            wait = 30 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        if result.stderr:
            print(f"  gh error: {result.stderr[:200]}", file=sys.stderr)
        return []
    return []
