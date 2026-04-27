"""Behavioral checks for open-skills-add-presenton-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/presenton/SKILL.md')
    assert 'Presenton is an open-source, locally-run AI presentation generator. It creates professional slideshows from text prompts or uploaded documents, exports to PPTX and PDF, and exposes a built-in MCP serv' in text, "expected to find: " + 'Presenton is an open-source, locally-run AI presentation generator. It creates professional slideshows from text prompts or uploaded documents, exports to PPTX and PDF, and exposes a built-in MCP serv'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/presenton/SKILL.md')
    assert 'description: "Generate AI-powered presentations locally using Presenton. Use when: (1) User asks to create a presentation or slideshow, (2) User wants to convert a document or prompt into slides, (3) ' in text, "expected to find: " + 'description: "Generate AI-powered presentations locally using Presenton. Use when: (1) User asks to create a presentation or slideshow, (2) User wants to convert a document or prompt into slides, (3) '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/presenton/SKILL.md')
    assert '- [../browser-automation-agent/SKILL.md](../browser-automation-agent/SKILL.md) — Automate the Presenton web UI when API access is not available' in text, "expected to find: " + '- [../browser-automation-agent/SKILL.md](../browser-automation-agent/SKILL.md) — Automate the Presenton web UI when API access is not available'[:80]

