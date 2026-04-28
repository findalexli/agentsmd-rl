"""Behavioral checks for libxmtp-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libxmtp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For changes in the `bindings_node` crate, run the `./dev/lint` script, but also run `yarn` and `yarn format:check` in the `bindings_node` folder.' in text, "expected to find: " + 'For changes in the `bindings_node` crate, run the `./dev/lint` script, but also run `yarn` and `yarn format:check` in the `bindings_node` folder.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When making code changes in Rust, always ensure that the code is linted and formatted by running the `./dev/lint` script.' in text, "expected to find: " + 'When making code changes in Rust, always ensure that the code is linted and formatted by running the `./dev/lint` script.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Uses Diesel ORM with SQLite backend. Migrations are in `xmtp_db/migrations/`.' in text, "expected to find: " + 'Uses Diesel ORM with SQLite backend. Migrations are in `xmtp_db/migrations/`.'[:80]

