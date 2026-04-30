"""Behavioral checks for dotnet-skills-add-constraintenforcing-value-objects-beyond (markdown_authoring task).

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
    text = _read('skills/csharp-coding-standards/value-objects-and-patterns.md')
    assert "Value objects aren't just for identifiers. They're equally valuable for **enforcing domain constraints** on strings, numbers, and URIs — making illegal states unrepresentable at the type level." in text, "expected to find: " + "Value objects aren't just for identifiers. They're equally valuable for **enforcing domain constraints** on strings, numbers, and URIs — making illegal states unrepresentable at the type level."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-coding-standards/value-objects-and-patterns.md')
    assert "- APIs like Slack Block Kit silently reject relative URLs with cryptic errors. Transactional email links break if they're relative. `AbsoluteUrl` makes the compiler prevent this." in text, "expected to find: " + "- APIs like Slack Block Kit silently reject relative URLs with cryptic errors. Transactional email links break if they're relative. `AbsoluteUrl` makes the compiler prevent this."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-coding-standards/value-objects-and-patterns.md')
    assert '- Platform gotchas belong in the value object — e.g., Linux `Uri.TryCreate` treating `/path` as `file:///path` is handled once in `FromRelative`, not at every call site.' in text, "expected to find: " + '- Platform gotchas belong in the value object — e.g., Linux `Uri.TryCreate` treating `/path` as `file:///path` is handled once in `FromRelative`, not at every call site.'[:80]

