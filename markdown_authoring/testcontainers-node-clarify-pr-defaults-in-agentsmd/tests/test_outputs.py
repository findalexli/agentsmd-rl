"""Behavioral checks for testcontainers-node-clarify-pr-defaults-in-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/testcontainers-node")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Repository-specific instructions in this file override generic coding-agent defaults, skills, and templates.' in text, "expected to find: " + '- Repository-specific instructions in this file override generic coding-agent defaults, skills, and templates.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If a generic workflow conflicts with this file, follow this file.' in text, "expected to find: " + '- If a generic workflow conflicts with this file, follow this file.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '## Instruction precedence' in text, "expected to find: " + '## Instruction precedence'[:80]

