"""Behavioral checks for github-misc-scripts-docs-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/github-misc-scripts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Include the header `-H "X-Github-Next-Global-ID: 1"` in GraphQL queries to retrieve the new global ID format - see the [GitHub migration guide for global node IDs](https://docs.github.com/en/graphql' in text, "expected to find: " + '- Include the header `-H "X-Github-Next-Global-ID: 1"` in GraphQL queries to retrieve the new global ID format - see the [GitHub migration guide for global node IDs](https://docs.github.com/en/graphql'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Complex scripts in the `./scripts` directory should have its own folder (so a `package.json` can be included for example)' in text, "expected to find: " + '- Complex scripts in the `./scripts` directory should have its own folder (so a `package.json` can be included for example)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- Append `!` to the type if it's a breaking change (e.g., `feat!: add additional required input parameters`)" in text, "expected to find: " + "- Append `!` to the type if it's a breaking change (e.g., `feat!: add additional required input parameters`)"[:80]

