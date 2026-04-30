"""Behavioral checks for ai-refine-instructions-in-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Use project specific exceptions instead of global exception classes like \\RuntimeException, \\InvalidArgumentException etc.' in text, "expected to find: " + '- Use project specific exceptions instead of global exception classes like \\RuntimeException, \\InvalidArgumentException etc.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Prefer classic if statements over short-circuit evaluation when possible' in text, "expected to find: " + '- Prefer classic if statements over short-circuit evaluation when possible'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Add @author tags to newly introduced classes by the user' in text, "expected to find: " + '- Add @author tags to newly introduced classes by the user'[:80]

