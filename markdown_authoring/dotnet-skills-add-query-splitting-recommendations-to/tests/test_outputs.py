"""Behavioral checks for dotnet-skills-add-query-splitting-recommendations-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/efcore-patterns/SKILL.md')
    assert 'When you load multiple navigation collections via `Include()`, EF Core generates a single query that can cause cartesian explosion. If you have 10 orders with 10 items each, you get 100 rows instead o' in text, "expected to find: " + 'When you load multiple navigation collections via `Include()`, EF Core generates a single query that can cause cartesian explosion. If you have 10 orders with 10 items each, you get 100 rows instead o'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/efcore-patterns/SKILL.md')
    assert 'description: Entity Framework Core best practices including NoTracking by default, query splitting for navigation collections, migration management, dedicated migration services, and common pitfalls t' in text, "expected to find: " + 'description: Entity Framework Core best practices including NoTracking by default, query splitting for navigation collections, migration management, dedicated migration services, and common pitfalls t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/efcore-patterns/SKILL.md')
    assert '**Recommendation**: Default to `SplitQuery` globally, override with `AsSingleQuery()` for specific queries where single-query is known to be better.' in text, "expected to find: " + '**Recommendation**: Default to `SplitQuery` globally, override with `AsSingleQuery()` for specific queries where single-query is known to be better.'[:80]

