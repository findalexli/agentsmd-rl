"""Behavioral checks for genie-featagents-optimize-agentsmd-75894-lines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/genie")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Critical:** @ is a lightweight path reference, NOT a content loader.' in text, "expected to find: " + '**Critical:** @ is a lightweight path reference, NOT a content loader.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'See `@.genie/docs/mcp-interface.md` for complete documentation.' in text, "expected to find: " + 'See `@.genie/docs/mcp-interface.md` for complete documentation.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `@.genie/agents/code/skills/execution-integrity-protocol.md`' in text, "expected to find: " + '- `@.genie/agents/code/skills/execution-integrity-protocol.md`'[:80]

