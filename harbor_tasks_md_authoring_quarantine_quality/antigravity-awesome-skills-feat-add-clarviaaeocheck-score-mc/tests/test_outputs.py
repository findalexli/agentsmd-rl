"""Behavioral checks for antigravity-awesome-skills-feat-add-clarviaaeocheck-score-mc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/clarvia-aeo-check/SKILL.md')
    assert 'Before adding any MCP server, API, or CLI tool to your agent workflow, use Clarvia to score its agent-readiness. Clarvia evaluates 15,400+ AI tools across four AEO dimensions: API accessibility, data ' in text, "expected to find: " + 'Before adding any MCP server, API, or CLI tool to your agent workflow, use Clarvia to score its agent-readiness. Clarvia evaluates 15,400+ AI tools across four AEO dimensions: API accessibility, data '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/clarvia-aeo-check/SKILL.md')
    assert 'description: "Score any MCP server, API, or CLI for agent-readiness using Clarvia AEO (Agent Experience Optimization). Search 15,400+ indexed tools before adding them to your workflow."' in text, "expected to find: " + 'description: "Score any MCP server, API, or CLI for agent-readiness using Clarvia AEO (Agent Experience Optimization). Search 15,400+ indexed tools before adding them to your workflow."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/clarvia-aeo-check/SKILL.md')
    assert '**Solution:** Use `get_score_breakdown` to see which dimensions are weak and decide if they matter for your use case' in text, "expected to find: " + '**Solution:** Use `get_score_breakdown` to see which dimensions are weak and decide if they matter for your use case'[:80]

