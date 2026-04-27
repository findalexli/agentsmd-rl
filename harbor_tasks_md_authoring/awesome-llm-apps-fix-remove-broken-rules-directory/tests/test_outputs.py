"""Behavioral checks for awesome-llm-apps-fix-remove-broken-rules-directory (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-llm-apps")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('awesome_agent_skills/python-expert/AGENTS.md')
    assert 'awesome_agent_skills/python-expert/AGENTS.md' in text, "expected to find: " + 'awesome_agent_skills/python-expert/AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('awesome_agent_skills/python-expert/SKILL.md')
    assert 'Detailed rules with examples are documented in [AGENTS.md](AGENTS.md), organized by category and priority.' in text, "expected to find: " + 'Detailed rules with examples are documented in [AGENTS.md](AGENTS.md), organized by category and priority.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('awesome_agent_skills/python-expert/SKILL.md')
    assert '- [Avoid Mutable Default Arguments](AGENTS.md#avoid-mutable-default-arguments)' in text, "expected to find: " + '- [Avoid Mutable Default Arguments](AGENTS.md#avoid-mutable-default-arguments)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('awesome_agent_skills/python-expert/SKILL.md')
    assert '2. **Follow priority order**: Correctness → Type Safety → Performance → Style' in text, "expected to find: " + '2. **Follow priority order**: Correctness → Type Safety → Performance → Style'[:80]

