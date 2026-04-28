"""Behavioral checks for lynx-stack-chore-move-skills-from-githubskills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lynx-stack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-ci-watch-subagent/SKILL.md')
    assert '.agents/skills/pr-ci-watch-subagent/SKILL.md' in text, "expected to find: " + '.agents/skills/pr-ci-watch-subagent/SKILL.md'[:80]

