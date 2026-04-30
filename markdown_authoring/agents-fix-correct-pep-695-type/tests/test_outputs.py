"""Behavioral checks for agents-fix-correct-pep-695-type (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/python-development/skills/python-type-safety/SKILL.md')
    assert '**Note:** The `type Alias = ...` statement syntax (PEP 695) was introduced in **Python 3.12**, not 3.10. For projects targeting earlier versions (including 3.10/3.11), use the `TypeAlias` annotation (' in text, "expected to find: " + '**Note:** The `type Alias = ...` statement syntax (PEP 695) was introduced in **Python 3.12**, not 3.10. For projects targeting earlier versions (including 3.10/3.11), use the `TypeAlias` annotation ('[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/python-development/skills/python-type-safety/SKILL.md')
    assert '# Python 3.10-3.11 style (needed for broader compatibility)' in text, "expected to find: " + '# Python 3.10-3.11 style (needed for broader compatibility)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/python-development/skills/python-type-safety/SKILL.md')
    assert '# Python 3.12+ type statement with generics (PEP 695)' in text, "expected to find: " + '# Python 3.12+ type statement with generics (PEP 695)'[:80]

