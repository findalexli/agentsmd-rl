"""Behavioral checks for antigravity-awesome-skills-add-videodb-skills-to-individual (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/videodb-skills/SKILL.md')
    assert 'The only video skill your agent needs. Upload any video, connect real-time streams, search inside by what was said or shown, build complex editing workflows with overlays, generate AI media, add subti' in text, "expected to find: " + 'The only video skill your agent needs. Upload any video, connect real-time streams, search inside by what was said or shown, build complex editing workflows with overlays, generate AI media, add subti'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/videodb-skills/SKILL.md')
    assert 'description: "The only video skill your agent needs — upload any video, connect real-time streams, search inside by what was said or shown, build complex editing workflows with overlays, generate AI m' in text, "expected to find: " + 'description: "The only video skill your agent needs — upload any video, connect real-time streams, search inside by what was said or shown, build complex editing workflows with overlays, generate AI m'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/videodb-skills/SKILL.md')
    assert 'The agent guides API key setup ($20 free credits, no credit card), installs the SDK, and verifies the connection.' in text, "expected to find: " + 'The agent guides API key setup ($20 free credits, no credit card), installs the SDK, and verifies the connection.'[:80]

