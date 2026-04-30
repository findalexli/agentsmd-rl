"""Behavioral checks for redisearch-improve-claude-tests-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/redisearch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/rust-tests-guidelines/SKILL.md')
    assert '6. Do not reference exact line numbers in comments, as they may change over time.' in text, "expected to find: " + '6. Do not reference exact line numbers in comments, as they may change over time.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/write-rust-tests/SKILL.md')
    assert 'Before writing each test, explicitly identify which branch or code path it will cover that no existing test already covers. An uncovered line is not sufficient justification — ask *why* it is uncovere' in text, "expected to find: " + 'Before writing each test, explicitly identify which branch or code path it will cover that no existing test already covers. An uncovered line is not sufficient justification — ask *why* it is uncovere'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/write-rust-tests/SKILL.md')
    assert '- **Trivial trait delegations** — `Default`, `From`, or similar trait impls that are single-line delegations to an already-tested constructor, since they will be covered transitively.' in text, "expected to find: " + '- **Trivial trait delegations** — `Default`, `From`, or similar trait impls that are single-line delegations to an already-tested constructor, since they will be covered transitively.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/write-rust-tests/SKILL.md')
    assert "Two tests are redundant if they exercise the same set of branches in the code under test. Differing only in input values that don't change control flow is not a distinct scenario." in text, "expected to find: " + "Two tests are redundant if they exercise the same set of branches in the code under test. Differing only in input values that don't change control flow is not a distinct scenario."[:80]

