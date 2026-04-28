"""Behavioral checks for dotnet-skills-combine-stackalloc-with-pooling (markdown_authoring task).

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
    assert '// Hybrid buffer pattern for transient UTF-8 work. See caveats of SkipLocalsInit in the corresponding section.' in text, "expected to find: " + '// Hybrid buffer pattern for transient UTF-8 work. See caveats of SkipLocalsInit in the corresponding section.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert 'if (rented is not null) ArrayPool<byte>.Shared.Return(rented);' in text, "expected to find: " + 'if (rented is not null) ArrayPool<byte>.Shared.Return(rented);'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert 'ComputeHash(buf[..written], out var h1, out var h2);' in text, "expected to find: " + 'ComputeHash(buf[..written], out var h1, out var h2);'[:80]

