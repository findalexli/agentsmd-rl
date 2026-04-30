"""Behavioral checks for compound-engineering-plugin-fixgitcommitpushpr-simplify-pr-p (markdown_authoring task).

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
    assert "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD; printf '\\n=== BRANCH ===\\n'; git branch --show-current; printf '\\n=== LOG ===\\n'; git log --oneline -10; printf '\\n=== " in text, "expected to find: " + "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD; printf '\\n=== BRANCH ===\\n'; git branch --show-current; printf '\\n=== LOG ===\\n'; git log --oneline -10; printf '\\n=== "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'If the existing PR check returned JSON with `state: OPEN`, note the URL — continue to Step 4 and Step 5, then skip to Step 7 (existing PR flow). Otherwise (`NO_OPEN_PR` or a non-OPEN state), continue ' in text, "expected to find: " + 'If the existing PR check returned JSON with `state: OPEN`, note the URL — continue to Step 4 and Step 5, then skip to Step 7 (existing PR flow). Otherwise (`NO_OPEN_PR` or a non-OPEN state), continue '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '2. **Remote default branch from context above:** If the remote default branch resolved (not `DEFAULT_BRANCH_UNRESOLVED`), strip the `origin/` prefix and use that. Use `origin` as the base remote.' in text, "expected to find: " + '2. **Remote default branch from context above:** If the remote default branch resolved (not `DEFAULT_BRANCH_UNRESOLVED`), strip the `origin/` prefix and use that. Use `origin` as the base remote.'[:80]

