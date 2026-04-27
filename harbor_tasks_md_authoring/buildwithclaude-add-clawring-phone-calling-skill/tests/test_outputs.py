"""Behavioral checks for buildwithclaude-add-clawring-phone-calling-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/clawring/SKILL.md')
    assert 'description: "Phone calling skill for OpenClaw: agent makes real outbound phone calls to users for alerts, briefings, reminders, and urgent notifications. Managed service, no Twilio setup needed. 100+' in text, "expected to find: " + 'description: "Phone calling skill for OpenClaw: agent makes real outbound phone calls to users for alerts, briefings, reminders, and urgent notifications. Managed service, no Twilio setup needed. 100+'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/clawring/SKILL.md')
    assert '- **Fast model recommended**: Assign the skill to a fast, lightweight model (Haiku-class) for natural conversation pace. Slow models make conversations feel laggy.' in text, "expected to find: " + '- **Fast model recommended**: Assign the skill to a fast, lightweight model (Haiku-class) for natural conversation pace. Slow models make conversations feel laggy.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/clawring/SKILL.md')
    assert "Give your OpenClaw agent the ability to make real outbound phone calls to you. The agent calls you — you don't call the agent. There is no inbound phone number." in text, "expected to find: " + "Give your OpenClaw agent the ability to make real outbound phone calls to you. The agent calls you — you don't call the agent. There is no inbound phone number."[:80]

