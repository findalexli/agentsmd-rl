"""Behavioral checks for compound-engineering-plugin-featskills-clean-up-argumenthint (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md')
    assert 'plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md' in text, "expected to find: " + 'plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert 'plugins/compound-engineering/skills/ce-compound/SKILL.md' in text, "expected to find: " + 'plugins/compound-engineering/skills/ce-compound/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-ideate/SKILL.md')
    assert 'argument-hint: "[feature, focus area, or constraint]"' in text, "expected to find: " + 'argument-hint: "[feature, focus area, or constraint]"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert 'argument-hint: "[optional: feature description, requirements doc path, or improvement idea]"' in text, "expected to find: " + 'argument-hint: "[optional: feature description, requirements doc path, or improvement idea]"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-review/SKILL.md')
    assert 'argument-hint: "[blank to review current branch, or provide PR link]"' in text, "expected to find: " + 'argument-hint: "[blank to review current branch, or provide PR link]"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert 'argument-hint: "[Plan doc path or description of work. Blank to auto use latest plan doc]"' in text, "expected to find: " + 'argument-hint: "[Plan doc path or description of work. Blank to auto use latest plan doc]"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert 'argument-hint: "[Plan doc path or description of work. Blank to auto use latest plan doc]"' in text, "expected to find: " + 'argument-hint: "[Plan doc path or description of work. Blank to auto use latest plan doc]"'[:80]

