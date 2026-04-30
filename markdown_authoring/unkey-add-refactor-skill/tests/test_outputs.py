"""Behavioral checks for unkey-add-refactor-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/unkey")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/refactor/SKILL.md')
    assert 'description: Structural refactoring pass on changed code. Use after implementing a feature to improve code structure, reduce duplication, and clean up APIs without changing behavior.' in text, "expected to find: " + 'description: Structural refactoring pass on changed code. Use after implementing a feature to improve code structure, reduce duplication, and clean up APIs without changing behavior.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/refactor/SKILL.md')
    assert '- **Stay within the branch diff.** Only refactor code that was added or modified in this branch. Do not refactor unrelated code unless it is directly entangled.' in text, "expected to find: " + '- **Stay within the branch diff.** Only refactor code that was added or modified in this branch. Do not refactor unrelated code unless it is directly entangled.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/refactor/SKILL.md')
    assert '3. **Clean up APIs and interfaces**: Remove unused parameters, exports, and return values. Simplify function signatures. Make types tighter and more precise.' in text, "expected to find: " + '3. **Clean up APIs and interfaces**: Remove unused parameters, exports, and return values. Simplify function signatures. Make types tighter and more precise.'[:80]

