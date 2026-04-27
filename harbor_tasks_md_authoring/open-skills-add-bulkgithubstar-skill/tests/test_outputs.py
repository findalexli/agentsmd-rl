"""Behavioral checks for open-skills-add-bulkgithubstar-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulk-github-star/SKILL.md')
    assert 'description: "Star all repositories from a GitHub user automatically. Use when: (1) Supporting open source creators, (2) Bulk discovery of useful projects, or (3) Automating GitHub engagement."' in text, "expected to find: " + 'description: "Star all repositories from a GitHub user automatically. Use when: (1) Supporting open source creators, (2) Bulk discovery of useful projects, or (3) Automating GitHub engagement."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulk-github-star/SKILL.md')
    assert "const output = execSync(`gh repo list ${username} --limit 100 --json nameWithOwner`, { encoding: 'utf8' });" in text, "expected to find: " + "const output = execSync(`gh repo list ${username} --limit 100 --json nameWithOwner`, { encoding: 'utf8' });"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulk-github-star/SKILL.md')
    assert 'You can bulk star GitHub repositories. When a user asks to star all repos from a GitHub user:' in text, "expected to find: " + 'You can bulk star GitHub repositories. When a user asks to star all repos from a GitHub user:'[:80]

