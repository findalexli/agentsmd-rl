"""Behavioral checks for agents-refactor-rename-skills-for-clarity (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/airflow-2-to-3-migration/SKILL.md')
    assert 'shared-skills/airflow-2-to-3-migration/SKILL.md' in text, "expected to find: " + 'shared-skills/airflow-2-to-3-migration/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/check-freshness/SKILL.md')
    assert 'name: check-freshness' in text, "expected to find: " + 'name: check-freshness'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/debug-dag/SKILL.md')
    assert 'name: debug-dag' in text, "expected to find: " + 'name: debug-dag'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/discover-data/SKILL.md')
    assert 'name: discover-data' in text, "expected to find: " + 'name: discover-data'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/downstream-lineage/SKILL.md')
    assert 'name: downstream-lineage' in text, "expected to find: " + 'name: downstream-lineage'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/profile-table/SKILL.md')
    assert 'name: profile-table' in text, "expected to find: " + 'name: profile-table'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('shared-skills/upstream-lineage/SKILL.md')
    assert 'name: upstream-lineage' in text, "expected to find: " + 'name: upstream-lineage'[:80]

