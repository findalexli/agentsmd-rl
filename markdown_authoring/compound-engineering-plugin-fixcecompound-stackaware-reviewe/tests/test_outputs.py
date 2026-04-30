"""Behavioral checks for compound-engineering-plugin-fixcecompound-stackaware-reviewe (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert "- Any code-heavy issue → always run `compound-engineering:review:code-simplicity-reviewer`, and additionally run the kieran reviewer that matches the repo's primary stack:" in text, "expected to find: " + "- Any code-heavy issue → always run `compound-engineering:review:code-simplicity-reviewer`, and additionally run the kieran reviewer that matches the repo's primary stack:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert '- **compound-engineering:research:framework-docs-researcher**: Links to framework/library documentation references' in text, "expected to find: " + '- **compound-engineering:research:framework-docs-researcher**: Links to framework/library documentation references'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert '- **compound-engineering:review:kieran-typescript-reviewer**: Reviews code examples for TypeScript best practices' in text, "expected to find: " + '- **compound-engineering:review:kieran-typescript-reviewer**: Reviews code examples for TypeScript best practices'[:80]

