"""Behavioral checks for davx5-ose-add-initial-agentsmd-for-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/davx5-ose")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use [Conventional Comments](https://conventionalcomments.org/) to label review feedback. Especially make a difference between more critical labels like `issue` or `todo` and less critical ones like `s' in text, "expected to find: " + 'Use [Conventional Comments](https://conventionalcomments.org/) to label review feedback. Especially make a difference between more critical labels like `issue` or `todo` and less critical ones like `s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Automated reviews shall assist in catching functional bugs, logic errors, and architectural concerns. They complement (not replace) human review by the core team.' in text, "expected to find: " + 'Automated reviews shall assist in catching functional bugs, logic errors, and architectural concerns. They complement (not replace) human review by the core team.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Functional bugs & logic errors** – incorrect behavior, missing edge cases, null/type safety issues' in text, "expected to find: " + '- **Functional bugs & logic errors** – incorrect behavior, missing edge cases, null/type safety issues'[:80]

