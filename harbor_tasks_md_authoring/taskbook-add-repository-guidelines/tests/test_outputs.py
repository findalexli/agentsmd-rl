"""Behavioral checks for taskbook-add-repository-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/taskbook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `src/` contains all Rust source. Key files: `main.rs` (CLI entry), `commands.rs` (flag routing), `taskbook.rs` (core logic), `storage.rs` (JSON persistence), `render.rs` (terminal output), and `mode' in text, "expected to find: " + '- `src/` contains all Rust source. Key files: `main.rs` (CLI entry), `commands.rs` (flag routing), `taskbook.rs` (core logic), `storage.rs` (JSON persistence), `render.rs` (terminal output), and `mode'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Naming follows standard Rust conventions: `snake_case` for functions/vars, `PascalCase` for types, `SCREAMING_SNAKE_CASE` for constants.' in text, "expected to find: " + '- Naming follows standard Rust conventions: `snake_case` for functions/vars, `PascalCase` for types, `SCREAMING_SNAKE_CASE` for constants.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Commit messages are short, imperative, and sentence case (e.g., “Add release script”, “Bump taskbook-rs version to 0.1.1”).' in text, "expected to find: " + '- Commit messages are short, imperative, and sentence case (e.g., “Add release script”, “Bump taskbook-rs version to 0.1.1”).'[:80]

