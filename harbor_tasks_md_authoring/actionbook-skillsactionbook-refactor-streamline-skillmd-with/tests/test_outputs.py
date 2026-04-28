"""Behavioral checks for actionbook-skillsactionbook-refactor-streamline-skillmd-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/actionbook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert '- Search by task description, not element name ("arxiv search papers" not "search button")' in text, "expected to find: " + '- Search by task description, not element name ("arxiv search papers" not "search button")'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert "- **Use Action Manual selectors first** - they are pre-verified and don't require snapshot" in text, "expected to find: " + "- **Use Action Manual selectors first** - they are pre-verified and don't require snapshot"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert '- [references/session-management.md](references/session-management.md) - Parallel sessions' in text, "expected to find: " + '- [references/session-management.md](references/session-management.md) - Parallel sessions'[:80]

