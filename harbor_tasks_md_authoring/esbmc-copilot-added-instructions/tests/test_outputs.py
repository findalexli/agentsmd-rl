"""Behavioral checks for esbmc-copilot-added-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/esbmc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'ESBMC is a context-bounded model checker for embedded C/C++ software. Reviews should prioritize correctness, safety, and maintainability given the critical nature of formal verification tools.' in text, "expected to find: " + 'ESBMC is a context-bounded model checker for embedded C/C++ software. Reviews should prioritize correctness, safety, and maintainability given the critical nature of formal verification tools.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Memory safety**: Check for potential memory leaks, buffer overflows, use-after-free, and null pointer dereferences' in text, "expected to find: " + '- **Memory safety**: Check for potential memory leaks, buffer overflows, use-after-free, and null pointer dereferences'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Logic errors**: Verify algorithmic correctness, especially in SMT encoding and verification logic' in text, "expected to find: " + '- **Logic errors**: Verify algorithmic correctness, especially in SMT encoding and verification logic'[:80]

