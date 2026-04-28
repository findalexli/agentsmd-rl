"""Behavioral checks for claude-code-boilerplate-update-typescript-typing-guidelines- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-boilerplate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'function updateUser(id: string, data: UpdateUserInput): Promise<User> { ... }' in text, "expected to find: " + 'function updateUser(id: string, data: UpdateUserInput): Promise<User> { ... }'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| Explicit types | **PREFERRED** | Always use concrete, specific types |' in text, "expected to find: " + '| Explicit types | **PREFERRED** | Always use concrete, specific types |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `unknown` | Allowed (avoid) | Acceptable but prefer explicit types |' in text, "expected to find: " + '| `unknown` | Allowed (avoid) | Acceptable but prefer explicit types |'[:80]

