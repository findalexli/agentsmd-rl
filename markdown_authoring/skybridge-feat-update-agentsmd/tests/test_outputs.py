"""Behavioral checks for skybridge-feat-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skybridge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The core loop: an MCP server exposes tools. When the host (ChatGPT, Claude, VSCode…) calls a tool, the server returns structured data **and** a reference to a React widget. The host renders that widge' in text, "expected to find: " + 'The core loop: an MCP server exposes tools. When the host (ChatGPT, Claude, VSCode…) calls a tool, the server returns structured data **and** a reference to a React widget. The host renders that widge'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Skybridge is a **fullstack TypeScript framework** for building ChatGPT Apps and MCP Apps — interactive React widgets that render inside AI conversations.' in text, "expected to find: " + 'Skybridge is a **fullstack TypeScript framework** for building ChatGPT Apps and MCP Apps — interactive React widgets that render inside AI conversations.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When the public API of `packages/core/` changes (exports from `src/server/index.ts`, `src/web/index.ts`, and CLI commands in `src/commands/`):' in text, "expected to find: " + 'When the public API of `packages/core/` changes (exports from `src/server/index.ts`, `src/web/index.ts`, and CLI commands in `src/commands/`):'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

