"""Behavioral checks for taiga-ui-chore-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/taiga-ui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Never add comments that restate what the code already says. Comment only non-obvious intent, constraints, or gotchas.' in text, "expected to find: " + '- Never add comments that restate what the code already says. Comment only non-obvious intent, constraints, or gotchas.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Prefer Angular built-in control flow like `@if`, `@for`, and `@switch` in new templates; keep flow control shallow.' in text, "expected to find: " + '- Prefer Angular built-in control flow like `@if`, `@for`, and `@switch` in new templates; keep flow control shallow.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For bug fixes, add the smallest failing automated test first and make sure it fails before implementing the fix.' in text, "expected to find: " + '- For bug fixes, add the smallest failing automated test first and make sure it fails before implementing the fix.'[:80]

