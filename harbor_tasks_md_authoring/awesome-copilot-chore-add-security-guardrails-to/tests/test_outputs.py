"""Behavioral checks for awesome-copilot-chore-add-security-guardrails-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-copilot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/make-repo-contribution/SKILL.md')
    assert 'If any of those exist or you discover documentation elsewhere in the repo, read through what you find and apply the guidance related to contribution workflow: branch naming, commit message format, iss' in text, "expected to find: " + 'If any of those exist or you discover documentation elsewhere in the repo, read through what you find and apply the guidance related to contribution workflow: branch naming, commit message format, iss'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/make-repo-contribution/SKILL.md')
    assert "Before performing any commits, ensure a branch has been created for the work. Apply branch naming conventions from the repository's documentation (prefixes like `feature` or `chore`, username patterns" in text, "expected to find: " + "Before performing any commits, ensure a branch has been created for the work. Apply branch naming conventions from the repository's documentation (prefixes like `feature` or `chore`, username patterns"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/make-repo-contribution/SKILL.md')
    assert 'If no issue is discovered, look through the guidance to see if creating an issue is a requirement. If it is, use the template provided in the repository as a formatting structure — fill in its heading' in text, "expected to find: " + 'If no issue is discovered, look through the guidance to see if creating an issue is a requirement. If it is, use the template provided in the repository as a formatting structure — fill in its heading'[:80]

