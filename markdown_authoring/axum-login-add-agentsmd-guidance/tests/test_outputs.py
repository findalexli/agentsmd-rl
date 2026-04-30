"""Behavioral checks for axum-login-add-agentsmd-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/axum-login")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Clippy is enforced: `cargo clippy --workspace --all-targets --all-features -- -D warnings`.' in text, "expected to find: " + '- Clippy is enforced: `cargo clippy --workspace --all-targets --all-features -- -D warnings`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Prefer the builder-based `require` API for new docs/examples; macros are legacy' in text, "expected to find: " + '- Prefer the builder-based `require` API for new docs/examples; macros are legacy'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Targeted runs are ok while iterating, but re-run full suite before shipping.' in text, "expected to find: " + '- Targeted runs are ok while iterating, but re-run full suite before shipping.'[:80]

