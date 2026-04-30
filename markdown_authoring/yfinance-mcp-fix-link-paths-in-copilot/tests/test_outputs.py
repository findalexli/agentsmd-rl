"""Behavioral checks for yfinance-mcp-fix-link-paths-in-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/yfinance-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Read [AGENTS.md](../AGENTS.md) and [CLAUDE.md](../CLAUDE.md) files for for instructions.' in text, "expected to find: " + 'Read [AGENTS.md](../AGENTS.md) and [CLAUDE.md](../CLAUDE.md) files for for instructions.'[:80]

