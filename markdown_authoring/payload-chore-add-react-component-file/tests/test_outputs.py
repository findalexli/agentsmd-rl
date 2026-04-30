"""Behavioral checks for payload-chore-add-react-component-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/payload")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **Don't:** Place multiple `ComponentName.tsx` files in a single folder with one shared `.scss` file" in text, "expected to find: " + "- **Don't:** Place multiple `ComponentName.tsx` files in a single folder with one shared `.scss` file"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Re-export from barrel files (`index.ts`) when grouping related components in a parent directory' in text, "expected to find: " + '- Re-export from barrel files (`index.ts`) when grouping related components in a parent directory'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Do:** Create a folder per component with `index.tsx` and `index.scss`' in text, "expected to find: " + '- **Do:** Create a folder per component with `index.tsx` and `index.scss`'[:80]

