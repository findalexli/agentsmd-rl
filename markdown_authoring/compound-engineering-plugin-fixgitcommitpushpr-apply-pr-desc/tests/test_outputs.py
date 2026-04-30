"""Behavioral checks for compound-engineering-plugin-fixgitcommitpushpr-apply-pr-desc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert "2. Apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block; if `<TITLE>` " in text, "expected to find: " + "2. Apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block; if `<TITLE>` "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'Using the `=== TITLE ===` / `=== BODY_FILE ===` block returned by `ce-pr-description`, substitute `<TITLE>` and `<BODY_FILE>` verbatim. If `<TITLE>` contains `"`, `` ` ``, `$`, or `\\`, escape them or ' in text, "expected to find: " + 'Using the `=== TITLE ===` / `=== BODY_FILE ===` block returned by `ce-pr-description`, substitute `<TITLE>` and `<BODY_FILE>` verbatim. If `<TITLE>` contains `"`, `` ` ``, `$`, or `\\`, escape them or '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '1. Run Step 6 to generate via `ce-pr-description` (passing the existing PR URL as `pr:`). `ce-pr-description` explicitly does not apply on its own; it returns its `=== TITLE ===` / `=== BODY_FILE ===`' in text, "expected to find: " + '1. Run Step 6 to generate via `ce-pr-description` (passing the existing PR URL as `pr:`). `ce-pr-description` explicitly does not apply on its own; it returns its `=== TITLE ===` / `=== BODY_FILE ===`'[:80]

