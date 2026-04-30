"""Behavioral checks for cc-wf-studio-chore-update-claudemd-guidelines-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cc-wf-studio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- The chat UI-based AI editing features (Refinement Chat Panel, AI Workflow Generation Dialog) are **no longer under active development**.' in text, "expected to find: " + '- The chat UI-based AI editing features (Refinement Chat Panel, AI Workflow Generation Dialog) are **no longer under active development**.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- The built-in MCP server (`cc-workflow-ai-editor` skill) is the primary interface for external AI agents to create and edit workflows.' in text, "expected to find: " + '- The built-in MCP server (`cc-workflow-ai-editor` skill) is the primary interface for external AI agents to create and edit workflows.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**When entering Plan Mode to design or plan implementation, always gather related knowledge from the github-knowledge MCP first.**' in text, "expected to find: " + '**When entering Plan Mode to design or plan implementation, always gather related knowledge from the github-knowledge MCP first.**'[:80]

