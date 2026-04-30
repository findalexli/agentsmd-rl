"""Behavioral checks for agent-orchestrator-docs-add-copilot-instructions-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-orchestrator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Agent Orchestrator (AO) is a TypeScript monorepo that manages fleets of parallel AI coding agents. Each agent gets its own git worktree, branch, and PR. The system handles CI feedback routing, review ' in text, "expected to find: " + 'Agent Orchestrator (AO) is a TypeScript monorepo that manages fleets of parallel AI coding agents. Each agent gets its own git worktree, branch, and PR. The system handles CI feedback routing, review '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Architecture:** 8 plugin slots (Runtime, Agent, Workspace, Tracker, SCM, Notifier, Terminal, Lifecycle). All interfaces are defined in `packages/core/src/types.ts`. There is no database; the system ' in text, "expected to find: " + '**Architecture:** 8 plugin slots (Runtime, Agent, Workspace, Tracker, SCM, Notifier, Terminal, Lifecycle). All interfaces are defined in `packages/core/src/types.ts`. There is no database; the system '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '2. **Reference file paths and line numbers.** Name the specific function, class, or pattern the author should use instead. Do not give generic advice like "consider using a different approach."' in text, "expected to find: " + '2. **Reference file paths and line numbers.** Name the specific function, class, or pattern the author should use instead. Do not give generic advice like "consider using a different approach."'[:80]

