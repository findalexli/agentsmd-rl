"""Behavioral checks for agenta-improve-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agenta")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "For data fetching, use `atomWithQuery` from `jotai-tanstack-query`. This combines Jotai's reactive state with TanStack Query's caching and synchronization." in text, "expected to find: " + "For data fetching, use `atomWithQuery` from `jotai-tanstack-query`. This combines Jotai's reactive state with TanStack Query's caching and synchronization."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use **atoms** when: State needs to be shared across non-parent-child components, multiple levels of drilling, or state is module/feature-scoped' in text, "expected to find: " + '- Use **atoms** when: State needs to be shared across non-parent-child components, multiple levels of drilling, or state is module/feature-scoped'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'We previously used SWR with Axios for data fetching. This pattern is still present in older code but should not be used for new features.' in text, "expected to find: " + 'We previously used SWR with Axios for data fetching. This pattern is still present in older code but should not be used for new features.'[:80]

