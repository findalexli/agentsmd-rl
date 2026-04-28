"""Behavioral checks for claude-skills-docs-add-skillmd-update-requirement (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `SKILL.md` - User-facing documentation, version in frontmatter, installation instructions' in text, "expected to find: " + '- `SKILL.md` - User-facing documentation, version in frontmatter, installation instructions'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "**SKILL.md is the source of truth** - it's what users see and what triggers releases." in text, "expected to find: " + "**SKILL.md is the source of truth** - it's what users see and what triggers releases."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'grep -n "tree-sitter" skill-name/*.md skill-name/scripts/*.py' in text, "expected to find: " + 'grep -n "tree-sitter" skill-name/*.md skill-name/scripts/*.py'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('mapping-codebases/SKILL.md')
    assert '**Function Signatures**: Extracts parameter lists from Python and partial TypeScript, showing what functions expect without reading the source.' in text, "expected to find: " + '**Function Signatures**: Extracts parameter lists from Python and partial TypeScript, showing what functions expect without reading the source.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('mapping-codebases/SKILL.md')
    assert '**Symbol Hierarchy**: Shows classes with nested methods, not just flat lists. See the structure at a glance with kind markers (C/m/f).' in text, "expected to find: " + '**Symbol Hierarchy**: Shows classes with nested methods, not just flat lists. See the structure at a glance with kind markers (C/m/f).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('mapping-codebases/SKILL.md')
    assert '**Directory Statistics**: Each map header shows file and subdirectory counts, helping you quickly assess scope.' in text, "expected to find: " + '**Directory Statistics**: Each map header shows file and subdirectory counts, helping you quickly assess scope.'[:80]

