"""Behavioral checks for swamp-docsskills-document-barespecifier-vs-scorer (markdown_authoring task).

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
    text = _read('.claude/skills/swamp-extension-publish/references/publishing.md')
    assert 'Other Deno-compatible imports (`npm:`, `jsr:`, `https://`) are inlined into the' in text, "expected to find: " + 'Other Deno-compatible imports (`npm:`, `jsr:`, `https://`) are inlined into the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-publish/references/publishing.md')
    assert 'cannot find the bare name and the command throws before factor scoring begins.' in text, "expected to find: " + 'cannot find the bare name and the command throws before factor scoring begins.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-publish/references/publishing.md')
    assert "The inline `npm:` form is the only form that resolves under both the bundler's" in text, "expected to find: " + "The inline `npm:` form is the only form that resolves under both the bundler's"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-quality/SKILL.md')
    assert '`swamp extension fmt` / `swamp extension push` reject the inline form as soon as' in text, "expected to find: " + '`swamp extension fmt` / `swamp extension push` reject the inline form as soon as'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-quality/SKILL.md')
    assert '- **`swamp extension quality` throws `Import "zod" not a dependency` instead of' in text, "expected to find: " + '- **`swamp extension quality` throws `Import "zod" not a dependency` instead of'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-quality/SKILL.md')
    assert 'suppress per-import with `// deno-lint-ignore no-import-prefix` above the zod' in text, "expected to find: " + 'suppress per-import with `// deno-lint-ignore no-import-prefix` above the zod'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-quality/references/templates.md')
    assert '`deno.json` and writes its own with no imports map, so a bare specifier cannot' in text, "expected to find: " + '`deno.json` and writes its own with no imports map, so a bare specifier cannot'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-quality/references/templates.md')
    assert "`swamp extension quality` run in a hermetic sandbox that strips the repo's" in text, "expected to find: " + "`swamp extension quality` run in a hermetic sandbox that strips the repo's"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/swamp-extension-quality/references/templates.md')
    assert 'resolve at score time even when an import map maps it at bundle time.' in text, "expected to find: " + 'resolve at score time even when an import map maps it at bundle time.'[:80]

