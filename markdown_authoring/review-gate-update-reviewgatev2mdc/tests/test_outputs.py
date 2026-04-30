"""Behavioral checks for review-gate-update-reviewgatev2mdc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/review-gate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('V2/ReviewGateV2.mdc')
    assert 'If I provide any response without calling review_gate_chat, treat it as an incomplete response that violates the protocol.' in text, "expected to find: " + 'If I provide any response without calling review_gate_chat, treat it as an incomplete response that violates the protocol.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('V2/ReviewGateV2.mdc')
    assert '- Handle any tool errors gracefully while maintaining the interactive review principle.' in text, "expected to find: " + '- Handle any tool errors gracefully while maintaining the interactive review principle.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('V2/ReviewGateV2.mdc')
    assert '## MANDATORY CHECKPOINT (Must be included in every response):' in text, "expected to find: " + '## MANDATORY CHECKPOINT (Must be included in every response):'[:80]

