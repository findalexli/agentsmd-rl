"""Behavioral checks for compound-engineering-plugin-fix-quote-frontenddesign-skill-d (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/frontend-design/SKILL.md')
    assert "description: 'Build web interfaces with genuine design quality, not AI slop. Use for any frontend work - landing pages, web apps, dashboards, admin panels, components, interactive experiences. Activat" in text, "expected to find: " + "description: 'Build web interfaces with genuine design quality, not AI slop. Use for any frontend work - landing pages, web apps, dashboards, admin panels, components, interactive experiences. Activat"[:80]

