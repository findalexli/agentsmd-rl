"""Behavioral checks for dotnet-skills-fix-api-design-optional-params (markdown_authoring task).

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
    text = _read('skills/csharp-api-design/SKILL.md')
    assert 'public void Send(Message msg, Priority priority = Priority.Normal);  // Breaks binary compat!' in text, "expected to find: " + 'public void Send(Message msg, Priority priority = Priority.Normal);  // Breaks binary compat!'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-api-design/SKILL.md')
    assert 'public void Process(Order order, CancellationToken ct = default);  // Breaks binary compat!' in text, "expected to find: " + 'public void Process(Order order, CancellationToken ct = default);  // Breaks binary compat!'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-api-design/SKILL.md')
    assert "// Optional parameter defaults are baked into the CALLER's assembly at compile time." in text, "expected to find: " + "// Optional parameter defaults are baked into the CALLER's assembly at compile time."[:80]

