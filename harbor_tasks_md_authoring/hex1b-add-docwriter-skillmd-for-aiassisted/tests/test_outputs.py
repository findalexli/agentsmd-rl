"""Behavioral checks for hex1b-add-docwriter-skillmd-for-aiassisted (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hex1b")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/doc-writer/SKILL.md')
    assert 'Use `<example>` and `<code>` tags for key APIs within the Hex1b framework. Examples should be consise yet contain sufficient context to help developers understand how they are used. For examples that ' in text, "expected to find: " + 'Use `<example>` and `<code>` tags for key APIs within the Hex1b framework. Examples should be consise yet contain sufficient context to help developers understand how they are used. For examples that '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/doc-writer/SKILL.md')
    assert 'This skill provides guidelines for AI coding agents to help maintainers produce accurate and easy-to-maintain documentation for the Hex1b project. The repository contains two primary types of document' in text, "expected to find: " + 'This skill provides guidelines for AI coding agents to help maintainers produce accurate and easy-to-maintain documentation for the Hex1b project. The repository contains two primary types of document'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/doc-writer/SKILL.md')
    assert 'description: Guidelines for producing accurate and maintainable documentation for the Hex1b TUI library. Use when writing XML API documentation comments, creating end-user guides, or updating existing' in text, "expected to find: " + 'description: Guidelines for producing accurate and maintainable documentation for the Hex1b TUI library. Use when writing XML API documentation comments, creating end-user guides, or updating existing'[:80]

