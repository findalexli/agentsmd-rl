"""Behavioral checks for antigravity-awesome-skills-feat-add-openclawgithubrepocomman (markdown_authoring task).

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
    text = _read('skills/openclaw-github-repo-commander/SKILL.md')
    assert 'A structured 7-stage super workflow for comprehensive GitHub repository management. This skill automates repository auditing, cleanup, competitor benchmarking, and optimization — turning a messy repo ' in text, "expected to find: " + 'A structured 7-stage super workflow for comprehensive GitHub repository management. This skill automates repository auditing, cleanup, competitor benchmarking, and optimization — turning a messy repo '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/openclaw-github-repo-commander/SKILL.md')
    assert 'Search GitHub for similar repositories. Compare documentation standards, feature coverage, star counts, and community adoption.' in text, "expected to find: " + 'Search GitHub for similar repositories. Compare documentation standards, feature coverage, star counts, and community adoption.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/openclaw-github-repo-commander/SKILL.md')
    assert 'Execute the plan: delete low-value files, fix security issues, upgrade documentation, add CI workflows, update changelogs.' in text, "expected to find: " + 'Execute the plan: delete low-value files, fix security issues, upgrade documentation, add CI workflows, update changelogs.'[:80]

