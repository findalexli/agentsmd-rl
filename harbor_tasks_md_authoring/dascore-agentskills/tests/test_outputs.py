"""Behavioral checks for dascore-agentskills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dascore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/agents.md')
    assert 'Important: if changing site structure, edit `scripts/_templates/_quarto.yml` (not `docs/_quarto.yml`, which is generated/overwritten).' in text, "expected to find: " + 'Important: if changing site structure, edit `scripts/_templates/_quarto.yml` (not `docs/_quarto.yml`, which is generated/overwritten).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/agents.md')
    assert '- Prefer `pathlib.Path` over raw path strings (except performance-sensitive bulk file workflows).' in text, "expected to find: " + '- Prefer `pathlib.Path` over raw path strings (except performance-sensitive bulk file workflows).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/agents.md')
    assert 'This file gives AI/code agents a practical checklist for contributing safely to DASCore.' in text, "expected to find: " + 'This file gives AI/code agents a practical checklist for contributing safely to DASCore.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/draft-release/SKILL.md')
    assert 'description: Draft the next release version and changelog by fetching tags, computing the next semantic v* tag, collecting merged PRs into master since last release via gh, and printing the proposed v' in text, "expected to find: " + 'description: Draft the next release version and changelog by fetching tags, computing the next semantic v* tag, collecting merged PRs into master since last release via gh, and printing the proposed v'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/draft-release/SKILL.md')
    assert '0. Ask for elevated permissions with network access to run `git fetch --all --tags` and the GitHub CLI PR commands used to collect merged PRs (for example `gh pr list`, `gh pr view`, or `gh api`).' in text, "expected to find: " + '0. Ask for elevated permissions with network access to run `git fetch --all --tags` and the GitHub CLI PR commands used to collect merged PRs (for example `gh pr list`, `gh pr view`, or `gh api`).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/draft-release/SKILL.md')
    assert '- Prefer explicit, user-facing PR summaries over internal implementation details.' in text, "expected to find: " + '- Prefer explicit, user-facing PR summaries over internal implementation details.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'All coding agents should load and follow `.agents/agents.md` before making changes.' in text, "expected to find: " + 'All coding agents should load and follow `.agents/agents.md` before making changes.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The canonical agent instructions for this repository are in:' in text, "expected to find: " + 'The canonical agent instructions for this repository are in:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `.agents/agents.md`' in text, "expected to find: " + '- `.agents/agents.md`'[:80]

