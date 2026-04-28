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

# Scaffold-time tier-1 patterns: what the deterministic verbatim-grep scaffolder
# (scripts/scaffold_markdown_only.py) is willing to build a task from. Slightly
# broader than AGENT_INSTRUCTION_PATTERNS — accepts any .md inside .claude/skills
# (not just SKILL.md), any file under .cursor/rules/, prompt files, etc.
# Mirrors the historical scaffold_markdown_only.TIER1_RE.
TIER1_SCAFFOLD_PATTERNS: list[str] = [
    r"(?:^|/)(CLAUDE\.md|CLAUDE\.local\.md|AGENTS\.md|CONVENTIONS\.md|SKILL\.md|"
    r"\.cursorrules|\.windsurfrules|\.clinerules|\.continuerules)$",
    r"^\.claude/(rules|skills|agents)/.+\.md$",
    r"^\.cursor/rules/.+",
    r"^\.github/(copilot-instructions\.md|skills/.+SKILL\.md|prompts/.+\.prompt\.md)$",
    r"^\.agents?/skills/.+SKILL\.md$",
    r"^\.opencode/skills/.+SKILL\.md$",
    r"^\.codex/skills/.+SKILL\.md$",
    # Anthropic-style top-level skills/<name>/ layout: SKILL.md sits next to
    # forms.md, reference.md, CHANGELOG.md, etc. — sibling .md files are still
    # scaffold-eligible (verbatim-grep works on text).
    r"^skills/[^/]+/.+\.md$",
    # Same pattern under each skill convention — admit non-SKILL.md text
    # rule/reference files (e.g. .claude/skills/foo/references/api.md is
    # already covered by the .claude/(rules|skills|agents)/.+\.md$ above).
    r"^\.agents?/skills/[^/]+/.+\.md$",
    r"^\.opencode/skills/[^/]+/.+\.md$",
    r"^\.codex/skills/[^/]+/.+\.md$",
    r"^\.github/skills/[^/]+/.+\.md$",
    r"\.mdc$",
]
TIER1_SCAFFOLD_RE = re.compile("|".join(TIER1_SCAFFOLD_PATTERNS), re.IGNORECASE)

# Discovery-time tier-1 patterns: broad recall for the cross-repo discover →
# Gemini-post-judge pipeline. Anthropic's official skills layout
# (github.com/anthropics/skills) puts adjacent files like scripts/build.py,
# references/api.md, assets/template.html, CHANGELOG.md, LICENSE.txt next to
# SKILL.md. PRs that touch those are real skill-authoring work, but the
# scaffolder cannot deterministically build from them — Gemini decides.
SKILL_DIR_BROAD_PATTERNS: list[str] = [
    r"^skills/[^/]+/.+",            # top-level skills/<name>/...  (anthropics/skills layout)
    r"^\.claude/skills/[^/]+/.+",   # any file under .claude/skills/<name>/
    r"^\.agents?/skills/[^/]+/.+",
    r"^\.opencode/skills/[^/]+/.+",
    r"^\.codex/skills/[^/]+/.+",
    r"^\.github/skills/[^/]+/.+",
]
TIER1_DISCOVERY_PATTERNS: list[str] = TIER1_SCAFFOLD_PATTERNS + SKILL_DIR_BROAD_PATTERNS
TIER1_DISCOVERY_RE = re.compile("|".join(TIER1_DISCOVERY_PATTERNS), re.IGNORECASE)

# Binary file extensions — common in skill assets/ subdirectories. The
# verbatim-grep scaffolder cannot test these, but discovery may include them.
BINARY_EXT_RE = re.compile(
    r"\.(png|jpe?g|gif|webp|svg|ico|pdf|zip|tar|gz|tgz|bz2|xz|"
    r"woff2?|ttf|otf|eot|"
    r"mp3|mp4|mov|avi|webm|wav|"
    r"wasm|so|dylib|dll|exe|class|jar)$",
    re.IGNORECASE,
)


def is_tier1_scaffold(path: str) -> bool:
    """File is something the deterministic verbatim-grep scaffolder can build a
    markdown_authoring task from (text rule file or skill .md)."""
    return bool(TIER1_SCAFFOLD_RE.search(path))


def is_tier1_discoverable(path: str) -> bool:
    """File is part of a skill / rule-file directory hierarchy. Used by the
    cross-repo discovery pipeline to keep skill-adjacent PRs (scripts/,
    references/, assets/) in the candidate pool — Gemini judges them."""
    return bool(TIER1_DISCOVERY_RE.search(path))

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

def gh_json(cmd: list[str], retries: int = 5, timeout: int = 120) -> list | dict:
    """Run a gh command and parse JSON output, with retries for rate limits.

    Retries up to `retries` times on:
      - subprocess timeouts
      - GH 5xx (502/503/504) — gateway errors
      - GH rate-limit / abuse messages

    Backoff: 5xx uses 10s × (attempt+1) capped at 60s. Rate-limit uses
    30s × (attempt+1). Both cap retries at 5 by default (was 3 — too low
    for sustained GraphQL 504 storms observed during deep-scout passes).
    """
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["gh"] + cmd,
                capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            wait = min(10 * (attempt + 1), 60)
            print(f"  gh timeout (attempt {attempt + 1}/{retries}), waiting {wait}s",
                  file=sys.stderr)
            time.sleep(wait)
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
        if any(c in result.stderr for c in ("502", "503", "504")) or \
           "stream error" in stderr_lower or "gateway" in stderr_lower:
            wait = min(10 * (attempt + 1), 60)
            print(f"  Server error (attempt {attempt + 1}/{retries}), retrying in {wait}s... "
                  f"({result.stderr[:100]})", file=sys.stderr)
            time.sleep(wait)
            continue
        if result.stderr:
            print(f"  gh error: {result.stderr[:200]}", file=sys.stderr)
        return []
    return []
