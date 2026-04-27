"""Behavioral checks for everything-claude-code-feat-ai-regression-testing-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-regression-testing/SKILL.md')
    assert 'description: Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and patterns to catch AI blind spots wher' in text, "expected to find: " + 'description: Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and patterns to catch AI blind spots wher'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-regression-testing/SKILL.md')
    assert 'Testing patterns specifically designed for AI-assisted development, where the same model writes code and reviews it — creating systematic blind spots that only automated tests can catch.' in text, "expected to find: " + 'Testing patterns specifically designed for AI-assisted development, where the same model writes code and reviews it — creating systematic blind spots that only automated tests can catch.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-regression-testing/SKILL.md')
    assert 'When an AI writes code and then reviews its own work, it carries the same assumptions into both steps. This creates a predictable failure pattern:' in text, "expected to find: " + 'When an AI writes code and then reviews its own work, it carries the same assumptions into both steps. This creates a predictable failure pattern:'[:80]

