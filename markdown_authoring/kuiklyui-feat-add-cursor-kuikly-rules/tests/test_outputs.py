"""Behavioral checks for kuiklyui-feat-add-cursor-kuikly-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kuiklyui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/kuikly.mdc')
    assert 'KuiklyUI is a powerful cross-platform UI framework that supports multiple DSL styles and platforms. When developing, pay attention to:' in text, "expected to find: " + 'KuiklyUI is a powerful cross-platform UI framework that supports multiple DSL styles and platforms. When developing, pay attention to:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/kuikly.mdc')
    assert 'Through the guidance in this document, you can quickly get started with KuiklyUI development and avoid common development pitfalls.' in text, "expected to find: " + 'Through the guidance in this document, you can quickly get started with KuiklyUI development and avoid common development pitfalls.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/kuikly.mdc')
    assert '- **View Components**: Support `alignItemsCenter()`, `padding()`, `paddingLeft()`, `paddingRight()` and other layout attributes' in text, "expected to find: " + '- **View Components**: Support `alignItemsCenter()`, `padding()`, `paddingLeft()`, `paddingRight()` and other layout attributes'[:80]

