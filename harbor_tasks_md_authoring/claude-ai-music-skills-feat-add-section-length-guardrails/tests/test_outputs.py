"""Behavioral checks for claude-ai-music-skills-feat-add-section-length-guardrails (markdown_authoring task).

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
    assert '7. **Section length check**: Count lines per section, compare against genre limits in `/skills/lyric-writer/SKILL.md`. **Hard fail** — trim any section exceeding its genre max before presenting.' in text, "expected to find: " + '7. **Section length check**: Count lines per section, compare against genre limits in `/skills/lyric-writer/SKILL.md`. **Hard fail** — trim any section exceeding its genre max before presenting.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '8. **Pitfalls check**: Run through Lyric Pitfalls Checklist (see `/skills/lyric-writer/SKILL.md`)' in text, "expected to find: " + '8. **Pitfalls check**: Run through Lyric Pitfalls Checklist (see `/skills/lyric-writer/SKILL.md`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '7. **Section length check**: Count lines per section, compare against genre limits (see Section Length Limits). **Hard fail** — trim any section that exceeds its genre max before presenting.' in text, "expected to find: " + '7. **Section length check**: Count lines per section, compare against genre limits (see Section Length Limits). **Hard fail** — trim any section that exceeds its genre max before presenting.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '**Why this matters**: Suno rushes, compresses, or skips content when sections are too long. These are hard limits — trim before presenting.' in text, "expected to find: " + '**Why this matters**: Suno rushes, compresses, or skips content when sections are too long. These are hard limits — trim before presenting.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '4. **Any chorus over 6 lines**: Trim. A long chorus loses its punch and causes Suno to rush.' in text, "expected to find: " + '4. **Any chorus over 6 lines**: Trim. A long chorus loses its punch and causes Suno to rush.'[:80]

