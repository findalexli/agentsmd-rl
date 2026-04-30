"""Behavioral checks for mcp-for-beginners-add-agentsmd-file-with-comprehensive (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**MCP for Beginners** is an open-source educational curriculum for learning the Model Context Protocol (MCP) - a standardized framework for interactions between AI models and client applications. This' in text, "expected to find: " + '**MCP for Beginners** is an open-source educational curriculum for learning the Model Context Protocol (MCP) - a standardized framework for interactions between AI models and client applications. This'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'A: Verify image paths are relative and use forward slashes. Images should be in the `images/` directory or `translated_images/` for localized versions.' in text, "expected to find: " + 'A: Verify image paths are relative and use forward slashes. Images should be in the `images/` directory or `translated_images/` for localized versions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "A: Ensure you've followed the setup instructions in the specific sample's README. Check that you have the correct versions of dependencies installed." in text, "expected to find: " + "A: Ensure you've followed the setup instructions in the specific sample's README. Check that you have the correct versions of dependencies installed."[:80]

