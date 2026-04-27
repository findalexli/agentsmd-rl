"""Behavioral checks for remix-tighten-makepr-skill-workflow (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/remix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/make-pr/SKILL.md')
    assert '- If `gh pr create` fails, leave the branch pushed when possible and give the user a ready-to-open compare URL plus the prepared title/body details.' in text, "expected to find: " + '- If `gh pr create` fails, leave the branch pushed when possible and give the user a ready-to-open compare URL plus the prepared title/body details.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/make-pr/SKILL.md')
    assert '- Before opening the PR, decide whether the change is user-facing enough to require release notes in `packages/*/.changes`.' in text, "expected to find: " + '- Before opening the PR, decide whether the change is user-facing enough to require release notes in `packages/*/.changes`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/make-pr/SKILL.md')
    assert '- If a change file is needed or likely needed, use the `make-change-file` skill instead of re-deriving that workflow here.' in text, "expected to find: " + '- If a change file is needed or likely needed, use the `make-change-file` skill instead of re-deriving that workflow here.'[:80]

