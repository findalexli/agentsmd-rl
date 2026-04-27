"""Behavioral checks for claude-ai-music-skills-feat-versechorus-echo-check-phrase (markdown_authoring task).

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
    assert '11. **Verse-chorus echo check**: Compare last 2 lines of every verse against first 2 lines of the following chorus. Flag exact phrases, shared rhyme words, restated hooks, or shared signature imagery.' in text, "expected to find: " + '11. **Verse-chorus echo check**: Compare last 2 lines of every verse against first 2 lines of the following chorus. Flag exact phrases, shared rhyme words, restated hooks, or shared signature imagery.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '11. **Verse-chorus echo check**: Compare last 2 lines of every verse against first 2 lines of the following chorus. Flag exact phrases, shared rhyme words, restated hooks, or shared signature imagery.' in text, "expected to find: " + '11. **Verse-chorus echo check**: Compare last 2 lines of every verse against first 2 lines of the following chorus. Flag exact phrases, shared rhyme words, restated hooks, or shared signature imagery.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert 'A verse must never repeat a key phrase, image, or rhyme word that appears in the chorus it leads into. The chorus is the hook — if the verse already said it, the chorus loses its impact.' in text, "expected to find: " + 'A verse must never repeat a key phrase, image, or rhyme word that appears in the chorus it leads into. The chorus is the hook — if the verse already said it, the chorus loses its impact.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '**Scope:** This applies to EVERY verse-to-chorus transition in the track, not just the first one. Check all of them. Also check bridge-to-chorus transitions.' in text, "expected to find: " + '**Scope:** This applies to EVERY verse-to-chorus transition in the track, not just the first one. Check all of them. Also check bridge-to-chorus transitions.'[:80]

