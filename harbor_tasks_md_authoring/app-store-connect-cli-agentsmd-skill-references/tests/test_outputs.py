"""Behavioral checks for app-store-connect-cli-agentsmd-skill-references (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/app-store-connect-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/asc-cli-usage/SKILL.md')
    assert '.agent/skills/asc-cli-usage/SKILL.md' in text, "expected to find: " + '.agent/skills/asc-cli-usage/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert '## References' in text, "expected to find: " + '## References'[:80]

