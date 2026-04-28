"""Behavioral checks for cube-docs-update-cursor-rules-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cube")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/namings-rule.mdc')
    assert '- Semantic Model IDE (short: "IDE")' in text, "expected to find: " + '- Semantic Model IDE (short: "IDE")'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/namings-rule.mdc')
    assert 'Make sure to use correct terms.' in text, "expected to find: " + 'Make sure to use correct terms.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/namings-rule.mdc')
    assert '- Semantic Model Agent' in text, "expected to find: " + '- Semantic Model Agent'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/writing-documentation.mdc')
    assert "Our cloud product codebase is located in ~/code/cubejs-enterprise (at least that is where it is located on Artyom's mac). Research the cloud product codebase when documenting new features." in text, "expected to find: " + "Our cloud product codebase is located in ~/code/cubejs-enterprise (at least that is where it is located on Artyom's mac). Research the cloud product codebase when documenting new features."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/writing-documentation.mdc')
    assert 'Our documenation is built with https://www.mintlify.com. Make sure you follow Mintlify best practices when designing documentation.' in text, "expected to find: " + 'Our documenation is built with https://www.mintlify.com. Make sure you follow Mintlify best practices when designing documentation.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/writing-documentation.mdc')
    assert 'Our competitors are [Omni](https://omni.co/) and [Hex](https://hex.tech/). We use their documentation sometimes as a reference.' in text, "expected to find: " + 'Our competitors are [Omni](https://omni.co/) and [Hex](https://hex.tech/). We use their documentation sometimes as a reference.'[:80]

