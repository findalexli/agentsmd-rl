"""Behavioral checks for claude-code-boilerplate-update-claudemd-workflow-and-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-boilerplate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**CRITICAL:** Steps 3-4 (TDD), Steps 7-9 (Impact Verification), and Steps 11-15 (Score ≥ 9.5) are NON-NEGOTIABLE.' in text, "expected to find: " + '**CRITICAL:** Steps 3-4 (TDD), Steps 7-9 (Impact Verification), and Steps 11-15 (Score ≥ 9.5) are NON-NEGOTIABLE.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- [15.4 Review Requirements (Score ≥ 9.5 to Merge)](#154-review-requirements-score-based-approval)' in text, "expected to find: " + '- [15.4 Review Requirements (Score ≥ 9.5 to Merge)](#154-review-requirements-score-based-approval)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| 11 | All Review Agents | **Team Review** - Each agent scores (1-10) + provides feedback |' in text, "expected to find: " + '| 11 | All Review Agents | **Team Review** - Each agent scores (1-10) + provides feedback |'[:80]

