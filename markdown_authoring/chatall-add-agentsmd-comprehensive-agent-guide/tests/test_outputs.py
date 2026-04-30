"""Behavioral checks for chatall-add-agentsmd-comprehensive-agent-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chatall")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use imperative, concise commit subjects similar to recent history (`Update dependencies`, `Remove deprecated Mixtral8x7b APIBot via Groq`), optionally with conventional prefixes (`fix:`) when approp' in text, "expected to find: " + '- Use imperative, concise commit subjects similar to recent history (`Update dependencies`, `Remove deprecated Mixtral8x7b APIBot via Groq`), optionally with conventional prefixes (`fix:`) when approp'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Prettier (`.prettierrc.js`) enforces semicolons, double quotes, two-space indentation, and 80-character line width; always format through Prettier rather than manual spacing.' in text, "expected to find: " + '- Prettier (`.prettierrc.js`) enforces semicolons, double quotes, two-space indentation, and 80-character line width; always format through Prettier rather than manual spacing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run the repo’s linting and formatting commands before committing; husky’s `pre-commit` hook (`.husky/pre-commit`) already invokes `npx lint-staged` on staged Vue/JS files.' in text, "expected to find: " + '- Run the repo’s linting and formatting commands before committing; husky’s `pre-commit` hook (`.husky/pre-commit`) already invokes `npx lint-staged` on staged Vue/JS files.'[:80]

