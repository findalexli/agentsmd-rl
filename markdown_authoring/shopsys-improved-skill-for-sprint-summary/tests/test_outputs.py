"""Behavioral checks for shopsys-improved-skill-for-sprint-summary (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shopsys")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/sprint-summary/SKILL.md')
    assert '**Required:** when Playwright MCP is available, generate screenshots for UX-relevant tickets as part of the workflow (do not wait for a separate prompt). Default target URL is the review environment `' in text, "expected to find: " + '**Required:** when Playwright MCP is available, generate screenshots for UX-relevant tickets as part of the workflow (do not wait for a separate prompt). Default target URL is the review environment `'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/sprint-summary/SKILL.md')
    assert 'https://shopsys.atlassian.net/wiki/spaces/PRG/folder/2698510337?atlOrigin=eyJpIjoiMTIzN2EwNmQyYzMyNGFiY2I1OTU1YmVkMjk4YTk1MTciLCJwIjoiYyJ9' in text, "expected to find: " + 'https://shopsys.atlassian.net/wiki/spaces/PRG/folder/2698510337?atlOrigin=eyJpIjoiMTIzN2EwNmQyYzMyNGFiY2I1OTU1YmVkMjk4YTk1MTciLCJwIjoiYyJ9'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/sprint-summary/SKILL.md')
    assert '5. After the user decides whether to open the file in PhpStorm, instruct them to create the article in Confluence:' in text, "expected to find: " + '5. After the user decides whether to open the file in PhpStorm, instruct them to create the article in Confluence:'[:80]

