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

# Tier 1: Agent instruction files — changes here directly affect agent behavior.
# These are what make agentmd tasks valuable.
AGENT_INSTRUCTION_PATTERNS: list[str] = [
    # Claude Code
    r"CLAUDE\.md$",
    r"CLAUDE\.local\.md$",
    r"\.claude/CLAUDE\.md$",
    r"\.claude/rules/.*\.md$",        # modular rules (path-scoped)
    r"\.claude/skills/.*/SKILL\.md$",  # skills with frontmatter
    r"\.claude/agents/.*\.md$",        # custom subagent definitions
    # GitHub-hosted skills (e.g., dotnet/maui .github/skills/)
    r"\.github/skills/.*SKILL\.md$",
    r"\.agents/skills/.*SKILL\.md$",   # alternative convention (PostHog, vscode, openai-agents-js)
    r"\.agent/skills/.*SKILL\.md$",    # singular variant (apache/beam)
    r"\.opencode/skills/.*SKILL\.md$", # cloudflare/workerd convention
    r"\.codex/skills/.*SKILL\.md$",    # dagger convention
    r"\.github/prompts/.*\.prompt\.md$",  # vscode + next.js prompt-files convention
    # Cross-tool
    r"AGENTS\.md$",
    r"SKILL\.md$",
    r"CONVENTIONS\.md$",
    # Cursor
    r"\.cursorrules$",
    r"\.cursor/rules",
    # GitHub Copilot
    r"copilot-instructions\.md$",
    # Other agents
    r"\.windsurfrules$",
    r"\.clinerules$",
    r"\.continuerules$",
    r"\.cody/",
    r"\.mdc$",
]

# Tier 2: Documentation files — usually noise (changelogs, version bumps),
# but occasionally meaningful when paired with a Tier 1 rule that requires doc updates.
DOC_PATTERNS: list[str] = [
    r"README\.md$",
    r"CONTRIBUTING\.md$",
    r"CHANGELOG\.md$",
]

# Combined: all config-like files (backward compat)
CONFIG_PATTERNS: list[str] = AGENT_INSTRUCTION_PATTERNS + DOC_PATTERNS

AGENT_INSTRUCTION_RE = re.compile("|".join(AGENT_INSTRUCTION_PATTERNS), re.IGNORECASE)
DOC_RE = re.compile("|".join(DOC_PATTERNS), re.IGNORECASE)
CONFIG_RE = re.compile("|".join(CONFIG_PATTERNS), re.IGNORECASE)

NON_CODE_EXTENSIONS = frozenset({
    ".md", ".rst", ".txt", ".toml", ".cfg", ".ini",
    ".yml", ".yaml", ".json", ".lock", ".sum",
})

NON_CODE_PREFIXES = (
    "docs/", "doc/", ".github/workflows/", ".github/ISSUE_TEMPLATE/",
)


def is_config_file(path: str) -> bool:
    """Check if a file path matches any config pattern (Tier 1 or 2)."""
    return bool(CONFIG_RE.search(path))


def is_agent_instruction_file(path: str) -> bool:
    """Check if a file is a Tier 1 agent instruction file (CLAUDE.md, AGENTS.md, etc.).

    These are the high-value files — changes here directly affect agent behavior.
    """
    return bool(AGENT_INSTRUCTION_RE.search(path))


def is_doc_file(path: str) -> bool:
    """Check if a file is a Tier 2 documentation file (README.md, CHANGELOG.md, etc.)."""
    return bool(DOC_RE.search(path))


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
        stderr_lower = result.stderr.lower()
        if "rate limit" in stderr_lower or "abuse" in stderr_lower:
            wait = 30 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        if "502" in result.stderr or "503" in result.stderr or "stream error" in stderr_lower:
            wait = 5 * (attempt + 1)
            print(f"  Server error, retrying in {wait}s... ({result.stderr[:100]})", file=sys.stderr)
            time.sleep(wait)
            continue
        if result.stderr:
            print(f"  gh error: {result.stderr[:200]}", file=sys.stderr)
        return []
    return []
