"""Behavioral checks for antigravity-awesome-skills-add-agentflow-skill-documentation (markdown_authoring task).

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
    text = _read('skills/agentflow/SKILL.md')
    assert 'AgentFlow turns your existing Kanban board into a fully autonomous AI development pipeline. Instead of building custom orchestration infrastructure, it treats your project management tool (Asana, GitH' in text, "expected to find: " + 'AgentFlow turns your existing Kanban board into a fully autonomous AI development pipeline. Instead of building custom orchestration infrastructure, it treats your project management tool (Asana, GitH'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentflow/SKILL.md')
    assert 'description: "Orchestrate autonomous AI development pipelines through your Kanban board (Asana, GitHub Projects, Linear). Manages multi-worker Claude Code dispatch, deterministic quality gates, advers' in text, "expected to find: " + 'description: "Orchestrate autonomous AI development pipelines through your Kanban board (Asana, GitHub Projects, Linear). Manages multi-worker Claude Code dispatch, deterministic quality gates, advers'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentflow/SKILL.md')
    assert 'Tasks flow through: Backlog, Research, Build, Review, Test, Integrate, Done. Each stage has specific gates. The Kanban board IS the orchestration layer — no separate database, no message queue, no cus' in text, "expected to find: " + 'Tasks flow through: Backlog, Research, Build, Review, Test, Integrate, Done. Each stage has specific gates. The Kanban board IS the orchestration layer — no separate database, no message queue, no cus'[:80]

