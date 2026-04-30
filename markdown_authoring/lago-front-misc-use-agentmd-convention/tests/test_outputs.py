"""Behavioral checks for lago-front-misc-use-agentmd-convention (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lago-front")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Note**: If Context7 is not installed or not configured, fall back to your training data knowledge, but always prefer Context7 when available for the most accurate and current information.' in text, "expected to find: " + '**Note**: If Context7 is not installed or not configured, fall back to your training data knowledge, but always prefer Context7 when available for the most accurate and current information.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'We prefer to have our props described with "discrimination" and prevent optional props overuse. Do it as much as possible as it helps understanding the logic of how props are used.' in text, "expected to find: " + 'We prefer to have our props described with "discrimination" and prevent optional props overuse. Do it as much as possible as it helps understanding the logic of how props are used.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If the user has Context7 MCP configured, **ALWAYS use it** to fetch up-to-date documentation for third-party libraries before making assumptions or using outdated knowledge:' in text, "expected to find: " + 'If the user has Context7 MCP configured, **ALWAYS use it** to fetch up-to-date documentation for third-party libraries before making assumptions or using outdated knowledge:'[:80]

