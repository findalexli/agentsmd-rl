"""Behavioral checks for agent-kanban-docs-update-agentkanban-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-kanban")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Repo management: `ak create repo` registers repo at tenant level. `ak get repo` lists registered repos.' in text, "expected to find: " + '- Repo management: `ak create repo` registers repo at tenant level. `ak get repo` lists registered repos.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-kanban/SKILL.md')
    assert '- Always create a PR and submit via `task review --pr-url` when your work produces code changes.' in text, "expected to find: " + '- Always create a PR and submit via `task review --pr-url` when your work produces code changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-kanban/SKILL.md')
    assert '| `ak get task --board <id> --status <s>` | List tasks filtered by board, status, label, repo |' in text, "expected to find: " + '| `ak get task --board <id> --status <s>` | List tasks filtered by board, status, label, repo |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-kanban/SKILL.md')
    assert '| `ak task reject <id> --reason "..."` | Reject task from review back to in_progress |' in text, "expected to find: " + '| `ak task reject <id> --reason "..."` | Reject task from review back to in_progress |'[:80]

