"""Behavioral checks for synthetic-monitoring-app-chore-move-cursor-rules-into (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/synthetic-monitoring-app")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/documentation.mdc')
    assert '.cursor/rules/documentation.mdc' in text, "expected to find: " + '.cursor/rules/documentation.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/engineering-best-practices.mdc')
    assert '.cursor/rules/engineering-best-practices.mdc' in text, "expected to find: " + '.cursor/rules/engineering-best-practices.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/file-organisation.mdc')
    assert '.cursor/rules/file-organisation.mdc' in text, "expected to find: " + '.cursor/rules/file-organisation.mdc'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/reference-directory.mdc')
    assert '.cursor/rules/reference-directory.mdc' in text, "expected to find: " + '.cursor/rules/reference-directory.mdc'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/team-composition.mdc')
    assert '.cursor/rules/team-composition.mdc' in text, "expected to find: " + '.cursor/rules/team-composition.mdc'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/this-product.mdc')
    assert '.cursor/rules/this-product.mdc' in text, "expected to find: " + '.cursor/rules/this-product.mdc'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/when-creating-prs.mdc')
    assert '.cursor/rules/when-creating-prs.mdc' in text, "expected to find: " + '.cursor/rules/when-creating-prs.mdc'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/when-writing-tests.mdc')
    assert '.cursor/rules/when-writing-tests.mdc' in text, "expected to find: " + '.cursor/rules/when-writing-tests.mdc'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/you-and-me.mdc')
    assert '.cursor/rules/you-and-me.mdc' in text, "expected to find: " + '.cursor/rules/you-and-me.mdc'[:80]

