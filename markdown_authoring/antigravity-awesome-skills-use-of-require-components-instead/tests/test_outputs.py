"""Behavioral checks for antigravity-awesome-skills-use-of-require-components-instead (markdown_authoring task).

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
    text = _read('skills/bevy-ecs-expert/SKILL.md')
    assert '### Example 1: Spawning Entities with Require Component' in text, "expected to find: " + '### Example 1: Spawning Entities with Require Component'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bevy-ecs-expert/SKILL.md')
    assert 'Sprite::from_image(asset_server.load("player.png")),' in text, "expected to find: " + 'Sprite::from_image(asset_server.load("player.png")),'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bevy-ecs-expert/SKILL.md')
    assert '#[derive(Component, Reflect, Default)]' in text, "expected to find: " + '#[derive(Component, Reflect, Default)]'[:80]

