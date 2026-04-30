"""Behavioral checks for sharezone-app-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sharezone-app")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Please refer to our [contribution guidelines](./CONTRIBUTING.md) for information on topics such as:' in text, "expected to find: " + 'Please refer to our [contribution guidelines](./CONTRIBUTING.md) for information on topics such as:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- How to add multi-language strings' in text, "expected to find: " + '- How to add multi-language strings'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- How to run the app' in text, "expected to find: " + '- How to run the app'[:80]

