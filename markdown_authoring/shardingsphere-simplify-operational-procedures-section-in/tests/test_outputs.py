"""Behavioral checks for shardingsphere-simplify-operational-procedures-section-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shardingsphere")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Strictly prohibit unrelated code modifications**: Unless explicitly instructed, absolutely prohibit modifying any existing code, comments, configurations' in text, "expected to find: " + '1. **Strictly prohibit unrelated code modifications**: Unless explicitly instructed, absolutely prohibit modifying any existing code, comments, configurations'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Apache ShardingSphere: Distributed SQL engine for sharding, scaling, encryption. Database Plus concept - unified service layer over existing databases.' in text, "expected to find: " + 'Apache ShardingSphere: Distributed SQL engine for sharding, scaling, encryption. Database Plus concept - unified service layer over existing databases.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **Prohibit autonomous decisions**: No operations beyond instruction scope based on "common sense" or "best practices"' in text, "expected to find: " + '2. **Prohibit autonomous decisions**: No operations beyond instruction scope based on "common sense" or "best practices"'[:80]

