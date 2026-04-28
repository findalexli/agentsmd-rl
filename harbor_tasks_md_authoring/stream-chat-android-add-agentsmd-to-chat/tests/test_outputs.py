"""Behavioral checks for stream-chat-android-add-agentsmd-to-chat (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stream-chat-android")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This project delivers **Stream Chat Android**, a modular SDK spanning low-level client APIs, offline persistence, and both Compose and XML UI kits. Treat it as customer-facing product code: changes ri' in text, "expected to find: " + 'This project delivers **Stream Chat Android**, a modular SDK spanning low-level client APIs, offline persistence, and both Compose and XML UI kits. Treat it as customer-facing product code: changes ri'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in Stream’s Android Chat repo. Humans are welcome too; tone is optimised for tools.' in text, "expected to find: " + 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in Stream’s Android Chat repo. Humans are welcome too; tone is optimised for tools.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Backtick test names (for example: ``fun `message list filters muted channels`()``) for readability; keep helper extensions private/internal.' in text, "expected to find: " + '- Backtick test names (for example: ``fun `message list filters muted channels`()``) for readability; keep helper extensions private/internal.'[:80]

