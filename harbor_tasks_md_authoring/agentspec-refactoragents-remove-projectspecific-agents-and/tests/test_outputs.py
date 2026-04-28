"""Behavioral checks for agentspec-refactoragents-remove-projectspecific-agents-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentspec")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-quality/dual-reviewer.md')
    assert '.claude/agents/code-quality/dual-reviewer.md' in text, "expected to find: " + '.claude/agents/code-quality/dual-reviewer.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/dev/dev-loop-executor.md')
    assert '.claude/agents/dev/dev-loop-executor.md' in text, "expected to find: " + '.claude/agents/dev/dev-loop-executor.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/dev/prompt-crafter.md')
    assert '.claude/agents/dev/prompt-crafter.md' in text, "expected to find: " + '.claude/agents/dev/prompt-crafter.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/developer/python-developer.md')
    assert '.claude/agents/developer/python-developer.md' in text, "expected to find: " + '.claude/agents/developer/python-developer.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/domain/dataops-builder.md')
    assert '.claude/agents/domain/dataops-builder.md' in text, "expected to find: " + '.claude/agents/domain/dataops-builder.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/domain/extraction-specialist.md')
    assert '.claude/agents/domain/extraction-specialist.md' in text, "expected to find: " + '.claude/agents/domain/extraction-specialist.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/domain/function-developer.md')
    assert '.claude/agents/domain/function-developer.md' in text, "expected to find: " + '.claude/agents/domain/function-developer.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/domain/infra-deployer.md')
    assert '.claude/agents/domain/infra-deployer.md' in text, "expected to find: " + '.claude/agents/domain/infra-deployer.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/domain/pipeline-architect.md')
    assert '.claude/agents/domain/pipeline-architect.md' in text, "expected to find: " + '.claude/agents/domain/pipeline-architect.md'[:80]

