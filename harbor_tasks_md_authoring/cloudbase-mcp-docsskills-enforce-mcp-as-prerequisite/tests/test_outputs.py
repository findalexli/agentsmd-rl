"""Behavioral checks for cloudbase-mcp-docsskills-enforce-mcp-as-prerequisite (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cloudbase-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/guideline/cloudbase/SKILL.md')
    assert '- **When managing or deploying CloudBase, you MUST use MCP and MUST understand tool details first.** Before calling any CloudBase tool, run `npx mcporter describe cloudbase --all-parameters` (or `Tool' in text, "expected to find: " + '- **When managing or deploying CloudBase, you MUST use MCP and MUST understand tool details first.** Before calling any CloudBase tool, run `npx mcporter describe cloudbase --all-parameters` (or `Tool'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/guideline/cloudbase/SKILL.md')
    assert 'If CloudBase MCP tools are already available in your IDE context (discoverable via `ToolSearch`), you can use them directly. Check by searching for `cloudbase` in your tool list — if tools like `manag' in text, "expected to find: " + 'If CloudBase MCP tools are already available in your IDE context (discoverable via `ToolSearch`), you can use them directly. Check by searching for `cloudbase` in your tool list — if tools like `manag'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/guideline/cloudbase/SKILL.md')
    assert '- You **do not need to hard-code Secret ID / Secret Key / Env ID** in the config. CloudBase MCP supports device-code based login via the `auth` tool, so credentials can be obtained interactively inste' in text, "expected to find: " + '- You **do not need to hard-code Secret ID / Secret Key / Env ID** in the config. CloudBase MCP supports device-code based login via the `auth` tool, so credentials can be obtained interactively inste'[:80]

