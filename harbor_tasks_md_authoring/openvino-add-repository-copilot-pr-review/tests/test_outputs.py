"""Behavioral checks for openvino-add-repository-copilot-pr-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openvino")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Flag debug/diagnostic print statements (`std::cout`, `std::cerr`, `printf`, `print()`, `LOG_DEBUG` used for temporary tracing) left in production or test code. This does not apply to PRs in Draft st' in text, "expected to find: " + '- Flag debug/diagnostic print statements (`std::cout`, `std::cerr`, `printf`, `print()`, `LOG_DEBUG` used for temporary tracing) left in production or test code. This does not apply to PRs in Draft st'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- For change-induced failures, provide actionable guidance on what in the diff likely caused it and how to fix it. Use the changed files and neighboring code context to build confidence in proposed so' in text, "expected to find: " + '- For change-induced failures, provide actionable guidance on what in the diff likely caused it and how to fix it. Use the changed files and neighboring code context to build confidence in proposed so'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'A revert PR restores a previously merged change. It is identified by the word "Revert" in the PR title or description, and typically references the original PR being reverted (e.g., `Reverts openvinot' in text, "expected to find: " + 'A revert PR restores a previously merged change. It is identified by the word "Revert" in the PR title or description, and typically references the original PR being reverted (e.g., `Reverts openvinot'[:80]

