"""Behavioral checks for autoresearchclaw-add-aevolve-agentic-evolution-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/autoresearchclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/a-evolve/SKILL.md')
    assert '"insight": "Synthetic benchmarks with <100 samples produce high-variance results. Always use ≥500 samples or report confidence intervals.",' in text, "expected to find: " + '"insight": "Synthetic benchmarks with <100 samples produce high-variance results. Always use ≥500 samples or report confidence intervals.",'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/a-evolve/SKILL.md')
    assert "Apply A-Evolve's agentic evolution methodology to improve AI agent performance" in text, "expected to find: " + "Apply A-Evolve's agentic evolution methodology to improve AI agent performance"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/a-evolve/SKILL.md')
    assert 'from errors", "what went wrong and how to fix it", or any mention of A-Evolve.' in text, "expected to find: " + 'from errors", "what went wrong and how to fix it", or any mention of A-Evolve.'[:80]

