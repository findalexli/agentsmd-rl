"""Behavioral checks for cultivation-world-simulator-docs-add-test-coverage-guideline (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cultivation-world-simulator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-validate/SKILL.md')
    assert 'For bug fixes, ensure the test would have **failed before the fix** and **passes after**.' in text, "expected to find: " + 'For bug fixes, ensure the test would have **failed before the fix** and **passes after**.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-validate/SKILL.md')
    assert '| New feature | Unit tests + integration test if affects multiple modules |' in text, "expected to find: " + '| New feature | Unit tests + integration test if affects multiple modules |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-validate/SKILL.md')
    assert '| Refactor | Existing tests should pass; add tests if behavior changes |' in text, "expected to find: " + '| Refactor | Existing tests should pass; add tests if behavior changes |'[:80]

