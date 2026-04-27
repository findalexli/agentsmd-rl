"""Behavioral checks for obsidian-wiki-summary-parser-safe-punctuation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-wiki")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-update/SKILL.md')
    assert '**Write a `summary:` frontmatter field** on every new/updated page (1–2 sentences, ≤200 chars), using `>-` folded style. For project sync, a good summary answers "what does this page tell me about the' in text, "expected to find: " + '**Write a `summary:` frontmatter field** on every new/updated page (1–2 sentences, ≤200 chars), using `>-` folded style. For project sync, a good summary answers "what does this page tell me about the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-update/SKILL.md')
    assert 'Use folded scalar syntax (summary: >-) for summary to keep frontmatter parser-safe across punctuation (:, #, quotes) without escaping rules.' in text, "expected to find: " + 'Use folded scalar syntax (summary: >-) for summary to keep frontmatter parser-safe across punctuation (:, #, quotes) without escaping rules.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-update/SKILL.md')
    assert 'One or two sentences (≤200 chars) describing what this page covers.' in text, "expected to find: " + 'One or two sentences (≤200 chars) describing what this page covers.'[:80]

