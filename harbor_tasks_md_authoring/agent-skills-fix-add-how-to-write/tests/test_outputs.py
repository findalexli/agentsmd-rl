"""Behavioral checks for agent-skills-fix-add-how-to-write (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert '| Field         | Required | Constraints                                                                     |' in text, "expected to find: " + '| Field         | Required | Constraints                                                                     |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `name`        | Yes      | 1-64 chars. Lowercase alphanumeric and hyphens only. Must match directory name. |' in text, "expected to find: " + '| `name`        | Yes      | 1-64 chars. Lowercase alphanumeric and hyphens only. Must match directory name. |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `description` | Yes      | 1-1024 chars. Describe what the skill does AND when to use it.                  |' in text, "expected to find: " + '| `description` | Yes      | 1-1024 chars. Describe what the skill does AND when to use it.                  |'[:80]

