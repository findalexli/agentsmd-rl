"""Behavioral checks for prairielearn-add-additional-conventions-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prairielearn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Don't add extra defensive checks or try/catch blocks that are abnormal for that area of the codebase (especially if called by trusted / validated codepaths)." in text, "expected to find: " + "- Don't add extra defensive checks or try/catch blocks that are abnormal for that area of the codebase (especially if called by trusted / validated codepaths)."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Don't add extra comments that a human wouldn't add or that are inconsistent with the rest of the file." in text, "expected to find: " + "- Don't add extra comments that a human wouldn't add or that are inconsistent with the rest of the file."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Titles and buttons should use sentence case ("Save course", "Discard these changes").' in text, "expected to find: " + '- Titles and buttons should use sentence case ("Save course", "Discard these changes").'[:80]

