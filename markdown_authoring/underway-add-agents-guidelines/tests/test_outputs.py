"""Behavioral checks for underway-add-agents-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/underway")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `RUSTDOCFLAGS="-D rustdoc::broken-intra-doc-links" cargo doc --all-features --no-deps`.' in text, "expected to find: " + '- `RUSTDOCFLAGS="-D rustdoc::broken-intra-doc-links" cargo doc --all-features --no-deps`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Commit messages are short, imperative, and lowercase (e.g., `clean up tests a bit`).' in text, "expected to find: " + '- Commit messages are short, imperative, and lowercase (e.g., `clean up tests a bit`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `cargo test --lib sanity_check_run_migrations -- --nocapture` (sqlx::test example).' in text, "expected to find: " + '- `cargo test --lib sanity_check_run_migrations -- --nocapture` (sqlx::test example).'[:80]

