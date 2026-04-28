"""Behavioral checks for edgeai-for-beginners-add-agentsmd-file-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/edgeai-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'EdgeAI for Beginners is a comprehensive educational repository teaching Edge AI development with Small Language Models (SLMs). The course covers EdgeAI fundamentals, model deployment, optimization tec' in text, "expected to find: " + 'EdgeAI for Beginners is a comprehensive educational repository teaching Edge AI development with Small Language Models (SLMs). The course covers EdgeAI fundamentals, model deployment, optimization tec'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**This is an educational repository focused on teaching Edge AI development. The primary contribution pattern is improving educational content and adding/enhancing sample applications that demonstrate' in text, "expected to find: " + '**This is an educational repository focused on teaching Edge AI development. The primary contribution pattern is improving educational content and adding/enhancing sample applications that demonstrate'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Architecture:** Multi-module learning path with practical samples demonstrating edge AI deployment patterns' in text, "expected to find: " + '**Architecture:** Multi-module learning path with practical samples demonstrating edge AI deployment patterns'[:80]

