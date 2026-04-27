"""Behavioral checks for last30days-skill-feat-inline-markdown-links-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/last30days-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**LAW 8 - EVERY CITATION IN THE NARRATIVE IS AN INLINE MARKDOWN LINK `[name](url)`. NEVER A RAW URL STRING. NEVER A PLAIN NAME WHEN A URL IS AVAILABLE.** Applies to every query type. In the "What I le' in text, "expected to find: " + '**LAW 8 - EVERY CITATION IN THE NARRATIVE IS AN INLINE MARKDOWN LINK `[name](url)`. NEVER A RAW URL STRING. NEVER A PLAIN NAME WHEN A URL IS AVAILABLE.** Applies to every query type. In the "What I le'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**Observed LAW 8 need (2026-04-20 inline-links saga):** the citation rule existed in SKILL.md but was placed in the CITATION PRIORITY block around line 1224 - below the chunked-read window. Four conse' in text, "expected to find: " + '**Observed LAW 8 need (2026-04-20 inline-links saga):** the citation rule existed in SKILL.md but was placed in the CITATION PRIORITY block around line 1224 - below the chunked-read window. Four conse'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**Post-synthesis self-check (do this BEFORE emitting your response):** scan your drafted "What I learned:" and KEY PATTERNS for the `[name](url)` pattern. Count how many inline markdown links appear. ' in text, "expected to find: " + '**Post-synthesis self-check (do this BEFORE emitting your response):** scan your drafted "What I learned:" and KEY PATTERNS for the `[name](url)` pattern. Count how many inline markdown links appear. '[:80]

