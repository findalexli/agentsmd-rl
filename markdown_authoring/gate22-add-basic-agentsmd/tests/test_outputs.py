"""Behavioral checks for gate22-add-basic-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gate22")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document provides coding agents with detailed context about the Gate22 repository structure, build processes, testing procedures, and conventions.' in text, "expected to find: " + 'This document provides coding agents with detailed context about the Gate22 repository structure, build processes, testing procedures, and conventions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Backend**: Python/FastAPI-based service that powers the control plane, MCP hosting, and Virtual MCP servers' in text, "expected to find: " + '- **Backend**: Python/FastAPI-based service that powers the control plane, MCP hosting, and Virtual MCP servers'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Gate22 is an open-source MCP (Model Context Protocol) Gateway and Control Plane for AI governance.' in text, "expected to find: " + 'Gate22 is an open-source MCP (Model Context Protocol) Gateway and Control Plane for AI governance.'[:80]

