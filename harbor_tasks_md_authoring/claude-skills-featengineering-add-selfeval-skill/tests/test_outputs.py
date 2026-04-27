"""Behavioral checks for claude-skills-featengineering-add-selfeval-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering/self-eval/SKILL.md')
    assert 'description: "Honestly evaluate AI work quality using a two-axis scoring system. Use after completing a task, code review, or work session to get an unbiased assessment. Detects score inflation, force' in text, "expected to find: " + 'description: "Honestly evaluate AI work quality using a two-axis scoring system. Use after completing a task, code review, or work session to get an unbiased assessment. Detects score inflation, force'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering/self-eval/SKILL.md')
    assert 'Self-eval is a Claude Code skill that produces honest, calibrated work evaluations. It replaces the default AI tendency to rate everything 4/5 with a structured two-axis scoring system, mandatory devi' in text, "expected to find: " + 'Self-eval is a Claude Code skill that produces honest, calibrated work evaluations. It replaces the default AI tendency to rate everything 4/5 with a structured two-axis scoring system, mandatory devi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('engineering/self-eval/SKILL.md')
    assert '- **High (3)** — Ambitious, unfamiliar, or high-stakes. Real risk of complete failure. Examples: building something from scratch in an unfamiliar domain, complex system redesign, performance-critical ' in text, "expected to find: " + '- **High (3)** — Ambitious, unfamiliar, or high-stakes. Real risk of complete failure. Examples: building something from scratch in an unfamiliar domain, complex system redesign, performance-critical '[:80]

