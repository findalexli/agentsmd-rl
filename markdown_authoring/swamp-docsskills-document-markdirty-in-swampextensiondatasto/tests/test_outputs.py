"""Behavioral checks for swamp-docsskills-document-markdirty-in-swampextensiondatasto (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swamp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-datastore/references/api.md')
    assert 'watermark to short-circuit zero-diff syncs (the recommended fast-path pattern —' in text, "expected to find: " + 'watermark to short-circuit zero-diff syncs (the recommended fast-path pattern —'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-datastore/references/api.md')
    assert 'Implementations that unconditionally walk the cache on every `pushChanged` have' in text, "expected to find: " + 'Implementations that unconditionally walk the cache on every `pushChanged` have'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-datastore/references/api.md')
    assert 'Signal that the local cache has uncommitted work. Swamp core calls this at the' in text, "expected to find: " + 'Signal that the local cache has uncommitted work. Swamp core calls this at the'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-datastore/references/examples.md')
    assert "// pushChanged walks the cache unconditionally, there's nothing" in text, "expected to find: " + "// pushChanged walks the cache unconditionally, there's nothing"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-datastore/references/examples.md')
    assert '// (fast-path pattern in design/datastores.md), flip it here.' in text, "expected to find: " + '// (fast-path pattern in design/datastores.md), flip it here.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-datastore/references/examples.md')
    assert '// Swamp core calls this before every cache write. If your' in text, "expected to find: " + '// Swamp core calls this before every cache write. If your'[:80]

