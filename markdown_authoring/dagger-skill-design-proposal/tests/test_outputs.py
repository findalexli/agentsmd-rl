"""Behavioral checks for dagger-skill-design-proposal (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dagger")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dagger-design-proposals/SKILL.md')
    assert 'description: Write design proposals for Dagger features. Use when asked to draft, review, or iterate on Dagger design documents, RFCs, or proposals.' in text, "expected to find: " + 'description: Write design proposals for Dagger features. Use when asked to draft, review, or iterate on Dagger design documents, RFCs, or proposals.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dagger-design-proposals/SKILL.md')
    assert '2. **One at a time** - Walk through each item individually, waiting for user response' in text, "expected to find: " + '2. **One at a time** - Walk through each item individually, waiting for user response'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dagger-design-proposals/SKILL.md')
    assert 'Example: To understand how `Host.findUp` works before proposing `Workspace.findUp`:' in text, "expected to find: " + 'Example: To understand how `Host.findUp` works before proposing `Workspace.findUp`:'[:80]

