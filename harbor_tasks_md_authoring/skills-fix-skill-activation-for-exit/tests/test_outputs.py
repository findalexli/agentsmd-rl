"""Behavioral checks for skills-fix-skill-activation-for-exit (markdown_authoring task).

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
    text = _read('plugins/dotnet-test/skills/migrate-vstest-to-mtp/SKILL.md')
    assert 'EnableNUnitRunner, UseMicrosoftTestingPlatformRunner, dotnet test exit' in text, "expected to find: " + 'EnableNUnitRunner, UseMicrosoftTestingPlatformRunner, dotnet test exit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet-test/skills/migrate-vstest-to-mtp/SKILL.md')
    assert 'global.json configuration, CI/CD pipeline updates, and MTP extension' in text, "expected to find: " + 'global.json configuration, CI/CD pipeline updates, and MTP extension'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet-test/skills/migrate-vstest-to-mtp/SKILL.md')
    assert 'translation, xUnit.net v3 filter syntax, Directory.Build.props and' in text, "expected to find: " + 'translation, xUnit.net v3 filter syntax, Directory.Build.props and'[:80]

