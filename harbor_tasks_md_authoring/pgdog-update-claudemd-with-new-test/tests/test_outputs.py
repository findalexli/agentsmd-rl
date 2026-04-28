"""Behavioral checks for pgdog-update-claudemd-with-new-test (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pgdog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "VERY IMPORTANT: you are to act as a detective, attempting to find ways to falsify the code or planning we've done by discovering gaps or inconsistencies. ONLY write code when it is absolutely required" in text, "expected to find: " + "VERY IMPORTANT: you are to act as a detective, attempting to find ways to falsify the code or planning we've done by discovering gaps or inconsistencies. ONLY write code when it is absolutely required"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- A local PostgreSQL server is required for some tests to pass. Ensure it is set up, and if necessary create a database called "pgdog", and create a user called "pgdog" with password "pgdog".' in text, "expected to find: " + '- A local PostgreSQL server is required for some tests to pass. Ensure it is set up, and if necessary create a database called "pgdog", and create a user called "pgdog" with password "pgdog".'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Small Modules**: Try to keep files under 200 lines, unless required by implementation. NEVER allow files to exceed 1000 lines unless specifically instructed.' in text, "expected to find: " + '- **Small Modules**: Try to keep files under 200 lines, unless required by implementation. NEVER allow files to exceed 1000 lines unless specifically instructed.'[:80]

