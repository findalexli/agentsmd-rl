"""Behavioral checks for claude-code-plugins-plus-skills-improve-contentconsistencyva (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/productivity/000-jeremy-content-consistency-validator/skills/000-jeremy-content-consistency-validator/SKILL.md')
    assert 'Checks content for tone, terminology, formatting, and structural consistency across multiple documentation sources (websites, GitHub repos, local docs). Generates read-only discrepancy reports with se' in text, "expected to find: " + 'Checks content for tone, terminology, formatting, and structural consistency across multiple documentation sources (websites, GitHub repos, local docs). Generates read-only discrepancy reports with se'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/productivity/000-jeremy-content-consistency-validator/skills/000-jeremy-content-consistency-validator/SKILL.md')
    assert '- **Pre-release audit**: Before tagging a new version, run the validator to catch version mismatches between your README, docs site, and changelog — e.g., the website says v2.1.0 but the GitHub README' in text, "expected to find: " + '- **Pre-release audit**: Before tagging a new version, run the validator to catch version mismatches between your README, docs site, and changelog — e.g., the website says v2.1.0 but the GitHub README'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/productivity/000-jeremy-content-consistency-validator/skills/000-jeremy-content-consistency-validator/SKILL.md')
    assert '- **Onboarding review**: When a new contributor flags confusing docs, run a consistency check to surface contradictory feature claims, outdated contact info, or missing sections across your documentat' in text, "expected to find: " + '- **Onboarding review**: When a new contributor flags confusing docs, run a consistency check to surface contradictory feature claims, outdated contact info, or missing sections across your documentat'[:80]

