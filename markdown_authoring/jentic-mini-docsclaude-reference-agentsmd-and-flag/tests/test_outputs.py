"""Behavioral checks for jentic-mini-docsclaude-reference-agentsmd-and-flag (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jentic-mini")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert "See @AGENTS.md for the agent-facing runtime guide (search, inspect, execute workflow; endpoint reference; credential-injection contract from the agent's perspective). Keep the overlapping sections in " in text, "expected to find: " + "See @AGENTS.md for the agent-facing runtime guide (search, inspect, execute workflow; endpoint reference; credential-injection contract from the agent's perspective). Keep the overlapping sections in "[:80]

