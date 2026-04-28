"""Behavioral checks for ifc-lite-consolidate-agent-guidelines-into-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ifc-lite")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'See [AGENTS.md](./AGENTS.md) for the full agent guidelines used by all AI assistants in this project.' in text, "expected to find: " + 'See [AGENTS.md](./AGENTS.md) for the full agent guidelines used by all AI assistants in this project.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This project works with the IFC (Industry Foundation Classes) standard. **All user-facing APIs, scripting interfaces, and data exports MUST use correct IFC schema nomenclature.** Never invent simplifi' in text, "expected to find: " + 'This project works with the IFC (Industry Foundation Classes) standard. **All user-facing APIs, scripting interfaces, and data exports MUST use correct IFC schema nomenclature.** Never invent simplifi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Entity types from STEP files are UPPERCASE (`IFCWALLSTANDARDCASE`). Use `store.entities.getTypeName(id)` for properly-cased names (`IfcWallStandardCase`). The `normalizeTypeName` helper only handles' in text, "expected to find: " + '- Entity types from STEP files are UPPERCASE (`IFCWALLSTANDARDCASE`). Use `store.entities.getTypeName(id)` for properly-cased names (`IfcWallStandardCase`). The `normalizeTypeName` helper only handles'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Entity attributes (`Description`, `ObjectType`, `Tag`), properties, quantities, classifications, and materials are **not** stored during the initial fast parse. They are extracted lazily from the sour' in text, "expected to find: " + 'Entity attributes (`Description`, `ObjectType`, `Tag`), properties, quantities, classifications, and materials are **not** stored during the initial fast parse. They are extracted lazily from the sour'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See [AGENTS.md](./AGENTS.md) for the full agent guidelines used by all AI assistants in this project.' in text, "expected to find: " + 'See [AGENTS.md](./AGENTS.md) for the full agent guidelines used by all AI assistants in this project.'[:80]

