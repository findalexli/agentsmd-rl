"""Behavioral checks for han-featcore-add-explicitconfiguration-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/han")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/explicit-configuration/SKILL.md')
    assert 'When configuring services, APIs, or framework features, explicitly set all parameters rather than relying on defaults. Defaults vary across versions, environments, and frameworks.' in text, "expected to find: " + 'When configuring services, APIs, or framework features, explicitly set all parameters rather than relying on defaults. Defaults vary across versions, environments, and frameworks.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/explicit-configuration/SKILL.md')
    assert 'What works with defaults in development may fail in production. Explicit configuration is documentation that runs.' in text, "expected to find: " + 'What works with defaults in development may fail in production. Explicit configuration is documentation that runs.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/explicit-configuration/SKILL.md')
    assert 'description: Prefer explicit configuration over framework defaults to prevent environment-dependent failures' in text, "expected to find: " + 'description: Prefer explicit configuration over framework defaults to prevent environment-dependent failures'[:80]

