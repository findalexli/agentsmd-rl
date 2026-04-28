"""Behavioral checks for k6-rename-claudemd-to-agentsmd-symlink (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/k6")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'k6 is a modern load testing tool built in Go. It allows developers to write JavaScript test scripts to simulate user behavior and measure system performance. The tool features configurable load genera' in text, "expected to find: " + 'k6 is a modern load testing tool built in Go. It allows developers to write JavaScript test scripts to simulate user behavior and measure system performance. The tool features configurable load genera'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Key commands: `run`, `archive`, `cloud`, `inspect`, `new`, `pause`, `resume`, `scale`, `stats`, `status`, `version`' in text, "expected to find: " + '- Key commands: `run`, `archive`, `cloud`, `inspect`, `new`, `pause`, `resume`, `scale`, `stats`, `status`, `version`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Examples: `fix-http-timeout-handling`, `add-websocket-compression`, `improve-browser-element-selection`' in text, "expected to find: " + '- Examples: `fix-http-timeout-handling`, `add-websocket-compression`, `improve-browser-element-selection`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

