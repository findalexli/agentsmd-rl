"""Behavioral checks for ruby-lsp-adopt-the-agentsmd-standard (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ruby-lsp")


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
    assert 'Ruby LSP is a Language Server Protocol implementation for Ruby, providing IDE features across different editors. The project consists of:' in text, "expected to find: " + 'Ruby LSP is a Language Server Protocol implementation for Ruby, providing IDE features across different editors. The project consists of:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`lib/ruby_lsp/global_state.rb`** - Central configuration and state management (formatters, linters, client capabilities)' in text, "expected to find: " + '- **`lib/ruby_lsp/global_state.rb`** - Central configuration and state management (formatters, linters, client capabilities)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`lib/ruby_lsp/base_server.rb`** - Abstract base with core LSP infrastructure (message I/O, worker threads)' in text, "expected to find: " + '- **`lib/ruby_lsp/base_server.rb`** - Abstract base with core LSP infrastructure (message I/O, worker threads)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

