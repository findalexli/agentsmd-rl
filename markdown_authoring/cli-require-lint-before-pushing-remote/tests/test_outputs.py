"""Behavioral checks for cli-require-lint-before-pushing-remote (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Before pushing commits or otherwise sending code changes to any remote, run `mise run lint` on the current tree and ensure it passes. If `mise run fmt` changed files, rerun `mise run lint` on the form' in text, "expected to find: " + 'Before pushing commits or otherwise sending code changes to any remote, run `mise run lint` on the current tree and ensure it passes. If `mise run fmt` changed files, rerun `mise run lint` on the form'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '### Before Any Push Or Remote Code Update (REQUIRED)' in text, "expected to find: " + '### Before Any Push Or Remote Code Update (REQUIRED)'[:80]

