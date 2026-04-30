"""Behavioral checks for screenpipe-choreskills-sync-claudeskills-from-crates (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/screenpipe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/screenpipe-cli/SKILL.md')
    assert 'description: Manage screenpipe pipes (scheduled AI automations) and connections (Telegram, Slack, Discord, etc.) via the CLI. Use when the user asks to create, list, enable, disable, run, or debug pip' in text, "expected to find: " + 'description: Manage screenpipe pipes (scheduled AI automations) and connections (Telegram, Slack, Discord, etc.) via the CLI. Use when the user asks to create, list, enable, disable, run, or debug pip'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/screenpipe-cli/SKILL.md')
    assert 'Reads `~/.screenpipe/pipes/<pipe-name>/pipe.md`, extracts title/description/icon/category from YAML frontmatter, and publishes to the screenpipe pipe store. Requires auth (SCREENPIPE_API_KEY env var o' in text, "expected to find: " + 'Reads `~/.screenpipe/pipes/<pipe-name>/pipe.md`, extracts title/description/icon/category from YAML frontmatter, and publishes to the screenpipe pipe store. Requires auth (SCREENPIPE_API_KEY env var o'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/screenpipe-cli/SKILL.md')
    assert '**Config fields**: `schedule`, `enabled` (bool), `preset` (string or array — e.g. `"Oai"` or `["Primary", "Fallback"]`), `history` (bool — include previous output as context)' in text, "expected to find: " + '**Config fields**: `schedule`, `enabled` (bool), `preset` (string or array — e.g. `"Oai"` or `["Primary", "Fallback"]`), `history` (bool — include previous output as context)'[:80]

