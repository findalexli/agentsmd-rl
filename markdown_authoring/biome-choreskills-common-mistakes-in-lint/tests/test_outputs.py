"""Behavioral checks for biome-choreskills-common-mistakes-in-lint (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/biome")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/biome-developer/SKILL.md')
    assert "- Calling `.to_string()` or `.to_string_trimmed()` (allocates a string) on a `SyntaxToken` or `SyntaxNode`. It's highly unlikely that you actually need to call these methods on a syntax node. As for s" in text, "expected to find: " + "- Calling `.to_string()` or `.to_string_trimmed()` (allocates a string) on a `SyntaxToken` or `SyntaxNode`. It's highly unlikely that you actually need to call these methods on a syntax node. As for s"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/biome-developer/SKILL.md')
    assert '- Calling `format!()` (allocates a string) when formatting strings in a `markup!` block. `markup!` supports interpolation, E.g. `markup! { "Hello, "{name}"!" }`.' in text, "expected to find: " + '- Calling `format!()` (allocates a string) when formatting strings in a `markup!` block. `markup!` supports interpolation, E.g. `markup! { "Hello, "{name}"!" }`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/biome-developer/SKILL.md')
    assert '## Common Mistakes to Avoid' in text, "expected to find: " + '## Common Mistakes to Avoid'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lint-rule-development/SKILL.md')
    assert '- Building strings or other data structures only used in the code action in `run()` instead of `action()`. `run()` should only decide whether to emit a diagnostic; `action()` should build the fix. Thi' in text, "expected to find: " + '- Building strings or other data structures only used in the code action in `run()` instead of `action()`. `run()` should only decide whether to emit a diagnostic; `action()` should build the fix. Thi'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lint-rule-development/SKILL.md')
    assert "- Placing `String` or `Box<str>` in a Rule's `State` type. It's a strong indicator that you are allocating a string unnecessarily. If the string comes from a CST token, this usually can be avoided by " in text, "expected to find: " + "- Placing `String` or `Box<str>` in a Rule's `State` type. It's a strong indicator that you are allocating a string unnecessarily. If the string comes from a CST token, this usually can be avoided by "[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lint-rule-development/SKILL.md')
    assert 'Generally, mistakes revolve around allocating unnecessary data during rule execution, which can lead to performance issues. Common examples include:' in text, "expected to find: " + 'Generally, mistakes revolve around allocating unnecessary data during rule execution, which can lead to performance issues. Common examples include:'[:80]

