"""Behavioral checks for libretto-docs-add-claudemd-with-release (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libretto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Source skill files live in `packages/libretto/skills/` and are mirrored to `.agents/skills/` and `.claude/skills/`.' in text, "expected to find: " + 'Source skill files live in `packages/libretto/skills/` and are mirrored to `.agents/skills/` and `.claude/skills/`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '5. Syncs all mirrors (`pnpm sync:mirrors`) — READMEs, skill directories, `create-libretto` version' in text, "expected to find: " + '5. Syncs all mirrors (`pnpm sync:mirrors`) — READMEs, skill directories, `create-libretto` version'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Skill files and READMEs are mirrored across multiple locations. After any change to source files:' in text, "expected to find: " + 'Skill files and READMEs are mirrored across multiple locations. After any change to source files:'[:80]

