"""Behavioral checks for cli-docsskills-add-gh-and-ghskill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh-skill/SKILL.md')
    assert 'description: Manage agent skills with gh skill. Use this skill to discover, preview, install, update, and publish Agent Skills so an agent can self-manage the skills available in its environment.' in text, "expected to find: " + 'description: Manage agent skills with gh skill. Use this skill to discover, preview, install, update, and publish Agent Skills so an agent can self-manage the skills available in its environment.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh-skill/SKILL.md')
    assert 'gh skill install <owner>/<repo> skills/<scope>/<skill-name>   # exact path, fastest' in text, "expected to find: " + 'gh skill install <owner>/<repo> skills/<scope>/<skill-name>   # exact path, fastest'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh-skill/SKILL.md')
    assert 'gh skill search <query> --owner <org>                    # restrict to one owner' in text, "expected to find: " + 'gh skill search <query> --owner <org>                    # restrict to one owner'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh/SKILL.md')
    assert 'description: Patterns for invoking the GitHub CLI (gh) from agents. Covers structured output, pagination, repo targeting, search vs list, gh api fallback.' in text, "expected to find: " + 'description: Patterns for invoking the GitHub CLI (gh) from agents. Covers structured output, pagination, repo targeting, search vs list, gh api fallback.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh/SKILL.md')
    assert 'prompting (e.g. `must provide --title and --body when not running interactively`).' in text, "expected to find: " + 'prompting (e.g. `must provide --title and --body when not running interactively`).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh/SKILL.md')
    assert '- Review-thread comments on a PR: `gh api repos/{owner}/{repo}/pulls/{n}/comments`' in text, "expected to find: " + '- Review-thread comments on a PR: `gh api repos/{owner}/{repo}/pulls/{n}/comments`'[:80]

