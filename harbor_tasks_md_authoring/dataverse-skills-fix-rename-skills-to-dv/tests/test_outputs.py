"""Behavioral checks for dataverse-skills-fix-rename-skills-to-dv (markdown_authoring task).

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
    text = _read('.github/plugins/dataverse/skills/dv-init/SKILL.md')
    assert 'Write and run `scripts/create_solution.py` to create the publisher and solution in the environment using the Python SDK. The script **must** follow the publisher discovery flow from the `dv-solution` ' in text, "expected to find: " + 'Write and run `scripts/create_solution.py` to create the publisher and solution in the environment using the Python SDK. The script **must** follow the publisher discovery flow from the `dv-solution` '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-init/SKILL.md')
    assert 'If MCP is needed and not yet configured, use the `dv-mcp-configure` skill. **This is always the last step** because `claude mcp add` requires a Claude Code restart, which ends the current session.' in text, "expected to find: " + 'If MCP is needed and not yet configured, use the `dv-mcp-configure` skill. **This is always the last step** because `claude mcp add` requires a Claude Code restart, which ends the current session.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-init/SKILL.md')
    assert 'If MCP is needed and not yet configured, use the `dv-mcp-configure` skill.' in text, "expected to find: " + 'If MCP is needed and not yet configured, use the `dv-mcp-configure` skill.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-mcp-configure/SKILL.md')
    assert "If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Do that first using the `dv-init` skill (do this by default when the user does not express a prefer" in text, "expected to find: " + "If the file or the variable doesn't exist, the user has not initialized the Dataverse workspace yet. Do that first using the `dv-init` skill (do this by default when the user does not express a prefer"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-mcp-configure/SKILL.md')
    assert 'If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, do that first using the `dv-init` skill (do this by default when the us' in text, "expected to find: " + 'If at any point during the MCP configuration process you discover that the user has not initialized the Dataverse workspace yet, do that first using the `dv-init` skill (do this by default when the us'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-mcp-configure/SKILL.md')
    assert '- If `claude` and the VSCode extension is used: set it to the same value as `CLIENT_ID` if already set, otherwise offer to create a new app registration following Scenario A, step 7 in the `dv-init` s' in text, "expected to find: " + '- If `claude` and the VSCode extension is used: set it to the same value as `CLIENT_ID` if already set, otherwise offer to create a new app registration following Scenario A, step 7 in the `dv-init` s'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-metadata/SKILL.md')
    assert 'DO NOT USE WHEN: reading/writing data records (use dv-python-sdk),' in text, "expected to find: " + 'DO NOT USE WHEN: reading/writing data records (use dv-python-sdk),'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-metadata/SKILL.md')
    assert 'exporting solutions (use dv-solution).' in text, "expected to find: " + 'exporting solutions (use dv-solution).'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-metadata/SKILL.md')
    assert 'name: dv-metadata' in text, "expected to find: " + 'name: dv-metadata'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-overview/SKILL.md')
    assert '**Tool priority (always follow this order):** MCP (if available) for simple reads, queries, and ≤10 record CRUD → Python SDK for scripted data, bulk operations, schema creation, and analysis → Web API' in text, "expected to find: " + '**Tool priority (always follow this order):** MCP (if available) for simple reads, queries, and ≤10 record CRUD → Python SDK for scripted data, bulk operations, schema creation, and analysis → Web API'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-overview/SKILL.md')
    assert '3. Load the `dv-mcp-configure` skill to set up the MCP server' in text, "expected to find: " + '3. Load the `dv-mcp-configure` skill to set up the MCP server'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-overview/SKILL.md')
    assert 'name: dv-overview' in text, "expected to find: " + 'name: dv-overview'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-python-sdk/SKILL.md')
    assert 'DO NOT USE WHEN: creating forms/views (use dv-metadata with Web API),' in text, "expected to find: " + 'DO NOT USE WHEN: creating forms/views (use dv-metadata with Web API),'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-python-sdk/SKILL.md')
    assert '- **Forms** (FormXml) — use the Web API directly (see `dv-metadata`)' in text, "expected to find: " + '- **Forms** (FormXml) — use the Web API directly (see `dv-metadata`)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-python-sdk/SKILL.md')
    assert 'exporting solutions (use dv-solution with PAC CLI).' in text, "expected to find: " + 'exporting solutions (use dv-solution with PAC CLI).'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-setup/SKILL.md')
    assert 'DO NOT USE WHEN: initializing a workspace/repo (use dv-init).' in text, "expected to find: " + 'DO NOT USE WHEN: initializing a workspace/repo (use dv-init).'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-setup/SKILL.md')
    assert 'name: dv-setup' in text, "expected to find: " + 'name: dv-setup'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-solution/SKILL.md')
    assert 'DO NOT USE WHEN: creating tables/columns/forms/views (use dv-metadata).' in text, "expected to find: " + 'DO NOT USE WHEN: creating tables/columns/forms/views (use dv-metadata).'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/dv-solution/SKILL.md')
    assert 'name: dv-solution' in text, "expected to find: " + 'name: dv-solution'[:80]

