"""Behavioral checks for atopile-skills-update-atolanguage-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/atopile")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ato-language/EXTENSION.md')
    assert 'This release will contain deep core changes.' in text, "expected to find: " + 'This release will contain deep core changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ato-language/EXTENSION.md')
    assert '`zig build test`' in text, "expected to find: " + '`zig build test`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ato-language/SKILL.md')
    assert 'Every entity (a resistor, a power rail, an I2C bus, a voltage parameter) is a **node** in a typed graph. Nodes relate to each other through **edges**: composition (parent–child), connection (same-net)' in text, "expected to find: " + 'Every entity (a resistor, a power rail, an I2C bus, a voltage parameter) is a **node** in a typed graph. Nodes relate to each other through **edges**: composition (parent–child), connection (same-net)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ato-language/SKILL.md')
    assert '`has_part_removed`, `is_atomic_part`, `can_bridge`, `can_bridge_by_name`, `has_datasheet`, `has_designator_prefix`, `has_doc_string`, `has_net_name_affix`, `has_net_name_suggestion`, `has_package_requ' in text, "expected to find: " + '`has_part_removed`, `is_atomic_part`, `can_bridge`, `can_bridge_by_name`, `has_datasheet`, `has_designator_prefix`, `has_doc_string`, `has_net_name_affix`, `has_net_name_suggestion`, `has_package_requ'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ato-language/SKILL.md')
    assert 'ato is a **declarative, constraint-based DSL** for describing electronic circuits. There is no control flow, no mutation, and no execution order — you declare _what_ a circuit is, and the compiler + s' in text, "expected to find: " + 'ato is a **declarative, constraint-based DSL** for describing electronic circuits. There is no control flow, no mutation, and no execution order — you declare _what_ a circuit is, and the compiler + s'[:80]

