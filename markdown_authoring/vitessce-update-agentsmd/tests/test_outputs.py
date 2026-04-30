"""Behavioral checks for vitessce-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitessce")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Test files are co-located with source, named `*.test.js`, `*.test.ts`, `*.test.jsx`, or `*.test.tsx` (use `.jsx`/`.tsx` for files containing JSX).' in text, "expected to find: " + '- Test files are co-located with source, named `*.test.js`, `*.test.ts`, `*.test.jsx`, or `*.test.tsx` (use `.jsx`/`.tsx` for files containing JSX).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Vitessce uses a **coordination model** for state management between components. Views communicate through a **coordination space**:' in text, "expected to find: " + 'Vitessce uses a **coordination model** for state management between components. Views communicate through a **coordination space**:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Dependency version consistency**: External dependencies via PNPM catalogs for version consistency' in text, "expected to find: " + '- **Dependency version consistency**: External dependencies via PNPM catalogs for version consistency'[:80]

