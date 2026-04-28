"""Behavioral checks for sui-update-claudemd-linting-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Alternatively, run individual lints on specific crates (much faster than linting the whole repo):' in text, "expected to find: " + '# Alternatively, run individual lints on specific crates (much faster than linting the whole repo):'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`cargo xclippy` does not recognize the `-p` option - cd into the crate directory instead.' in text, "expected to find: " + '`cargo xclippy` does not recognize the `-p` option - cd into the crate directory instead.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# For crates in `external-crates/`: cd into the crate directory and run:' in text, "expected to find: " + '# For crates in `external-crates/`: cd into the crate directory and run:'[:80]

