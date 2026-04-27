"""Behavioral checks for cocoindex-chore-upgrade-the-upgradeexamples-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cocoindex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/upgrade-examples/SKILL.md')
    assert '6. Report the number of files updated and provide the PR link from the `gh pr create` output to the user.' in text, "expected to find: " + '6. Report the number of files updated and provide the PR link from the `gh pr create` output to the user.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/upgrade-examples/SKILL.md')
    assert 'gh pr create --base v1 --title "chore: upgrade examples deps to cocoindex-VERSION" --body ""' in text, "expected to find: " + 'gh pr create --base v1 --title "chore: upgrade examples deps to cocoindex-VERSION" --body ""'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/upgrade-examples/SKILL.md')
    assert '5. Create a PR using the `gh` CLI and capture the PR URL from its output:' in text, "expected to find: " + '5. Create a PR using the `gh` CLI and capture the PR URL from its output:'[:80]

