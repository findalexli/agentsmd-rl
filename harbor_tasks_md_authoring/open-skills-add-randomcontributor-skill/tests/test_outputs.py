"""Behavioral checks for open-skills-add-randomcontributor-skill (markdown_authoring task).

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
    text = _read('skills/random-contributor/SKILL.md')
    assert '"Find a random contributor for {owner}/{repo}. Use the GitHub API; if API rate limits block you, fall back to scraping the contributors page. Return JSON: {login, name?, avatar, profile, contributions' in text, "expected to find: " + '"Find a random contributor for {owner}/{repo}. Use the GitHub API; if API rate limits block you, fall back to scraping the contributors page. Return JSON: {login, name?, avatar, profile, contributions'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/random-contributor/SKILL.md')
    assert '- Select a uniformly random contributor from a public GitHub repository. Useful for sampling, shoutouts, delegation, or fair assignment among contributors.' in text, "expected to find: " + '- Select a uniformly random contributor from a public GitHub repository. Useful for sampling, shoutouts, delegation, or fair assignment among contributors.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/random-contributor/SKILL.md')
    assert 'description: Pick a random contributor from a GitHub repository using the GitHub API or repository pages (no auth required for public repos).' in text, "expected to find: " + 'description: Pick a random contributor from a GitHub repository using the GitHub API or repository pages (no auth required for public repos).'[:80]

