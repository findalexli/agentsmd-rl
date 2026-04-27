"""Behavioral checks for skills-remove-curl-from-allowed-tools (markdown_authoring task).

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
    text = _read('skills/apollo-connectors/SKILL.md')
    assert 'allowed-tools: Bash(rover:*) Read Write Edit Glob Grep' in text, "expected to find: " + 'allowed-tools: Bash(rover:*) Read Write Edit Glob Grep'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/apollo-mcp-server/SKILL.md')
    assert 'allowed-tools: Bash(rover:*) Bash(npx:*) Read Write Edit Glob Grep' in text, "expected to find: " + 'allowed-tools: Bash(rover:*) Bash(npx:*) Read Write Edit Glob Grep'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rover/SKILL.md')
    assert 'allowed-tools: Bash(rover:*) Bash(npm:*) Bash(npx:*) Read Write Edit Glob Grep' in text, "expected to find: " + 'allowed-tools: Bash(rover:*) Bash(npm:*) Bash(npx:*) Read Write Edit Glob Grep'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert '- NEVER include `Bash(curl:*)` in `allowed-tools` as it grants unrestricted network access and enables `curl | sh` remote code execution patterns' in text, "expected to find: " + '- NEVER include `Bash(curl:*)` in `allowed-tools` as it grants unrestricted network access and enables `curl | sh` remote code execution patterns'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-creator/SKILL.md')
    assert '| `allowed-tools` | No | Space-delimited list of pre-approved tools. Do not include `Bash(curl:*)`. |' in text, "expected to find: " + '| `allowed-tools` | No | Space-delimited list of pre-approved tools. Do not include `Bash(curl:*)`. |'[:80]

