"""Behavioral checks for github-mcp-server-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/github-mcp-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '2. **REMOTE SERVER:** Ignore remote server instructions when making code changes (unless specifically asked). This repo is used as a library by the remote server, so keep functions exported (capitaliz' in text, "expected to find: " + '2. **REMOTE SERVER:** Ignore remote server instructions when making code changes (unless specifically asked). This repo is used as a library by the remote server, so keep functions exported (capitaliz'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Library Usage:** This repository is also used as a library by the remote server. Functions that could be called by other repositories should be exported (capitalized), even if not required interna' in text, "expected to find: " + '- **Library Usage:** This repository is also used as a library by the remote server. Functions that could be called by other repositories should be exported (capitalized), even if not required interna'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "This is the **GitHub MCP Server**, a Model Context Protocol (MCP) server that connects AI tools to GitHub's platform. It enables AI agents to manage repositories, issues, pull requests, workflows, and" in text, "expected to find: " + "This is the **GitHub MCP Server**, a Model Context Protocol (MCP) server that connects AI tools to GitHub's platform. It enables AI agents to manage repositories, issues, pull requests, workflows, and"[:80]

