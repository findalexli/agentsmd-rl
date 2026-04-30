"""Behavioral checks for skills-improve-runtests-skill-description (markdown_authoring task).

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
    text = _read('plugins/dotnet-test/skills/run-tests/SKILL.md')
    assert 'detect the test platform (VSTest or Microsoft.Testing.Platform), identify the' in text, "expected to find: " + 'detect the test platform (VSTest or Microsoft.Testing.Platform), identify the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet-test/skills/run-tests/SKILL.md')
    assert 'test framework, apply test filters, or troubleshoot test execution failures.' in text, "expected to find: " + 'test framework, apply test filters, or troubleshoot test execution failures.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet-test/skills/run-tests/SKILL.md')
    assert 'Covers MSTest, xUnit, NUnit, and TUnit across both VSTest and MTP platforms.' in text, "expected to find: " + 'Covers MSTest, xUnit, NUnit, and TUnit across both VSTest and MTP platforms.'[:80]

