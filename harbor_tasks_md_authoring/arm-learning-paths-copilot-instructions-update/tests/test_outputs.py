"""Behavioral checks for arm-learning-paths-copilot-instructions-update (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/arm-learning-paths")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Common phrases: "To [action]" (not "Follow the steps below to [action]"), "for example" (not "e.g."), "that is" (not "i.e."), "because" (not "since"), "also" (not "in addition"), "to" (not "in order' in text, "expected to find: " + '- Common phrases: "To [action]" (not "Follow the steps below to [action]"), "for example" (not "e.g."), "that is" (not "i.e."), "because" (not "since"), "also" (not "in addition"), "to" (not "in order'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The `/content` directory is the primary workspace where contributors add new Learning Paths as markdown files, organized into category-specific subdirectories that correspond to the different learning' in text, "expected to find: " + 'The `/content` directory is the primary workspace where contributors add new Learning Paths as markdown files, organized into category-specific subdirectories that correspond to the different learning'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Each Learning Path must have an `_index.md` file and a `_next-steps.md` file. The `_index.md` file contains the main content of the Learning Path. The `_next-steps.md` file contains links to related c' in text, "expected to find: " + 'Each Learning Path must have an `_index.md` file and a `_next-steps.md` file. The `_index.md` file contains the main content of the Learning Path. The `_next-steps.md` file contains links to related c'[:80]

