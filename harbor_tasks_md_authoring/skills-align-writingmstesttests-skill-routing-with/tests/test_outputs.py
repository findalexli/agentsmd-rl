"""Behavioral checks for skills-align-writingmstesttests-skill-routing-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet-test/skills/writing-mstest-tests/SKILL.md')
    assert '- User needs to review or audit existing tests for anti-patterns or test quality (use `test-anti-patterns`)' in text, "expected to find: " + '- User needs to review or audit existing tests for anti-patterns or test quality (use `test-anti-patterns`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet-test/skills/writing-mstest-tests/SKILL.md')
    assert '| Existing test code | No | Current tests to improve or modernize |' in text, "expected to find: " + '| Existing test code | No | Current tests to improve or modernize |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet-test/skills/writing-mstest-tests/SKILL.md')
    assert '- User needs targeted help fixing or modernizing MSTest tests' in text, "expected to find: " + '- User needs targeted help fixing or modernizing MSTest tests'[:80]

