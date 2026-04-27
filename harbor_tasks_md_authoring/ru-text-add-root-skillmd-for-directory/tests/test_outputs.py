"""Behavioral checks for ru-text-add-root-skillmd-for-directory (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ru-text")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**Style priority**: if the user explicitly requests a specific style (casual, academic, SEO, literary, etc.), their prompt overrides these default rules where they conflict. These rules are defaults, ' in text, "expected to find: " + '**Style priority**: if the user explicitly requests a specific style (casual, academic, SEO, literary, etc.), their prompt overrides these default rules where they conflict. These rules are defaults, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '| Grammar, capitalization, agreement, pleonasms | [editorial-grammar.md](skills/ru-text/references/editorial-grammar.md) |' in text, "expected to find: " + '| Grammar, capitalization, agreement, pleonasms | [editorial-grammar.md](skills/ru-text/references/editorial-grammar.md) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '| Punctuation review, comma placement | [editorial-punctuation.md](skills/ru-text/references/editorial-punctuation.md) |' in text, "expected to find: " + '| Punctuation review, comma placement | [editorial-punctuation.md](skills/ru-text/references/editorial-punctuation.md) |'[:80]

