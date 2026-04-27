"""Behavioral checks for modularity-unlock-modeldriven-question-discovery-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/modularity")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/high-level-design/SKILL.md')
    assert "Ask the user about each gap individually using `AskUserQuestion`. Skip what's clear from the requirements. Do not ask questions whose answers would not change your design — every question should resol" in text, "expected to find: " + "Ask the user about each gap individually using `AskUserQuestion`. Skip what's clear from the requirements. Do not ask questions whose answers would not change your design — every question should resol"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/high-level-design/SKILL.md')
    assert "2. **Discover what's missing for coupling-aware design.** Think about what you need to make good Balanced Coupling decisions — domain classification (determines volatility), organizational structure (" in text, "expected to find: " + "2. **Discover what's missing for coupling-aware design.** Think about what you need to make good Balanced Coupling decisions — domain classification (determines volatility), organizational structure ("[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/high-level-design/SKILL.md')
    assert '- Business areas where core vs supporting vs generic classification is ambiguous — propose your interpretation and ask the user to confirm or correct' in text, "expected to find: " + '- Business areas where core vs supporting vs generic classification is ambiguous — propose your interpretation and ask the user to confirm or correct'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/review/SKILL.md')
    assert '4. **Discover what you still need.** You know the Balanced Coupling model. You know you need volatility (from domain classification), distance (from organizational structure), and strength (from code)' in text, "expected to find: " + '4. **Discover what you still need.** You know the Balanced Coupling model. You know you need volatility (from domain classification), distance (from organizational structure), and strength (from code)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/review/SKILL.md')
    assert '1. Use `AskUserQuestion` to ask which parts of the codebase to analyze. Header: "Scope". Options: "Entire codebase — Analyze all components", "Specific directory — I\'ll tell you which path", "Specific' in text, "expected to find: " + '1. Use `AskUserQuestion` to ask which parts of the codebase to analyze. Header: "Scope". Options: "Entire codebase — Analyze all components", "Specific directory — I\'ll tell you which path", "Specific'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/review/SKILL.md')
    assert '2. **Read before asking.** Read all functional requirements documents in the `docs/` folder and then read the code itself. Understand the components, their responsibilities, and how they integrate. Us' in text, "expected to find: " + '2. **Read before asking.** Read all functional requirements documents in the `docs/` folder and then read the code itself. Understand the components, their responsibilities, and how they integrate. Us'[:80]

