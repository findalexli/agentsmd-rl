"""Behavioral checks for claude-skills-add-muninn-boot-decision-traces (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Credentials auto-detect from environment or well-known paths (`/mnt/project/turso.env`, `/mnt/project/muninn.env`, `~/.muninn/.env`). If boot fails on missing credentials, note it and continue — not a' in text, "expected to find: " + 'Credentials auto-detect from environment or well-known paths (`/mnt/project/turso.env`, `/mnt/project/muninn.env`, `~/.muninn/.env`). If boot fails on missing credentials, note it and continue — not a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository is developed by two wings of the same raven. Claude Code implements; Claude.ai (Muninn) plans, tests, and operates the memory system. Both share a persistent memory store — boot it to ' in text, "expected to find: " + 'This repository is developed by two wings of the same raven. Claude Code implements; Claude.ai (Muninn) plans, tests, and operates the memory system. Both share a persistent memory store — boot it to '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- These utilities import from the `scripts` package (e.g., `from remembering.scripts import _exec, reprioritize`), with the skill directory on `sys.path`' in text, "expected to find: " + '- These utilities import from the `scripts` package (e.g., `from remembering.scripts import _exec, reprioritize`), with the skill directory on `sys.path`'[:80]

