"""Behavioral checks for awesome-cursorrules-refactor-python-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/python-cursorrules-prompt-file-best-practices/.cursorrules')
    assert '- When writing tests, ONLY use pytest or pytest plugins (not unittest). All tests should have typing annotations. Place all tests under ./tests. Create any necessary directories. If you create package' in text, "expected to find: " + '- When writing tests, ONLY use pytest or pytest plugins (not unittest). All tests should have typing annotations. Place all tests under ./tests. Create any necessary directories. If you create package'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/python-cursorrules-prompt-file-best-practices/.cursorrules')
    assert '- For any Python file, ALWAYS add typing annotations to each function or class. Include explicit return types (including None where appropriate). Add descriptive docstrings to all Python functions and' in text, "expected to find: " + '- For any Python file, ALWAYS add typing annotations to each function or class. Include explicit return types (including None where appropriate). Add descriptive docstrings to all Python functions and'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/python-cursorrules-prompt-file-best-practices/.cursorrules')
    assert '- You provide code snippets and explanations tailored to these principles, optimizing for clarity and AI-assisted development.' in text, "expected to find: " + '- You provide code snippets and explanations tailored to these principles, optimizing for clarity and AI-assisted development.'[:80]

