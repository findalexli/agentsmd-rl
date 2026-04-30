"""Behavioral checks for airflow-agents-require-tracking-issue-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/airflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When a PR applies a **workaround, version cap, mitigation, or partial fix**' in text, "expected to find: " + 'When a PR applies a **workaround, version cap, mitigation, or partial fix**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'rather than solving the underlying problem (for example: upper-binding a' in text, "expected to find: " + 'rather than solving the underlying problem (for example: upper-binding a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'captured in a GitHub tracking issue **and** the tracking issue URL must' in text, "expected to find: " + 'captured in a GitHub tracking issue **and** the tracking issue URL must'[:80]

