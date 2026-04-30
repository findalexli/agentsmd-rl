"""Behavioral checks for dotnet-skills-add-documentation-context-for-skiplocalsinit (markdown_authoring task).

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
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert '// See: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/attributes/general#skiplocalsinit-attribute' in text, "expected to find: " + '// See: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/attributes/general#skiplocalsinit-attribute'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert '// By default, .NET zero-initializes all locals (.locals init flag). This can have' in text, "expected to find: " + '// By default, .NET zero-initializes all locals (.locals init flag). This can have'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert '// SkipLocalsInit with stackalloc - skips zero-initialization for performance' in text, "expected to find: " + '// SkipLocalsInit with stackalloc - skips zero-initialization for performance'[:80]

