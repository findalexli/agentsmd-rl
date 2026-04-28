"""Behavioral checks for iii-chorefeatcursor-rules-revise-ui-steps (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/iii")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/ui-steps.mdc')
    assert 'Based on analysis of actual implementations across all examples, there are **exactly three** valid patterns for UI steps in Motia.' in text, "expected to find: " + 'Based on analysis of actual implementations across all examples, there are **exactly three** valid patterns for UI steps in Motia.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/ui-steps.mdc')
    assert 'description: RULES for UI Steps in Motia - Three distinct patterns based on actual codebase implementations' in text, "expected to find: " + 'description: RULES for UI Steps in Motia - Three distinct patterns based on actual codebase implementations'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/snap/src/cursor-rules/dot-files/.cursor/rules/ui-steps.mdc')
    assert 'Use this for custom visual representations of existing workflow steps that have their own business logic.' in text, "expected to find: " + 'Use this for custom visual representations of existing workflow steps that have their own business logic.'[:80]

