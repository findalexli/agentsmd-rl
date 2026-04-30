"""Behavioral checks for antigravity-awesome-skills-feat-add-frontend-api-integration (markdown_authoring task).

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
    text = _read('skills/frontend-api-integration-patterns/SKILL.md')
    assert 'description: "Production-ready patterns for integrating frontend applications with backend APIs, including race condition handling, request cancellation, retry strategies, error normalization, and UI ' in text, "expected to find: " + 'description: "Production-ready patterns for integrating frontend applications with backend APIs, including race condition handling, request cancellation, retry strategies, error normalization, and UI '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/frontend-api-integration-patterns/SKILL.md')
    assert 'Most frontend issues are not caused by APIs being difficult to call, but by **incorrect handling of asynchronous behavior**—leading to race conditions, stale data, duplicated requests, and poor user e' in text, "expected to find: " + 'Most frontend issues are not caused by APIs being difficult to call, but by **incorrect handling of asynchronous behavior**—leading to race conditions, stale data, duplicated requests, and poor user e'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/frontend-api-integration-patterns/SKILL.md')
    assert "* These examples use vanilla JavaScript patterns; adapt them to your framework's data-fetching library when using React Query, SWR, Apollo, Relay, or similar tools." in text, "expected to find: " + "* These examples use vanilla JavaScript patterns; adapt them to your framework's data-fetching library when using React Query, SWR, Apollo, Relay, or similar tools."[:80]

