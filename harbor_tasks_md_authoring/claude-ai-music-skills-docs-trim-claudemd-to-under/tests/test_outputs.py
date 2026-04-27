"""Behavioral checks for claude-ai-music-skills-docs-trim-claudemd-to-under (markdown_authoring task).

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
    assert '| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error cost (6 skills) | lyric-writer, suno-engineer, album-conceptualizer, lyric-reviewer |' in text, "expected to find: " + '| **Opus 4.5** | `claude-opus-4-5-20251101` | Music-defining output, high error cost (6 skills) | lyric-writer, suno-engineer, album-conceptualizer, lyric-reviewer |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| **Ready to Generate** | All track lyrics written | Review statuses, verify Suno boxes filled, run `/bitwize-music:explicit-checker`, phonetic check |' in text, "expected to find: " + '| **Ready to Generate** | All track lyrics written | Review statuses, verify Suno boxes filled, run `/bitwize-music:explicit-checker`, phonetic check |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | Reasoning and coordination (21 skills) | researcher, pronunciation-specialist, explicit-checker |' in text, "expected to find: " + '| **Sonnet 4.5** | `claude-sonnet-4-5-20250929` | Reasoning and coordination (21 skills) | researcher, pronunciation-specialist, explicit-checker |'[:80]

