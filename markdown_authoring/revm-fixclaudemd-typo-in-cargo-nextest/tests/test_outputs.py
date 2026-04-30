"""Behavioral checks for revm-fixclaudemd-typo-in-cargo-nextest (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/revm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Update relevant examples if needed' in text, "expected to find: " + '- Update relevant examples if needed'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'cargo nextest run --workspace' in text, "expected to find: " + 'cargo nextest run --workspace'[:80]

