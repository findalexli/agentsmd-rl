"""Behavioral checks for ouroboros-featrun-add-interactive-context-protection (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ouroboros")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert 'description: "Check once when each parallel level completes. Most context-efficient with meaningful updates."' in text, "expected to find: " + 'description: "Check once when each parallel level completes. Most context-efficient with meaningful updates."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert 'If this session is needed for follow-up (ooo evaluate, ooo evolve), shorter polling = more context consumed.' in text, "expected to find: " + 'If this session is needed for follow-up (ooo evaluate, ooo evolve), shorter polling = more context consumed.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert '5. **Ask user about polling strategy** using `AskUserQuestion` immediately after IDs are returned:' in text, "expected to find: " + '5. **Ask user about polling strategy** using `AskUserQuestion` immediately after IDs are returned:'[:80]

