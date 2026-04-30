"""Behavioral checks for ingress-intel-total-conversion-add-claudemd-with-version-man (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ingress-intel-total-conversion")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Minor version** (0.3.4 → 0.4.0): New features, API changes, significant enhancements' in text, "expected to find: " + '- **Minor version** (0.3.4 → 0.4.0): New features, API changes, significant enhancements'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **Core**: `'Fix RegionScore tooltip HTML rendering'`, `'Update MODs display colors'`" in text, "expected to find: " + "- **Core**: `'Fix RegionScore tooltip HTML rendering'`, `'Update MODs display colors'`"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Keep descriptions concise and user-focused, avoiding technical implementation details.' in text, "expected to find: " + 'Keep descriptions concise and user-focused, avoiding technical implementation details.'[:80]

