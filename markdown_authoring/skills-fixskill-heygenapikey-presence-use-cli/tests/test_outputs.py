"""Behavioral checks for skills-fixskill-heygenapikey-presence-use-cli (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '1. **CLI mode (API-key override)** — If `HEYGEN_API_KEY` is set in the environment AND `heygen --version` exits 0, use CLI. API-key presence is an explicit user signal that they want direct API access' in text, "expected to find: " + '1. **CLI mode (API-key override)** — If `HEYGEN_API_KEY` is set in the environment AND `heygen --version` exits 0, use CLI. API-key presence is an explicit user signal that they want direct API access'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '4. **Neither** — tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."' in text, "expected to find: " + '4. **Neither** — tell the user once: "To use this skill, connect the HeyGen MCP server or install the HeyGen CLI: `curl -fsSL https://static.heygen.ai/cli/install.sh | bash` then `heygen auth login`."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '2. **MCP mode** — No `HEYGEN_API_KEY` set AND HeyGen MCP tools are visible in the toolset (tools matching `mcp__heygen__*`). OAuth auth, uses existing plan credits.' in text, "expected to find: " + '2. **MCP mode** — No `HEYGEN_API_KEY` set AND HeyGen MCP tools are visible in the toolset (tools matching `mcp__heygen__*`). OAuth auth, uses existing plan credits.'[:80]

