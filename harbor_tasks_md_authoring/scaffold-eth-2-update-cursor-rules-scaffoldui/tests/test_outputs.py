"""Behavioral checks for scaffold-eth-2-update-cursor-rules-scaffoldui (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scaffold-eth-2")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/scaffold-eth.mdc')
    assert 'With the `@scaffold-ui/components` library, SE-2 provides a set of pre-built React components for common Ethereum use cases:' in text, "expected to find: " + 'With the `@scaffold-ui/components` library, SE-2 provides a set of pre-built React components for common Ethereum use cases:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/scaffold-eth.mdc')
    assert 'For fully customizable components, you can use the hooks from the `@scaffold-ui/hooks` library to get the data you need.' in text, "expected to find: " + 'For fully customizable components, you can use the hooks from the `@scaffold-ui/hooks` library to get the data you need.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/scaffold-eth.mdc')
    assert 'description:' in text, "expected to find: " + 'description:'[:80]

