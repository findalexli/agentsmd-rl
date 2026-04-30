"""Behavioral checks for rhino-created-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rhino")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `rhino-tools`: Contains the shell, debugger, and the "Global" object, which many tests and other Rhino-based tools use' in text, "expected to find: " + '- `rhino-tools`: Contains the shell, debugger, and the "Global" object, which many tests and other Rhino-based tools use'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `tests`: The tests that depend on all of Rhino and also the external tests, including the Mozilla legacy test scripts' in text, "expected to find: " + '- `tests`: The tests that depend on all of Rhino and also the external tests, including the Mozilla legacy test scripts'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [Parser](rhino/src/main/java/org/mozilla/javascript/Parser.java) is the parser, which produces an AST modeled by the' in text, "expected to find: " + '- [Parser](rhino/src/main/java/org/mozilla/javascript/Parser.java) is the parser, which produces an AST modeled by the'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

