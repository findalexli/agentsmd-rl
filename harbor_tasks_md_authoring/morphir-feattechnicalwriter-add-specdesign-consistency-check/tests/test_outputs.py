"""Behavioral checks for morphir-feattechnicalwriter-add-specdesign-consistency-check (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/morphir")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technical-writer/SKILL.md')
    assert 'When specification documents (`docs/spec/`) need to match design documents (`docs/design/`), use the consistency checklist at [spec-design-consistency.md](references/spec-design-consistency.md).' in text, "expected to find: " + 'When specification documents (`docs/spec/`) need to match design documents (`docs/design/`), use the consistency checklist at [spec-design-consistency.md](references/spec-design-consistency.md).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technical-writer/SKILL.md')
    assert '- File name patterns are consistent (e.g., `.type.json`, `.value.json`, `module.json`)' in text, "expected to find: " + '- File name patterns are consistent (e.g., `.type.json`, `.value.json`, `module.json`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technical-writer/SKILL.md')
    assert '9. **Spec/Design Consistency** - Verify specification docs match design docs' in text, "expected to find: " + '9. **Spec/Design Consistency** - Verify specification docs match design docs'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technical-writer/references/spec-design-consistency.md')
    assert 'Package and module paths expand to fully split directories. Definition files (`.type.json`, `.value.json`) reside directly in the module directory—the suffixes distinguish types from values.' in text, "expected to find: " + 'Package and module paths expand to fully split directories. Definition files (`.type.json`, `.value.json`) reside directly in the module directory—the suffixes distinguish types from values.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technical-writer/references/spec-design-consistency.md')
    assert '- [ ] All spec types listed: `TypeAliasSpecification`, `OpaqueTypeSpecification`, `CustomTypeSpecification`, `DerivedTypeSpecification`' in text, "expected to find: " + '- [ ] All spec types listed: `TypeAliasSpecification`, `OpaqueTypeSpecification`, `CustomTypeSpecification`, `DerivedTypeSpecification`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technical-writer/references/spec-design-consistency.md')
    assert '| Path with FQName separators | `morphir/sdk:string` | `morphir/sdk` (path) or `morphir/sdk:string#string` (FQName) |' in text, "expected to find: " + '| Path with FQName separators | `morphir/sdk:string` | `morphir/sdk` (path) or `morphir/sdk:string#string` (FQName) |'[:80]

