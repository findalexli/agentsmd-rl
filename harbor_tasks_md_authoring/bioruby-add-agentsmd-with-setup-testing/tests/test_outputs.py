"""Behavioral checks for bioruby-add-agentsmd-with-setup-testing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bioruby")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- From the package root you can just call `bundle exec rake`. The commit should pass all tests before you merge.' in text, "expected to find: " + '- From the package root you can just call `bundle exec rake`. The commit should pass all tests before you merge.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- After updating .rb files, run `rubocop` to be sure RuboCop rules still pass.' in text, "expected to find: " + '- After updating .rb files, run `rubocop` to be sure RuboCop rules still pass.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Add or update tests for the code you change, even if nobody asked.' in text, "expected to find: " + '- Add or update tests for the code you change, even if nobody asked.'[:80]

