"""Behavioral checks for agent-governance-toolkit-docs-add-spamscam-pr-filter (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-governance-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Marketing content disguised as a contribution (e.g., adding the contributor\'s company to COMMUNITY.md or README.md as a "Related Project" when there\'s no genuine technical integration)' in text, "expected to find: " + '- Marketing content disguised as a contribution (e.g., adding the contributor\'s company to COMMUNITY.md or README.md as a "Related Project" when there\'s no genuine technical integration)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Repetitive submissions from the same contributor after previous PR was closed for the same reason (e.g., kevinkaylie/AgentNexus pattern)' in text, "expected to find: " + '- Repetitive submissions from the same contributor after previous PR was closed for the same reason (e.g., kevinkaylie/AgentNexus pattern)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- From an account with <5 repos, <5 followers, created <3 months ago that submits promotional content to core docs' in text, "expected to find: " + '- From an account with <5 repos, <5 followers, created <3 months ago that submits promotional content to core docs'[:80]

