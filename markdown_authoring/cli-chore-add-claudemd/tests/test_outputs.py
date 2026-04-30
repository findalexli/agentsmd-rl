"""Behavioral checks for cli-chore-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Format and Lint Fix**: Use `bun run format:fix && bun run lint:fix` to automatically fix formatting and linting issues' in text, "expected to find: " + '- **Format and Lint Fix**: Use `bun run format:fix && bun run lint:fix` to automatically fix formatting and linting issues'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '6. **Consistency**: Always refer to projects under <https://github.com/honojs> for implementation patterns and conventions' in text, "expected to find: " + '6. **Consistency**: Always refer to projects under <https://github.com/honojs> for implementation patterns and conventions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Testability**: Parts that can be benchmarked or tested independently become standalone modules' in text, "expected to find: " + '- **Testability**: Parts that can be benchmarked or tested independently become standalone modules'[:80]

