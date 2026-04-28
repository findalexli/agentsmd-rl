"""Behavioral checks for samui-wallet-chore-add-opencode-generated-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/samui-wallet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Formatting**: Prettier (single quotes, 120 width, no semicolons, trailing commas)' in text, "expected to find: " + '- **Formatting**: Prettier (single quotes, 120 width, no semicolons, trailing commas)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Imports**: Type imports separate, alphabetical perfectionist sorting' in text, "expected to find: " + '- **Imports**: Type imports separate, alphabetical perfectionist sorting'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Linting**: ESLint with perfectionist (alphabetical imports/sorting)' in text, "expected to find: " + '- **Linting**: ESLint with perfectionist (alphabetical imports/sorting)'[:80]

