"""Behavioral checks for kopia-choreci-update-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kopia")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Ensure there are tests that cover and exercise the new or changed functionality' in text, "expected to find: " + '- Ensure there are tests that cover and exercise the new or changed functionality'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '## Review Test Coverage' in text, "expected to find: " + '## Review Test Coverage'[:80]

