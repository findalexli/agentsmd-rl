"""Behavioral checks for generative-ai-with-javascript-add-agentsmd-file-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/generative-ai-with-javascript")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository is a comprehensive learning course called "Generative AI for Beginners with JavaScript". It teaches developers how to integrate Generative AI into JavaScript applications through a tim' in text, "expected to find: " + 'This repository is a comprehensive learning course called "Generative AI for Beginners with JavaScript". It teaches developers how to integrate Generative AI into JavaScript applications through a tim'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains fictional AI-generated content. Historical characters generate responses via AI based on training data, not actual historical views. Content is for educational and entertainme' in text, "expected to find: " + 'This repository contains fictional AI-generated content. Historical characters generate responses via AI based on training data, not actual historical views. Content is for educational and entertainme'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is primarily an educational repository focused on tutorial content. There are no automated unit or integration tests for the code samples.' in text, "expected to find: " + 'This is primarily an educational repository focused on tutorial content. There are no automated unit or integration tests for the code samples.'[:80]

