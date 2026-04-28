"""Behavioral checks for cnpmcore-docs-enhance-copilot-instructions-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cnpmcore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Enterprise customization layer for PaaS integration. cnpmcore provides default implementations, but enterprises should implement their own based on their infrastructure:' in text, "expected to find: " + 'Enterprise customization layer for PaaS integration. cnpmcore provides default implementations, but enterprises should implement their own based on their infrastructure:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'These adapters allow cnpmcore to integrate with different cloud providers and enterprise systems without modifying core business logic.' in text, "expected to find: " + 'These adapters allow cnpmcore to integrate with different cloud providers and enterprise systems without modifying core business logic.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Test at the right layer** - Controller tests for HTTP, Service tests for business logic' in text, "expected to find: " + '- **Test at the right layer** - Controller tests for HTTP, Service tests for business logic'[:80]

