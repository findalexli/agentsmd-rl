"""Behavioral checks for formal-conjectures-feat-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/formal-conjectures")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Follow [Mathlib's naming conventions](https://leanprover-community.github.io/contribute/naming.html). Unlike Lean 3, Lean 4 uses a combination of `snake_case`, `lowerCamelCase`, and `UpperCamelCase`:" in text, "expected to find: " + "Follow [Mathlib's naming conventions](https://leanprover-community.github.io/contribute/naming.html). Unlike Lean 3, Lean 4 uses a combination of `snake_case`, `lowerCamelCase`, and `UpperCamelCase`:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. **UpperCamelCase in snake_case contexts**: When something named with `UpperCamelCase` is part of something named with `snake_case`, it is referenced in `lowerCamelCase`:' in text, "expected to find: " + '5. **UpperCamelCase in snake_case contexts**: When something named with `UpperCamelCase` is part of something named with `snake_case`, it is referenced in `lowerCamelCase`:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Note:** Providing a term inside `answer()` does NOT automatically mean the problem is mathematically solved - trivial or tautological answers don't count as solutions." in text, "expected to find: " + "**Note:** Providing a term inside `answer()` does NOT automatically mean the problem is mathematically solved - trivial or tautological answers don't count as solutions."[:80]

