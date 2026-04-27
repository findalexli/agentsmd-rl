"""Behavioral checks for antigravity-awesome-skills-add-gdbcli-skill-gdb-debugging (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gdb-cli/SKILL.md')
    assert 'A GDB debugging skill designed for AI agents. Combines **source code analysis** with **runtime state inspection** using gdb-cli to provide intelligent debugging assistance for C/C++ programs.' in text, "expected to find: " + 'A GDB debugging skill designed for AI agents. Combines **source code analysis** with **runtime state inspection** using gdb-cli to provide intelligent debugging assistance for C/C++ programs.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gdb-cli/SKILL.md')
    assert 'description: "GDB debugging assistant for AI agents - analyze core dumps, debug live processes, investigate crashes and deadlocks with source code correlation"' in text, "expected to find: " + 'description: "GDB debugging assistant for AI agents - analyze core dumps, debug live processes, investigate crashes and deadlocks with source code correlation"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gdb-cli/SKILL.md')
    assert '**Output:** A session_id like `"session_id": "a1b2c3"`. Store this for subsequent commands.' in text, "expected to find: " + '**Output:** A session_id like `"session_id": "a1b2c3"`. Store this for subsequent commands.'[:80]

