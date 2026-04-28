"""Behavioral checks for markdowndb-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/markdowndb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'MarkdownDB is a JavaScript library that parses markdown files and stores them in a queryable database (SQLite or JSON). It extracts structured data from markdown content including frontmatter, tags, l' in text, "expected to find: " + 'MarkdownDB is a JavaScript library that parses markdown files and stores them in a queryable database (SQLite or JSON). It extracts structured data from markdown content including frontmatter, tags, l'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '2. **File Extensions**: Always include `.js` extension in imports (TypeScript will resolve to `.ts`)' in text, "expected to find: " + '2. **File Extensions**: Always include `.js` extension in imports (TypeScript will resolve to `.ts`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '// Jest globals (describe, test, expect, beforeAll, etc.) are injected automatically' in text, "expected to find: " + '// Jest globals (describe, test, expect, beforeAll, etc.) are injected automatically'[:80]

