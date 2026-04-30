"""Behavioral checks for han-docs-clean-up-develop-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/han")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/develop/SKILL.md')
    assert 'Structured 8-phase process for building new features from requirement gathering through documentation. Each phase produces a concrete output that feeds the next.' in text, "expected to find: " + 'Structured 8-phase process for building new features from requirement gathering through documentation. Each phase produces a concrete output that feeds the next.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/develop/SKILL.md')
    assert 'explore codebase patterns, clarify ambiguities with the user, design architecture,' in text, "expected to find: " + 'explore codebase patterns, clarify ambiguities with the user, design architecture,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/develop/SKILL.md')
    assert 'implement with TDD, run multi-agent code review, validate all quality gates, and' in text, "expected to find: " + 'implement with TDD, run multi-agent code review, validate all quality gates, and'[:80]

