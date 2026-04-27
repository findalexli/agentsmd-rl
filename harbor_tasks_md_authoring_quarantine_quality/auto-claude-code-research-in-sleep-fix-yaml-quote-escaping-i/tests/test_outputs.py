"""Behavioral checks for auto-claude-code-research-in-sleep-fix-yaml-quote-escaping-i (markdown_authoring task).

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
    text = _read('skills/skills-codex-claude-review/auto-paper-improvement-loop/SKILL.md')
    assert 'description: "Autonomously improve a generated paper via Claude review through claude-review MCP → implement fixes → recompile, for 2 rounds. Use when user says \\"改论文\\", \\"improve paper\\", \\"论文润色循环\\",' in text, "expected to find: " + 'description: "Autonomously improve a generated paper via Claude review through claude-review MCP → implement fixes → recompile, for 2 rounds. Use when user says \\"改论文\\", \\"improve paper\\", \\"论文润色循环\\",'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills-codex-claude-review/paper-figure/SKILL.md')
    assert 'description: "Generate publication-quality figures and tables from experiment results. Use when user says \\"画图\\", \\"作图\\", \\"generate figures\\", \\"paper figures\\", or needs plots for a paper."' in text, "expected to find: " + 'description: "Generate publication-quality figures and tables from experiment results. Use when user says \\"画图\\", \\"作图\\", \\"generate figures\\", \\"paper figures\\", or needs plots for a paper."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills-codex-claude-review/paper-plan/SKILL.md')
    assert 'description: "Generate a structured paper outline from review conclusions and experiment results. Use when user says \\"写大纲\\", \\"paper outline\\", \\"plan the paper\\", \\"论文规划\\", or wants to create a pape' in text, "expected to find: " + 'description: "Generate a structured paper outline from review conclusions and experiment results. Use when user says \\"写大纲\\", \\"paper outline\\", \\"plan the paper\\", \\"论文规划\\", or wants to create a pape'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skills-codex-claude-review/paper-write/SKILL.md')
    assert 'description: "Draft LaTeX paper section by section from an outline. Use when user says \\"写论文\\", \\"write paper\\", \\"draft LaTeX\\", \\"开始写\\", or wants to generate LaTeX content from a paper plan."' in text, "expected to find: " + 'description: "Draft LaTeX paper section by section from an outline. Use when user says \\"写论文\\", \\"write paper\\", \\"draft LaTeX\\", \\"开始写\\", or wants to generate LaTeX content from a paper plan."'[:80]

