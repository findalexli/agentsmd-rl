"""Behavioral checks for compound-engineering-plugin-feat-improve-commitpushpr-skill- (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert '- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no chaining (`&&`, `||`, `;`) and no error suppression (`2>/dev/null`, `|| ' in text, "expected to find: " + '- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no chaining (`&&`, `||`, `;`) and no error suppression (`2>/dev/null`, `|| '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '- **Describe the net result, not the journey**: The PR description is about the end state -- what changed and why. Do not include work-product details like bugs found and fixed during development, int' in text, "expected to find: " + '- **Describe the net result, not the journey**: The PR description is about the end state -- what changed and why. Do not include work-product details like bugs found and fixed during development, int'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert "The new commits are already on the PR from the push in Step 5. Report the PR URL, then ask the user whether they want the PR description updated to reflect the new changes. Use the platform's blocking" in text, "expected to find: " + "The new commits are already on the PR from the push in Step 5. Report the PR URL, then ask the user whether they want the PR description updated to reflect the new changes. Use the platform's blocking"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '- If **yes** -- write a new description following the same principles in Step 6 (size the full PR, not just the new commits), including the Compound Engineering badge unless one is already present in ' in text, "expected to find: " + '- If **yes** -- write a new description following the same principles in Step 6 (size the full PR, not just the new commits), including the Compound Engineering badge unless one is already present in '[:80]

