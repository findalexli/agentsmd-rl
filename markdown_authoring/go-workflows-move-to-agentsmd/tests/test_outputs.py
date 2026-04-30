"""Behavioral checks for go-workflows-move-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/go-workflows")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '.github/copilot-instructions.md' in text, "expected to find: " + '.github/copilot-instructions.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The project includes comprehensive documentation built with Slate, a static documentation generator. The documentation is located in the `/docs/` directory and provides detailed guides, API references' in text, "expected to find: " + 'The project includes comprehensive documentation built with Slate, a static documentation generator. The documentation is located in the `/docs/` directory and provides detailed guides, API references'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Durable workflows library for Go that borrows heavily from Temporal and DTFx. Supports multiple backends (MySQL, Redis, SQLite, in-memory) and provides comprehensive workflow orchestration capabilitie' in text, "expected to find: " + 'Durable workflows library for Go that borrows heavily from Temporal and DTFx. Supports multiple backends (MySQL, Redis, SQLite, in-memory) and provides comprehensive workflow orchestration capabilitie'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This guide provides essential information for AI coding agents working on this project. Always reference this information first before exploring the codebase or running commands.' in text, "expected to find: " + 'This guide provides essential information for AI coding agents working on this project. Always reference this information first before exploring the codebase or running commands.'[:80]

