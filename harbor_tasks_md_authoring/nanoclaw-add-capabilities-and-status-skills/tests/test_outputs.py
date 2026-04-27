"""Behavioral checks for nanoclaw-add-capabilities-and-status-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/capabilities/SKILL.md')
    assert "description: Show what this NanoClaw instance can do — installed skills, available tools, and system info. Read-only. Use when the user asks what the bot can do, what's installed, or runs /capabilitie" in text, "expected to find: " + "description: Show what this NanoClaw instance can do — installed skills, available tools, and system info. Read-only. Use when the user asks what the bot can do, what's installed, or runs /capabilitie"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/capabilities/SKILL.md')
    assert 'ls /workspace/extra/ 2>/dev/null && echo "Extra mounts: $(ls /workspace/extra/ 2>/dev/null | wc -l | tr -d \' \')" || echo "Extra mounts: none"' in text, "expected to find: " + 'ls /workspace/extra/ 2>/dev/null && echo "Extra mounts: $(ls /workspace/extra/ 2>/dev/null | wc -l | tr -d \' \')" || echo "Extra mounts: none"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/capabilities/SKILL.md')
    assert 'Each directory is an installed skill. The directory name is the skill name (e.g., `agent-browser` → `/agent-browser`).' in text, "expected to find: " + 'Each directory is an installed skill. The directory name is the skill name (e.g., `agent-browser` → `/agent-browser`).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/status/SKILL.md')
    assert 'description: Quick read-only health check — session context, workspace mounts, tool availability, and task snapshot. Use when the user asks for system status or runs /status.' in text, "expected to find: " + 'description: Quick read-only health check — session context, workspace mounts, tool availability, and task snapshot. Use when the user asks for system status or runs /status.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/status/SKILL.md')
    assert '- **MCP:** mcp__nanoclaw__* (send_message, schedule_task, list_tasks, pause_task, resume_task, cancel_task, update_task, register_group)' in text, "expected to find: " + '- **MCP:** mcp__nanoclaw__* (send_message, schedule_task, list_tasks, pause_task, resume_task, cancel_task, update_task, register_group)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('container/skills/status/SKILL.md')
    assert 'Adapt based on what you actually find. Keep it concise — this is a quick health check, not a deep diagnostic.' in text, "expected to find: " + 'Adapt based on what you actually find. Keep it concise — this is a quick health check, not a deep diagnostic.'[:80]

