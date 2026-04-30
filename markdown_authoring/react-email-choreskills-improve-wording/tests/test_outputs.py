"""Behavioral checks for react-email-choreskills-improve-wording (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/react-email")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/react-email/SKILL.md')
    assert '- If the user is asking to use media queries, inform them that not all email clients support them, and suggest a different approach;' in text, "expected to find: " + '- If the user is asking to use media queries, inform them that not all email clients support them, and suggest a different approach;'[:80]

