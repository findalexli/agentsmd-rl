"""Behavioral checks for lxd-github-add-us-english-check (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lxd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Use **US English spelling** throughout all user-facing text, including documentation, CLI output, and error messages. Common examples:' in text, "expected to find: " + '- Use **US English spelling** throughout all user-facing text, including documentation, CLI output, and error messages. Common examples:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `initialize` not `initialise`' in text, "expected to find: " + '- `initialize` not `initialise`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `behavior` not `behaviour`' in text, "expected to find: " + '- `behavior` not `behaviour`'[:80]

