"""Behavioral checks for sentry-cli-metaclaude-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "This project uses **Cursor's Context Rules** system located in `.cursor/rules/`. **ALWAYS** read and load the content of relevant rules from this directory into context when working on the codebase." in text, "expected to find: " + "This project uses **Cursor's Context Rules** system located in `.cursor/rules/`. **ALWAYS** read and load the content of relevant rules from this directory into context when working on the codebase."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Read all files in the `.cursor/rules/` directory to discover what rules are available. Each rule file uses the `.mdc` extension (Markdown with frontmatter).' in text, "expected to find: " + 'Read all files in the `.cursor/rules/` directory to discover what rules are available. Each rule file uses the `.mdc` extension (Markdown with frontmatter).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Treat these rules as **mandatory guidance** that you must follow for all code changes and development activities within this project.' in text, "expected to find: " + 'Treat these rules as **mandatory guidance** that you must follow for all code changes and development activities within this project.'[:80]

