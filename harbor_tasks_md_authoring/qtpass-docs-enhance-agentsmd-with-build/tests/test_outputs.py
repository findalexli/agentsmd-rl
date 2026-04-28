"""Behavioral checks for qtpass-docs-enhance-agentsmd-with-build (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `QCoreApplication::arguments()` instead of raw `argv[]` for CLI parsing (for proper Unicode handling and cross-platform consistency)' in text, "expected to find: " + '- Use `QCoreApplication::arguments()` instead of raw `argv[]` for CLI parsing (for proper Unicode handling and cross-platform consistency)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Verify signing works: `git commit -S --allow-empty -m "test signed commit"` (then reset if needed).' in text, "expected to find: " + '- Verify signing works: `git commit -S --allow-empty -m "test signed commit"` (then reset if needed).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If signing fails, set up your signing key and Git `user.signingkey`/signing format, then retry.' in text, "expected to find: " + '- If signing fails, set up your signing key and Git `user.signingkey`/signing format, then retry.'[:80]

