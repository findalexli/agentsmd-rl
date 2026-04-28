"""Behavioral checks for aqua-registry-feat-add-claude-skills-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aqua-registry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fetch-doc/SKILL.md')
    assert 'description: Fetch the document of aqua from the other repository aquaproj/aqua. This skill is useful when you want to know the specification of aqua.' in text, "expected to find: " + 'description: Fetch the document of aqua from the other repository aquaproj/aqua. This skill is useful when you want to know the specification of aqua.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fetch-doc/SKILL.md')
    assert 'Especially, about the registry settings, please see .ai/aqua/website/docs/reference/registry-config/\\*.md.' in text, "expected to find: " + 'Especially, about the registry settings, please see .ai/aqua/website/docs/reference/registry-config/\\*.md.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fetch-doc/SKILL.md')
    assert 'The document of aqua is hosted at https://github.com/aquaproj/aqua.' in text, "expected to find: " + 'The document of aqua is hosted at https://github.com/aquaproj/aqua.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-change/SKILL.md')
    assert 'description: Review changes. Use this skill when adding or changing pkgs/**/*.yaml' in text, "expected to find: " + 'description: Review changes. Use this skill when adding or changing pkgs/**/*.yaml'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-change/SKILL.md')
    assert 'Please review pkgs/\\*_/_.yaml according to AGENTS.md' in text, "expected to find: " + 'Please review pkgs/\\*_/_.yaml according to AGENTS.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/review-change/SKILL.md')
    assert 'name: review-change' in text, "expected to find: " + 'name: review-change'[:80]

