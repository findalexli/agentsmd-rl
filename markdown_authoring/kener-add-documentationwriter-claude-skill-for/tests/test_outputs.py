"""Behavioral checks for kener-add-documentationwriter-claude-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kener")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/documentation-writer/SKILL.md')
    assert 'description: Specialized skill for creating and editing high-quality Kener documentation. MUST be used whenever creating or editing documentation files in the src/routes/(docs)/docs/content/ directory' in text, "expected to find: " + 'description: Specialized skill for creating and editing high-quality Kener documentation. MUST be used whenever creating or editing documentation files in the src/routes/(docs)/docs/content/ directory'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/documentation-writer/SKILL.md')
    assert 'This skill provides guidelines and best practices for creating high-quality, easy-to-follow documentation for Kener. Use this skill when creating new documentation or editing existing documentation fi' in text, "expected to find: " + 'This skill provides guidelines and best practices for creating high-quality, easy-to-follow documentation for Kener. Use this skill when creating new documentation or editing existing documentation fi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/documentation-writer/SKILL.md')
    assert 'Kener supports email notifications through SMTP or Resend. For detailed configuration instructions, see the [Email Setup](/docs/setup/email-setup) guide.' in text, "expected to find: " + 'Kener supports email notifications through SMTP or Resend. For detailed configuration instructions, see the [Email Setup](/docs/setup/email-setup) guide.'[:80]

