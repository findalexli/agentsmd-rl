"""Behavioral checks for mcp-server-tree-sitter-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp-server-tree-sitter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'tree-sitter >= 0.24 removed `Query.captures()`. Always use the `query_captures(query, node)` wrapper from `utils/tree_sitter_helpers.py` instead of calling `query.captures()` directly. This applies to' in text, "expected to find: " + 'tree-sitter >= 0.24 removed `Query.captures()`. Always use the `query_captures(query, node)` wrapper from `utils/tree_sitter_helpers.py` instead of calling `query.captures()` directly. This applies to'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Circular imports with `di.py`:** The DI container constructs registries. Don't import `get_container` from `__init__` methods of objects the container creates. Use method injection instead." in text, "expected to find: " + "- **Circular imports with `di.py`:** The DI container constructs registries. Don't import `get_container` from `__init__` methods of objects the container creates. Use method injection instead."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Config:** `config.py` — `ConfigurationManager` auto-loads YAML from `MCP_TS_CONFIG_PATH` or `~/.config/tree-sitter/config.yaml`. Precedence: env vars > YAML > defaults' in text, "expected to find: " + '- **Config:** `config.py` — `ConfigurationManager` auto-loads YAML from `MCP_TS_CONFIG_PATH` or `~/.config/tree-sitter/config.yaml`. Precedence: env vars > YAML > defaults'[:80]

