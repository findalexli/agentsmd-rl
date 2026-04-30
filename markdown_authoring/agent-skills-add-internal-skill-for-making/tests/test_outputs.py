"""Behavioral checks for agent-skills-add-internal-skill-for-making (markdown_authoring task).

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
    text = _read('internal/skills/flux-controller-patch-releases/SKILL.md')
    assert '- Group multiple dependency bump PRs naturally when the repo history already does that' in text, "expected to find: " + '- Group multiple dependency bump PRs naturally when the repo history already does that'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/skills/flux-controller-patch-releases/SKILL.md')
    assert '- Cherry-pick only the changelog commit back to `main`, not the release version bump.' in text, "expected to find: " + '- Cherry-pick only the changelog commit back to `main`, not the release version bump.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/skills/flux-controller-patch-releases/SKILL.md')
    assert '- Tag from the release series branch merge commit, not from the release prep branch.' in text, "expected to find: " + '- Tag from the release series branch merge commit, not from the release prep branch.'[:80]

