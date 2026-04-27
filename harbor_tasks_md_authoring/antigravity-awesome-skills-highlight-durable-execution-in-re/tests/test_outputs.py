"""Behavioral checks for antigravity-awesome-skills-highlight-durable-execution-in-re (markdown_authoring task).

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
    text = _read('skills/ai-agents-architect/SKILL.md')
    assert '| Agent workflows lost on crash or restart | high | Use durable execution (e.g. DBOS) to persist workflow state: |' in text, "expected to find: " + '| Agent workflows lost on crash or restart | high | Use durable execution (e.g. DBOS) to persist workflow state: |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-agents-architect/SKILL.md')
    assert 'Works well with: `rag-engineer`, `prompt-engineer`, `backend`, `mcp-builder`, `dbos-python`' in text, "expected to find: " + 'Works well with: `rag-engineer`, `prompt-engineer`, `backend`, `mcp-builder`, `dbos-python`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-patterns/SKILL.md')
    assert '5. For workflows that must survive failures (payments, order fulfillment, multi-step processes), use durable execution at the infrastructure layer — frameworks like DBOS persist workflow state, provid' in text, "expected to find: " + '5. For workflows that must survive failures (payments, order fulfillment, multi-step processes), use durable execution at the infrastructure layer — frameworks like DBOS persist workflow state, provid'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-patterns/SKILL.md')
    assert 'Works well with: `event-sourcing-architect`, `saga-orchestration`, `workflow-automation`, `dbos-*`' in text, "expected to find: " + 'Works well with: `event-sourcing-architect`, `saga-orchestration`, `workflow-automation`, `dbos-*`'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/architecture-patterns/SKILL.md')
    assert '## Related Skills' in text, "expected to find: " + '## Related Skills'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/event-sourcing-architect/SKILL.md')
    assert '- Use durable execution for process managers and sagas — frameworks like DBOS persist workflow state automatically, making cross-aggregate orchestration resilient to crashes' in text, "expected to find: " + '- Use durable execution for process managers and sagas — frameworks like DBOS persist workflow state automatically, making cross-aggregate orchestration resilient to crashes'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/event-sourcing-architect/SKILL.md')
    assert 'Works well with: `saga-orchestration`, `architecture-patterns`, `dbos-*`' in text, "expected to find: " + 'Works well with: `saga-orchestration`, `architecture-patterns`, `dbos-*`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/event-sourcing-architect/SKILL.md')
    assert '## Related Skills' in text, "expected to find: " + '## Related Skills'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/saga-orchestration/SKILL.md')
    assert 'The templates above build saga infrastructure from scratch — saga stores, event publishers, compensation tracking. **Durable execution frameworks** (like DBOS) eliminate much of this boilerplate: the ' in text, "expected to find: " + 'The templates above build saga infrastructure from scratch — saga stores, event publishers, compensation tracking. **Durable execution frameworks** (like DBOS) eliminate much of this boilerplate: the '[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/saga-orchestration/SKILL.md')
    assert 'Works well with: `event-sourcing-architect`, `workflow-automation`, `dbos-*`' in text, "expected to find: " + 'Works well with: `event-sourcing-architect`, `workflow-automation`, `dbos-*`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/saga-orchestration/SKILL.md')
    assert '## Durable Execution Alternative' in text, "expected to find: " + '## Durable Execution Alternative'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/workflow-automation/SKILL.md')
    assert 'Works well with: `multi-agent-orchestration`, `agent-tool-builder`, `backend`, `devops`, `dbos-*`' in text, "expected to find: " + 'Works well with: `multi-agent-orchestration`, `agent-tool-builder`, `backend`, `devops`, `dbos-*`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/workflow-automation/SKILL.md')
    assert 'Inngest balances developer experience with reliability. DBOS uses your' in text, "expected to find: " + 'Inngest balances developer experience with reliability. DBOS uses your'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/workflow-automation/SKILL.md')
    assert 'existing PostgreSQL for durable execution with minimal infrastructure' in text, "expected to find: " + 'existing PostgreSQL for durable execution with minimal infrastructure'[:80]

