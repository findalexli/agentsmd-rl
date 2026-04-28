"""Behavioral checks for distr-docs-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/distr")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'All database access should go through `internal/db/` functions. Never write raw SQL in handlers or services. If you need a new query, add it to the appropriate file in `internal/db/`.' in text, "expected to find: " + 'All database access should go through `internal/db/` functions. Never write raw SQL in handlers or services. If you need a new query, add it to the appropriate file in `internal/db/`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The platform consists of a control plane (Hub) running in the cloud, agents that run in customer environments, and an MCP server for AI integrations.' in text, "expected to find: " + 'The platform consists of a control plane (Hub) running in the cloud, agents that run in customer environments, and an MCP server for AI integrations.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Distr is an open-source software distribution platform that enables companies to distribute applications to self-managed customers.' in text, "expected to find: " + 'Distr is an open-source software distribution platform that enables companies to distribute applications to self-managed customers.'[:80]

