"""Behavioral checks for claude-ai-music-skills-feat-add-strict-homograph-handling (markdown_authoring task).

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
    assert '**Homograph handling — hard rule**: Suno CANNOT infer pronunciation from context. "Context is clear" is NEVER an acceptable resolution. When any homograph is found (live, read, lead, wound, close, bas' in text, "expected to find: " + '**Homograph handling — hard rule**: Suno CANNOT infer pronunciation from context. "Context is clear" is NEVER an acceptable resolution. When any homograph is found (live, read, lead, wound, close, bas'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **Fix** with phonetic spelling in Suno lyrics only (streaming lyrics keep standard spelling)' in text, "expected to find: " + '2. **Fix** with phonetic spelling in Suno lyrics only (streaming lyrics keep standard spelling)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **ASK** the user which pronunciation is intended — do NOT assume or guess' in text, "expected to find: " + '1. **ASK** the user which pronunciation is intended — do NOT assume or guess'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert 'Suno CANNOT infer pronunciation from context. **"Context is clear" is NEVER an acceptable resolution for a homograph.**' in text, "expected to find: " + 'Suno CANNOT infer pronunciation from context. **"Context is clear" is NEVER an acceptable resolution for a homograph.**'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '3. **Fix**: Replace with phonetic spelling in Suno lyric lines only (streaming lyrics keep standard spelling)' in text, "expected to find: " + '3. **Fix**: Replace with phonetic spelling in Suno lyric lines only (streaming lyrics keep standard spelling)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lyric-writer/SKILL.md')
    assert '- Only apply phonetic spelling to Suno lyrics — streaming/distributor lyrics use standard English' in text, "expected to find: " + '- Only apply phonetic spelling to Suno lyrics — streaming/distributor lyrics use standard English'[:80]

