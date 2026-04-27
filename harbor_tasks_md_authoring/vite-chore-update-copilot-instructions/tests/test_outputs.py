"""Behavioral checks for vite-chore-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vite")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- If this adds a new config option, verify problem can't be solved with smarter defaults, existing options, or a plugin" in text, "expected to find: " + "- If this adds a new config option, verify problem can't be solved with smarter defaults, existing options, or a plugin"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- If this is a bug fix, explain what caused the bug - Link to relevant code if possible' in text, "expected to find: " + '- If this is a bug fix, explain what caused the bug - Link to relevant code if possible'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `packages/plugin-legacy`: The source code for the `@vitejs/plugin-legacy` plugin' in text, "expected to find: " + '- `packages/plugin-legacy`: The source code for the `@vitejs/plugin-legacy` plugin'[:80]

