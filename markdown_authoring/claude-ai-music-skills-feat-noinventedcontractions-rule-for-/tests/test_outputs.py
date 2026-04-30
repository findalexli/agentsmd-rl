"""Behavioral checks for claude-ai-music-skills-feat-noinventedcontractions-rule-for- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-ai-music-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- No invented contractions (signal'd, TV'd — spell out instead)" in text, "expected to find: " + "- No invented contractions (signal'd, TV'd — spell out instead)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert "Suno only recognizes standard English contractions. Never use made-up contractions by appending 'd, 'll, etc. to nouns, brand names, or non-standard words." in text, "expected to find: " + "Suno only recognizes standard English contractions. Never use made-up contractions by appending 'd, 'll, etc. to nouns, brand names, or non-standard words."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert "**Rule:** If the base word isn't a pronoun or standard auxiliary verb, don't contract it. Suno will mispronounce or skip invented contractions." in text, "expected to find: " + "**Rule:** If the base word isn't a pronoun or standard auxiliary verb, don't contract it. Suno will mispronounce or skip invented contractions."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert "3. **Pronunciation check**: Proper nouns, homographs, acronyms, tech terms, invented contractions (no noun'd/brand'd)" in text, "expected to find: " + "3. **Pronunciation check**: Proper nouns, homographs, acronyms, tech terms, invented contractions (no noun'd/brand'd)"[:80]

