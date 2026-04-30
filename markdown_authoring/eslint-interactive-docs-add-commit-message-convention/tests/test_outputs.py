"""Behavioral checks for eslint-interactive-docs-add-commit-message-convention (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eslint-interactive")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)' in text, "expected to find: " + '- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `<type>` is one of: feat, fix, docs, refactor, test, chore, deps' in text, "expected to find: " + '- `<type>` is one of: feat, fix, docs, refactor, test, chore, deps'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Example: `feat: implement some feature`' in text, "expected to find: " + '- Example: `feat: implement some feature`'[:80]

