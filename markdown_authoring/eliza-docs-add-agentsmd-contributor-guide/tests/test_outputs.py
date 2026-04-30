"""Behavioral checks for eliza-docs-add-agentsmd-contributor-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eliza")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Formatting: Prettier (2 spaces, semicolons, single quotes, trailing comma es5, width 100). Run `bun run format` or `format:check`.' in text, "expected to find: " + '- Formatting: Prettier (2 spaces, semicolons, single quotes, trailing comma es5, width 100). Run `bun run format` or `format:check`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Conventional Commits: `feat:`, `fix:`, `chore:`, optional scope (e.g., `fix(server): ...`). Use `[skip ci]` for docs-only.' in text, "expected to find: " + '- Conventional Commits: `feat:`, `fix:`, `chore:`, optional scope (e.g., `fix(server): ...`). Use `[skip ci]` for docs-only.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PRs must include: clear description, linked issues, test plan, screenshots for UI changes, and pass build/lint/tests.' in text, "expected to find: " + '- PRs must include: clear description, linked issues, test plan, screenshots for UI changes, and pass build/lint/tests.'[:80]

