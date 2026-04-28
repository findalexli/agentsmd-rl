"""Behavioral checks for olmo-core-updates-to-claudemd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/olmo-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Name individual test functions `test_*` and prefer `pytest.mark.parametrize` to cover multiple inputs or configurations without duplicating code.' in text, "expected to find: " + '- Name individual test functions `test_*` and prefer `pytest.mark.parametrize` to cover multiple inputs or configurations without duplicating code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- The syntax of the docstrings is a superset of reStructuredText with additional Sphinx-specific syntax for things like:' in text, "expected to find: " + '- The syntax of the docstrings is a superset of reStructuredText with additional Sphinx-specific syntax for things like:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Documenting parameters (`:param ...:`), return values (`:returns:`), or expected exceptions (`:raises ...:`).' in text, "expected to find: " + '- Documenting parameters (`:param ...:`), return values (`:returns:`), or expected exceptions (`:raises ...:`).'[:80]

