"""Behavioral checks for background-agents-docs-rewrite-agentsmd-following-best (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/background-agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| Package         | Lang / Framework                   | Purpose                                                     |' in text, "expected to find: " + '| Package         | Lang / Framework                   | Purpose                                                     |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `shared`        | TypeScript                         | Shared types, auth utilities, model definitions             |' in text, "expected to find: " + '| `shared`        | TypeScript                         | Shared types, auth utilities, model definitions             |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `control-plane` | TypeScript / CF Workers + DO       | Session management, WebSocket streaming, GitHub integration |' in text, "expected to find: " + '| `control-plane` | TypeScript / CF Workers + DO       | Session management, WebSocket streaming, GitHub integration |'[:80]

