"""Behavioral checks for dataverse-skills-improving-the-wording-in-the (markdown_authoring task).

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
    assert "**Execute every numbered step in order.** Do not skip ahead to a later step, even if it appears more relevant to the user's immediate goal. Steps that seem unrelated to the current task (e.g., MCP set" in text, "expected to find: " + "**Execute every numbered step in order.** Do not skip ahead to a later step, even if it appears more relevant to the user's immediate goal. Steps that seem unrelated to the current task (e.g., MCP set"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert 'Always ask the user to confirm the Dataverse environment URL and pause to let the user respond even if you can derive it from `pac auth list` or other sources.' in text, "expected to find: " + 'Always ask the user to confirm the Dataverse environment URL and pause to let the user respond even if you can derive it from `pac auth list` or other sources.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert 'Follow steps 3–4 from Scenario A above. Ask the user for SOLUTION_NAME if not already known (but use the DATAVERSE_URL you obtained and confirmed in step 2).' in text, "expected to find: " + 'Follow steps 3–4 from Scenario A above. Ask the user for SOLUTION_NAME if not already known (but use the DATAVERSE_URL you obtained and confirmed in step 2).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert 'If you installed the MCP server, pause and give the user a chance to restart the session to enable it before proceeding. Do not perform any subsequent or parallel operations until the user responds.' in text, "expected to find: " + 'If you installed the MCP server, pause and give the user a chance to restart the session to enable it before proceeding. Do not perform any subsequent or parallel operations until the user responds.'[:80]

