"""Behavioral checks for it-autonomos-spain-improve-claudemd-legacy-anchors (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/it-autonomos-spain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**CRITICAL RULE**: When renaming any heading that may have been publicly shared, ALWAYS add a legacy anchor to preserve old links.' in text, "expected to find: " + '**CRITICAL RULE**: When renaming any heading that may have been publicly shared, ALWAYS add a legacy anchor to preserve old links.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- [ ] Legacy anchors added in ALL language versions if content was renamed' in text, "expected to find: " + '- [ ] Legacy anchors added in ALL language versions if content was renamed'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Add invisible anchor with the old ID immediately before the new heading:' in text, "expected to find: " + 'Add invisible anchor with the old ID immediately before the new heading:'[:80]

