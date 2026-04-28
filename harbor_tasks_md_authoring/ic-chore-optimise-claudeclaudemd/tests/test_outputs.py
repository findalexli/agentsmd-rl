"""Behavioral checks for ic-chore-optimise-claudeclaudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ic")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'After changing Rust code (`*.rs`) first format the code using:' in text, "expected to find: " + 'After changing Rust code (`*.rs`) first format the code using:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'cargo fmt -- <MODIFIED_RUST_FILES>' in text, "expected to find: " + 'cargo fmt -- <MODIFIED_RUST_FILES>'[:80]

