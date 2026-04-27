"""Behavioral checks for nanoclaw-fixgmail-add-onecli-credential-mode (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail/SKILL.md')
    assert 'Check that `config.hasCredentials` is `true` or `connection` is not null. The response `hint` field has instructions and a docs URL for what stub credential files to create under `~/.gmail-mcp/`. Foll' in text, "expected to find: " + 'Check that `config.hasCredentials` is `true` or `connection` is not null. The response `hint` field has instructions and a docs URL for what stub credential files to create under `~/.gmail-mcp/`. Foll'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail/SKILL.md')
    assert '**If OneCLI:** Tell the user to open `${ONECLI_URL}/connections?connect=gmail` to set up their Gmail connection. The dashboard walks them through creating a Google Cloud OAuth app and authorizing it. ' in text, "expected to find: " + '**If OneCLI:** Tell the user to open `${ONECLI_URL}/connections?connect=gmail` to set up their Gmail connection. The dashboard walks them through creating a Google Cloud OAuth app and authorizing it. '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail/SKILL.md')
    assert 'If `credentials.json` already exists with real tokens (not `onecli-managed` values), skip to "Build and restart" below.' in text, "expected to find: " + 'If `credentials.json` already exists with real tokens (not `onecli-managed` values), skip to "Build and restart" below.'[:80]

