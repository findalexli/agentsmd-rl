"""Behavioral checks for antigravity-awesome-skills-feat-add-ideaos-for-5phase (markdown_authoring task).

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
    text = _read('skills/idea-os/SKILL.md')
    assert "idea-os is a 5-phase sequential pipeline where each phase's output feeds the next — research shapes the PRD, PRD shapes the plan, plan's kill criteria tie back to research insights. Unlike single-comm" in text, "expected to find: " + "idea-os is a 5-phase sequential pipeline where each phase's output feeds the next — research shapes the PRD, PRD shapes the plan, plan's kill criteria tie back to research insights. Unlike single-comm"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/idea-os/SKILL.md')
    assert 'idea-os classifies T2 · S1, writes 8 plain-language clarifying questions, runs research with sourced competitor pricing and community signal from ADHD subreddits, produces a PRD with ADHD-specific non' in text, "expected to find: " + 'idea-os classifies T2 · S1, writes 8 plain-language clarifying questions, runs research with sourced competitor pricing and community signal from ADHD subreddits, produces a PRD with ADHD-specific non'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/idea-os/SKILL.md')
    assert 'Write `plan.md` with: user journey (text + mermaid), platform recommendation tied to research findings, stack in conservative/modern/cutting-edge matrix, phased build (MVP → v1 → target) with kill cri' in text, "expected to find: " + 'Write `plan.md` with: user journey (text + mermaid), platform recommendation tied to research findings, stack in conservative/modern/cutting-edge matrix, phased build (MVP → v1 → target) with kill cri'[:80]

