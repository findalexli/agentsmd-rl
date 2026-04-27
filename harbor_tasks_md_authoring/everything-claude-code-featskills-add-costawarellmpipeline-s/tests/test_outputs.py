"""Behavioral checks for everything-claude-code-featskills-add-costawarellmpipeline-s (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cost-aware-llm-pipeline/SKILL.md')
    assert 'Patterns for controlling LLM API costs while maintaining quality. Combines model routing, budget tracking, retry logic, and prompt caching into a composable pipeline.' in text, "expected to find: " + 'Patterns for controlling LLM API costs while maintaining quality. Combines model routing, budget tracking, retry logic, and prompt caching into a composable pipeline.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cost-aware-llm-pipeline/SKILL.md')
    assert 'description: Cost optimization patterns for LLM API usage — model routing by task complexity, budget tracking, retry logic, and prompt caching.' in text, "expected to find: " + 'description: Cost optimization patterns for LLM API usage — model routing by task complexity, budget tracking, retry logic, and prompt caching.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cost-aware-llm-pipeline/SKILL.md')
    assert '- **Never retry on authentication or validation errors** — only transient failures (network, rate limit, server error)' in text, "expected to find: " + '- **Never retry on authentication or validation errors** — only transient failures (network, rate limit, server error)'[:80]

