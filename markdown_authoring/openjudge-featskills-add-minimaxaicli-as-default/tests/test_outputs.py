"""Behavioral checks for openjudge-featskills-add-minimaxaicli-as-default (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openjudge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mmx-cli/SKILL.md')
    assert 'narrated audio from text, compose music, or search the web through MiniMax AI services.' in text, "expected to find: " + 'narrated audio from text, compose music, or search the web through MiniMax AI services.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mmx-cli/SKILL.md')
    assert '| Voice name | No | For speech; run `mmx speech list-voices` to browse 300+ options |' in text, "expected to find: " + '| Voice name | No | For speech; run `mmx speech list-voices` to browse 300+ options |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mmx-cli/SKILL.md')
    assert 'music generation (music-2.6 with lyrics, cover, and instrumental), and web search.' in text, "expected to find: " + 'music generation (music-2.6 with lyrics, cover, and instrumental), and web search.'[:80]

