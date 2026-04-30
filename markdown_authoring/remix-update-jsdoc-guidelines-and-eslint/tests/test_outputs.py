"""Behavioral checks for remix-update-jsdoc-guidelines-and-eslint (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/remix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/write-api-docs/SKILL.md')
    assert '- Include an `@example` code block when it helps to show a use-case or pattern. Skip `@example` for simple getters, trivial constructors, or APIs whose usage is self-evident.' in text, "expected to find: " + '- Include an `@example` code block when it helps to show a use-case or pattern. Skip `@example` for simple getters, trivial constructors, or APIs whose usage is self-evident.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/write-api-docs/SKILL.md')
    assert "- Use `{@link API}` to link to related Remix APIs when it adds value. Don't link every related API — use discretion to avoid noise." in text, "expected to find: " + "- Use `{@link API}` to link to related Remix APIs when it adds value. Don't link every related API — use discretion to avoid noise."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/write-api-docs/SKILL.md')
    assert '- Specify `@param` default values in parenthesis at the end of the comment, do not use `@default` tags' in text, "expected to find: " + '- Specify `@param` default values in parenthesis at the end of the comment, do not use `@default` tags'[:80]

