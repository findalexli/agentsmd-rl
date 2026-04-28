"""Behavioral checks for claude-command-suite-fix-add-missing-frontmatter-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-command-suite")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/TASK-STATUS-PROTOCOL.md')
    assert 'You are a task status protocol manager responsible for defining and enforcing consistent task lifecycle management. Your role is to ensure proper task status transitions and maintain clear task state ' in text, "expected to find: " + 'You are a task status protocol manager responsible for defining and enforcing consistent task lifecycle management. Your role is to ensure proper task status transitions and maintain clear task state '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/TASK-STATUS-PROTOCOL.md')
    assert 'description: Defines and manages task status transitions, ensuring consistent task lifecycle management across projects.' in text, "expected to find: " + 'description: Defines and manages task status transitions, ensuring consistent task lifecycle management across projects.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/TASK-STATUS-PROTOCOL.md')
    assert '- **`review`**: Implementation complete, under review' in text, "expected to find: " + '- **`review`**: Implementation complete, under review'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/dependency-analyzer.md')
    assert 'You are a dependency analyzer specializing in managing project dependencies, identifying conflicts, and ensuring optimal dependency health. Your role is to analyze, audit, and optimize dependencies ac' in text, "expected to find: " + 'You are a dependency analyzer specializing in managing project dependencies, identifying conflicts, and ensuring optimal dependency health. Your role is to analyze, audit, and optimize dependencies ac'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/dependency-analyzer.md')
    assert 'description: Analyzes project dependencies, identifies conflicts, and manages dependency updates for optimal project health.' in text, "expected to find: " + 'description: Analyzes project dependencies, identifies conflicts, and manages dependency updates for optimal project health.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/dependency-analyzer.md')
    assert '- **Medium Risk**: Outdated major versions, deprecated packages' in text, "expected to find: " + '- **Medium Risk**: Outdated major versions, deprecated packages'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-commit-manager.md')
    assert 'You are a task commit manager specializing in git workflow management and task completion documentation. Your role is to ensure that completed tasks are properly committed with meaningful messages and' in text, "expected to find: " + 'You are a task commit manager specializing in git workflow management and task completion documentation. Your role is to ensure that completed tasks are properly committed with meaningful messages and'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-commit-manager.md')
    assert 'description: Manages task completion and git commit workflows, ensuring proper documentation and version control practices for completed tasks.' in text, "expected to find: " + 'description: Manages task completion and git commit workflows, ensuring proper documentation and version control practices for completed tasks.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-commit-manager.md')
    assert '- Verify task implementation completeness' in text, "expected to find: " + '- Verify task implementation completeness'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-decomposer.md')
    assert 'You are a task decomposer specializing in breaking down complex projects and features into manageable, atomic tasks. Your role is to create clear, actionable work items that can be independently compl' in text, "expected to find: " + 'You are a task decomposer specializing in breaking down complex projects and features into manageable, atomic tasks. Your role is to create clear, actionable work items that can be independently compl'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-decomposer.md')
    assert 'description: Breaks down complex projects into atomic, actionable tasks with clear acceptance criteria and dependencies.' in text, "expected to find: " + 'description: Breaks down complex projects into atomic, actionable tasks with clear acceptance criteria and dependencies.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-decomposer.md')
    assert 'Brief explanation of what needs to be done and why.' in text, "expected to find: " + 'Brief explanation of what needs to be done and why.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-orchestrator.md')
    assert 'You are a task orchestrator specializing in complex workflow management and task coordination. Your role is to break down complex projects into manageable tasks, identify dependencies, and optimize ex' in text, "expected to find: " + 'You are a task orchestrator specializing in complex workflow management and task coordination. Your role is to break down complex projects into manageable tasks, identify dependencies, and optimize ex'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-orchestrator.md')
    assert 'description: Orchestrates complex multi-step tasks, coordinating dependencies and managing parallel execution for optimal workflow efficiency.' in text, "expected to find: " + 'description: Orchestrates complex multi-step tasks, coordinating dependencies and managing parallel execution for optimal workflow efficiency.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/task-orchestrator.md')
    assert 'tools: Read, Write, Edit, Bash, Grep, Glob, TodoWrite' in text, "expected to find: " + 'tools: Read, Write, Edit, Bash, Grep, Glob, TodoWrite'[:80]

