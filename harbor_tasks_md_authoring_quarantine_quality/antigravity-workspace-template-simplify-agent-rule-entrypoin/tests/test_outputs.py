"""Behavioral checks for antigravity-workspace-template-simplify-agent-rule-entrypoin (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-workspace-template")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'There should be one-- and preferably only one --obvious way to do it.' in text, "expected to find: " + 'There should be one-- and preferably only one --obvious way to do it.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Although that way may not be obvious at first unless you're Dutch." in text, "expected to find: " + "Although that way may not be obvious at first unless you're Dutch."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If the implementation is easy to explain, it may be a good idea.' in text, "expected to find: " + 'If the implementation is easy to explain, it may be a good idea.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. Load project context from `CONTEXT.md`, `.antigravity/`, and `mission.md` only as needed.' in text, "expected to find: " + '3. Load project context from `CONTEXT.md`, `.antigravity/`, and `mission.md` only as needed.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. For spec or proposal work, follow `openspec/AGENTS.md`.' in text, "expected to find: " + '2. For spec or proposal work, follow `openspec/AGENTS.md`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Primary behavior rules live in `AGENTS.md`.' in text, "expected to find: " + 'Primary behavior rules live in `AGENTS.md`.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/src/ag_cli/templates/AGENTS.md')
    assert 'There should be one-- and preferably only one --obvious way to do it.' in text, "expected to find: " + 'There should be one-- and preferably only one --obvious way to do it.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/src/ag_cli/templates/AGENTS.md')
    assert "Although that way may not be obvious at first unless you're Dutch." in text, "expected to find: " + "Although that way may not be obvious at first unless you're Dutch."[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/src/ag_cli/templates/AGENTS.md')
    assert 'If the implementation is easy to explain, it may be a good idea.' in text, "expected to find: " + 'If the implementation is easy to explain, it may be a good idea.'[:80]

