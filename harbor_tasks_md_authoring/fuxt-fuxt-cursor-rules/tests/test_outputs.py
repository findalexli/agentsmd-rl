"""Behavioral checks for fuxt-fuxt-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fuxt")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/fh-rules.mdc')
    assert 'When creating grid components (e.g., `grid-text`, `grid-work`, `grid-*`), **ALWAYS** use this template structure:' in text, "expected to find: " + 'When creating grid components (e.g., `grid-text`, `grid-work`, `grid-*`), **ALWAYS** use this template structure:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/fh-rules.mdc')
    assert '- **Block width formula**: `width: calc((100% - (var(--columns) - 1) * var(--gap-col)) / var(--columns));`' in text, "expected to find: " + '- **Block width formula**: `width: calc((100% - (var(--columns) - 1) * var(--gap-col)) / var(--columns));`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/fh-rules.mdc')
    assert '- Grids should default to **3 blocks on --gt-cinema, 2 blocks by default, and 1 block on --lt-phone**.' in text, "expected to find: " + '- Grids should default to **3 blocks on --gt-cinema, 2 blocks by default, and 1 block on --lt-phone**.'[:80]

