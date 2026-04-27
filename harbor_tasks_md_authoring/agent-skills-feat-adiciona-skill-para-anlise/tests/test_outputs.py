"""Behavioral checks for agent-skills-feat-adiciona-skill-para-anlise (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/skills-catalog/skills/(architecture)/coupling-analysis/SKILL.md')
    assert 'description: Analyzes coupling in a codebase following the three-dimensional model from "Balancing Coupling in Software Design" (Vlad Khononov). Use when evaluating architectural quality, identifying ' in text, "expected to find: " + 'description: Analyzes coupling in a codebase following the three-dimensional model from "Balancing Coupling in Software Design" (Vlad Khononov). Use when evaluating architectural quality, identifying '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/skills-catalog/skills/(architecture)/coupling-analysis/SKILL.md')
    assert 'You are an expert software architect specializing in coupling analysis. You analyze codebases following the **three-dimensional model** from _Balancing Coupling in Software Design_ (Vlad Khononov):' in text, "expected to find: " + 'You are an expert software architect specializing in coupling analysis. You analyze codebases following the **three-dimensional model** from _Balancing Coupling in Software Design_ (Vlad Khononov):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/skills-catalog/skills/(architecture)/coupling-analysis/SKILL.md')
    assert "Upstream exposes its internal domain model as part of the public interface. Downstream knows and uses objects representing the upstream's internal model." in text, "expected to find: " + "Upstream exposes its internal domain model as part of the public interface. Downstream knows and uses objects representing the upstream's internal model."[:80]

