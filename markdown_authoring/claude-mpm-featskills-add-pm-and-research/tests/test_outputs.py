"""Behavioral checks for claude-mpm-featskills-add-pm-and-research (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-mpm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/cross-source-research/SKILL.md')
    assert '5. **Stop when you can teach it.** If you can only say "I found 3 mentions of X in Slack and a Confluence page about it," you are not done. You are done when you can explain what X is, why it exists, ' in text, "expected to find: " + '5. **Stop when you can teach it.** If you can only say "I found 3 mentions of X in Slack and a Confluence page about it," you are not done. You are done when you can explain what X is, why it exists, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/cross-source-research/SKILL.md')
    assert 'description: Multi-source investigation workflow for researching topics across configured MCP tools (Slack, Confluence, Jira, GitHub, Drive, databases, analytics). Enforces depth over breadth by requi' in text, "expected to find: " + 'description: Multi-source investigation workflow for researching topics across configured MCP tools (Slack, Confluence, Jira, GitHub, Drive, databases, analytics). Enforces depth over breadth by requi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/cross-source-research/SKILL.md')
    assert 'Structured workflow for investigating topics across multiple MCP-connected sources. The goal is synthesis, not citation. Research is not complete until you can explain the topic conversationally, not ' in text, "expected to find: " + 'Structured workflow for investigating topics across multiple MCP-connected sources. The goal is synthesis, not citation. Research is not complete until you can explain the topic conversationally, not '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/end-of-session/SKILL.md')
    assert "Claude Code sessions are ephemeral. Everything discovered, debugged, decided, or learned during a session disappears when the conversation ends, unless it's written to files that persist. This protoco" in text, "expected to find: " + "Claude Code sessions are ephemeral. Everything discovered, debugged, decided, or learned during a session disappears when the conversation ends, unless it's written to files that persist. This protoco"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/end-of-session/SKILL.md')
    assert '**Technical discoveries**: Code paths traced, API patterns figured out, configuration gotchas hit, root causes identified. These are the things that took 20 minutes to figure out and would take 20 min' in text, "expected to find: " + '**Technical discoveries**: Code paths traced, API patterns figured out, configuration gotchas hit, root causes identified. These are the things that took 20 minutes to figure out and would take 20 min'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/end-of-session/SKILL.md')
    assert 'description: Captures session learnings into persistent project memory before closing. Updates task files, project knowledge, and configuration so the next session starts with full context instead of ' in text, "expected to find: " + 'description: Captures session learnings into persistent project memory before closing. Updates task files, project knowledge, and configuration so the next session starts with full context instead of '[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/mcp-security-review/SKILL.md')
    assert 'MCP servers run as child processes with access to your shell environment, filesystem, and any credentials passed to them. Unlike browser extensions (sandboxed) or npm packages (typically build-time on' in text, "expected to find: " + 'MCP servers run as child processes with access to your shell environment, filesystem, and any credentials passed to them. Unlike browser extensions (sandboxed) or npm packages (typically build-time on'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/mcp-security-review/SKILL.md')
    assert 'Gate that runs before any MCP server is installed or updated. MCP servers handle credentials (OAuth tokens, API keys, AWS profiles) and have network access. A compromised or malicious package can exfi' in text, "expected to find: " + 'Gate that runs before any MCP server is installed or updated. MCP servers handle credentials (OAuth tokens, API keys, AWS profiles) and have network access. A compromised or malicious package can exfi'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/mcp-security-review/SKILL.md')
    assert 'description: Security review gate for MCP server installations. Checks provenance, classifies risk, enforces version pinning, and documents credentials exposure before any MCP is added to your environ' in text, "expected to find: " + 'description: Security review gate for MCP server installations. Checks provenance, classifies risk, enforces version pinning, and documents credentials exposure before any MCP is added to your environ'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/prep-meeting/SKILL.md')
    assert 'Gather context and produce a structured agenda with talking points before a meeting. The goal is to walk in prepared: knowing what each attendee cares about, having data to support your points, and an' in text, "expected to find: " + 'Gather context and produce a structured agenda with talking points before a meeting. The goal is to walk in prepared: knowing what each attendee cares about, having data to support your points, and an'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/prep-meeting/SKILL.md')
    assert 'description: Prepares for meetings by gathering context about attendees, topics, and relevant data across connected tools. Produces an agenda with talking points, supporting data, and anticipated ques' in text, "expected to find: " + 'description: Prepares for meetings by gathering context about attendees, topics, and relevant data across connected tools. Produces an agenda with talking points, supporting data, and anticipated ques'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('src/claude_mpm/skills/bundled/main/prep-meeting/SKILL.md')
    assert 'when_to_use: when preparing for a meeting, creating an agenda, getting ready for a call, or when the user mentions an upcoming meeting they want to be prepared for' in text, "expected to find: " + 'when_to_use: when preparing for a meeting, creating an agenda, getting ready for a call, or when the user mentions an upcoming meeting they want to be prepared for'[:80]

