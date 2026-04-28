"""Behavioral checks for kilo-docs-add-worktree-instruction-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kilo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- You may be running in a git worktree. All changes must be made in your current working directory — never modify files in the main repo checkout.' in text, "expected to find: " + '- You may be running in a git worktree. All changes must be made in your current working directory — never modify files in the main repo checkout.'[:80]

