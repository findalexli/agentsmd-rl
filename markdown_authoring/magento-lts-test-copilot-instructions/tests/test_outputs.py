"""Behavioral checks for magento-lts-test-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/magento-lts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Ignore support for PHP versions below PHP 8.1 in new code.' in text, "expected to find: " + '- Ignore support for PHP versions below PHP 8.1 in new code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Use short array syntax `[]` for arrays in new code.' in text, "expected to find: " + '- Use short array syntax `[]` for arrays in new code.'[:80]

