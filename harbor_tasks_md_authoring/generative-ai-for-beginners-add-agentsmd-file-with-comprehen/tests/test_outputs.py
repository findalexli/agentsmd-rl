"""Behavioral checks for generative-ai-for-beginners-add-agentsmd-file-with-comprehen (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/generative-ai-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains a comprehensive 21-lesson curriculum teaching Generative AI fundamentals and application development. The course is designed for beginners and covers everything from basic con' in text, "expected to find: " + 'This repository contains a comprehensive 21-lesson curriculum teaching Generative AI fundamentals and application development. The course is designed for beginners and covers everything from basic con'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is an educational repository focused on tutorials and examples. There are no unit tests or integration tests to run. Validation is primarily:' in text, "expected to find: " + 'This is an educational repository focused on tutorials and examples. There are no unit tests or integration tests to run. Validation is primarily:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Python 3.9+ with libraries: `openai`, `python-dotenv`, `tiktoken`, `azure-ai-inference`, `pandas`, `numpy`, `matplotlib`' in text, "expected to find: " + '- Python 3.9+ with libraries: `openai`, `python-dotenv`, `tiktoken`, `azure-ai-inference`, `pandas`, `numpy`, `matplotlib`'[:80]

