"""Behavioral checks for hive-docs-clarify-test-generation-responsibility (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hive")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive/SKILL.md')
    assert '2. **Generate tests** - The calling agent writes pytest files in `exports/agent_name/tests/` using hive-test guidelines and templates' in text, "expected to find: " + '2. **Generate tests** - The calling agent writes pytest files in `exports/agent_name/tests/` using hive-test guidelines and templates'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive/SKILL.md')
    assert 'Guides the creation and execution of a comprehensive test suite:' in text, "expected to find: " + 'Guides the creation and execution of a comprehensive test suite:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hive/SKILL.md')
    assert '### What This Phase Does' in text, "expected to find: " + '### What This Phase Does'[:80]

