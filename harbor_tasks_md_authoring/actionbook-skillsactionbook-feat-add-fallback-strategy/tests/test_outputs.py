"""Behavioral checks for actionbook-skillsactionbook-feat-add-fallback-strategy (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/actionbook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert 'When Actionbook data does not work as expected, direct browser access to the target website allows for real-time retrieval of current page structure, element information, and interaction capabilities.' in text, "expected to find: " + 'When Actionbook data does not work as expected, direct browser access to the target website allows for real-time retrieval of current page structure, element information, and interaction capabilities.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert 'Actionbook stores pre-computed page data captured at indexing time. This data may become outdated as websites evolve. The following signals indicate that fallback may be necessary:' in text, "expected to find: " + 'Actionbook stores pre-computed page data captured at indexing time. This data may become outdated as websites evolve. The following signals indicate that fallback may be necessary:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert 'These conditions are not signaled in Actionbook API responses. They can only be detected during browser automation execution when selectors fail to locate the expected elements.' in text, "expected to find: " + 'These conditions are not signaled in Actionbook API responses. They can only be detected during browser automation execution when selectors fail to locate the expected elements.'[:80]

