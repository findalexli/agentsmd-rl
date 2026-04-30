"""Behavioral checks for claude-ai-music-skills-fix-resolve-5-consistency-issues (markdown_authoring task).

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
    assert '| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error cost (6 skills) | lyric-writer, suno-engineer, album-conceptualizer, lyric-reviewer, researchers-legal, researchers-veri' in text, "expected to find: " + '| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error cost (6 skills) | lyric-writer, suno-engineer, album-conceptualizer, lyric-reviewer, researchers-legal, researchers-veri'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '1. **Load override first** - Read config for overrides path, then check `{overrides}/lyric-writing-guide.md`' in text, "expected to find: " + '1. **Load override first** - Read config for overrides path, then check `{overrides}/lyric-writing-guide.md`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '3. Is syllable count roughly consistent across corresponding lines? (see tolerance in Line Length table)' in text, "expected to find: " + '3. Is syllable count roughly consistent across corresponding lines? (see tolerance in Line Length table)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '| Outro | 2–4 | Spoken word / ad-lib sections exempt from limit |' in text, "expected to find: " + '| Outro | 2–4 | Spoken word / ad-lib sections exempt from limit |'[:80]

