"""Behavioral checks for efcore-release100-port-servicingpr-skill-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/efcore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/servicing-pr/SKILL.md')
    assert 'How the bug affects users without internal technical detail. Include a short (3-4 lines) code sample if possible. If data corruption occurs, state that explicitly. If a feasible workaround exists, bri' in text, "expected to find: " + 'How the bug affects users without internal technical detail. Include a short (3-4 lines) code sample if possible. If data corruption occurs, state that explicitly. If a feasible workaround exists, bri'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/servicing-pr/SKILL.md')
    assert 'How the bug was discovered based on the information in the issue description. If user-reported, mention "User reported on <version>". If multiple users are affected, note that. Count the number of upv' in text, "expected to find: " + 'How the bug was discovered based on the information in the issue description. If user-reported, mention "User reported on <version>". If multiple users are affected, note that. Count the number of upv'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/servicing-pr/SKILL.md')
    assert "description: 'Create EF Core PRs targeting servicing release branches (release/*). Use when working on a PR that targets a release branch, backporting a fix from main, or when the user mentions servic" in text, "expected to find: " + "description: 'Create EF Core PRs targeting servicing release branches (release/*). Use when working on a PR that targets a release branch, backporting a fix from main, or when the user mentions servic"[:80]

