"""Behavioral checks for optimism-airust-add-rust-code-reviewer (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/optimism")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/rust-code-reviewer.md')
    assert 'description: "IMPORTANT: For Rust projects, ALWAYS invoke this agent proactively after completing ANY implementation task. This is mandatory, not optional. Use this agent after writing new functions, ' in text, "expected to find: " + 'description: "IMPORTANT: For Rust projects, ALWAYS invoke this agent proactively after completing ANY implementation task. This is mandatory, not optional. Use this agent after writing new functions, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/rust-code-reviewer.md')
    assert "Run the project's `just` lint recipe (e.g. `mise exec -- just l`) at the START of every review (see Step 0) — never invoke `cargo clippy` directly, and always go through `mise` (either an active mise " in text, "expected to find: " + "Run the project's `just` lint recipe (e.g. `mise exec -- just l`) at the START of every review (see Step 0) — never invoke `cargo clippy` directly, and always go through `mise` (either an active mise "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/rust-code-reviewer.md')
    assert '- [ ] Did I scan for the project-specific patterns above (tuple pairs, string sentinels, runtime validation that belongs in a type, `type Err = String`, repeated closures, combined match arms with `ma' in text, "expected to find: " + '- [ ] Did I scan for the project-specific patterns above (tuple pairs, string sentinels, runtime validation that belongs in a type, `type Err = String`, repeated closures, combined match arms with `ma'[:80]

