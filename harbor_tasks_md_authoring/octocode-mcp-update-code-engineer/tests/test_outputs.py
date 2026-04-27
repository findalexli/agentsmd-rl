"""Behavioral checks for octocode-mcp-update-code-engineer (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/octocode-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/octocode-engineer/SKILL.md')
    assert 'description: "Flexible system-engineering skill for technical code understanding, project/feature deep dives, bug investigation, quality and architecture analysis, and safe delivery from research and ' in text, "expected to find: " + 'description: "Flexible system-engineering skill for technical code understanding, project/feature deep dives, bug investigation, quality and architecture analysis, and safe delivery from research and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/octocode-engineer/SKILL.md')
    assert '7. Check architecture, layering/modularity, contracts/protocols, reliability/observability/rollout/data correctness, build/configuration, docs, and flow risk with the scanner and relevant project file' in text, "expected to find: " + '7. Check architecture, layering/modularity, contracts/protocols, reliability/observability/rollout/data correctness, build/configuration, docs, and flow risk with the scanner and relevant project file'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/octocode-engineer/SKILL.md')
    assert '| Rollout & migration safety | Can this ship safely without breaking old producers/consumers? | migration docs, versioned contracts, compatibility checks, feature-flag/release-path review |' in text, "expected to find: " + '| Rollout & migration safety | Can this ship safely without breaking old producers/consumers? | migration docs, versioned contracts, compatibility checks, feature-flag/release-path review |'[:80]

