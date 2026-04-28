"""Behavioral checks for nx.js-docs-add-stub-pattern-note (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nx.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`stub()` does NOT mean unimplemented.** Methods marked with `stub()` in TypeScript (from `./utils`) are placeholders for type generation only. At runtime, the C side overwrites them on the prototy' in text, "expected to find: " + '- **`stub()` does NOT mean unimplemented.** Methods marked with `stub()` in TypeScript (from `./utils`) are placeholders for type generation only. At runtime, the C side overwrites them on the prototy'[:80]

