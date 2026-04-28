"""Behavioral checks for ssw.cleanarchitecture-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ssw.cleanarchitecture")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a .NET 10 Clean Architecture template using Domain-Driven Design (DDD) tactical patterns, CQRS with MediatR, and .NET Aspire for orchestration.' in text, "expected to find: " + 'This is a .NET 10 Clean Architecture template using Domain-Driven Design (DDD) tactical patterns, CQRS with MediatR, and .NET Aspire for orchestration.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '# SSW Clean Architecture - AGENTS.md' in text, "expected to find: " + '# SSW Clean Architecture - AGENTS.md'[:80]

