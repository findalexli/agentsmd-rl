"""Behavioral checks for hmcl-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hmcl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Any type, field, parameter, return value, local variable, or generic type argument that may be `null` must be explicitly annotated with `@Nullable`.' in text, "expected to find: " + '- Any type, field, parameter, return value, local variable, or generic type argument that may be `null` must be explicitly annotated with `@Nullable`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Immutable arrays and collections must be explicitly annotated with JetBrains Annotations `@Unmodifiable` or `@UnmodifiableView` as appropriate.' in text, "expected to find: " + '- Immutable arrays and collections must be explicitly annotated with JetBrains Annotations `@Unmodifiable` or `@UnmodifiableView` as appropriate.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Add concise implementation comments inside complex logic whenever they materially improve readability or explain non-obvious behavior.' in text, "expected to find: " + '- Add concise implementation comments inside complex logic whenever they materially improve readability or explain non-obvious behavior.'[:80]

