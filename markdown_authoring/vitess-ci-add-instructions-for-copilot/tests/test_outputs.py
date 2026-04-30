"""Behavioral checks for vitess-ci-add-instructions-for-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitess")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Do not flag issues that are caught by our automated CI/CD pipeline (linting, tests, type checks).' in text, "expected to find: " + 'Do not flag issues that are caught by our automated CI/CD pipeline (linting, tests, type checks).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Only leave a comment when you have HIGH CONFIDENCE (>80%) that a real problem exists.' in text, "expected to find: " + 'Only leave a comment when you have HIGH CONFIDENCE (>80%) that a real problem exists.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Do NOT comment on: style preferences, minor naming conventions, formatting, or' in text, "expected to find: " + 'Do NOT comment on: style preferences, minor naming conventions, formatting, or'[:80]

