"""Behavioral checks for auto-claude-code-research-in-sleep-add-dseloop-skill-for-aut (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-claude-code-research-in-sleep")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dse-loop/SKILL.md')
    assert 'description: "Autonomous design space exploration loop for computer architecture and EDA. Runs a program, analyzes results, tunes parameters, and iterates until objective is met or timeout. Use when u' in text, "expected to find: " + 'description: "Autonomous design space exploration loop for computer architecture and EDA. Runs a program, analyzes results, tunes parameters, and iterates until objective is met or timeout. Use when u'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dse-loop/SKILL.md')
    assert "5. **Write a parameter extraction script** (`dse_results/parse_result.py` or similar) that takes a run's output and returns the objective metric as a number. Test it on a baseline run first." in text, "expected to find: " + "5. **Write a parameter extraction script** (`dse_results/parse_result.py` or similar) that takes a run's output and returns the objective metric as a number. Test it on a baseline run first."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dse-loop/SKILL.md')
    assert 'Autonomously explore a design space: run → analyze → pick next parameters → repeat, until the objective is met or timeout is reached. Designed for computer architecture and EDA problems.' in text, "expected to find: " + 'Autonomously explore a design space: run → analyze → pick next parameters → repeat, until the objective is met or timeout is reached. Designed for computer architecture and EDA problems.'[:80]

