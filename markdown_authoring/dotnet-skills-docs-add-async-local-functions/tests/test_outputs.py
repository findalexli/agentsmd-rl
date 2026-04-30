"""Behavioral checks for dotnet-skills-docs-add-async-local-functions (markdown_authoring task).

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
    text = _read('skills/csharp-concurrency-patterns/SKILL.md')
    assert '| **Exception handling** | Cleaner try/catch structure without `AggregateException` unwrapping |' in text, "expected to find: " + '| **Exception handling** | Cleaner try/catch structure without `AggregateException` unwrapping |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-concurrency-patterns/SKILL.md')
    assert '| **Debugging** | Stack traces show meaningful function names instead of `<>c__DisplayClass` |' in text, "expected to find: " + '| **Debugging** | Stack traces show meaningful function names instead of `<>c__DisplayClass` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-concurrency-patterns/SKILL.md')
    assert '| **Readability** | Named functions are self-documenting; anonymous lambdas obscure intent |' in text, "expected to find: " + '| **Readability** | Named functions are self-documenting; anonymous lambdas obscure intent |'[:80]

