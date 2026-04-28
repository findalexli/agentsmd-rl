"""Behavioral checks for arcade-mcp-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/arcade-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`MCPApp` (`libs/arcade-mcp-server/arcade_mcp_server/mcp_app.py`) provides a FastAPI-like decorator API. At build time, `@app.tool` registers functions into a `ToolCatalog`; `@app.resource` and `app.ad' in text, "expected to find: " + '`MCPApp` (`libs/arcade-mcp-server/arcade_mcp_server/mcp_app.py`) provides a FastAPI-like decorator API. At build time, `@app.tool` registers functions into a `ToolCatalog`; `@app.resource` and `app.ad'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The decision point is in `create_arcade_mcp()` (`libs/arcade-mcp-server/arcade_mcp_server/worker.py`): if `ARCADE_WORKER_SECRET` (read via `MCPSettings.arcade.server_secret`) is set, a `FastAPIWorker`' in text, "expected to find: " + 'The decision point is in `create_arcade_mcp()` (`libs/arcade-mcp-server/arcade_mcp_server/worker.py`): if `ARCADE_WORKER_SECRET` (read via `MCPSettings.arcade.server_secret`) is set, a `FastAPIWorker`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Local file discovery** (default): scans cwd for `*.py`, `tools/*.py`, `arcade_tools/*.py`, `tools/**/*.py`. Uses a fast AST pass (`get_tools_from_file`) to find `@tool`-decorated functions withou' in text, "expected to find: " + '3. **Local file discovery** (default): scans cwd for `*.py`, `tools/*.py`, `arcade_tools/*.py`, `tools/**/*.py`. Uses a fast AST pass (`get_tools_from_file`) to find `@tool`-decorated functions withou'[:80]

