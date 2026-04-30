"""Behavioral checks for voicemode-docs-add-tailscale-serve-section (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/voicemode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/voicemode/SKILL.md')
    assert '- **Path mapping**: Tailscale strips the incoming path before forwarding, so you MUST include the full path in the target URL' in text, "expected to find: " + '- **Path mapping**: Tailscale strips the incoming path before forwarding, so you MUST include the full path in the target URL'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/voicemode/SKILL.md')
    assert '- **Multiple paths**: You can configure different paths to different backends on the same or different machines' in text, "expected to find: " + '- **Multiple paths**: You can configure different paths to different backends on the same or different machines'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/voicemode/SKILL.md')
    assert "- **Same-machine testing**: Traffic doesn't route through Tailscale locally — test from another Tailnet device" in text, "expected to find: " + "- **Same-machine testing**: Traffic doesn't route through Tailscale locally — test from another Tailnet device"[:80]

