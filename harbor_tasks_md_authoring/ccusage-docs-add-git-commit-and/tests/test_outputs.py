"""Behavioral checks for ccusage-docs-add-git-commit-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ccusage")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'PR titles should follow the same format as commit messages. When a PR contains multiple commits, the title should describe the main change:' in text, "expected to find: " + 'PR titles should follow the same format as commit messages. When a PR contains multiple commits, the title should describe the main change:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Follow the Conventional Commits specification with package/area prefixes:' in text, "expected to find: " + 'Follow the Conventional Commits specification with package/area prefixes:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `refactor:` - Code change that neither fixes a bug nor adds a feature' in text, "expected to find: " + '- `refactor:` - Code change that neither fixes a bug nor adds a feature'[:80]

