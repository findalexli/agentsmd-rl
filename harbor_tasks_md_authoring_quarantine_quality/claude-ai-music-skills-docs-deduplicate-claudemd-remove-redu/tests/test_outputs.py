"""Behavioral checks for claude-ai-music-skills-docs-deduplicate-claudemd-remove-redu (markdown_authoring task).

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
    assert '1. **Load configuration** - Read `~/.bitwize-music/config.yaml` and resolve all path variables (see Path Resolution above). If config missing, tell user to run `/bitwize-music:configure` or copy `conf' in text, "expected to find: " + '1. **Load configuration** - Read `~/.bitwize-music/config.yaml` and resolve all path variables (see Path Resolution above). If config missing, tell user to run `/bitwize-music:configure` or copy `conf'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Pronunciation check**: Apply all rules from the Pronunciation section below (proper nouns, homographs, phonetic spelling, acronyms, tech terms, numbers, no invented contractions)' in text, "expected to find: " + '3. **Pronunciation check**: Apply all rules from the Pronunciation section below (proper nouns, homographs, phonetic spelling, acronyms, tech terms, numbers, no invented contractions)'[:80]

