"""Behavioral checks for claude-code-toolkit-fix-add-missing-agents-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/do/references/routing-tables.md')
    assert '| **test-driven-development** | User wants RED-GREEN-REFACTOR cycle with strict phase gates: write failing test first, make it pass with minimal code, then refactor. Common phrasings: "TDD", "test fir' in text, "expected to find: " + '| **test-driven-development** | User wants RED-GREEN-REFACTOR cycle with strict phase gates: write failing test first, make it pass with minimal code, then refactor. Common phrasings: "TDD", "test fir'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/do/references/routing-tables.md')
    assert '| **research-subagent-executor** | Subagent that executes delegated research tasks using OODA-loop investigation, intelligence gathering, and source evaluation. Dispatched by research-coordinator-engi' in text, "expected to find: " + '| **research-subagent-executor** | Subagent that executes delegated research tasks using OODA-loop investigation, intelligence gathering, and source evaluation. Dispatched by research-coordinator-engi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/do/references/routing-tables.md')
    assert '| **systematic-code-review** | User wants a structured 4-phase code review: UNDERSTAND changes, VERIFY claims against actual behavior, ASSESS security/performance/architecture risks, DOCUMENT findings' in text, "expected to find: " + '| **systematic-code-review** | User wants a structured 4-phase code review: UNDERSTAND changes, VERIFY claims against actual behavior, ASSESS security/performance/architecture risks, DOCUMENT findings'[:80]

