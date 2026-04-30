"""Behavioral checks for skills-feat-add-microsoftdocs-skill-for (markdown_authoring task).

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
    text = _read('.github/skills/microsoft-docs/SKILL.md')
    assert 'description: Understand Microsoft technologies by querying official documentation. Use whenever the user asks how something works, wants tutorials, needs configuration options, limits, quotas, or best' in text, "expected to find: " + 'description: Understand Microsoft technologies by querying official documentation. Use whenever the user asks how something works, wants tutorials, needs configuration options, limits, quotas, or best'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/microsoft-docs/SKILL.md')
    assert 'compatibility: Primarily uses the Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp); if that is unavailable, fall back to the mslearn CLI (`npx @microsoft/learn-cli`).' in text, "expected to find: " + 'compatibility: Primarily uses the Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp); if that is unavailable, fall back to the mslearn CLI (`npx @microsoft/learn-cli`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/microsoft-docs/SKILL.md')
    assert 'The `fetch` command also supports `--section <heading>` to extract a single section and `--max-chars <number>` to truncate output.' in text, "expected to find: " + 'The `fetch` command also supports `--section <heading>` to extract a single section and `--max-chars <number>` to truncate output.'[:80]

