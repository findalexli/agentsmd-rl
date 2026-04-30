"""Behavioral checks for juju-feat-initial-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/juju")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Business logic should be in the service layer, unless strictly required within a transaction, in which case it may' in text, "expected to find: " + '- Business logic should be in the service layer, unless strictly required within a transaction, in which case it may'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- State method arguments should be simple types (string, int, etc.) or types internal to the domain they reside in.' in text, "expected to find: " + '- State method arguments should be simple types (string, int, etc.) or types internal to the domain they reside in.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Juju is an orchestration engine for deploying, managing, scaling and integrating infrastructure and applications.' in text, "expected to find: " + 'Juju is an orchestration engine for deploying, managing, scaling and integrating infrastructure and applications.'[:80]

