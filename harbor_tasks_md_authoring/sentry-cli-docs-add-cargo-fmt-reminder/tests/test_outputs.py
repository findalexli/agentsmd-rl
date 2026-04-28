"""Behavioral checks for sentry-cli-docs-add-cargo-fmt-reminder (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**ALWAYS** run `cargo fmt` before committing any Rust code changes to ensure consistent formatting across the codebase.' in text, "expected to find: " + '**ALWAYS** run `cargo fmt` before committing any Rust code changes to ensure consistent formatting across the codebase.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Code Formatting' in text, "expected to find: " + '# Code Formatting'[:80]

