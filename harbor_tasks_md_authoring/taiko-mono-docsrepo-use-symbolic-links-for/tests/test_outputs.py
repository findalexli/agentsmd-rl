"""Behavioral checks for taiko-mono-docsrepo-use-symbolic-links-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/taiko-mono")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'AGENTS.md' in text, "expected to find: " + 'AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert 'Agents.md' in text, "expected to find: " + 'Agents.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/protocol/AGENTS.md')
    assert 'packages/protocol/AGENTS.md' in text, "expected to find: " + 'packages/protocol/AGENTS.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/protocol/Agents.md')
    assert 'packages/protocol/Agents.md' in text, "expected to find: " + 'packages/protocol/Agents.md'[:80]

