"""Behavioral checks for datahub-docs-improve-code-comment-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/datahub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- What the code does when it's self-evident (`# Loop through items`, `// Set variable to true`)" in text, "expected to find: " + "- What the code does when it's self-evident (`# Loop through items`, `// Set variable to true`)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **References** to tickets, RFCs, or external documentation that explain decisions' in text, "expected to find: " + '- **References** to tickets, RFCs, or external documentation that explain decisions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Only add comments that provide real value beyond what the code already expresses.' in text, "expected to find: " + 'Only add comments that provide real value beyond what the code already expresses.'[:80]

