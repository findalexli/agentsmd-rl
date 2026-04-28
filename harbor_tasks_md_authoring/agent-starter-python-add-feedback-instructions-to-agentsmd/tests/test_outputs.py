"""Behavioral checks for agent-starter-python-add-feedback-instructions-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-starter-python")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If you use the LiveKit Docs MCP Server to search or browse documentation, also submit constructive feedback to LiveKit with the submit_docs_feedback tool. Add this to your to-do list when planning wor' in text, "expected to find: " + 'If you use the LiveKit Docs MCP Server to search or browse documentation, also submit constructive feedback to LiveKit with the submit_docs_feedback tool. Add this to your to-do list when planning wor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'In particular, you can use it to manage SIP trunks for telephony-based agents. Refer to `lk sip --help` for more information.' in text, "expected to find: " + 'In particular, you can use it to manage SIP trunks for telephony-based agents. Refer to `lk sip --help` for more information.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '### Submit docs feedback to LiveKit' in text, "expected to find: " + '### Submit docs feedback to LiveKit'[:80]

