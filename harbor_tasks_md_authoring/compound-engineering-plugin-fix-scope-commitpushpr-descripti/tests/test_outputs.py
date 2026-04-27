"""Behavioral checks for compound-engineering-plugin-fix-scope-commitpushpr-descripti (markdown_authoring task).

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
    assert "If none resolve, ask the user to specify the target branch. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no que" in text, "expected to find: " + "If none resolve, ask the user to specify the target branch. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no que"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'Before writing, determine the **base branch** and gather the **full branch scope**. The working-tree diff from Step 1 only shows uncommitted changes at invocation time -- the PR description must cover' in text, "expected to find: " + 'Before writing, determine the **base branch** and gather the **full branch scope**. The working-tree diff from Step 1 only shows uncommitted changes at invocation time -- the PR description must cover'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'Extract `baseRefName` as the base branch name. The PR URL contains the base repository (`https://github.com/<owner>/<repo>/pull/...`). Determine which local remote corresponds to that repository:' in text, "expected to find: " + 'Extract `baseRefName` as the base branch name. The PR URL contains the base repository (`https://github.com/<owner>/<repo>/pull/...`). Determine which local remote corresponds to that repository:'[:80]

