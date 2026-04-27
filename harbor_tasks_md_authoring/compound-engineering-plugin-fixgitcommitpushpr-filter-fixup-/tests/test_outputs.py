"""Behavioral checks for compound-engineering-plugin-fixgitcommitpushpr-filter-fixup- (markdown_authoring task).

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
    assert 'Follow the "Detect the base branch and remote" and "Gather the branch scope" sections of Step 6 to get the full branch diff. Use the PR found in DU-2 as the existing PR for base branch detection. Clas' in text, "expected to find: " + 'Follow the "Detect the base branch and remote" and "Gather the branch scope" sections of Step 6 to get the full branch diff. Use the PR found in DU-2 as the existing PR for base branch detection. Clas'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '- If **yes** -- write a new description following the same principles in Step 6 (size the full PR, not just the new commits). Classify commits per "Classify commits before writing" -- the new commits ' in text, "expected to find: " + '- If **yes** -- write a new description following the same principles in Step 6 (size the full PR, not just the new commits). Classify commits per "Classify commits before writing" -- the new commits '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'Only feature commits inform the description. Fix-up commits are noise -- they describe the iteration process, not the end result. The full diff already includes whatever the fix-up commits changed, so' in text, "expected to find: " + 'Only feature commits inform the description. Fix-up commits are noise -- they describe the iteration process, not the end result. The full diff already includes whatever the fix-up commits changed, so'[:80]

