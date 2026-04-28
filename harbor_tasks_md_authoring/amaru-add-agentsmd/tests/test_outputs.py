"""Behavioral checks for amaru-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/amaru")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Always check neighboring files, similar modules, and Cargo.toml for existing patterns, libs, imports, error types before adding new code' in text, "expected to find: " + '- Always check neighboring files, similar modules, and Cargo.toml for existing patterns, libs, imports, error types before adding new code'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file provides instructions for agentic coding tools (e.g. opencode, Cursor agents, etc.) working on the Amaru codebase.' in text, "expected to find: " + 'This file provides instructions for agentic coding tools (e.g. opencode, Cursor agents, etc.) working on the Amaru codebase.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Implement: Debug, Clone, Copy (if applicable), PartialEq/Eq/Ord, Display, Serialize/Deserialize, CBOR Encode/Decode' in text, "expected to find: " + '- Implement: Debug, Clone, Copy (if applicable), PartialEq/Eq/Ord, Display, Serialize/Deserialize, CBOR Encode/Decode'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

