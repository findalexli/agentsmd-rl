"""Behavioral checks for opencomputer-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opencomputer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When making changes, prefer the narrowest layer that can correctly own the work:' in text, "expected to find: " + 'When making changes, prefer the narrowest layer that can correctly own the work:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'deployment steps, and current rollout details should live in the real source of' in text, "expected to find: " + 'deployment steps, and current rollout details should live in the real source of'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If a change crosses one of these boundaries, treat it as a contract change, not' in text, "expected to find: " + 'If a change crosses one of these boundaries, treat it as a contract change, not'[:80]

