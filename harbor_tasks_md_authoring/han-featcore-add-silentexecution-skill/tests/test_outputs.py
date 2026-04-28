"""Behavioral checks for han-featcore-add-silentexecution-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/han")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/silent-execution/SKILL.md')
    assert 'When executing a sequence of related tool calls (running tests, fixing lint, applying edits), batch operations and report results only when complete.' in text, "expected to find: " + 'When executing a sequence of related tool calls (running tests, fixing lint, applying edits), batch operations and report results only when complete.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/silent-execution/SKILL.md')
    assert '4. **Exception: interactive debugging** — when the user is watching you debug, narration helps them follow along' in text, "expected to find: " + '4. **Exception: interactive debugging** — when the user is watching you debug, narration helps them follow along'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/silent-execution/SKILL.md')
    assert "1. **Batch independent operations** — if operations don't depend on each other, run them all before commenting" in text, "expected to find: " + "1. **Batch independent operations** — if operations don't depend on each other, run them all before commenting"[:80]

