"""Behavioral checks for yfinance-mcp-update-agentsmd (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert '- `README.md`: end-user setup and usage guide. Demo chatbot link points to the dedicated `yfinance-mcp-demo` repository.' in text, "expected to find: " + '- `README.md`: end-user setup and usage guide. Demo chatbot link points to the dedicated `yfinance-mcp-demo` repository.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PRs should summarize intent and list the validation commands run.' in text, "expected to find: " + '- PRs should summarize intent and list the validation commands run.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `uv sync --extra dev`: install development dependencies.' in text, "expected to find: " + '- `uv sync --extra dev`: install development dependencies.'[:80]

