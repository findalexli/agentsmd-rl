"""Behavioral checks for vscode-hygiene-skill-updates (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/hygiene/SKILL.md')
    assert "description: Use when making code changes to ensure they pass VS Code's hygiene checks. Covers the pre-commit hook, unicode restrictions, string quoting rules, copyright headers, indentation, formatti" in text, "expected to find: " + "description: Use when making code changes to ensure they pass VS Code's hygiene checks. Covers the pre-commit hook, unicode restrictions, string quoting rules, copyright headers, indentation, formatti"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/hygiene/SKILL.md')
    assert '- **Unicode characters**: Non-ASCII characters (em-dashes, curly quotes, emoji, etc.) are rejected. Use ASCII equivalents in comments and code. Suppress with `// allow-any-unicode-next-line` or `// al' in text, "expected to find: " + '- **Unicode characters**: Non-ASCII characters (em-dashes, curly quotes, emoji, etc.) are rejected. Use ASCII equivalents in comments and code. Suppress with `// allow-any-unicode-next-line` or `// al'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/hygiene/SKILL.md')
    assert '- **Double-quoted strings**: Only use `"double quotes"` for externalized (localized) strings. Use `\'single quotes\'` everywhere else.' in text, "expected to find: " + '- **Double-quoted strings**: Only use `"double quotes"` for externalized (localized) strings. Use `\'single quotes\'` everywhere else.'[:80]

