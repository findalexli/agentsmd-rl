"""Behavioral checks for caddy-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/caddy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Disclosed** — Tell reviewers when code was AI-generated or AI-assisted, mentioning which agent/model is used' in text, "expected to find: " + '1. **Disclosed** — Tell reviewers when code was AI-generated or AI-assisted, mentioning which agent/model is used'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Caddy is built around a **module system** where everything is a module registered via `caddy.RegisterModule()`:' in text, "expected to find: " + 'Caddy is built around a **module system** where everything is a module registered via `caddy.RegisterModule()`:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Context**: Use `caddy.Context` for accessing other apps/modules and logging—don't store contexts in structs." in text, "expected to find: " + "**Context**: Use `caddy.Context` for accessing other apps/modules and logging—don't store contexts in structs."[:80]

