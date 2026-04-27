"""Behavioral checks for dataverse-skills-fix-detect-missing-mcp-tools (markdown_authoring task).

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
    assert "- The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP) **and** the user has not explicitl" in text, "expected to find: " + "- The user's immediate task does not require MCP (e.g., they asked to create tables, import data, or build a solution — all of which use the SDK or PAC CLI, not MCP) **and** the user has not explicitl"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert "If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Offer to do that first using the `dataverse-init` skill, which will set up the necessary environmen" in text, "expected to find: " + "If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Offer to do that first using the `dataverse-init` skill, which will set up the necessary environmen"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert 'Pause and give the user a chance to restart their editor before proceeding. Do not perform any subsequent or parallel operations until the user responds — they need MCP tools to be active first.' in text, "expected to find: " + 'Pause and give the user a chance to restart their editor before proceeding. Do not perform any subsequent or parallel operations until the user responds — they need MCP tools to be active first.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert '**If the API call fails** (user not logged in, network error, no environments found, or any other error), tell the user what went wrong and fall back to step 3c.' in text, "expected to find: " + '**If the API call fails** (user not logged in, network error, no environments found, or any other error), tell the user what went wrong and fall back to step 3c.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert '**When in doubt:** MCP tools not in your tool list? → Load `dataverse-mcp-configure` to set them up (see below). MCP for conversational data work (single records, simple queries) → Python SDK for scri' in text, "expected to find: " + '**When in doubt:** MCP tools not in your tool list? → Load `dataverse-mcp-configure` to set them up (see below). MCP for conversational data work (single records, simple queries) → Python SDK for scri'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert 'If the user\'s request involves MCP — either explicitly ("connect via MCP", "use MCP", "query via MCP") or implicitly (conversational data queries where MCP would be the natural tool) — check whether D' in text, "expected to find: " + 'If the user\'s request involves MCP — either explicitly ("connect via MCP", "use MCP", "query via MCP") or implicitly (conversational data queries where MCP would be the natural tool) — check whether D'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert '4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear. Do not fall back to the SDK or proceed with other tools. Wait for the user to restart and come back.' in text, "expected to find: " + '4. After MCP is configured, **stop here** — the session must be restarted for MCP tools to appear. Do not fall back to the SDK or proceed with other tools. Wait for the user to restart and come back.'[:80]

