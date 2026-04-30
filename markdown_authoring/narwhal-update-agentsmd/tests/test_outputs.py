"""Behavioral checks for narwhal-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/narwhal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Whenever you modify, create, or delete Rust (`.rs`) files, you MUST follow this exact validation loop before considering your task complete and returning control to the user:' in text, "expected to find: " + 'Whenever you modify, create, or delete Rust (`.rs`) files, you MUST follow this exact validation loop before considering your task complete and returning control to the user:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **Lint:** Run `cargo clippy --workspace --all-targets -- -D warnings` (or use `-p <package>` if scoped to a specific crate) to check for idiomatic code and errors.' in text, "expected to find: " + '2. **Lint:** Run `cargo clippy --workspace --all-targets -- -D warnings` (or use `-p <package>` if scoped to a specific crate) to check for idiomatic code and errors.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. **Completion:** Do not report that you are finished until `cargo fmt` has been run and `cargo clippy` returns a clean, zero-exit-code run with no warnings.' in text, "expected to find: " + '4. **Completion:** Do not report that you are finished until `cargo fmt` has been run and `cargo clippy` returns a clean, zero-exit-code run with no warnings.'[:80]

