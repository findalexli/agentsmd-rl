"""Behavioral checks for agent-skills-improve-remotionbestpractices-skill-description (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/remotion/SKILL.md')
    assert '**Critical rules**: Always use `useCurrentFrame()` for animations. Never use CSS transitions or Tailwind animation classes — they will not render.' in text, "expected to find: " + '**Critical rules**: Always use `useCurrentFrame()` for animations. Never use CSS transitions or Tailwind animation classes — they will not render.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/remotion/SKILL.md')
    assert '<Composition id="MyVideo" component={MyVideo} width={1920} height={1080} fps={30} durationInFrames={90} />' in text, "expected to find: " + '<Composition id="MyVideo" component={MyVideo} width={1920} height={1080} fps={30} durationInFrames={90} />'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/remotion/SKILL.md')
    assert 'Use this skill when working with Remotion code — creating compositions, animating scenes,' in text, "expected to find: " + 'Use this skill when working with Remotion code — creating compositions, animating scenes,'[:80]

