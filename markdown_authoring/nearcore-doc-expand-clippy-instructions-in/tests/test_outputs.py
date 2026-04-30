"""Behavioral checks for nearcore-doc-expand-clippy-instructions-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nearcore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run with `RUSTFLAGS="-D warnings"` env variable and `--all-features --all-targets` args.' in text, "expected to find: " + '- Run with `RUSTFLAGS="-D warnings"` env variable and `--all-features --all-targets` args.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'RUSTFLAGS="-D warnings" cargo clippy --all-features --all-targets' in text, "expected to find: " + 'RUSTFLAGS="-D warnings" cargo clippy --all-features --all-targets'[:80]

