"""Behavioral checks for dotnet-skills-add-ilspydecompile-skill-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ilspy-decompile/SKILL.md')
    assert 'description: Understand implementation details of .NET code by decompiling assemblies. Use when you want to see how a .NET API works internally, inspect NuGet package source, view framework implementa' in text, "expected to find: " + 'description: Understand implementation details of .NET code by decompiling assemblies. Use when you want to see how a .NET API works internally, inspect NuGet package source, view framework implementa'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ilspy-decompile/SKILL.md')
    assert 'Use this skill to understand how .NET code works internally by decompiling compiled assemblies.' in text, "expected to find: " + 'Use this skill to understand how .NET code works internally by decompiling compiled assemblies.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ilspy-decompile/SKILL.md')
    assert 'Both forms are shown below. Use the one that works in your environment.' in text, "expected to find: " + 'Both forms are shown below. Use the one that works in your environment.'[:80]

