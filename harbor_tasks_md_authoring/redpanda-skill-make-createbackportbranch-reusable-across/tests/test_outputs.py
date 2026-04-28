"""Behavioral checks for redpanda-skill-make-createbackportbranch-reusable-across (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/redpanda")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-backport-branch/SKILL.md')
    assert '**Optional: machine-readable report.** If the `SKILL_REPORT_FILE` env var is set (callers like GitHub Actions workflows use this), write the exact same report text to that file path. The file content ' in text, "expected to find: " + '**Optional: machine-readable report.** If the `SKILL_REPORT_FILE` env var is set (callers like GitHub Actions workflows use this), write the exact same report text to that file path. The file content '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-backport-branch/SKILL.md')
    assert '`gh` resolves the `{owner}` and `{repo}` placeholders from the git remote of the current directory (see [`gh api` docs](https://cli.github.com/manual/gh_api)). Run this from a checkout of the repo tha' in text, "expected to find: " + '`gh` resolves the `{owner}` and `{repo}` placeholders from the git remote of the current directory (see [`gh api` docs](https://cli.github.com/manual/gh_api)). Run this from a checkout of the repo tha'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-backport-branch/SKILL.md')
    assert 'gh api "repos/{owner}/{repo}/pulls/$pr_number/commits" --paginate --jq \'[.[].sha[0:10]]|join(" ")\'' in text, "expected to find: " + 'gh api "repos/{owner}/{repo}/pulls/$pr_number/commits" --paginate --jq \'[.[].sha[0:10]]|join(" ")\''[:80]

