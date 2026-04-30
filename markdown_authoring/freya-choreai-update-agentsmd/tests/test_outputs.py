"""Behavioral checks for freya-choreai-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/freya")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When you are just starting to work on something you must not run any check or format command right away, leave that for the end and ask the developer for confirmation' in text, "expected to find: " + '- When you are just starting to work on something you must not run any check or format command right away, leave that for the end and ask the developer for confirmation'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Most hooks APIs like `use_state` return `Copy` values like `State`, when moving these around there is no need to `.clone()` them as they are `Copy` already.' in text, "expected to find: " + '- Most hooks APIs like `use_state` return `Copy` values like `State`, when moving these around there is no need to `.clone()` them as they are `Copy` already.'[:80]

