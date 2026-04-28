"""Behavioral checks for beads-enhanced-naturallanguage-activation-for-beads (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/beads")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/beads/SKILL.md')
    assert '**Progressive Disclosure**: This skill provides essential instructions for all 30 beads commands. For advanced topics (compaction, templates, team workflows), see the references directory. Slash comma' in text, "expected to find: " + '**Progressive Disclosure**: This skill provides essential instructions for all 30 beads commands. For advanced topics (compaction, templates, team workflows), see the references directory. Slash comma'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/beads/SKILL.md')
    assert '**bd (beads)** replaces markdown task lists with a dependency-aware graph stored in git. Unlike TodoWrite (session-scoped), bd persists across compactions and tracks complex dependencies.' in text, "expected to find: " + '**bd (beads)** replaces markdown task lists with a dependency-aware graph stored in git. Unlike TodoWrite (session-scoped), bd persists across compactions and tracks complex dependencies.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/beads/SKILL.md')
    assert 'Graph-based issue tracker that survives conversation compaction. Provides persistent memory for multi-session work with complex dependencies.' in text, "expected to find: " + 'Graph-based issue tracker that survives conversation compaction. Provides persistent memory for multi-session work with complex dependencies.'[:80]

