"""Behavioral checks for anytype-swift-ios5415-add-code-review-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anytype-swift")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Code Review Guidelines**: `/.github/workflows/code-review-guidelines.md` - Shared review standards for local and automated CI reviews' in text, "expected to find: " + '- **Code Review Guidelines**: `/.github/workflows/code-review-guidelines.md` - Shared review standards for local and automated CI reviews'[:80]

