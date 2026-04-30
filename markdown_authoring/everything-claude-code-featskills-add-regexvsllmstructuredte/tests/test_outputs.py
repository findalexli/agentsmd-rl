"""Behavioral checks for everything-claude-code-featskills-add-regexvsllmstructuredte (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/regex-vs-llm-structured-text/SKILL.md')
    assert 'A practical decision framework for parsing structured text (quizzes, forms, invoices, documents). The key insight: regex handles 95-98% of cases cheaply and deterministically. Reserve expensive LLM ca' in text, "expected to find: " + 'A practical decision framework for parsing structured text (quizzes, forms, invoices, documents). The key insight: regex handles 95-98% of cases cheaply and deterministically. Reserve expensive LLM ca'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/regex-vs-llm-structured-text/SKILL.md')
    assert 'description: Decision framework for choosing between regex and LLM when parsing structured text — start with regex, add LLM only for low-confidence edge cases.' in text, "expected to find: " + 'description: Decision framework for choosing between regex and LLM when parsing structured text — start with regex, add LLM only for low-confidence edge cases.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/regex-vs-llm-structured-text/SKILL.md')
    assert '- **TDD works well** for parsers — write tests for known patterns first, then edge cases' in text, "expected to find: " + '- **TDD works well** for parsers — write tests for known patterns first, then edge cases'[:80]

