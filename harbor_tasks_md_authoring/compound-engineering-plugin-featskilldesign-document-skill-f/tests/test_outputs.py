"""Behavioral checks for compound-engineering-plugin-featskilldesign-document-skill-f (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **Note (March 2026):** This constraint reflects current Claude Code skill resolution behavior and known path-resolution bugs ([#11011](https://github.com/anthropics/claude-code/issues/11011), [#1774' in text, "expected to find: " + '> **Note (March 2026):** This constraint reflects current Claude Code skill resolution behavior and known path-resolution bugs ([#11011](https://github.com/anthropics/claude-code/issues/11011), [#1774'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This plugin is authored once and converted for multiple agent platforms (Claude Code, Codex, Gemini CLI, etc.). Do not use platform-specific environment variables or string substitutions (e.g., `${CLA' in text, "expected to find: " + 'This plugin is authored once and converted for multiple agent platforms (Claude Code, Codex, Gemini CLI, etc.). Do not use platform-specific environment variables or string substitutions (e.g., `${CLA'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Each skill directory is a self-contained unit. A SKILL.md file must only reference files within its own directory tree (e.g., `references/`, `assets/`, `scripts/`) using relative paths from the skill ' in text, "expected to find: " + 'Each skill directory is a self-contained unit. A SKILL.md file must only reference files within its own directory tree (e.g., `references/`, `assets/`, `scripts/`) using relative paths from the skill '[:80]

