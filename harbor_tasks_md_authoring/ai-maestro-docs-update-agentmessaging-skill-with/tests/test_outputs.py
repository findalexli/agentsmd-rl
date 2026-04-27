"""Behavioral checks for ai-maestro-docs-update-agentmessaging-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-maestro")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-messaging/SKILL.md')
    assert '- If still not found, the error shows available hosts - check those for valid agent names' in text, "expected to find: " + '- If still not found, the error shows available hosts - check those for valid agent names'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-messaging/SKILL.md')
    assert '- `to_agent[@host]` (required) - Target agent (host is optional thanks to smart lookup):' in text, "expected to find: " + '- `to_agent[@host]` (required) - Target agent (host is optional thanks to smart lookup):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-messaging/SKILL.md')
    assert 'send-aimaestro-message.sh api-form "Customer data sync" "Please sync customer records"' in text, "expected to find: " + 'send-aimaestro-message.sh api-form "Customer data sync" "Please sync customer records"'[:80]

