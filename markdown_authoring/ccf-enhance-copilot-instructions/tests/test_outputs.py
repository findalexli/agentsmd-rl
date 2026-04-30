"""Behavioral checks for ccf-enhance-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ccf")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **No secrets in code**: Avoid committing API keys, passwords, or other secrets. Some certificates and keys are included in the repository for testing purposes, but if adding more ensure these are fr' in text, "expected to find: " + '- **No secrets in code**: Avoid committing API keys, passwords, or other secrets. Some certificates and keys are included in the repository for testing purposes, but if adding more ensure these are fr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Take particular care with changes to the consensus and crypto code, as these are critical for security and correctness. Ensure you have a thorough understanding of the existing code and the implicat' in text, "expected to find: " + '- Take particular care with changes to the consensus and crypto code, as these are critical for security and correctness. Ensure you have a thorough understanding of the existing code and the implicat'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Pay attention to existing helpers and utilities in the test suite when writing new tests, and avoid duplicating code. If you find yourself copying and pasting code, consider refactoring it into a sh' in text, "expected to find: " + '- Pay attention to existing helpers and utilities in the test suite when writing new tests, and avoid duplicating code. If you find yourself copying and pasting code, consider refactoring it into a sh'[:80]

