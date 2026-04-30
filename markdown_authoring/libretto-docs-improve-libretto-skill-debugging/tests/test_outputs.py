"""Behavioral checks for libretto-docs-improve-libretto-skill-debugging (markdown_authoring task).

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
    text = _read('.agents/skills/libretto/SKILL.md')
    assert '- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.' in text, "expected to find: " + '- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert '- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.' in text, "expected to find: " + '- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert '- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.' in text, "expected to find: " + '- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/libretto/SKILL.md')
    assert '- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.' in text, "expected to find: " + '- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/libretto/SKILL.md')
    assert '- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.' in text, "expected to find: " + '- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/libretto/SKILL.md')
    assert '- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.' in text, "expected to find: " + '- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/libretto/SKILL.md')
    assert '- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.' in text, "expected to find: " + '- Available globals: `page`, `context`, `browser`, `state`, `networkLog(opts?)`, `actionLog(opts?)`, `fetch`, `Buffer`.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/libretto/SKILL.md')
    assert '- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.' in text, "expected to find: " + '- Workflows pause by calling `await pause("session-name")` in the workflow file. Import `pause` from `"libretto"`.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/libretto/SKILL.md')
    assert '- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.' in text, "expected to find: " + '- By default in headed mode, a ghost cursor and element highlights are shown. Use `--no-visualize` to disable.'[:80]

