"""Behavioral checks for antigravity-awesome-skills-feat-add-skillrouter-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-router/SKILL.md')
    assert 'description: "Use when the user is unsure which skill to use or where to start. Interviews the user with targeted questions and recommends the best skill(s) from the installed library for their goal."' in text, "expected to find: " + 'description: "Use when the user is unsure which skill to use or where to start. Interviews the user with targeted questions and recommends the best skill(s) from the installed library for their goal."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-router/SKILL.md')
    assert '- Web app testing: `@burp-suite-testing`, `@sql-injection-testing`, `@xss-html-injection`' in text, "expected to find: " + '- Web app testing: `@burp-suite-testing`, `@sql-injection-testing`, `@xss-html-injection`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-router/SKILL.md')
    assert '- Git workflow: `@git-pushing`, `@using-git-worktrees`, `@github-workflow-automation`' in text, "expected to find: " + '- Git workflow: `@git-pushing`, `@using-git-worktrees`, `@github-workflow-automation`'[:80]

