"""Behavioral checks for kaos-featskills-redesign-dependabotfix-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kaos")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dependabot-fix/SKILL.md')
    assert 'description: Comprehensively diagnose and fix a failing Dependabot PR. Use this skill when asked to run /dependabot-fix <pr-number>. The user provides the PR number in their prompt. The skill loads PR' in text, "expected to find: " + 'description: Comprehensively diagnose and fix a failing Dependabot PR. Use this skill when asked to run /dependabot-fix <pr-number>. The user provides the PR number in their prompt. The skill loads PR'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dependabot-fix/SKILL.md')
    assert '- **High (runtime / wire)** — reproduce against a locally-built Docker image for the affected component (see ecosystem appendix). If it touches operator/agent behaviour, bring up a KIND cluster per `.' in text, "expected to find: " + '- **High (runtime / wire)** — reproduce against a locally-built Docker image for the affected component (see ecosystem appendix). If it touches operator/agent behaviour, bring up a KIND cluster per `.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dependabot-fix/SKILL.md')
    assert 'Ask it to read matching `docs/` pages for the changed modules: module overview, testing notes, architecture diagrams. Return a briefing no longer than ~40 lines covering what the module does, its publ' in text, "expected to find: " + 'Ask it to read matching `docs/` pages for the changed modules: module overview, testing notes, architecture diagrams. Return a briefing no longer than ~40 lines covering what the module does, its publ'[:80]

