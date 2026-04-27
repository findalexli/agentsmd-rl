"""Behavioral checks for skills-mention-more-directives-in-the (markdown_authoring task).

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
    text = _read('plugins/dotnet/skills/csharp-scripts/SKILL.md')
    assert 'description: Run single-file C# programs as scripts (file-based apps) for quick experimentation, prototyping, and concept testing. Use when the user wants to write and execute a small C# program witho' in text, "expected to find: " + 'description: Run single-file C# programs as scripts (file-based apps) for quick experimentation, prototyping, and concept testing. Use when the user wants to write and execute a small C# program witho'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet/skills/csharp-scripts/SKILL.md')
    assert '| Directives placed after C# code | All `#:` directives must appear immediately after an optional shebang line (if present) and before any `using` directives or other C# statements |' in text, "expected to find: " + '| Directives placed after C# code | All `#:` directives must appear immediately after an optional shebang line (if present) and before any `using` directives or other C# statements |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/dotnet/skills/csharp-scripts/SKILL.md')
    assert 'Place directives at the top of the file (immediately after an optional shebang line), before any `using` directives or other C# code. All directives start with `#:`.' in text, "expected to find: " + 'Place directives at the top of the file (immediately after an optional shebang line), before any `using` directives or other C# code. All directives start with `#:`.'[:80]

