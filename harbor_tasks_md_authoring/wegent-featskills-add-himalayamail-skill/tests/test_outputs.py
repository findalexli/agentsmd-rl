"""Behavioral checks for wegent-featskills-add-himalayamail-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wegent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/init_data/skills/browser/SKILL.md')
    assert 'description: Complete real user web tasks end-to-end via browser-tool, navigate, interact, wait for page state, extract results, and provide evidence when needed.' in text, "expected to find: " + 'description: Complete real user web tasks end-to-end via browser-tool, navigate, interact, wait for page state, extract results, and provide evidence when needed.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/init_data/skills/himalaya-mail/SKILL.md')
    assert '- Do not use `himalaya message send` unless the user explicitly asks to send a raw RFC5322/MIME message; then validate `From:` exactly matches the selected account `email = "..."` from `~/.wegent-exec' in text, "expected to find: " + '- Do not use `himalaya message send` unless the user explicitly asks to send a raw RFC5322/MIME message; then validate `From:` exactly matches the selected account `email = "..."` from `~/.wegent-exec'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/init_data/skills/himalaya-mail/SKILL.md')
    assert 'First, discover the folder-list subcommand via local help (see step 2). Then list folders for the selected account and use the exact folder name from the CLI output in subsequent commands.' in text, "expected to find: " + 'First, discover the folder-list subcommand via local help (see step 2). Then list folders for the selected account and use the exact folder name from the CLI output in subsequent commands.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/init_data/skills/himalaya-mail/SKILL.md')
    assert 'description: Use Himalaya CLI to manage email (accounts/folders, list/read/search messages, compose/send). Prefer safe triage flows and require confirmation before any destructive action.' in text, "expected to find: " + 'description: Use Himalaya CLI to manage email (accounts/folders, list/read/search messages, compose/send). Prefer safe triage flows and require confirmation before any destructive action.'[:80]

