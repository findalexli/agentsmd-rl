"""Behavioral checks for dotnet-skills-add-formatmessage-method-with-skiplocalsinit (markdown_authoring task).

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
    assert 'var message = new string(buffer.Slice(0, written));' in text, "expected to find: " + 'var message = new string(buffer.Slice(0, written));'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert '// SkipLocalsInit with stackalloc and Span<T>' in text, "expected to find: " + '// SkipLocalsInit with stackalloc and Span<T>'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert 'Span<char> buffer = stackalloc char[256];' in text, "expected to find: " + 'Span<char> buffer = stackalloc char[256];'[:80]

