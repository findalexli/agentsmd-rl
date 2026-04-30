"""Behavioral checks for dataverse-skills-updated-the-skills-to-remind (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dataverse-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert 'Do not skip MCP configuration (step 8 in Scenario A, step 11 in Scenario B) unless an MCP server is already configured (`.mcp.json` exists with a Dataverse server entry, or `claude mcp list` shows one' in text, "expected to find: " + 'Do not skip MCP configuration (step 8 in Scenario A, step 11 in Scenario B) unless an MCP server is already configured (`.mcp.json` exists with a Dataverse server entry, or `claude mcp list` shows one'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert '> Remember to **use `claude --continue` to resume the session** without losing context.' in text, "expected to find: " + '> Remember to **use `claude --continue` to resume the session** without losing context.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert 'If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill.' in text, "expected to find: " + 'If MCP is needed and not yet configured, use the `dataverse-mcp-configure` skill.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert "If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Do that first using the `dataverse-init` skill (do this by default when the user does not express a" in text, "expected to find: " + "If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Do that first using the `dataverse-init` skill (do this by default when the user does not express a"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert 'If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, do that first using the `dataverse-init` skill (do this by default when' in text, "expected to find: " + 'If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, do that first using the `dataverse-init` skill (do this by default when'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert '- After running the command, they must restart Claude Code for the changes to take effect (remind them: "Remember to **use `claude --continue` to resume the session** without losing context")' in text, "expected to find: " + '- After running the command, they must restart Claude Code for the changes to take effect (remind them: "Remember to **use `claude --continue` to resume the session** without losing context")'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert '4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear (if running in Claude Code, remind them to resume the session correctly: "Remember to **use `claude --' in text, "expected to find: " + '4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear (if running in Claude Code, remind them to resume the session correctly: "Remember to **use `claude --'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/setup/SKILL.md')
    assert 'After any `winget` install, the new tool may not be in PATH until the shell is restarted. If a tool is not found immediately after install, ask the user to close and reopen the terminal (if running in' in text, "expected to find: " + 'After any `winget` install, the new tool may not be in PATH until the shell is restarted. If a tool is not found immediately after install, ask the user to close and reopen the terminal (if running in'[:80]

