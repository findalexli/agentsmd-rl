"""Behavioral checks for julia-agent-skills-small-improvement-to-dv-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/julia-agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/documenter-vitepress/SKILL.md')
    assert 'The server starts at `http://localhost:SOMEPORT/` with hot reload.  The port number is reported in the output of the command.' in text, "expected to find: " + 'The server starts at `http://localhost:SOMEPORT/` with hot reload.  The port number is reported in the output of the command.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/documenter-vitepress/SKILL.md')
    assert 'From shell (be sure to run this in the background):' in text, "expected to find: " + 'From shell (be sure to run this in the background):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/documenter-vitepress/SKILL.md')
    assert 'From Julia REPL / MCP tool:' in text, "expected to find: " + 'From Julia REPL / MCP tool:'[:80]

