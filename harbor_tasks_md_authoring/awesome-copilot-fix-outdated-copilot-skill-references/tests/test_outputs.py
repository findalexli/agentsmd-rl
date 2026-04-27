"""Behavioral checks for awesome-copilot-fix-outdated-copilot-skill-references (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-copilot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/github-copilot-starter/SKILL.md')
    assert '- [ ] Skills and agents include relevant descriptions; include MCP/tool-related metadata only when the target Copilot environment actually supports or requires it' in text, "expected to find: " + '- [ ] Skills and agents include relevant descriptions; include MCP/tool-related metadata only when the target Copilot environment actually supports or requires it'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/github-copilot-starter/SKILL.md')
    assert 'Main repository instructions that apply to all Copilot interactions. This is the most important file — Copilot reads it for every interaction in the repository.' in text, "expected to find: " + 'Main repository instructions that apply to all Copilot interactions. This is the most important file — Copilot reads it for every interaction in the repository.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/github-copilot-starter/SKILL.md')
    assert '7. **Set up specialized agents**, fetching from awesome-copilot where applicable (especially for expert engineer agents matching the tech stack)' in text, "expected to find: " + '7. **Set up specialized agents**, fetching from awesome-copilot where applicable (especially for expert engineer agents matching the tech stack)'[:80]

