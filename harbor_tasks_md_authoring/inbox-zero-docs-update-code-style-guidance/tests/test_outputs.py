"""Behavioral checks for inbox-zero-docs-update-code-style-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/inbox-zero")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do not duplicate substantial logic or correctness-sensitive rules. If copied code must stay in sync to avoid bugs, extract or centralize it early.' in text, "expected to find: " + '- Do not duplicate substantial logic or correctness-sensitive rules. If copied code must stay in sync to avoid bugs, extract or centralize it early.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Extract helpers when they make surrounding code clearer, name a meaningful domain concept, or keep shared behavior consistent across flows.' in text, "expected to find: " + '- Extract helpers when they make surrounding code clearer, name a meaningful domain concept, or keep shared behavior consistent across flows.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Avoid premature abstraction. Small duplicated expressions are usually fine; extracting them often adds indirection without meaning.' in text, "expected to find: " + '- Avoid premature abstraction. Small duplicated expressions are usually fine; extracting them often adds indirection without meaning.'[:80]

