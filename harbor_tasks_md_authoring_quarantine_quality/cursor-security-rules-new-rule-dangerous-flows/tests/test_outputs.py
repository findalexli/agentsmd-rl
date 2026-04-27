"""Behavioral checks for cursor-security-rules-new-rule-dangerous-flows (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cursor-security-rules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('dangerous-flows.mdc')
    assert 'A **Dangerous Flow** occurs when user input—or data derived from it—is used in a way that introduces **vulnerabilities, undefined behavior, or unwanted system interactions**. This can range from comma' in text, "expected to find: " + 'A **Dangerous Flow** occurs when user input—or data derived from it—is used in a way that introduces **vulnerabilities, undefined behavior, or unwanted system interactions**. This can range from comma'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('dangerous-flows.mdc')
    assert 'Dangerous functions are operations that can cause unintended side effects, system compromise, or data exposure **when given untrusted input**. These functions are not always obviously labeled as "dang' in text, "expected to find: " + 'Dangerous functions are operations that can cause unintended side effects, system compromise, or data exposure **when given untrusted input**. These functions are not always obviously labeled as "dang'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('dangerous-flows.mdc')
    assert "Here's a detailed section you can add to your system prompt to help the AI **identify dangerous functions**, even when they're hidden behind abstraction or naming tricks:" in text, "expected to find: " + "Here's a detailed section you can add to your system prompt to help the AI **identify dangerous functions**, even when they're hidden behind abstraction or naming tricks:"[:80]

